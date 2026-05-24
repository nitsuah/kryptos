from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from kryptos import autopilot
from kryptos.pipeline.k4_campaign import K4CampaignOrchestrator


class _Res:
    def __init__(self, code: int = 0, out: str = "") -> None:
        self.returncode = code
        self.stdout = out


def test_k4_campaign_init_and_exception_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    orch = K4CampaignOrchestrator(workspace_dir=tmp_path)
    assert orch.workspace_dir == tmp_path
    assert isinstance(orch.cribs, list)

    monkeypatch.setattr(
        "kryptos.pipeline.k4_campaign.recover_key_by_frequency",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    pt, conf = orch.execute_vigenere_attack("ABC", 4)
    assert pt is None and conf == 0.0

    monkeypatch.setattr(
        "kryptos.pipeline.k4_campaign.solve_columnar_permutation_simulated_annealing_multi_start",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    pt2, score2 = orch.execute_transposition_attack("ABCD", 9, method="simulated_annealing")
    assert pt2 is None and score2 == 0.0


def test_k4_campaign_run_campaign_time_break(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    orch = object.__new__(K4CampaignOrchestrator)
    orch.workspace_dir = tmp_path
    orch.log = SimpleNamespace(warning=lambda *_args, **_kwargs: None)
    orch.attack_generator = SimpleNamespace(
        generate_comprehensive_queue=lambda **_kwargs: [
            SimpleNamespace(parameters=SimpleNamespace(cipher_type="vigenere", key_or_params={"key_length": 4})),
            SimpleNamespace(parameters=SimpleNamespace(cipher_type="vigenere", key_or_params={"key_length": 5})),
        ],
    )
    orch.execute_attack = lambda *_args, **_kwargs: ("TEXT", 0.9)
    orch.validator = SimpleNamespace(
        validate=lambda _t: SimpleNamespace(is_valid=True, confidence=0.95, to_dict=lambda: {"ok": True}),
    )
    orch.search_space = SimpleNamespace(get_coverage_report=lambda: {"cov": 1})

    class _FakeDT:
        ticks = 0

        @classmethod
        def now(cls):
            from datetime import datetime, timedelta

            base = datetime(2025, 1, 1, 0, 0, 0)
            cls.ticks += 1
            return base + timedelta(seconds=2 * cls.ticks)

    monkeypatch.setattr("kryptos.pipeline.k4_campaign.datetime", _FakeDT)

    result = orch.run_campaign("OBKRUOX", max_attacks=2, max_time_seconds=1.0)
    assert result.total_attacks == 1


def test_autopilot_helpers_and_recommendations(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    state_path = tmp_path / "state.json"
    monkeypatch.setattr(autopilot, "STATE_PATH", state_path)
    state_path.write_text("{broken", encoding="utf-8")
    assert autopilot._load_state() == {}

    repo_root = tmp_path / "repo"
    agents_dir = repo_root / "agents"
    scripts_dir = repo_root / "scripts"
    tr_dir = tmp_path / "runs"
    dec_dir = tmp_path / "decisions"
    for d in (agents_dir, scripts_dir, tr_dir, dec_dir):
        d.mkdir(parents=True, exist_ok=True)

    (agents_dir / "q.prompt").write_text("Q prompt", encoding="utf-8")
    (agents_dir / "ops.prompt").write_text("OPS prompt", encoding="utf-8")
    (agents_dir / "spy.prompt").write_text("SPY prompt", encoding="utf-8")

    monkeypatch.setattr(autopilot, "REPO_ROOT", repo_root)
    monkeypatch.setattr(autopilot, "DECISIONS_DIR", dec_dir)
    monkeypatch.setattr(autopilot, "get_tuning_runs_root", lambda: tr_dir)

    # has_ops=False path
    rec1, _just1, plan1 = autopilot.recommend_next_action()
    assert rec1 == "finish OPS automation"
    assert plan1["action"] == "noop"

    # has_artifacts=True and has_spy=False path
    (scripts_dir / "tuning.py").write_text("# ok", encoding="utf-8")
    (tr_dir / "run1").mkdir(parents=True, exist_ok=True)

    real_import = __import__

    def _fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "kryptos.spy.extractor":
            raise ImportError("missing")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", _fake_import)
    rec2, _just2, plan2 = autopilot.recommend_next_action()
    assert rec2 == "implement SPY extractor"
    assert plan2["action"] == "analyze_artifacts"

    # defaults in persona prompt map
    monkeypatch.setattr(autopilot, "_load_state", lambda: {"learned": [{"persona": "Q", "note": "n"}]})
    prompts = autopilot._persona_prompts()
    assert "Q" in prompts and "OPS" in prompts and "SPY" in prompts

    # default recommendation branch when ops+spy are available
    monkeypatch.setattr("builtins.__import__", real_import)
    rec3, _just3, plan3 = autopilot.recommend_next_action()
    assert rec3 == "push branch & open PR"
    assert plan3["action"] == "push_pr"

    # _simulate_action remaining branches
    assert "Reviewed plan" in autopilot._simulate_action("SPY", "PLAN_CHECK: test")
    assert "Recommendation" in autopilot._simulate_action("Q", "PLAN_CHECK: test")
    assert "crib_weight_sweep" in autopilot._simulate_action("OPS", "PLAN_CHECK: crib_weight_sweep")
    assert autopilot._simulate_action("OTHER", "x") == "UNKNOWN_PERSONA"


def test_autopilot_exchange_and_loop_branches(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    log_dir = tmp_path / "logs"
    dec_dir = tmp_path / "decisions"
    state_path = tmp_path / "state.json"
    log_dir.mkdir(parents=True, exist_ok=True)
    dec_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(autopilot, "LOG_DIR", log_dir)
    monkeypatch.setattr(autopilot, "DECISIONS_DIR", dec_dir)
    monkeypatch.setattr(autopilot, "STATE_PATH", state_path)

    monkeypatch.setattr(
        autopilot,
        "_persona_prompts",
        lambda: {"Q": "q", "OPS": "o", "SPY": "s"},
    )
    monkeypatch.setattr(
        autopilot,
        "_simulate_action",
        lambda name, prompt: f"{name}:{prompt} LEARN: ok" if name != "OPS" else "OPS_SUMMARY",
    )
    monkeypatch.setattr(autopilot, "recommend_next_action", lambda: ("push branch & open PR", "ok", {"action": "x"}))
    monkeypatch.setattr(autopilot, "_update_cribs_from_spy", lambda **_kwargs: (_ for _ in ()).throw(ValueError("x")))

    out = autopilot.run_exchange(plan_text=None, autopilot=True)
    assert out.exists()
    printed = capsys.readouterr().out
    assert "recommendation" in printed
    assert "Warning: crib update failed" in printed

    assert autopilot._latest_decision() is None
    (dec_dir / "a.json").write_text("not-json", encoding="utf-8")

    class _Logger:
        def info(self, *_args, **_kwargs):
            pass

        def exception(self, *_args, **_kwargs):
            pass

    calls = {"n": 0}

    def _fake_run_exchange(**_kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("recoverable")
        return out

    monkeypatch.setattr(autopilot, "run_exchange", _fake_run_exchange)
    monkeypatch.setattr(autopilot, "setup_logging", lambda **_kwargs: _Logger())
    monkeypatch.setattr(autopilot.time, "sleep", lambda *_args, **_kwargs: None)

    # Invalid precision path in _decision_safe
    assert autopilot._decision_safe({"holdout_pass": True, "spy_precision": "bad"}, 0.9) is False

    code = autopilot.run_autopilot_loop(iterations=2, interval=0, plan="p")
    assert code == 0


def test_autopilot_crib_update_and_sleep_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("kryptos.spy.crib_store.load_promoted_cribs", lambda: ["A"])
    monkeypatch.setattr("kryptos.spy.crib_store.promote_cribs", lambda _obs: ["A", "B"])
    update = autopilot._update_cribs_from_spy("run")
    assert update["cribs_total"] == 2 and update["new"] == 1

    # Hit run_autopilot_loop sleep path (unsafe decision + no iteration cap on first cycle).
    class _Logger:
        def info(self, *_args, **_kwargs):
            pass

        def exception(self, *_args, **_kwargs):
            pass

    calls = {"n": 0}

    def _fake_exchange(**_kwargs):
        _ = _kwargs
        calls["n"] += 1
        return None

    monkeypatch.setattr(autopilot, "run_exchange", _fake_exchange)
    monkeypatch.setattr(autopilot, "setup_logging", lambda **_kwargs: _Logger())
    monkeypatch.setattr(autopilot, "_latest_decision", lambda: Path("decision.json"))
    monkeypatch.setattr(Path, "read_text", lambda self, encoding="utf-8": '{"holdout_pass": false}', raising=False)
    monkeypatch.setattr(autopilot.time, "sleep", lambda *_args, **_kwargs: None)

    code = autopilot.run_autopilot_loop(iterations=2, interval=0, plan="p")
    assert code == 0
