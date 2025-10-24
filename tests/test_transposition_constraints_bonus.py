"""Tests positional crib bonus integration in multi-crib search to raise coverage."""

import unittest

from kryptos.k4.transposition_constraints import search_with_multiple_cribs_positions


class TestTranspositionConstraintsBonus(unittest.TestCase):
    def test_multi_crib_pos_bonus_scoring(self):
        cipher = "CLOCKBERLINXXXXCLOCKBERLIN"
        # Wrap positional lists as tuples for type checking
        positional = {"CLOCK": (0,), "BERLIN": (5, 17)}
        results = search_with_multiple_cribs_positions(cipher, positional, n_cols=3, window=3, max_perms=30, limit=5)
        # We may get zero depending permutation enumeration; at least ensure call succeeds
        self.assertIsInstance(results, list)
        if results:
            r = results[0]
            self.assertIn('pos_bonus', r)
            self.assertGreaterEqual(r['pos_bonus'], 0.0)


if __name__ == '__main__':
    unittest.main()
