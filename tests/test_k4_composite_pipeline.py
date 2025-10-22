"""Tests for composite multi-stage pipeline aggregation."""

import unittest

from src.k4 import (
    make_berlin_clock_stage,
    make_hill_constraint_stage,
    make_transposition_adaptive_stage,
    run_composite_pipeline,
)


class TestCompositePipeline(unittest.TestCase):
    def test_composite_run_aggregates_candidates(self):
        ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQ"[:40]
        stages = [
            make_hill_constraint_stage(),
            make_transposition_adaptive_stage(min_cols=5, max_cols=5, sample_perms=60, limit=8),
            make_berlin_clock_stage(step_seconds=14400, limit=5),
        ]
        result = run_composite_pipeline(ct, stages, report=False, limit=30)
        self.assertIn('aggregated', result)
        agg = result['aggregated']
        self.assertTrue(len(agg) > 0)
        self.assertIn('stage', agg[0])
        self.assertIn('score', agg[0])
        # Ensure ordering by score descending
        scores = [c['score'] for c in agg]
        self.assertEqual(scores, sorted(scores, reverse=True))
        # Ensure presence of adaptive transposition candidates
        self.assertTrue(any(c['stage'] == 'transposition-adaptive' for c in agg))


if __name__ == '__main__':
    unittest.main()
