"""High-level hypothesis tests for K4."""

import unittest

from kryptos.k4.hypotheses import HillCipherHypothesisStub


class TestK4Hypotheses(unittest.TestCase):
    def test_hill_cipher_candidate(self):
        """Test HillCipherHypothesisStub returns valid candidate(s)."""
        hyp = HillCipherHypothesisStub()
        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=5)
        # Assertions
        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        c = candidates[0]
        self.assertIsNotNone(c.id, "Candidate must have an id")
        self.assertIsNotNone(c.plaintext, "Candidate must have plaintext")
        self.assertIsNotNone(c.key_info, "Candidate must have key_info")
        self.assertIsInstance(c.score, (int, float), "Score must be numeric")
        # Deterministic check: stub always returns same plaintext
        self.assertEqual(c.plaintext, "STUBPLAINTEXTFORHILL")

    @unittest.skip("Transposition constraint hypothesis not implemented")
    def test_transposition_candidate(self):
        pass

    @unittest.skip("Berlin clock vigenere hypothesis not implemented")
    def test_berlin_clock_vigenere_candidate(self):
        pass


if __name__ == '__main__':
    unittest.main()
