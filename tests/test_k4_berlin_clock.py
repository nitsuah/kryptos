"""Skipped tests for Berlin Clock key stream generator."""
import unittest
from datetime import time
from src.k4 import berlin_clock_shifts, apply_clock_shifts

class TestBerlinClock(unittest.TestCase):
    @unittest.skip("Berlin Clock hypothesis tests deferred")
    def test_shift_pattern_generation(self):
        shifts = berlin_clock_shifts(time(13, 37, 42))
        self.assertEqual(len(shifts), 5)

    @unittest.skip("Berlin Clock hypothesis tests deferred")
    def test_apply_shifts_length(self):
        ct = "OBKRUOXOGHULB"  # sample
        shifts = berlin_clock_shifts(time(13, 37, 42))
        pt = apply_clock_shifts(ct, shifts)
        self.assertEqual(len(pt), len(ct))

if __name__ == '__main__':
    unittest.main()
