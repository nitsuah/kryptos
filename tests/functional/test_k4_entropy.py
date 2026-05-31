"""Tests for entropy and repeating bigram metrics."""

import unittest

from kryptos.k4 import letter_entropy, repeating_bigram_fraction


class TestK4Entropy(unittest.TestCase):
    def test_letter_entropy_range(self):
        low = 'AAAAAAAAAAAAAA'
        high = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.assertLess(letter_entropy(low), letter_entropy(high))

    def test_repeating_bigram_fraction(self):
        text = 'ABABABAB'
        frac = repeating_bigram_fraction(text)
        self.assertGreater(frac, 0.0)
        unique = 'ABCDEFGH'
        self.assertLess(repeating_bigram_fraction(unique), frac)


if __name__ == '__main__':
    unittest.main()
