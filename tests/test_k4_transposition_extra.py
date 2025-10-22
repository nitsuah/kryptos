import unittest

from src.k4 import transposition


class TestTranspositionExtra(unittest.TestCase):
    def make_columnar_cipher(self, plaintext: str, cols: int, perm: tuple[int, ...]) -> str:
        """Build a columnar ciphertext from plaintext by filling row-major into
        columns, permuting, then reading columns top-to-bottom.
        """
        seq = ''.join(c for c in plaintext if c.isalpha())

        # fill original columns (columns are built top-to-bottom from row-major input)
        orig_cols = [''] * cols
        for i, ch in enumerate(seq):
            # row index is not used in the helper; compute column only
            c = i % cols
            orig_cols[c] += ch

        # permute columns according to perm and read columns top-to-bottom
        permuted = [orig_cols[p] for p in perm]
        # concatenate columns (top-to-bottom) in permuted order
        ct = ''.join(permuted)
        return ct

    def test_empty_early_exit(self):
        # empty input should return empty string when inverting
        ct = self.make_columnar_cipher('', 1, (0,))
        out = transposition.apply_columnar_permutation(ct, 1, (0,))
        self.assertEqual(out, '')

    def test_columnar_basic_inversion(self):
        plaintext = 'ABCDEFGH'
        cols = 4
        perm = tuple(range(cols))
        ct = self.make_columnar_cipher(plaintext, cols, perm)
        # apply_columnar_permutation should reconstruct the plaintext (letters only)
        pt = transposition.apply_columnar_permutation(ct, cols, perm)
        self.assertEqual(''.join([c for c in pt if c.isalpha()])[: len(plaintext)], plaintext)

    def test_search_columnar_adaptive_small(self):
        text = 'THEQUICKBROWNFOX'
        # adaptive search should return a list (sampled)
        res = transposition.search_columnar_adaptive(text, min_cols=3, max_cols=4, sample_perms=10, prefix_len=2)
        self.assertIsInstance(res, list)


if __name__ == '__main__':
    unittest.main()
