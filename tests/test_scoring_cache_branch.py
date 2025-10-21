"""Test caching branch of combined_plaintext_score_cached."""
import unittest
from src.k4.scoring import combined_plaintext_score_cached

class TestScoringCacheBranch(unittest.TestCase):
    def test_cache_reuse(self):
        text = "ABCDTEXTABCDTEXT"  # repeated pattern
        first = combined_plaintext_score_cached(text)
        second = combined_plaintext_score_cached(text)
        # Values should be equal; second call hits cache (not directly assertable but branch executed)
        self.assertEqual(first, second)

if __name__ == '__main__':
    unittest.main()
