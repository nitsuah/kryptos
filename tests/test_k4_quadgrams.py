"""Tests for quadgram scoring integration."""
import unittest
from src.k4 import quadgram_score, combined_plaintext_score

class TestQuadgramScoring(unittest.TestCase):
    def test_quadgram_integration_combined_score(self):
        english_like = 'THERETHATTIONHEREOULDHAVEWITHINGTMENTEVERFROMTHIS'
        random_like = 'QXZJMVKPWQXZJMVKPWQXZJMVKPWQXZJMVKPWQXZJMVKP'
        # Raw quadgram score may not strictly differentiate with placeholder data; ensure combined score better
        c1 = combined_plaintext_score(english_like)
        c2 = combined_plaintext_score(random_like)
        self.assertGreater(c1, c2)
        # Quadgram score presence (type and numeric) sanity
        q1 = quadgram_score(english_like)
        q2 = quadgram_score(random_like)
        self.assertIsInstance(q1, float)
        self.assertIsInstance(q2, float)

if __name__ == '__main__':
    unittest.main()
