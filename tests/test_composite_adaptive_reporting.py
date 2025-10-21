"""Tests covering adaptive fusion and reporting attempt log path for composite pipeline."""
import os
import unittest
from src.k4 import run_composite_pipeline, make_hill_constraint_stage, make_masking_stage

class TestCompositeAdaptiveReporting(unittest.TestCase):
    def test_adaptive_weights_present_and_attempt_log(self):
        stages = [
            make_hill_constraint_stage(partial_len=20, partial_min=-900.0),
            make_masking_stage(limit=5),
        ]
        res = run_composite_pipeline(
            "OBKRUOXOGHULBSOLIFB",  # short slice
            stages,
            report=True,
            adaptive=True,
            limit=10,
        )
        self.assertIn('profile', res)
        diag = res['profile'].get('adaptive_diagnostics')
        self.assertIsInstance(diag, dict)
        self.assertTrue(diag)
        self.assertIn('attempt_log', res)
        self.assertTrue(os.path.exists(res['attempt_log']))

if __name__ == '__main__':
    unittest.main()
