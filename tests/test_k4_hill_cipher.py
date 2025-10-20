"""Tests (skipped placeholders) for Hill cipher utilities."""
import unittest
from src.k4 import hill_encrypt, hill_decrypt, matrix_inv_mod

class TestHillCipher(unittest.TestCase):
    @unittest.skip("Hill cipher hypothesis tests not yet implemented")
    def test_encrypt_decrypt_roundtrip_2x2(self):
        key = [[3,3],[2,5]]  # classic example (det=9-6=3, invertible mod 26)
        pt = "TESTMESSAGE"
        ct = hill_encrypt(pt, key)
        dec = hill_decrypt(ct, key)
        self.assertEqual(dec, pt.upper())

    @unittest.skip("Hill cipher hypothesis tests not yet implemented")
    def test_key_invertibility(self):
        key = [[6,24,1],[13,16,10],[20,17,15]]  # det=441 mod 26 = 25 invertible
        inv = matrix_inv_mod(key)
        self.assertIsNotNone(inv)

if __name__ == '__main__':
    unittest.main()
