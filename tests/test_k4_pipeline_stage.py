"""Test pipeline stage for Hill constraint integration."""

import unittest

from src.k4 import Pipeline, StageResult, make_hill_constraint_stage


class TestPipelineHillStage(unittest.TestCase):
    def test_hill_constraint_stage_runs(self):
        stage = make_hill_constraint_stage()
        pipe = Pipeline([stage])
        ct = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQ"  # sample start of K4
        results = pipe.run(ct)
        self.assertEqual(len(results), 1)
        r = results[0]
        self.assertIsInstance(r, StageResult)
        self.assertIn('candidates', r.metadata)
        self.assertTrue('score' in r.__dict__)


if __name__ == '__main__':
    unittest.main()
