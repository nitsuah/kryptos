"""Tests empty positional crib path for transposition constraints."""

import unittest

from kryptos.k4.transposition_constraints import search_with_multiple_cribs_positions


class TestTranspositionConstraintsEmpty(unittest.TestCase):
    def test_empty_positional_dict_returns_empty(self):
        res = search_with_multiple_cribs_positions("ABCDEF", {}, n_cols=3)
        self.assertEqual(res, [])


if __name__ == '__main__':
    unittest.main()
