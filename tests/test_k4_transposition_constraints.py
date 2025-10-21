"""Tests for positional crib columnar transposition constraint search."""
import unittest
from src.k4 import search_with_crib_at_position

def _make_columnar_ciphertext(plaintext: str, n_cols: int, perm: tuple[int, ...]) -> str:
    """Produce ciphertext matching invert_columnar model for given permutation."""
    pt = ''.join(c for c in plaintext.upper() if c.isalpha())
    cols = ['' for _ in range(n_cols)]
    for i, ch in enumerate(pt):
        c = i % n_cols
        cols[c] += ch
    # Ciphertext constructed by concatenating columns in permuted order
    pieces = [cols[p] for p in perm]
    return ''.join(pieces)

class TestTranspositionConstraints(unittest.TestCase):
    def test_search_with_crib_at_position_finds_expected(self):
        plaintext = 'ABCKNOWNXYZ'  # crib 'KNOWN' starts at index 3
        crib = 'KNOWN'
        n_cols = 4
        perm = (2, 0, 1, 3)
        ct = _make_columnar_ciphertext(plaintext, n_cols, perm)
        results = search_with_crib_at_position(ct, crib, n_cols, expected_index=3, window=0, max_perms=50)
        self.assertTrue(any(r['perm'] == perm for r in results))
        self.assertTrue(all(abs(r['start_idx'] - 3) <= 0 for r in results))

    def test_search_with_crib_at_position_strict_window_excludes(self):
        plaintext = 'ABCKNOWNXYZ'
        crib = 'KNOWN'
        n_cols = 4
        perm = (2, 0, 1, 3)
        ct = _make_columnar_ciphertext(plaintext, n_cols, perm)
        results = search_with_crib_at_position(ct, crib, n_cols, expected_index=0, window=0, max_perms=50)
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
