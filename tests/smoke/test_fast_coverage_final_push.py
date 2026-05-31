from __future__ import annotations

import csv
import runpy
import sys
from pathlib import Path

import pytest

from kryptos.k4 import report as k4_report
from kryptos.k4 import transposition
from kryptos.k4.tuning import artifacts as art
from kryptos.meta_coordinator import AgentStatus, MetaCoordinator, TaskPriority, demo_meta_coordinator
from kryptos.spy import extractor as spy_extractor
from kryptos.tuning import spy_eval


def test_report_edge_branches(tmp_path: Path) -> None:
    # CondensedRow.as_dict
    row = k4_report.CondensedRow(1.0, 2.0, "abc")
    assert row.as_dict()["weight"] == 1.0

    # Missing parse file
    assert k4_report._parse_weight_details(tmp_path / "missing.csv") == []

    run_dir = tmp_path / "run_x"
    run_dir.mkdir()

    # Bad weight filename and empty samples branch.
    (run_dir / "weight_bad_details.csv").write_text("sample,delta\na,1\n", encoding="utf-8")
    (run_dir / "weight_1_0_details.csv").write_text("sample,delta\na,notnum\n", encoding="utf-8")

    # build_condensed_rows missing run dir branch
    assert k4_report.build_condensed_rows(tmp_path / "no_run") == []

    # No valid samples due to parse errors
    assert k4_report.build_condensed_rows(run_dir) == []

    # Create valid condensed report source with one invalid CSV row.
    condensed = run_dir / "condensed_report.csv"
    condensed.write_text("weight,top_delta,sample_snippet\n1.0,ok,txt\n2.0,1.5,good\n", encoding="utf-8")

    # Learned lines absent branch.
    assert k4_report._load_learned_lines(tmp_path) == []

    # Prepare detail file + learned match branch.
    detail = run_dir / "weight_2_0_details.csv"
    detail.write_text("sample,delta\nS,1\n", encoding="utf-8")
    learned_dir = tmp_path / "agents"
    learned_dir.mkdir(parents=True, exist_ok=True)
    (learned_dir / "LEARNED.md").write_text("weight_2_0_details.csv HIT\n", encoding="utf-8")

    # Patch repo root so learned lines are loaded from tmp.
    old_get_repo_root = k4_report.get_repo_root
    k4_report.get_repo_root = lambda: tmp_path
    try:
        out_md = k4_report.write_top_candidates_markdown(run_dir, out_dir=tmp_path / "reports", top_n=2)
    finally:
        k4_report.get_repo_root = old_get_repo_root

    md = out_md.read_text(encoding="utf-8")
    assert "SPY matches" in md


def test_meta_coordinator_edge_branches(monkeypatch, tmp_path: Path, capsys) -> None:
    coord = MetaCoordinator(cache_dir=tmp_path)

    # complete_task unknown id
    coord.complete_task("missing", {}, success=True)

    t_spy = coord.assign_task("SPY", "a", "d", priority=TaskPriority.HIGH)
    t_linguist = coord.assign_task(
        "LINGUIST",
        "b",
        "d",
        priority=TaskPriority.LOW,
        dependencies=["missing_dep"],
    )

    # Wrong agent skip path in get_next_task
    assert coord.get_next_task("LINGUIST") is None

    # Dependencies unmet path via get_next_task
    assert coord.get_next_task("LINGUIST") is None

    # Invalid reallocation agent path
    coord.reallocate_resources("NOT_REAL", boost_percent=10)

    # Direct dependency missing branch
    assert coord._dependencies_met(t_linguist) is False

    # Demo + __main__ coverage lines
    demo_meta_coordinator()
    out = capsys.readouterr().out
    assert "META-COORDINATOR DEMO" in out

    monkeypatch.setattr(sys, "argv", ["meta"])
    sys.modules.pop("kryptos.meta_coordinator", None)
    runpy.run_module("kryptos.meta_coordinator", run_name="__main__")


