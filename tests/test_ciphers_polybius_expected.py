"""Unit tests for Polybius cipher decryption with expected outputs."""
import unittest
from src.ciphers import polybius_decrypt


class TestPolybiusExpected(unittest.TestCase):
    """Test Polybius decryption with expected outputs."""
    def test_polybius_expected_match(self):
        """Test Polybius decryption with expected output."""
        square = [
            ["A", "B", "C", "D", "E"],
            ["F", "G", "H", "I", "K"],
            ["V", "W", "X", "Y", "Z"],
        ]
        pt = polybius_decrypt("111213", square)
        # Expectation: pairs 11->A, 12->B, 13->C
        self.assertEqual(pt, "ABC")


if __name__ == '__main__':
    unittest.main()
