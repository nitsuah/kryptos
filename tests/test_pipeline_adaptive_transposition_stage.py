"""Test adaptive transposition stage branch."""

import unittest

from src.k4.pipeline import Pipeline, make_transposition_adaptive_stage


class TestPipelineAdaptiveTranspositionStage(unittest.TestCase):
    def test_adaptive_stage_runs(self):
        stage = make_transposition_adaptive_stage(min_cols=5, max_cols=5, sample_perms=20, partial_length=10, limit=5)
        pipe = Pipeline([stage])
        res = pipe.run("OBKRUOXOGHULBSOLIFB")
        self.assertEqual(len(res), 1)
        meta = res[0].metadata
        self.assertIn('candidates', meta)
        self.assertTrue(isinstance(meta['candidates'], list))


if __name__ == '__main__':
    unittest.main()
