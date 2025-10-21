"""Tests for positional_crib_bonus scoring function.

Validates bonus awarded near expected indices and zero outside window.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from collections.abc import Sequence  # noqa: E402

from src.k4.scoring import positional_crib_bonus  # noqa: E402


class TestPositionalCribBonus(unittest.TestCase):
    def test_bonus_within_window(self):
        text = "XXXXBERLINYYYYCLOCKZZZZ"  # BERLIN at index 4 (0-based), CLOCK later
        # Provide expected positions near 4 with small window
        positional: dict[str, Sequence[int]] = {"BERLIN": (3, 4, 5)}
        bonus = positional_crib_bonus(text, positional, window=2)
        # Formula: 8 * len(crib) - distance (distance min should be 0)
        expected = 8 * len("BERLIN") - 0
        self.assertEqual(bonus, expected)

    def test_zero_outside_window(self):
        text = "AAAABERLINBBBB"  # BERLIN at index 4
        positional: dict[str, Sequence[int]] = {"BERLIN": (50,)}  # Far away
        bonus = positional_crib_bonus(text, positional, window=2)
        self.assertEqual(bonus, 0.0)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
