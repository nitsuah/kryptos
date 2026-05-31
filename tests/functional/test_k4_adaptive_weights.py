"""Tests for adaptive fusion weighting logic."""

import unittest

from kryptos.k4 import (
    adaptive_fusion_weights,
    make_hill_constraint_stage,
    make_route_transposition_stage,
    run_composite_pipeline,
)

CIPHER_SAMPLE = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQ"


class TestAdaptiveFusionWeights(unittest.TestCase):
    """Test adaptive fusion weights computation and integration in composite pipeline."""

    def test_adaptive_fusion_weights_range(self):
        """Test that adaptive fusion weights are computed within expected range"""
        # Build mock candidates across stages
        candidates = [
            {'stage': 'A', 'score': 100, 'text': 'AAAAA' * 10},
            {'stage': 'B', 'score': 200, 'text': 'CLOCKBERLIN' * 5},
            {'stage': 'C', 'score': 150, 'text': 'BERLINCLOCK' * 5},
        ]
        weights = adaptive_fusion_weights(candidates)
        self.assertTrue(all(0.3 <= w <= 2.5 for w in weights.values()))
        self.assertEqual(set(weights.keys()), {'A', 'B', 'C'})

    def test_run_composite_pipeline_adaptive_profile(self):
        """Test that running a composite pipeline with adaptive weights"""
        stages = [
            make_hill_constraint_stage(partial_len=30, partial_min=-900.0),
            make_route_transposition_stage(min_cols=5, max_cols=5),
        ]
        result = run_composite_pipeline(
            CIPHER_SAMPLE,
            stages,
            report=False,
            adaptive=True,
            limit=20,
        )
        diag = result['profile'].get('adaptive_diagnostics')
        self.assertIsInstance(diag, dict)
        self.assertTrue(len(diag) > 0)
        # Check adaptive weights present, omit stage
        for _, info in diag.items():
            self.assertIn('adaptive_weight', info)
            self.assertTrue(0.3 <= info['adaptive_weight'] <= 2.5)


if __name__ == '__main__':
    unittest.main()
