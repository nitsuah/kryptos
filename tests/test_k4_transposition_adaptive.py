"""Tests for adaptive transposition search and pipeline stage."""
import unittest
from src.k4 import search_columnar_adaptive, make_transposition_adaptive_stage, Pipeline

class TestK4TranspositionAdaptive(unittest.TestCase):
    def test_search_columnar_adaptive_basic(self):
        ct = 'THISISATESTOFTRANSPOSEDONPLAINTEXTSEGMENT'
        results = search_columnar_adaptive(ct, min_cols=5, max_cols=5, sample_perms=50)
        self.assertTrue(len(results) > 0)
        self.assertIn('partial', results[0])
        self.assertIn('score', results[0])

    def test_transposition_adaptive_stage_runs(self):
        ct = 'THISISATESTOFTRANSPOSEDONPLAINTEXTSEGMENT'
        stage = make_transposition_adaptive_stage(min_cols=5, max_cols=5, sample_perms=60, limit=10)
        pipe = Pipeline([stage])
        res = pipe.run(ct)[0]
        self.assertIn('candidates', res.metadata)
        self.assertTrue(len(res.metadata['candidates']) <= 10)
        self.assertIsInstance(res.score, float)

if __name__ == '__main__':
    unittest.main()
