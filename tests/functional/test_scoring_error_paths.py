"""Tests for scoring error/fallback behaviors."""

import math

from kryptos.k4.scoring import baseline_stats, bigram_score, combined_plaintext_score, quadgram_score, trigram_score


def test_empty_text_scores_zero_for_ngrams():
    assert bigram_score("") == 0.0
    assert trigram_score("") == 0.0
    # quadgram may be 0 if table loaded; ensure non-negative
    assert quadgram_score("") == 0.0


def test_combined_plaintext_score_empty_negative_infinite():
    score = combined_plaintext_score("")
    assert math.isinf(score) and score < 0


def test_baseline_stats_empty_text():
    stats = baseline_stats("")
    assert stats["bigram_score"] == 0.0
    assert stats["crib_bonus"] == 0.0
    assert stats["rarity_weighted_crib_bonus"] == 0.0
