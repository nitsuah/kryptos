from __future__ import annotations

import importlib
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

cli_mod = importlib.import_module("kryptos.cli.main")


def _invoke(argv: list[str]) -> int:
    return cli_mod.main(argv)


def _make_fake_run(root: Path) -> Path:
    run_dir = root / "run_20250101T000000"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "attempts.json").write_text("[]", encoding="utf-8")
    (run_dir / "crib_weight_sweep.csv").write_text(
        "weight,sample,baseline,with_cribs,delta\n1.0,SAMP,0.0,1.0,1.0\n",
        encoding="utf-8",
    )
    (run_dir / "weight_1_0_details.csv").write_text("sample,delta\nSAMP,1.0\n", encoding="utf-8")
    return run_dir


def test_tuning_pick_best_csv_missing(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "missing.csv"
    code = _invoke(["tuning-pick-best", "--csv", str(missing)])
    assert code == 2
    out = json.loads(capsys.readouterr().out)
    assert out["error"] == "csv_not_found"


def test_tuning_pick_best_skips_bad_rows(tmp_path: Path, capsys) -> None:
    csv_path = tmp_path / "crib_weight_sweep.csv"
    csv_path.write_text(
        "weight,sample,baseline,with_cribs,delta\n"
        "bad,row\n"
        "not,float,a,b,c\n",
        encoding="utf-8",
    )
    code = _invoke(["tuning-pick-best", "--csv", str(csv_path)])
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["best_weight"] == 0.0


def test_tuning_summarize_and_report_not_found(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "missing_run"
    code1 = _invoke(["tuning-summarize-run", "--run-dir", str(missing)])
    assert code1 == 2
    out1 = json.loads(capsys.readouterr().out)
    assert out1["error"] == "run_dir_not_found"

    code2 = _invoke(["tuning-report", "--run-dir", str(missing)])
    assert code2 == 2
    out2 = json.loads(capsys.readouterr().out)
    assert out2["error"] == "run_dir_not_found"


def test_tuning_report_no_markdown(tmp_path: Path, capsys) -> None:
    run_dir = _make_fake_run(tmp_path)
    code = _invoke(["tuning-report", "--run-dir", str(run_dir), "--no-markdown"])
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["condensed_csv"]
    assert out["markdown"] is None


def test_tuning_holdout_score_write_path(tmp_path: Path, capsys) -> None:
    out_csv = tmp_path / "holdout.csv"
    code = _invoke(["tuning-holdout-score", "--weight", "1.0", "--out", str(out_csv)])
    assert code == 0
    text = capsys.readouterr().out
    assert str(out_csv) in text
    assert out_csv.exists()


def test_autopilot_loop_mode(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setattr(cli_mod.autopilot_mod, "run_autopilot_loop", lambda **_kwargs: 7)
    code = _invoke(["autopilot", "--loop", "--iterations", "1", "--interval", "1"])
    assert code == 7
    out = json.loads(capsys.readouterr().out)
    assert out["mode"] == "loop"


def test_autonomous_modes(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Ok:
        def __init__(self, **_kwargs):
            pass

        def run_autonomous_loop(self, **_kwargs):
            return None

    class _Interrupt(_Ok):
        def run_autonomous_loop(self, **_kwargs):
            raise KeyboardInterrupt()

    class _Fail(_Ok):
        def run_autonomous_loop(self, **_kwargs):
            raise RuntimeError("boom")

    monkeypatch.setattr("kryptos.autonomous_coordinator.AutonomousCoordinator", _Ok)
    assert _invoke(["autonomous", "--max-cycles", "1", "--cycle-interval", "0"]) == 0

    monkeypatch.setattr("kryptos.autonomous_coordinator.AutonomousCoordinator", _Interrupt)
    assert _invoke(["autonomous", "--max-cycles", "1", "--cycle-interval", "0"]) == 130

    monkeypatch.setattr("kryptos.autonomous_coordinator.AutonomousCoordinator", _Fail)
    assert _invoke(["autonomous", "--max-cycles", "1", "--cycle-interval", "0"]) == 1


def test_cmd_autopilot_single_direct(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setattr(cli_mod.autopilot_mod, "run_exchange", lambda **_kwargs: Path("exchange.json"))
    args = SimpleNamespace(loop=False, plan="p", iterations=0, interval=1)
    code = cli_mod.cmd_autopilot(args)
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["mode"] == "single"
    assert out["log_path"] == "exchange.json"


def test_cmd_autonomous_direct_branches(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Logger:
        def info(self, *_args, **_kwargs):
            return None

        def exception(self, *_args, **_kwargs):
            return None

    class _Ok:
        def __init__(self, **_kwargs):
            pass

        def run_autonomous_loop(self, **_kwargs):
            return None

    class _Interrupt(_Ok):
        def run_autonomous_loop(self, **_kwargs):
            raise KeyboardInterrupt()

    class _Fail(_Ok):
        def run_autonomous_loop(self, **_kwargs):
            raise RuntimeError("boom")

    monkeypatch.setattr(cli_mod, "setup_logging", lambda **_kwargs: _Logger())
    args = SimpleNamespace(max_hours=None, max_cycles=1, cycle_interval=0, ops_cycle=0, web_intel_hours=0)

    monkeypatch.setattr("kryptos.autonomous_coordinator.AutonomousCoordinator", _Ok)
    assert cli_mod.cmd_autonomous(args) == 0

    monkeypatch.setattr("kryptos.autonomous_coordinator.AutonomousCoordinator", _Interrupt)
    assert cli_mod.cmd_autonomous(args) == 130

    monkeypatch.setattr("kryptos.autonomous_coordinator.AutonomousCoordinator", _Fail)
    assert cli_mod.cmd_autonomous(args) == 1


def test_examples_smoke_success_and_error(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    class _PurgeRes:
        def __init__(self):
            self.removed = [Path("old1")]
            self.kept = [Path("new1")]

    monkeypatch.setattr(cli_mod, "run_sections_demo", lambda: [{"name": "K1"}, {"name": "K2"}])
    monkeypatch.setattr(cli_mod, "run_tiny_weight_sweep", lambda: Path("tiny_dir"))
    monkeypatch.setattr(cli_mod, "run_composite_demo", lambda limit=5: "comp_dir")
    monkeypatch.setattr(cli_mod, "purge_demo_artifacts", lambda max_keep=4: _PurgeRes())

    code = _invoke(["examples-smoke", "--limit", "2", "--keep", "2"])
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "ok"
    assert out["sections"] == ["K1", "K2"]

    monkeypatch.setattr(cli_mod, "run_sections_demo", lambda: (_ for _ in ()).throw(RuntimeError("x")))
    code2 = _invoke(["examples-smoke"])
    assert code2 == 2
    out2 = json.loads(capsys.readouterr().out)
    assert out2["status"] == "error"


def test_cmd_examples_smoke_direct_success(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    class _PurgeRes:
        def __init__(self):
            self.removed = [Path("old2")]
            self.kept = [Path("new2")]

    monkeypatch.setattr(cli_mod, "run_sections_demo", lambda: [{"name": "K3"}])
    monkeypatch.setattr(cli_mod, "run_tiny_weight_sweep", lambda: Path("tiny2"))
    monkeypatch.setattr(cli_mod, "run_composite_demo", lambda limit=5: "comp2")
    monkeypatch.setattr(cli_mod, "purge_demo_artifacts", lambda max_keep=4: _PurgeRes())

    code = cli_mod.cmd_examples_smoke(SimpleNamespace(limit=3, keep=1))
    assert code == 0
    out = json.loads(capsys.readouterr().out)
    assert out["sections"] == ["K3"]


def test_cli_main_run_as_script(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["kryptos", "sections"])
    sys.modules.pop("kryptos.cli.main", None)
    with pytest.raises(SystemExit) as exc:
        runpy.run_module("kryptos.cli.main", run_name="__main__")
    assert exc.value.code == 0
