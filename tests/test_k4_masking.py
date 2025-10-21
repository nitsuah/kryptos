"""Tests for masking/null-removal heuristics and pipeline stage."""
import unittest
from src.k4 import mask_variants, score_mask_variants, make_masking_stage, Pipeline

class TestK4Masking(unittest.TestCase):
    def test_mask_variants_generation(self):
        ct = 'XXOBKRUOXOGHULBXXSOLIYFBBWFLRVQXXQPRNGKSSOTWTQYY'
        variants = mask_variants(ct)
        self.assertTrue(len(variants) >= 3)
        # Ensure removal variant shorter
        self.assertTrue(any(len(v) < len(ct) for v in variants))

    def test_score_mask_variants(self):
        ct = 'XXOBKRUOXOGHULBXXSOLIYFBBWFLRVQXXQPRNGKSSOTWTQYY'
        scored = score_mask_variants(ct)
        self.assertTrue(len(scored) > 0)
        self.assertIn('score', scored[0])

    def test_masking_stage_runs(self):
        ct = 'XXOBKRUOXOGHULBXXSOLIYFBBWFLRVQXXQPRNGKSSOTWTQYY'
        stage = make_masking_stage(limit=5)
        pipe = Pipeline([stage])
        res = pipe.run(ct)[0]
        self.assertIn('candidates', res.metadata)
        self.assertTrue(len(res.metadata['candidates']) <= 5)

if __name__ == '__main__':
    unittest.main()
