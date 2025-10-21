"""Tests for route-based transposition variants (spiral, boustrophedon, diagonal)."""
import unittest
from src.k4 import generate_route_variants

CIPHER_SAMPLE = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQ"

class TestRouteTransposition(unittest.TestCase):
    def test_generate_route_variants_lengths(self):
        results = generate_route_variants(CIPHER_SAMPLE, cols_min=5, cols_max=6, routes=("spiral","boustrophedon","diagonal"))
        self.assertTrue(len(results) > 0)
        # All plaintext lengths must equal original normalized length
        norm_len = len(''.join(c for c in CIPHER_SAMPLE if c.isalpha()))
        for r in results:
            self.assertEqual(len(r['text']), norm_len)
            self.assertIn(r['route'], ("spiral","boustrophedon","diagonal"))
        # Ensure scores present
        self.assertTrue(all('score' in r for r in results))

if __name__ == '__main__':
    unittest.main()
