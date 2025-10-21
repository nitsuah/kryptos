"""Polybius cipher expected output test (fixed formatting)."""
import unittest
from src.ciphers import polybius_decrypt


class TestPolybiusExpectedFixed(unittest.TestCase):
    def test_polybius_expected_match(self):
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