def test_spy_extractor_edge_branches(tmp_path: Path, monkeypatch) -> None:
    # find_latest_run no dir
    monkeypatch.setattr(spy_extractor, "REPO", tmp_path)
    assert spy_extractor.find_latest_run() is None

    tr = tmp_path / "artifacts" / "tuning_runs"
    tr.mkdir(parents=True, exist_ok=True)
    assert spy_extractor.find_latest_run() is None

    run_dir = tr / "run_1"
    run_dir.mkdir()
    assert spy_extractor.find_latest_run() == run_dir

    # scan_run invalid delta + non-positive delta branch
    details = run_dir / "weight_1_0_details.csv"
    details.write_text("sample,delta\nAAA,notnum\nBBB,0\nCCC,1.0\n", encoding="utf-8")
    matches = spy_extractor.scan_run(run_dir, {"CCC"})
    assert matches and matches[0].confidence == 1.0

    # extract no run branch
    monkeypatch.setattr(spy_extractor, "find_latest_run", lambda: None)
    assert spy_extractor.extract(min_conf=0.0, run_dir=None) == []

    # extract confidence filter continue branch
    monkeypatch.setattr(spy_extractor, "find_latest_run", lambda: run_dir)
    monkeypatch.setattr(spy_extractor, "load_cribs", lambda _p=spy_extractor.CRIBS_DEFAULT: {"CCC"})
    monkeypatch.setattr(
        spy_extractor,
        "scan_run",
        lambda _run, _cribs: [spy_extractor.SpyMatch("f.csv", ("CCC",), 1.0, 0.2)],
    )
    assert spy_extractor.extract(min_conf=0.9, run_dir=None) == []


def test_transposition_edge_branches(monkeypatch) -> None:
    # n_cols <= 0
    assert transposition.apply_columnar_permutation("ABC", 0, tuple()) == "ABC"

    # prune branch with continue
    monkeypatch.setattr(transposition, "_partial_score", lambda _t, _l: -999.0)
    out = transposition.search_columnar("ABCDEFG", min_cols=2, max_cols=2, max_perms_per_width=2, prune=True, partial_min_score=0)
    assert out == []

    # adaptive prune + cache trim + early stop pass line
    monkeypatch.setattr(transposition, "_partial_score", lambda _t, _l: 1.0)
    monkeypatch.setattr(transposition, "combined_plaintext_score", lambda _t: 2000.0)
    res = transposition.search_columnar_adaptive(
        "ABCDEFGH",
        min_cols=2,
        max_cols=2,
        sample_perms=2,
        prefix_len=1,
        prefix_cache_max=1,
        early_stop_threshold=1500.0,
    )
    assert res


def test_artifacts_edge_branches(tmp_path: Path, monkeypatch) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    # Missing match file
    assert art._clean_match_file(run_dir / "none.csv") == []

    mf = run_dir / "matches_weight_1_0.csv"
    mf.write_text("sample,matched_cribs\n\nS,\nT,B|A|B\n", encoding="utf-8")
    cleaned = art.clean_all_match_files(run_dir)
    assert "1_0" in cleaned

    # Missing sweep csv
    assert art.load_weight_sweep_csv(tmp_path / "nope") == []

    sweep = run_dir / "crib_weight_sweep.csv"
    with sweep.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["weight", "sample", "base", "with", "delta"])
        w.writerow(["1.0", "SAMPLE", "0", "0", "x"])  # invalid delta
        w.writerow(["short"])  # short row
        w.writerow(["2.0", "HELLO", "0", "0", "1.5"])

    summary = art.summarize_run(run_dir)
    assert summary["top_deltas"]

    # Force line 116 path by returning non-existing file in iterator.
    monkeypatch.setattr(art, "find_match_files", lambda _run: [run_dir / "missing_matches.csv"])
    assert art.crib_hit_counts(run_dir) == {}

    # malformed lines and empty crib entries paths
    monkeypatch.setattr(art, "find_match_files", lambda _run: [mf])
    counts = art.crib_hit_counts(run_dir)
    assert isinstance(counts, dict)


def test_spy_eval_remaining_branches(tmp_path: Path) -> None:
    labels = tmp_path / "labels.csv"
    # row with one element triggers index error path currently uncovered
    labels.write_text("run_only\n", encoding="utf-8")

    with pytest.raises(IndexError):
        spy_eval.load_labels(labels)

    # thresholds empty evaluate map branch in select_best_threshold.
    valid_labels = tmp_path / "labels_valid.csv"
    valid_labels.write_text("run_a,TOK\n", encoding="utf-8")
    runs = tmp_path / "runs"
    runs.mkdir()
    assert spy_eval.select_best_threshold(valid_labels, runs, thresholds=[], extractor=lambda _r, _t: set()) == 0.0
