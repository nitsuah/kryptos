"""
 Unit tests for K4 transposition functions.
"""
import unittest
from src.k4 import search_columnar, apply_columnar_permutation

class TestK4Transposition(unittest.TestCase):
    """Test cases for K4 transposition functions."""
    def test_apply_columnar_permutation_roundtrip_shape(self):
        """Test applying a columnar permutation returns text of expected length & character set."""
        ct = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        perm = (2, 0, 1, 3, 4)
        pt = apply_columnar_permutation(ct, 5, perm)
        self.assertTrue(len(pt) <= len(ct))
        self.assertTrue(all(c.isalpha() for c in pt))

    def test_search_columnar_runs(self):
        """Test that search_columnar runs and returns results."""
        ct = 'THISISATESTOFTRANSPOSEDONPLAINTEXTSEGMENT'
        results = search_columnar(ct, min_cols=5, max_cols=5, max_perms_per_width=10)
        self.assertTrue(len(results) > 0)
        self.assertIn('score', results[0])
        # Scores should be numeric
        self.assertIsInstance(results[0]['score'], float)

if __name__ == '__main__':
    unittest.main()
