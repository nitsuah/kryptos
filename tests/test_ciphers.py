"""
Unit tests for cipher decryption functions.
"""

import json
import logging
import os
import unittest

from kryptos.ciphers import kryptos_k3_decrypt, vigenere_decrypt

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from config.json
config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config/config.json'))
with open(config_path, encoding='utf-8') as config_file:
    config = json.load(config_file)


class TestCiphers(unittest.TestCase):
    """Unit tests for cipher decryption functions."""

    def test_vigenere_k1(self):
        """Test the Vigenère decryption for K1 using the keyed alphabet."""
        ciphertext_k1 = config["ciphertexts"]["K1"].replace(" ", "")
        key_k1 = config["parameters"]["vigenere_keys"][0]
        expected_plaintext_k1 = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
        decrypted_text_k1 = vigenere_decrypt(ciphertext_k1, key_k1, preserve_non_alpha=False)
        self.assertEqual(decrypted_text_k1, expected_plaintext_k1)

    def test_vigenere_k2(self):
        """Test the Vigenère decryption for K2 using the keyed alphabet."""
        ciphertext_k2 = config["ciphertexts"]["K2"]
        key_k2 = config["parameters"]["vigenere_keys"][1]
        expected_plaintext_k2 = (
            "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLE?THEYUSEDTHEEARTHSMAGNETICFIELDX"
            "THEINFORMATIONWASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONX"
            "DOESLANGLEYKNOWABOUTTHIS?THEYSHOULDITSBURIEDOUTTHERESOMEWHEREX"
            "WHOKNOWSTHEEXACTLOCATION?ONLYWWTHISWASHISLASTMESSAGEX"
            "THIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSNORTH"
            "SEVENTYSEVENDEGREESEIGHTMINUTESFORTYFOURSECONDSWESTXLAYERTWO"
        )
        decrypted_text_k2 = vigenere_decrypt(ciphertext_k2, key_k2, preserve_non_alpha=True)
        self.assertEqual(decrypted_text_k2.replace(" ", ""), expected_plaintext_k2)

    def test_k3(self):
        """Test the K3 double rotational transposition decryption."""
        ciphertext_k3 = config["ciphertexts"]["K3"]
        expected_plaintext_k3 = (
            "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAY"
            "WASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLE"
            "IINSERTEDTHECANDLEANDPEEREDINTHEHOTAIRESCAPINGFROMTHECHAMBERCAUSEDTHEFLAMETOFLICKER"
            "BUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYOUSEEANYTHINGQ"
        )
        decrypted_text_k3 = kryptos_k3_decrypt(ciphertext_k3)
        self.assertEqual(decrypted_text_k3.replace(" ", ""), expected_plaintext_k3)


if __name__ == "__main__":
    unittest.main()
