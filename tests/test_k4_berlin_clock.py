"""Berlin Clock key stream tests."""
import unittest
from datetime import time
from src.k4 import (
    berlin_clock_shifts,
    full_clock_state,
    full_berlin_clock_shifts,
    enumerate_clock_shift_sequences,
    make_berlin_clock_stage, Pipeline, StageResult,
)

class TestBerlinClock(unittest.TestCase):
    def test_basic_shift_pattern_generation(self):
        shifts = berlin_clock_shifts(time(13, 37, 42))
        self.assertEqual(len(shifts), 5)
        self.assertTrue(all(isinstance(x, int) for x in shifts))

    def test_full_clock_state_encoding(self):
        t = time(13, 37, 42)
        state = full_clock_state(t)
        self.assertEqual(len(state['top_hours']), 4)
        self.assertEqual(len(state['bottom_hours']), 4)
        self.assertEqual(len(state['top_minutes']), 11)
        self.assertEqual(len(state['bottom_minutes']), 4)
        self.assertEqual(len(state['seconds']), 1)
        seq = full_berlin_clock_shifts(t)
        self.assertEqual(len(seq), 4+4+11+4+1)

    def test_enumerate_sequences(self):
        seqs = enumerate_clock_shift_sequences(step_seconds=7200)  # every 2 hours
        self.assertTrue(len(seqs) > 5)
        self.assertIn('time', seqs[0])
        self.assertIn('shifts', seqs[0])

    def test_pipeline_stage(self):
        stage = make_berlin_clock_stage(step_seconds=10800, limit=10)  # every 3 hours
        pipe = Pipeline([stage])
        ct = "OBKRUOXOGHULBSOLIFB"  # shortened sample
        results = pipe.run(ct)
        self.assertEqual(len(results), 1)
        r = results[0]
        self.assertIsInstance(r, StageResult)
        self.assertIn('candidates', r.metadata)
        self.assertTrue(len(r.metadata['candidates']) <= 10)

if __name__ == '__main__':
    unittest.main()
