"""Tests for attempt log persistence artifact."""
import unittest
import os
from glob import glob
from src.k4 import (
    make_hill_constraint_stage,
    make_transposition_adaptive_stage,
    make_berlin_clock_stage,
    run_composite_pipeline,
    persist_attempt_logs
)

CIPHER_SAMPLE = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQ"

class TestAttemptLogging(unittest.TestCase):
    def test_persist_attempt_logs(self):
        stages = [
            make_hill_constraint_stage(partial_len=40, partial_min=-900.0),
            make_transposition_adaptive_stage(min_cols=5, max_cols=5, sample_perms=30, partial_length=30, limit=5),
            make_berlin_clock_stage(step_seconds=21600, limit=5),
        ]
        # Run composite to populate attempt logs
        run_composite_pipeline(CIPHER_SAMPLE, stages, report=False, limit=20)
        path = persist_attempt_logs(out_dir='reports', label='TEST', clear=True)
        self.assertTrue(os.path.exists(path))
        with open(path, 'r', encoding='utf-8') as fh:
            data = fh.read()
        self.assertIn('hill_attempts', data)
        self.assertIn('clock_attempts', data)
        self.assertIn('transposition_attempts', data)

    def test_attempt_log_clear(self):
        stages = [make_hill_constraint_stage(partial_len=30, partial_min=-950.0)]
        run_composite_pipeline(CIPHER_SAMPLE, stages, report=False, limit=10)
        path = persist_attempt_logs(out_dir='reports', label='CLR', clear=True)
        # Second write should have zero counts after clear
        path2 = persist_attempt_logs(out_dir='reports', label='CLR2', clear=True)
        with open(path2, 'r', encoding='utf-8') as fh:
            data2 = fh.read()
        self.assertIn('"hill": 0', data2)

if __name__ == '__main__':
    unittest.main()
