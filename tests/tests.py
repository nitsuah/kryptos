import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ciphers import vigenere_decrypt
import unittest

# Load configuration from config.json
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config/config.json'))
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

class TestCiphers(unittest.TestCase):
    def test_vigenere_k1(self):
        """
        Test the Vigenère decryption for K1 using values from config.json.
        """
        # Get K1 ciphertext and key from config
        ciphertext_k1 = config["ciphertexts"]["K1"]
        key_k1 = config["parameters"]["vigenere_keys"][0]  # Use the first key from vigenere_keys for K1
        
        # Expected plaintext for K1
        expected_plaintext_k1 = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
        
        # Decrypt the ciphertext
        decrypted_text_k1 = vigenere_decrypt(ciphertext_k1, key_k1)
        
        # Print the decrypted text for debugging
        print(f"Key used: {key_k1}")
        print(f"Ciphertext: {ciphertext_k1}")
        print(f"Decrypted Text: {decrypted_text_k1}")
        print(f"Expected Plaintext: {expected_plaintext_k1}")
        
        # Assert the decrypted text matches the expected plaintext
        self.assertEqual(decrypted_text_k1, expected_plaintext_k1)

if __name__ == "__main__":
    unittest.main()