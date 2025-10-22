"""Hill cipher edge case tests."""

import unittest

from src.k4.hill_cipher import brute_force_crib, matrix_inv_mod


class TestHillCipherEdge(unittest.TestCase):
    def test_matrix_inv_mod_non_invertible(self):
        # Determinant 0 mod 26 => non-invertible
        mat = [[2, 4], [1, 2]]  # det = 0
        self.assertIsNone(matrix_inv_mod(mat))

    def test_brute_force_crib_limit(self):
        res = brute_force_crib("TESTTEXT", "AAAA", limit=10)
        self.assertLessEqual(len(res), 10)


if __name__ == '__main__':
    unittest.main()
