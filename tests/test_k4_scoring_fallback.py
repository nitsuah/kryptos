"""Tests for scoring fallback behavior when n-gram tables are empty.

Ensures combined_plaintext_score still returns a finite float and does not raise.
"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.k4 import combined_plaintext_score  # noqa: E402
from src.k4 import scoring as scoring_mod  # noqa: E402


class TestScoringFallback(unittest.TestCase):
    def test_score_with_empty_ngrams(self):
        text = "THISISATESTPLAINTEXTWITHSOMECOMMONTERMSBERLINCLOCK"
        original = combined_plaintext_score(text)
        # Backup original tables
        big = scoring_mod.BIGRAMS
        tri = scoring_mod.TRIGRAMS
        quad = scoring_mod.QUADGRAMS
        try:
            scoring_mod.BIGRAMS = {}
            scoring_mod.TRIGRAMS = {}
            scoring_mod.QUADGRAMS = {}
            fallback = combined_plaintext_score(text)
        finally:
            scoring_mod.BIGRAMS = big
            scoring_mod.TRIGRAMS = tri
            scoring_mod.QUADGRAMS = quad
        self.assertIsInstance(fallback, float)
        self.assertFalse(math.isnan(fallback))
        self.assertTrue(math.isfinite(fallback))
        # Fallback may differ (can rise if chi-square penalty shifts relative weight). Assert stability bounds.
        diff = abs(fallback - original)
        self.assertLess(diff, 500.0, msg=f"Fallback diverged too much: original={original}, fallback={fallback}")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
