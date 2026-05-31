"""Tests for attempt log persistence artifact."""

import os
import unittest

from kryptos.k4.attempt_logging import persist_attempt_logs
from kryptos.k4.composite import run_composite_pipeline
from kryptos.k4.pipeline import (
    make_berlin_clock_stage,
    make_hill_constraint_stage,
    make_transposition_adaptive_stage,
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
        log_path = persist_attempt_logs(out_dir=None, label='TEST', clear=True)
        self.assertTrue(os.path.exists(log_path))
        with open(log_path, encoding='utf-8') as fh:
            data = fh.read()
        self.assertIn('hill_attempts', data)
        self.assertIn('clock_attempts', data)
        self.assertIn('transposition_attempts', data)

    def test_attempt_log_clear(self):
        stages = [make_hill_constraint_stage(partial_len=30, partial_min=-950.0)]
        run_composite_pipeline(CIPHER_SAMPLE, stages, report=False, limit=10)
        persist_attempt_logs(out_dir=None, label='CLR', clear=True)
        second_path = persist_attempt_logs(out_dir=None, label='CLR2', clear=True)
        with open(second_path, encoding='utf-8') as fh:
            data2 = fh.read()
        self.assertIn('"hill": 0', data2)


if __name__ == '__main__':
    unittest.main()
