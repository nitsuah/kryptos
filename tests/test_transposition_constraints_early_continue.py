"""Test early continue path where a crib is not found causing skip of permutation."""
import unittest
from collections.abc import Sequence
from src.k4.transposition_constraints import search_with_multiple_cribs_positions


class TestTranspositionConstraintsEarlyContinue(unittest.TestCase):
    def test_missing_crib_skips(self):
        cipher = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        positional: dict[str, Sequence[int]] = {"ZZZZ": (0,), "AAAA": (0,)}
        res = search_with_multiple_cribs_positions(
            cipher,
            positional_cribs=positional,
            n_cols=4,
            max_perms=10,
            limit=5,
        )  # type: ignore[arg-type]
        self.assertIsInstance(res, list)


if __name__ == "__main__":
    unittest.main()
