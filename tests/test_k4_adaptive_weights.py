"""Tests for adaptive fusion weighting logic."""
import unittest
from src.k4 import (
    make_hill_constraint_stage,
    make_route_transposition_stage,
    run_composite_pipeline,
    adaptive_fusion_weights
)

CIPHER_SAMPLE = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQ"

class TestAdaptiveFusionWeights(unittest.TestCase):
    def test_adaptive_fusion_weights_range(self):
        # Build mock candidates across stages
        candidates = [
            {'stage': 'A', 'score': 100, 'text': 'AAAAA'*10},
            {'stage': 'B', 'score': 200, 'text': 'CLOCKBERLIN' * 5},
            {'stage': 'C', 'score': 150, 'text': 'BERLINCLOCK' * 5},
        ]
        weights = adaptive_fusion_weights(candidates)
        self.assertTrue(all(0.3 <= w <= 2.5 for w in weights.values()))
        self.assertEqual(set(weights.keys()), {'A','B','C'})

    def test_run_composite_pipeline_adaptive_profile(self):
        stages = [
            make_hill_constraint_stage(partial_len=30, partial_min=-900.0),
            make_route_transposition_stage(min_cols=5, max_cols=5)
        ]
        result = run_composite_pipeline(CIPHER_SAMPLE, stages, report=False, adaptive=True, limit=20)
        diag = result['profile'].get('adaptive_diagnostics')
        self.assertIsInstance(diag, dict)
        self.assertTrue(len(diag) > 0)
        # Check adaptive weights present
        for stage, info in diag.items():
            self.assertIn('adaptive_weight', info)
            self.assertTrue(0.3 <= info['adaptive_weight'] <= 2.5)

if __name__ == '__main__':
    unittest.main()
