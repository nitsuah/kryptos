"""Tests to cover composite pipeline branching (weights, no normalize)."""

import unittest

from kryptos.k4 import run_composite_pipeline
from kryptos.k4.composite import fuse_scores_weighted, normalize_scores
from kryptos.k4.pipeline import make_hill_constraint_stage, make_masking_stage


class TestCompositeBranchCoverage(unittest.TestCase):
    def test_pipeline_weights_no_normalize(self):
        stages = [
            make_hill_constraint_stage(partial_len=15, partial_min=-900.0),
            make_masking_stage(limit=5),
        ]
        weights = {'hill-constraint': 1.5, 'masking': 0.8}
        res = run_composite_pipeline(
            "OBKRUOXOGHULBSOLIFB",
            stages,
            report=False,
            adaptive=False,
            normalize=False,
            weights=weights,
            limit=10,
        )
        fused = res.get('fused')
        self.assertIsInstance(fused, list)
        self.assertTrue(len(fused) <= 10)
        for c in fused:  # type: ignore[union-attr]
            self.assertIn('fused_score', c)

    def test_normalize_scores_all_equal(self):
        cands = [{'stage': 's', 'score': 100.0, 'text': 'AAAA'}]
        normed = normalize_scores(cands)
        self.assertEqual(normed[0]['norm_score'], 0.5)

    def test_fuse_scores_weighted_raw(self):
        cands = [
            {'stage': 'A', 'score': 10.0, 'text': 'AAAA'},
            {'stage': 'B', 'score': 20.0, 'text': 'BBBB'},
        ]
        weights = {'A': 2.0, 'B': 1.0}
        fused = fuse_scores_weighted(cands, weights, use_normalized=False)
        a = next(c for c in fused if c['stage'] == 'A')
        b = next(c for c in fused if c['stage'] == 'B')
        self.assertEqual(a['fused_score'], 20.0)
        self.assertEqual(b['fused_score'], 20.0)


if __name__ == '__main__':
    unittest.main()
