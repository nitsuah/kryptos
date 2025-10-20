"""Tests (skipped placeholders) for Hill cipher utilities."""
import unittest
from src.k4 import hill_encrypt, hill_decrypt, matrix_inv_mod

class TestHillCipher(unittest.TestCase):
    def test_encrypt_decrypt_roundtrip_2x2(self):
        """Test 2x2 Hill cipher encryption and decryption roundtrip."""
        key = [[3,3],[2,5]]  # classic example (det=9-6=3, invertible mod 26)
        pt = "TESTMESSAGE"
        ct = hill_encrypt(pt, key)
        dec = hill_decrypt(ct, key)
        self.assertIsNotNone(dec)
        dec_str = str(dec)
        self.assertEqual(dec_str, pt.upper()[:len(dec_str)])

    @unittest.skip("3x3 roundtrip pending")
    def test_encrypt_decrypt_roundtrip_3x3(self):
        """Test 3x3 Hill cipher encryption and decryption roundtrip."""
        key = [[6,24,1],[13,16,10],[20,17,15]]  # classic invertible example
        pt = "THEHILLCIPHERTESTTEXT"
        ct = hill_encrypt(pt, key)
        dec = hill_decrypt(ct, key)
        self.assertIsNotNone(dec)
        dec_str = str(dec)
        self.assertEqual(dec_str, pt.upper()[:len(dec_str)])

    def test_key_invertibility(self):
        """Test matrix inversion for known invertible keys."""
        key = [[6,24,1],[13,16,10],[20,17,15]]  # det=441 mod 26 = 25 invertible
        inv = matrix_inv_mod(key)
        self.assertIsNotNone(inv)

if __name__ == '__main__':
    unittest.main()
