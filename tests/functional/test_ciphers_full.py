"""Recreated ciphers full test with corrected Polybius ABC expectation."""

import unittest

from kryptos.ciphers import (
    double_rotational_transposition,
    k3_decrypt,
    polybius_decrypt,
    rotate_matrix_right_90,
    transposition_decrypt,
    vigenere_decrypt,
)


class TestCiphersFull(unittest.TestCase):
    def test_vigenere_preserve_non_alpha(self):
        pt = vigenere_decrypt("KRY PTOS!", "KEY", preserve_non_alpha=True)
        self.assertIn("!", pt)

    def test_vigenere_basic(self):
        pt = vigenere_decrypt("KRYPTOS", "KEY")
        self.assertEqual(len(pt), 7)

    def test_rotate_matrix_right_90_shape(self):
        m = [["A", "B"], ["C", "D"], ["E", "F"]]
        rotated = rotate_matrix_right_90(m)
        self.assertEqual(len(rotated), 2)
        self.assertEqual(len(rotated[0]), 3)

    def test_double_rotational_transposition_length(self):
        text = "A" * 336
        out = double_rotational_transposition(text)
        self.assertEqual(len(out), 336)

    def test_k3_decrypt_leading_q(self):
        text = "?" + ("A" * 336)
        out = k3_decrypt(text)
        self.assertEqual(len(out), 336)

    def test_transposition_decrypt_invalid_length(self):
        with self.assertRaises(ValueError):
            transposition_decrypt("TOO_SHORT")

    def test_transposition_decrypt_with_key(self):
        base = ("ABCD" * 86)[:344]
        out = transposition_decrypt(base, key="KEY")
        self.assertEqual(len(out), 344)

    def test_polybius_decrypt_valid(self):
        square = [
            ["A", "B", "C", "D", "E"],
            ["F", "G", "H", "I", "K"],
            ["L", "M", "N", "O", "P"],
            ["Q", "R", "S", "T", "U"],
            ["V", "W", "X", "Y", "Z"],
        ]
        pt = polybius_decrypt("111213", square)
        self.assertEqual(pt, "ABC")


if __name__ == '__main__':
    unittest.main()
