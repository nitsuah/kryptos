"""Edge case tests for ciphers module."""

import unittest

from src.ciphers import double_rotational_transposition, polybius_decrypt, vigenere_decrypt


class TestCiphersEdgeCases(unittest.TestCase):
    def test_vigenere_decrypt_mixed_case(self):
        ct = "KRYPTOS"
        key = "key"
        # Just ensure it runs without error and returns uppercase
        pt = vigenere_decrypt(ct, key)
        self.assertTrue(pt.isupper())

    def test_polybius_invalid_square(self):
        with self.assertRaises(ValueError):
            polybius_decrypt("1111", [["A"]])

    def test_double_rotational_invalid_length(self):
        with self.assertRaises(ValueError):
            double_rotational_transposition("TOOSHORT")


if __name__ == '__main__':
    unittest.main()
