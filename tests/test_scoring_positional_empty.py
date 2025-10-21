"""Test positional crib bonus early exit and combined score with no positional bonus."""
import unittest
from src.k4.scoring import positional_crib_bonus, combined_plaintext_score_with_positions, combined_plaintext_score

class TestScoringPositionalEmpty(unittest.TestCase):
    def test_positional_crib_bonus_empty(self):
        self.assertEqual(positional_crib_bonus("TEXT", {}), 0.0)

    def test_combined_plaintext_score_with_positions_no_bonus(self):
        base = combined_plaintext_score("TEXT")
        augmented = combined_plaintext_score_with_positions("TEXT", {}, window=2)
        self.assertEqual(base, augmented)

if __name__ == '__main__':
    unittest.main()
