"""Test noop path for make_transposition_multi_crib_stage when positional_cribs is None."""
import unittest
from src.k4.pipeline import make_transposition_multi_crib_stage, Pipeline

class TestPipelineNoopMultiCrib(unittest.TestCase):
    def test_noop_stage(self):
        stage = make_transposition_multi_crib_stage(positional_cribs=None)
        pipe = Pipeline([stage])
        res = pipe.run("ABCD")
        self.assertEqual(len(res), 1)
        r = res[0]
        self.assertEqual(r.metadata.get('candidates'), [])
        self.assertEqual(r.output, "ABCD")

if __name__ == '__main__':
    unittest.main()
