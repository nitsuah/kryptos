"""High-level hypothesis tests for K4."""

import unittest

from kryptos.k4.hypotheses import HillCipher2x2Hypothesis


class TestK4Hypotheses(unittest.TestCase):
    def test_hill_cipher_exhaustive_search(self):
        """Test HillCipher2x2Hypothesis exhaustively searches 2x2 key space."""
        hyp = HillCipher2x2Hypothesis()
        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=10)

        # Should return candidates
        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 10, "Should respect limit")

        # Validate structure
        c = candidates[0]
        self.assertIsNotNone(c.id, "Candidate must have an id")
        self.assertTrue(c.id.startswith("hill_2x2_"), "ID should indicate Hill 2x2")
        self.assertIsNotNone(c.plaintext, "Candidate must have plaintext")
        self.assertIsNotNone(c.key_info, "Candidate must have key_info")
        self.assertEqual(c.key_info['size'], 2, "Should be 2x2 matrix")
        self.assertIsInstance(c.score, (int, float), "Score must be numeric")

        # Check candidates are ranked by score (descending)
        if len(candidates) > 1:
            self.assertGreaterEqual(
                candidates[0].score,
                candidates[1].score,
                "Candidates should be sorted by score (highest first)",
            )

    @unittest.skip("Transposition constraint hypothesis not implemented")
    def test_transposition_candidate(self):
        pass

    @unittest.skip("Berlin clock vigenere hypothesis not implemented")
    def test_berlin_clock_vigenere_candidate(self):
        pass


if __name__ == '__main__':
    unittest.main()
