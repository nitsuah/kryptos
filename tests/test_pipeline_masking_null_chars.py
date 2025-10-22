"""Test masking stage with explicit null chars parameter."""

import unittest

from src.k4.pipeline import Pipeline, make_masking_stage


class TestPipelineMaskingNullChars(unittest.TestCase):
    def test_masking_with_null_chars(self):
        stage = make_masking_stage(null_chars="X", limit=5)
        pipe = Pipeline([stage])
        res = pipe.run("ABXCXDXXEF")
        self.assertEqual(len(res), 1)
        meta = res[0].metadata
        cands = meta.get('candidates', [])
        self.assertTrue(isinstance(cands, list))


if __name__ == '__main__':
    unittest.main()
