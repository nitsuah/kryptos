"""Test route transposition stage to cover generate_route_variants path."""

import unittest

from kryptos.k4.pipeline import Pipeline, make_route_transposition_stage


class TestPipelineRouteStage(unittest.TestCase):
    def test_route_stage_basic(self):
        stage = make_route_transposition_stage(min_cols=5, max_cols=5, routes=("spiral",))
        pipe = Pipeline([stage])
        res = pipe.run("OBKRUOXOGHULB")
        self.assertEqual(len(res), 1)
        r = res[0]
        self.assertIn('candidates', r.metadata)
        self.assertTrue(isinstance(r.metadata['candidates'], list))


if __name__ == '__main__':
    unittest.main()
