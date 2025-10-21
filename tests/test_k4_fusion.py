"""Tests for weighted fusion utilities in composite module."""
import unittest
from src.k4 import normalize_scores, fuse_scores_weighted

class TestK4Fusion(unittest.TestCase):
    def test_normalize_and_fuse(self):
        candidates = [
            {'stage': 'hill-constraint', 'score': 100.0, 'text': 'A'},
            {'stage': 'hill-constraint', 'score': 50.0, 'text': 'B'},
            {'stage': 'berlin-clock', 'score': 10.0, 'text': 'C'},
            {'stage': 'berlin-clock', 'score': 5.0, 'text': 'D'},
        ]
        norm = normalize_scores(candidates)
        self.assertTrue(all('norm_score' in c for c in norm))
        weights = {'hill-constraint': 2.0, 'berlin-clock': 1.0}
        fused = fuse_scores_weighted(norm, weights, use_normalized=True)
        self.assertTrue(all('fused_score' in c for c in fused))
        # Highest hill candidate should appear before highest berlin candidate due to weight
        self.assertEqual(fused[0]['stage'], 'hill-constraint')

if __name__ == '__main__':
    unittest.main()
