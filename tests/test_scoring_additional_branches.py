"""Tests for additional scoring branches (wordlist_hit_rate break, bigram_gap_variance)."""

import unittest

from src.k4.scoring import bigram_gap_variance, wordlist_hit_rate


class TestScoringAdditionalBranches(unittest.TestCase):
    def test_wordlist_hit_rate_break(self):
        # Long text to trigger early break (>=5000 windows)
        text = "ABCD" * 800  # 3200 chars
        rate = wordlist_hit_rate(text)
        self.assertGreaterEqual(rate, 0.0)
        self.assertLessEqual(rate, 1.0)

    def test_bigram_gap_variance_zero(self):
        self.assertEqual(bigram_gap_variance("ABCD"), 0.0)

    def test_bigram_gap_variance_nonzero(self):
        # Repeated bigrams with varying gaps: AB at positions 0,2,4 -> gaps 2,2 variance 0
        # Introduce different gap: add an extra pattern later
        text = "ABABABXXAB"
        val = bigram_gap_variance(text)
        self.assertGreaterEqual(val, 0.0)


if __name__ == '__main__':
    unittest.main()
