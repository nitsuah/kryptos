"""High-level hypothesis tests for K4."""

import unittest

import pytest

from kryptos.k4.hypotheses import (
    AutokeyHypothesis,
    AutokeyThenTranspositionHypothesis,
    BerlinClockTranspositionHypothesis,
    BerlinClockVigenereHypothesis,
    BifidHypothesis,
    CompositeHypothesis,
    DoubleTranspositionHypothesis,
    FourSquareHypothesis,
    HillCipher2x2Hypothesis,
    HillThenTranspositionHypothesis,
    PlayfairHypothesis,
    PlayfairThenTranspositionHypothesis,
    SimpleSubstitutionHypothesis,
    SubstitutionThenTranspositionHypothesis,
    TranspositionThenHillHypothesis,
    VigenereHypothesis,
    VigenereThenHillHypothesis,
    VigenereThenTranspositionHypothesis,
)


class TestK4Hypotheses(unittest.TestCase):
    @pytest.mark.slow
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

    def test_simple_substitution_hypothesis(self):
        """Test SimpleSubstitutionHypothesis (Caesar, Atbash, Reverse)."""
        hyp = SimpleSubstitutionHypothesis()
        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=30)

        # Should return 28 candidates (26 Caesar + Atbash + Reverse)
        self.assertEqual(len(candidates), 28, "Should return 26 Caesar + Atbash + Reverse")

        # Find Caesar, Atbash, Reverse candidates
        caesar_candidates = [c for c in candidates if c.key_info.get('type') == 'caesar']
        atbash_candidates = [c for c in candidates if c.key_info.get('type') == 'atbash']
        reverse_candidates = [c for c in candidates if c.key_info.get('type') == 'reverse']

        self.assertEqual(len(caesar_candidates), 26, "Should have 26 Caesar variants")
        self.assertEqual(len(atbash_candidates), 1, "Should have 1 Atbash variant")
        self.assertEqual(len(reverse_candidates), 1, "Should have 1 Reverse variant")

        # Validate Caesar structure
        c = caesar_candidates[0]
        self.assertIn('shift', c.key_info, "Caesar must have shift")
        self.assertIsInstance(c.key_info['shift'], int, "Shift must be integer")

        # Check candidates are sorted by score
        for i in range(len(candidates) - 1):
            self.assertGreaterEqual(
                candidates[i].score,
                candidates[i + 1].score,
                "Candidates should be sorted by score",
            )

    def test_autokey_hypothesis(self):
        """Test AutokeyHypothesis with keyword primer."""
        hyp = AutokeyHypothesis()
        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=5)

        # Should return candidates
        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 5, "Should respect limit")

        # Validate structure
        c = candidates[0]
        self.assertIsNotNone(c.id, "Candidate must have an id")
        self.assertTrue(c.id.startswith("autokey_"), "ID should indicate Autokey")
        self.assertIsNotNone(c.plaintext, "Candidate must have plaintext")
        self.assertIn('type', c.key_info, "key_info must have type field")
        self.assertEqual(c.key_info['type'], 'autokey', "Should be Autokey type")
        self.assertIn('primer', c.key_info, "key_info must have primer field")
        self.assertIsInstance(c.score, (int, float), "Score must be numeric")

    def test_four_square_hypothesis(self):
        """Test FourSquareHypothesis with keyword pairs."""
        hyp = FourSquareHypothesis()
        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=5)

        # Should return candidates
        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 5, "Should respect limit")

        # Validate structure
        c = candidates[0]
        self.assertIsNotNone(c.id, "Candidate must have an id")
        self.assertTrue(c.id.startswith("foursquare_"), "ID should indicate foursquare")
        self.assertIsNotNone(c.plaintext, "Candidate must have plaintext")
        self.assertIn('type', c.key_info, "key_info must have type field")
        self.assertEqual(c.key_info['type'], 'foursquare', "Should be foursquare type")
        self.assertIn('key1', c.key_info, "key_info must have key1 field")
        self.assertIn('key2', c.key_info, "key_info must have key2 field")
        self.assertIsInstance(c.score, (int, float), "Score must be numeric")

    def test_bifid_hypothesis(self):
        """Test BifidHypothesis with period and keyword."""
        hyp = BifidHypothesis()
        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=5)

        # Should return candidates
        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 5, "Should respect limit")

        # Validate structure
        c = candidates[0]
        self.assertIsNotNone(c.id, "Candidate must have an id")
        self.assertTrue(c.id.startswith("bifid_"), "ID should indicate Bifid")
        self.assertIsNotNone(c.plaintext, "Candidate must have plaintext")
        self.assertIn('type', c.key_info, "key_info must have type field")
        self.assertEqual(c.key_info['type'], 'bifid', "Should be Bifid type")
        self.assertIn('period', c.key_info, "key_info must have period field")
        self.assertIn('keyword', c.key_info, "key_info must have keyword field")
        self.assertIsInstance(c.score, (int, float), "Score must be numeric")


