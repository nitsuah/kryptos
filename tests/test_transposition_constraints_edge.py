"""Edge case tests for transposition constraints module."""
import unittest
from src.k4.transposition_constraints import (
    invert_columnar,
    search_with_crib,
    search_with_crib_at_position,
    search_with_multiple_cribs_positions,
)

CIPHER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

class TestTranspositionConstraintsEdge(unittest.TestCase):
    def test_invert_columnar_roundtrip(self):
        ct = CIPHER
        perm = (0, 1, 2, 3, 4)
        pt = invert_columnar(ct, 5, perm)
        self.assertEqual(len(pt), len(ct))

    def test_search_with_crib_none_found(self):
        results = search_with_crib(CIPHER, "ZZZZ", 5, max_perms=10)
        self.assertEqual(results, [])

    def test_search_with_crib_at_position_outside_window(self):
        results = search_with_crib_at_position(CIPHER, "ABCDE", 5, expected_index=20, window=1, max_perms=10)
        # crib appears at index 0; out of window so expect empty
        self.assertEqual(results, [])

    def test_search_with_multiple_cribs_positions_empty(self):
        results = search_with_multiple_cribs_positions(CIPHER, {"ZZZ": [0]}, 5, max_perms=10)
        self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()
