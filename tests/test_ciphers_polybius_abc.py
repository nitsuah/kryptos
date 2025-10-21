import unittest
from src.ciphers import polybius_decrypt

class TestPolybiusABC(unittest.TestCase):
    def test_polybius_abc(self):
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