class TestCompositeHypotheses(unittest.TestCase):
    """Test suite for composite hypothesis framework."""

    def test_composite_hypothesis_chaining(self):
        """Test that CompositeHypothesis properly chains two hypotheses."""
        # Create simple stage1 and stage2 hypotheses
        stage1 = SimpleSubstitutionHypothesis()
        stage2 = SimpleSubstitutionHypothesis()

        # Create composite (will test simple substitutions chained)
        composite = CompositeHypothesis(stage1, stage2, stage1_candidates=5)

        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = composite.generate_candidates(ciphertext, limit=10)

        # Should return candidates
        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 10, "Should respect limit")

        # Validate composite structure
        c = candidates[0]
        self.assertIsNotNone(c.id, "Candidate must have an id")
        self.assertTrue("__then__" in c.id, "ID should contain composite separator")
        self.assertIsNotNone(c.plaintext, "Candidate must have plaintext")
        self.assertIsInstance(c.score, (int, float), "Score must be numeric")

        # Check candidates are sorted by score
        if len(candidates) > 1:
            self.assertGreaterEqual(
                candidates[0].score,
                candidates[1].score,
                "Candidates should be sorted by score (highest first)",
            )

    def test_composite_transformation_chain_metadata(self):
        """Test that composite preserves full transformation chain metadata."""
        stage1 = SimpleSubstitutionHypothesis()
        stage2 = SimpleSubstitutionHypothesis()
        composite = CompositeHypothesis(stage1, stage2, stage1_candidates=3)

        ciphertext = "ABCDEFGHIJ"
        candidates = composite.generate_candidates(ciphertext, limit=5)

        # Should have candidates
        self.assertGreater(len(candidates), 0)

        # Check metadata structure
        c = candidates[0]
        self.assertIn('stage1', c.key_info, "key_info must have stage1 field")
        self.assertIn('stage2', c.key_info, "key_info must have stage2 field")
        self.assertIn('transformation_chain', c.key_info, "key_info must have transformation_chain")

        # Verify stage1 metadata
        stage1_info = c.key_info['stage1']
        self.assertIn('id', stage1_info, "stage1 must have id")
        self.assertIn('key', stage1_info, "stage1 must have key")
        self.assertIn('score', stage1_info, "stage1 must have score")

        # Verify stage2 metadata
        stage2_info = c.key_info['stage2']
        self.assertIn('id', stage2_info, "stage2 must have id")
        self.assertIn('key', stage2_info, "stage2 must have key")
        self.assertIn('score', stage2_info, "stage2 must have score")

        # Verify transformation chain is a list with both stage IDs
        chain = c.key_info['transformation_chain']
        self.assertIsInstance(chain, list, "transformation_chain must be a list")
        self.assertEqual(len(chain), 2, "transformation_chain should have 2 stages")

    def test_composite_score_propagation(self):
        """Test that final composite score comes from stage2."""
        stage1 = SimpleSubstitutionHypothesis()
        stage2 = SimpleSubstitutionHypothesis()
        composite = CompositeHypothesis(stage1, stage2, stage1_candidates=2)

        ciphertext = "TESTCIPHERTEXT"
        candidates = composite.generate_candidates(ciphertext, limit=3)

        self.assertGreater(len(candidates), 0)

        # Final composite score should match stage2 score
        c = candidates[0]
        self.assertEqual(
            c.score,
            c.key_info['stage2']['score'],
            "Composite score should equal stage2 score",
        )

    @pytest.mark.slow
    def test_transposition_then_hill_basic(self):
        """Test TranspositionThenHillHypothesis generates candidates."""
        # Minimal smoke test: 1 transposition × 5 Hill matrices = 5 operations (~3-5s)
        # Full exploration tested in scripts/test_composite_hypotheses.py
        hyp = TranspositionThenHillHypothesis(
            transposition_candidates=1,
            hill_limit=5,
            transposition_widths=[5],
        )

        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=3)

        # Should return candidates
        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 5, "Should respect limit")

        # Validate structure
        c = candidates[0]
        self.assertIn("transposition", c.id.lower(), "ID should mention transposition")
        self.assertIn("hill", c.id.lower(), "ID should mention hill")
        self.assertIsNotNone(c.plaintext, "Candidate must have plaintext")
        self.assertIn('stage1', c.key_info, "Composite must have stage1")
        self.assertIn('stage2', c.key_info, "Composite must have stage2")
        self.assertIsInstance(c.score, (int, float), "Score must be numeric")

    def test_vigenere_then_transposition_basic(self):
        """Test VigenereThenTranspositionHypothesis generates candidates."""
        # Use reduced parameters for fast test
        hyp = VigenereThenTranspositionHypothesis(
            vigenere_candidates=5,
            transposition_limit=10,
            vigenere_max_key_length=5,
            transposition_widths=[5, 6],
        )

        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=5)

        # Should return candidates
        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 5, "Should respect limit")

        # Validate structure
        c = candidates[0]
        self.assertIn("vigenere", c.id.lower(), "ID should mention vigenere")
        self.assertIn("transposition", c.id.lower(), "ID should mention transposition")
        self.assertIsNotNone(c.plaintext, "Candidate must have plaintext")
        self.assertIn('stage1', c.key_info, "Composite must have stage1")
        self.assertIn('stage2', c.key_info, "Composite must have stage2")
        self.assertIsInstance(c.score, (int, float), "Score must be numeric")

    def test_substitution_then_transposition_basic(self):
        """Test SubstitutionThenTranspositionHypothesis generates candidates."""
        # Use reduced parameters for fast test
        hyp = SubstitutionThenTranspositionHypothesis(
            transposition_limit=10,
            transposition_widths=[5, 6, 7],
        )

        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=5)

        # Should return candidates
        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 5, "Should respect limit")

        # Validate structure
        c = candidates[0]
        # ID contains stage1 (caesar/atbash/reverse) and stage2 (transposition)
        self.assertTrue(
            any(x in c.id.lower() for x in ["caesar", "atbash", "reverse"]),
            "ID should mention simple substitution method",
        )
        self.assertIn("transposition", c.id.lower(), "ID should mention transposition")
        self.assertIsNotNone(c.plaintext, "Candidate must have plaintext")
        self.assertIn('stage1', c.key_info, "Composite must have stage1")
        self.assertIn('stage2', c.key_info, "Composite must have stage2")
        self.assertIsInstance(c.score, (int, float), "Score must be numeric")

    def test_composite_stage1_candidate_limit(self):
        """Test that stage1_candidates parameter controls exploration depth."""
        stage1 = SimpleSubstitutionHypothesis()
        stage2 = SimpleSubstitutionHypothesis()

        # Test with different stage1_candidates values
        composite_small = CompositeHypothesis(stage1, stage2, stage1_candidates=2)
        composite_large = CompositeHypothesis(stage1, stage2, stage1_candidates=10)

        ciphertext = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        # Generate candidates with different stage1 depths
        candidates_small = composite_small.generate_candidates(ciphertext, limit=50)
        candidates_large = composite_large.generate_candidates(ciphertext, limit=50)

        # Larger stage1_candidates should potentially explore more combinations
        # (though final count limited by 'limit' parameter)
        self.assertGreater(len(candidates_small), 0, "Small composite should generate candidates")
        self.assertGreater(len(candidates_large), 0, "Large composite should generate candidates")

        # Both should respect the final limit
        self.assertLessEqual(len(candidates_small), 50)
        self.assertLessEqual(len(candidates_large), 50)

    @pytest.mark.slow
    def test_hill_then_transposition_basic(self):
        """Test HillThenTranspositionHypothesis (reverse order)."""
        hyp = HillThenTranspositionHypothesis(
            hill_candidates=2,
            transposition_limit=10,
            transposition_widths=[5, 6],
        )

        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=3)

        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 3, "Should respect limit")

        c = candidates[0]
        self.assertIn("hill", c.id.lower(), "ID should mention hill")
        self.assertIn("transposition", c.id.lower(), "ID should mention transposition")
        self.assertIn('stage1', c.key_info, "Composite must have stage1")
        self.assertIn('stage2', c.key_info, "Composite must have stage2")

    def test_autokey_then_transposition_basic(self):
        """Test AutokeyThenTranspositionHypothesis."""
        hyp = AutokeyThenTranspositionHypothesis(
            autokey_candidates=3,
            transposition_limit=10,
            transposition_widths=[5, 6],
        )

        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=3)

        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 3, "Should respect limit")

        c = candidates[0]
        self.assertIn("autokey", c.id.lower(), "ID should mention autokey")
        self.assertIn("transposition", c.id.lower(), "ID should mention transposition")

    def test_playfair_then_transposition_basic(self):
        """Test PlayfairThenTranspositionHypothesis."""
        hyp = PlayfairThenTranspositionHypothesis(
            playfair_candidates=3,
            transposition_limit=10,
            transposition_widths=[5, 6],
        )

        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=3)

        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 3, "Should respect limit")

        c = candidates[0]
        self.assertIn("playfair", c.id.lower(), "ID should mention playfair")
        self.assertIn("transposition", c.id.lower(), "ID should mention transposition")

    def test_double_transposition_basic(self):
        """Test DoubleTranspositionHypothesis."""
        hyp = DoubleTranspositionHypothesis(
            stage1_candidates=3,
            stage2_limit=10,
            stage1_widths=[5, 6],
            stage2_widths=[7, 8],
        )

        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=3)

        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 3, "Should respect limit")

        c = candidates[0]
        self.assertIn("transposition", c.id.lower(), "ID should mention transposition")
        # Should have two transposition stages
        self.assertIn('stage1', c.key_info, "Composite must have stage1")
        self.assertIn('stage2', c.key_info, "Composite must have stage2")

    @pytest.mark.slow
    def test_vigenere_then_hill_basic(self):
        """Test VigenereThenHillHypothesis."""
        hyp = VigenereThenHillHypothesis(
            vigenere_candidates=3,
            hill_limit=10,
            vigenere_max_key_length=5,
        )

        ciphertext = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"
        candidates = hyp.generate_candidates(ciphertext, limit=3)

        self.assertGreater(len(candidates), 0, "Should return at least one candidate")
        self.assertLessEqual(len(candidates), 3, "Should respect limit")

        c = candidates[0]
        self.assertIn("vigenere", c.id.lower(), "ID should mention vigenere")
        self.assertIn("hill", c.id.lower(), "ID should mention hill")


if __name__ == '__main__':
    unittest.main()
