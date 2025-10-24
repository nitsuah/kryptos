"""High-level hypothesis tests for K4."""

import unittest

from kryptos.k4.hypotheses import (
    BerlinClockTranspositionHypothesis,
    BerlinClockVigenereHypothesis,
    HillCipher2x2Hypothesis,
    PlayfairHypothesis,
    VigenereHypothesis,
)


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

    def test_transposition_berlin_clock_constraints(self):
        """Test BerlinClockTranspositionHypothesis searches clock-inspired column widths."""
        hyp = BerlinClockTranspositionHypothesis()
        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=10)

        # Should return candidates
        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 10, "Should respect limit")

        # Validate structure
        c = candidates[0]
        self.assertIsNotNone(c.id, "Candidate must have an id")
        self.assertTrue(c.id.startswith("transposition_"), "ID should indicate transposition")
        self.assertIsNotNone(c.plaintext, "Candidate must have plaintext")
        self.assertIn('columns', c.key_info, "key_info must have columns field")
        self.assertIn('permutation', c.key_info, "key_info must have permutation field")
        self.assertIsInstance(c.score, (int, float), "Score must be numeric")

        # Check columns are clock-inspired widths
        clock_widths = [5, 6, 7, 8, 10, 11, 12, 15, 24]
        self.assertIn(c.key_info['columns'], clock_widths, "Should use Berlin Clock period widths")

        # Check candidates are ranked by score (descending)
        if len(candidates) > 1:
            self.assertGreaterEqual(
                candidates[0].score,
                candidates[1].score,
                "Candidates should be sorted by score (highest first)",
            )

    def test_vigenere_hypothesis(self):
        """Test VigenereHypothesis searches key lengths 1-20 with frequency analysis."""
        hyp = VigenereHypothesis(min_key_length=1, max_key_length=20, keys_per_length=10)
        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=10)

        # Should return candidates
        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 10, "Should respect limit")

        # Validate structure
        c = candidates[0]
        self.assertIsNotNone(c.id, "Candidate must have an id")
        self.assertTrue(c.id.startswith("vigenere_"), "ID should indicate Vigenère")
        self.assertIsNotNone(c.plaintext, "Candidate must have plaintext")
        self.assertIn('type', c.key_info, "key_info must have type field")
        self.assertEqual(c.key_info['type'], 'vigenere', "Should be Vigenère type")
        self.assertIn('key', c.key_info, "key_info must have key field")
        self.assertIn('key_length', c.key_info, "key_info must have key_length field")
        self.assertIsInstance(c.score, (int, float), "Score must be numeric")

        # Check key length is in expected range
        self.assertGreaterEqual(c.key_info['key_length'], 1, "Key length should be >= 1")
        self.assertLessEqual(c.key_info['key_length'], 20, "Key length should be <= 20")

        # Check candidates are ranked by score (descending)
        if len(candidates) > 1:
            self.assertGreaterEqual(
                candidates[0].score,
                candidates[1].score,
                "Candidates should be sorted by score (highest first)",
            )

    def test_playfair_hypothesis(self):
        """Test PlayfairHypothesis with Sanborn-related keywords."""
        hyp = PlayfairHypothesis()
        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=10)

        # Should return candidates
        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 10, "Should respect limit")

        # Validate structure
        c = candidates[0]
        self.assertIsNotNone(c.id, "Candidate must have an id")
        self.assertTrue(c.id.startswith("playfair_"), "ID should indicate Playfair")
        self.assertIsNotNone(c.plaintext, "Candidate must have plaintext")
        self.assertIn('type', c.key_info, "key_info must have type field")
        self.assertEqual(c.key_info['type'], 'playfair', "Should be Playfair type")
        self.assertIn('keyword', c.key_info, "key_info must have keyword field")
        self.assertIsInstance(c.score, (int, float), "Score must be numeric")

        # Check candidates are ranked by score (descending)
        if len(candidates) > 1:
            self.assertGreaterEqual(
                candidates[0].score,
                candidates[1].score,
                "Candidates should be sorted by score (highest first)",
            )

    def test_berlin_clock_vigenere_candidate(self):
        """Test BerlinClockVigenereHypothesis generates valid candidates."""
        hyp = BerlinClockVigenereHypothesis(hours=[12, 18, 0])  # Test subset
        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=3)

        # Should return candidates
        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 3, "Should respect limit")

        # Validate structure
        c = candidates[0]
        self.assertIsInstance(c.plaintext, str, "Plaintext must be string")
        self.assertEqual(c.key_info['type'], 'berlin_clock_vigenere')
        self.assertIn('hour', c.key_info, "Should include hour in key_info")
        self.assertIsInstance(c.score, (int, float), "Score must be numeric")


if __name__ == '__main__':
    unittest.main()
