"""Tests for pipeline pruning utility replacing legacy executor _prune."""

from kryptos.k4.pruning import prune_candidates


def test_prune_keeps_top_n_and_bonus():
    candidates = [
        {"text": "AAAA", "score": 100.0, "crib_bonus": 0.0},
        {"text": "BBBB", "score": 90.0, "crib_bonus": 0.0},
        {"text": "CLOCK BERLIN", "score": 10.0, "crib_bonus": 6.0},  # bonus outside top_n
        {"text": "CCCC", "score": 80.0, "crib_bonus": 0.0},
    ]
    pruned = prune_candidates(candidates, top_n=2, candidate_cap=6, crib_bonus_threshold=5.0)
    texts = [c["text"] for c in pruned]
    assert "AAAA" in texts and "BBBB" in texts
    assert "CLOCK BERLIN" in texts  # bonus kept


def test_prune_caps_size():
    candidates = [{"text": f"T{i}", "score": 100 - i} for i in range(10)]
    pruned = prune_candidates(candidates, top_n=3, candidate_cap=4, crib_bonus_threshold=5.0)
    assert len(pruned) <= 4
