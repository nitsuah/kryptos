"""Skipped high-level hypothesis tests for K4."""

import unittest


class TestK4Hypotheses(unittest.TestCase):
    @unittest.skip("Hill hypothesis not implemented")
    def test_hill_cipher_candidate(self):
        pass

    @unittest.skip("Transposition constraint hypothesis not implemented")
    def test_transposition_candidate(self):
        pass

    @unittest.skip("Berlin clock vigenere hypothesis not implemented")
    def test_berlin_clock_vigenere_candidate(self):
        pass


if __name__ == '__main__':
    unittest.main()
