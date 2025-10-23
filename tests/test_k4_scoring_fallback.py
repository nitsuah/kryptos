"""Tests for scoring fallback behavior when n-gram tables are empty.

Ensures combined_plaintext_score still returns a finite float and does not raise.
"""

from __future__ import annotations

import math
import unittest

from kryptos.k4 import scoring as scoring_mod

combined_plaintext_score = scoring_mod.combined_plaintext_score


class TestScoringFallback(unittest.TestCase):
    def test_score_with_empty_ngrams(self):
        text = "THISISATESTPLAINTEXTWITHSOMECOMMONTERMSBERLINCLOCK"
        original = combined_plaintext_score(text)
        # Backup original tables
        big = dict(scoring_mod.BIGRAMS)
        tri = dict(scoring_mod.TRIGRAMS)
        quad = dict(scoring_mod.QUADGRAMS)
        try:
            scoring_mod.BIGRAMS.clear()
            scoring_mod.TRIGRAMS.clear()
            scoring_mod.QUADGRAMS.clear()
            fallback = combined_plaintext_score(text)
        finally:
            scoring_mod.BIGRAMS.update(big)
            scoring_mod.TRIGRAMS.update(tri)
            scoring_mod.QUADGRAMS.update(quad)
        self.assertIsInstance(fallback, float)
        self.assertFalse(math.isnan(fallback))
        self.assertTrue(math.isfinite(fallback))
        # Fallback may differ (can rise if chi-square penalty shifts relative weight). Assert stability bounds.
        diff = abs(fallback - original)
        self.assertLess(diff, 500.0, msg=f"Fallback diverged too much: original={original}, fallback={fallback}")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
