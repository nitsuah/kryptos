from __future__ import annotations

from kryptos.k4.tuning import (
    compare_crib_integration,
    pick_best_weight_from_rows,
    run_crib_weight_sweep,
    tiny_param_sweep,
)


def test_run_crib_weight_sweep_and_pick_best():
    cribs = ["LIGHT", "MAGNETIC", "SHADOWS"]
    rows = run_crib_weight_sweep(weights=[0.1, 0.5], cribs=cribs)
    assert rows, "expected rows from sweep"
    weights = {r.weight for r in rows}
    assert weights == {0.1, 0.5}
    best = pick_best_weight_from_rows(rows)
    # sanity: best must be one of provided
    assert best in weights


def test_tiny_param_sweep_structure():
    res = tiny_param_sweep()
    assert len(res) >= 1
    first = res[0]
    assert {"run_id", "chi_weight", "ngram_weight", "crib_bonus", "top_sample", "top_score"} <= set(first)


def test_compare_crib_integration():
    cribs = ["LIGHT"]
    rows = compare_crib_integration(cribs=cribs)
    assert rows
    keys = {"sample", "baseline_combined", "with_cribs_combined", "crib_count"}
    assert keys <= set(rows[0])
    assert rows[0]["crib_count"] >= 0
