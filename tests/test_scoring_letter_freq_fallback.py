"""Test letter frequency fallback branch by temporarily clearing LETTER_FREQ."""
import unittest
import src.k4.scoring as scoring


class TestScoringLetterFreqFallback(unittest.TestCase):
    def test_letter_freq_fallback(self):
        # Backup
        original = dict(scoring.LETTER_FREQ)
        try:
            scoring.LETTER_FREQ.clear()
            # Force fallback use by calling chi_square_stat (should not crash)
            val = scoring.chi_square_stat("TESTTEXT")
            self.assertGreaterEqual(val, 0.0)
        finally:
            scoring.LETTER_FREQ.update(original)


if __name__ == '__main__':
    unittest.main()
