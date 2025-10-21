"""Tests for hill_search.score_decryptions."""
import unittest
from src.k4.hill_search import score_decryptions

class TestHillSearchModule(unittest.TestCase):
    def test_score_decryptions_empty_keys(self):
        res = score_decryptions("ABC", [])
        self.assertEqual(res, [])

    def test_score_decryptions_with_key(self):
        # 2x2 identity key
        key = [[1, 0], [0, 1]]
        res = score_decryptions("ABCD", [key])
        self.assertEqual(len(res), 1)
        self.assertIn('score', res[0])
        self.assertIn('text', res[0])

if __name__ == '__main__':
    unittest.main()
