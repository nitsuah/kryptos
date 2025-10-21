"""Unit tests for Polybius cipher decryption of 'ABC'."""
import unittest
from src.ciphers import polybius_decrypt


class TestPolybiusABC(unittest.TestCase):
    """Test Polybius decryption of 'ABC'."""
    def test_polybius_abc(self):
        """Test decryption of '111213' to 'ABC'."""
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
