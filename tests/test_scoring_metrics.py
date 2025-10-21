"""Additional scoring metrics tests."""
import unittest
from src.k4.scoring import (
    quadgram_score,
    repeating_bigram_fraction,
    letter_entropy,
    baseline_stats,
    positional_crib_bonus,
    combined_plaintext_score_with_positions,
)


class TestScoringMetrics(unittest.TestCase):
    def test_repeating_bigram_fraction(self):
        self.assertGreater(repeating_bigram_fraction("ABABAB"), 0.0)
        self.assertEqual(repeating_bigram_fraction("ABC"), 0.0)

    def test_letter_entropy(self):
        self.assertEqual(letter_entropy(""), 0.0)
        e1 = letter_entropy("AAAA")
        e2 = letter_entropy("ABCD")
        self.assertLess(e1, e2)

    def test_baseline_stats_keys(self):
        stats = baseline_stats("SAMPLETEXT")
        for key in [
            'chi_square', 'bigram_score', 'trigram_score', 'quadgram_score', 'crib_bonus', 'combined_score',
            'index_of_coincidence', 'vowel_ratio', 'letter_coverage', 'letter_entropy', 'repeating_bigram_fraction',
            'wordlist_hit_rate', 'trigram_entropy', 'bigram_gap_variance',
        ]:
            self.assertIn(key, stats)

    def test_positional_crib_bonus(self):
        bonus = positional_crib_bonus("AAAAATESTTEXT", {"TEST": [5]}, window=2)
        self.assertGreater(bonus, 0.0)
        self.assertEqual(positional_crib_bonus("NOPE", {"TEST": [0]}), 0.0)

    def test_combined_plaintext_score_with_positions(self):
        score_plain = quadgram_score("TESTTEXT")
        score_pos = combined_plaintext_score_with_positions("TESTTEXT", {"TEST": [0]}, window=1)
        self.assertGreaterEqual(score_pos, score_plain)


if __name__ == '__main__':
    unittest.main()
