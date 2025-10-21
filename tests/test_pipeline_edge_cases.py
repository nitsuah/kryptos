"""Pipeline edge case tests."""
import unittest
from src.k4.pipeline import Pipeline, Stage, make_hill_constraint_stage

class TestPipelineEdgeCases(unittest.TestCase):
    def test_pipeline_no_stages(self):
        pipe = Pipeline([])
        # run returns empty results
        self.assertEqual(pipe.run("ABC"), [])

    def test_pipeline_single_stage(self):
        stage = make_hill_constraint_stage(partial_len=10, partial_min=-900.0)
        pipe = Pipeline([stage])
        res = pipe.run("ABCDEF")
        self.assertEqual(len(res), 1)
        self.assertTrue(res[0].output)

    def test_stage_exception(self):
        def bad_func(ct: str):
            raise RuntimeError("boom")
        stage = Stage(name="bad", func=bad_func)
        pipe = Pipeline([stage])
        with self.assertRaises(RuntimeError):
            pipe.run("ABC")

if __name__ == '__main__':
    unittest.main()
