"""Test composite reporting path when adaptive False and no weights (aggregated artifact source)."""
import unittest
from src.k4 import run_composite_pipeline, make_hill_constraint_stage, make_masking_stage

class TestCompositeReportNoWeights(unittest.TestCase):
    def test_report_without_weights_no_adaptive(self):
        stages = [
            make_hill_constraint_stage(partial_len=15, partial_min=-900.0),
            make_masking_stage(limit=5),
        ]
        res = run_composite_pipeline(
            "OBKRUOXOGHULB",
            stages,
            report=True,
            adaptive=False,
            weights=None,
            normalize=True,
            limit=5,
        )
        self.assertIn('artifacts', res)
        self.assertIn('attempt_log', res)

if __name__ == '__main__':
    unittest.main()
