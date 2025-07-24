import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ciphers import vigenere_decrypt, transposition_decrypt
import unittest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from config.json
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config/config.json'))
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

class TestCiphers(unittest.TestCase):
    def test_vigenere_k1(self):
        """
        Test the Vigenère decryption for K1 using the KRYPTOS keyed alphabet.
        """
        # Get K1 ciphertext and key from config
        ciphertext_k1 = config["ciphertexts"]["K1"].replace(" ", "")  # Strip spaces from ciphertext
        key_k1 = config["parameters"]["vigenere_keys"][0]  # Use the first key from vigenere_keys for K1
        
        # Expected plaintext for K1
        expected_plaintext_k1 = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
        
        # Decrypt the ciphertext
        decrypted_text_k1 = vigenere_decrypt(ciphertext_k1, key_k1, preserve_non_alpha=False)
        
        # Debugging output
        logging.info(f"Test K1:")
        logging.debug(f"Cipher: {ciphertext_k1}")
        logging.info(f"Key: {key_k1}")
        logging.debug(f"Decrypted Text: {decrypted_text_k1}")
        logging.debug(f"Expected Plaintext: {expected_plaintext_k1}")
        
        # Assert the decrypted text matches the expected plaintext
        self.assertEqual(decrypted_text_k1, expected_plaintext_k1)
    
    def test_vigenere_k2(self):
        """
        Test the Vigenère decryption for K2 using the KRYPTOS keyed alphabet.
        """
        # Get the modified K2 ciphertext and key from config
        ciphertext_k2 = config["ciphertexts"]["K2"]  # The modified ciphertext already includes the 'S'
        logging.debug(f"Original Ciphertext (with spaces): {ciphertext_k2}")

        # Get the key for K2
        key_k2 = config["parameters"]["vigenere_keys"][1]  # Use the second key from vigenere_keys for K2

        # Expected plaintext for K2
        expected_plaintext_k2 = (
            "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLE?THEYUSEDTHEEARTHSMAGNETICFIELDX"
            "THEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONX"
            "DOESLANGLEYKNOWABOUTTHIS?THEYSHOULDITSBURIEDOUTTHERESOMEWHEREX"
            "WHOKNOWSTHEEXACTLOCATION?ONLYWWTHISWASHISLASTMESSAGEX"
            "THIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSNORTH"
            "SEVENTYSEVENDEGREESEIGHTMINUTESFORTYFOURSECONDSWESTXLAYERTWO"
        )

        # Decrypt the ciphertext without removing spaces
        decrypted_text_k2 = vigenere_decrypt(ciphertext_k2, key_k2, preserve_non_alpha=True)

        # Debugging output
        logging.info(f"Test K2:")
        logging.debug(f"Cipher: {ciphertext_k2}")
        logging.info(f"Key: {key_k2}")
        logging.debug(f"Decrypted Text (with spaces): {decrypted_text_k2}")
        logging.debug(f"Expected Plaintext: {expected_plaintext_k2}")

        # Assert the decrypted text matches the expected plaintext
        self.assertEqual(decrypted_text_k2.replace(" ", ""), expected_plaintext_k2)

    def test_transposition_k3(self):
        """
        Test the transposition decryption for K3.
        """
        ciphertext_k3 = config["ciphertexts"]["K3"]
        key = "KRYPTOS"

        # Debug: Log ciphertext length and content
        logging.info(f"TEST K3:")
        logging.info(f"Key: {key}")
        logging.debug(f"K3 Ciphertext: {ciphertext_k3}")
        logging.debug(f"K3 Ciphertext Length: {len(ciphertext_k3)}")
        logging.debug(f"K3 Ciphertext Hex: {ciphertext_k3.encode().hex()}")

        expected_plaintext_k3 = (
            "SLOWLYDESPERATELYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAY"
            "WASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLE"
            "IINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRESCAPINGFROMTHECHAMBERCAUSEDTHEFLAMETOFLICKER"
            "BUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"
        )
        
        # Decrypt the ciphertext using the transposition decryption function
        decrypted_text_k3 = transposition_decrypt(ciphertext_k3, key)

        # Debugging output
        logging.info(f"Decrypted Text: {decrypted_text_k3}")
        logging.info(f"Expected Plaintext: {expected_plaintext_k3}")

        # Assertion
        self.assertEqual(decrypted_text_k3.replace(" ", ""), expected_plaintext_k3, 
                        "K3 decryption failed")
if __name__ == "__main__":
    unittest.main()