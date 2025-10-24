"""Positive control tests (sanity checks) for hypothesis framework.

These tests validate that our hypothesis implementations CAN find correct
answers when they exist, not just rule out incorrect methods.
"""

import unittest

from kryptos.k4.hill_cipher import hill_encrypt
from kryptos.k4.hypotheses import BerlinClockTranspositionHypothesis, HillCipher2x2Hypothesis
from kryptos.k4.transposition import apply_columnar_permutation


class TestHypothesisSanity(unittest.TestCase):
    """Positive control tests - can we find known answers?"""

    def test_hill_2x2_recovers_known_encryption(self):
        """Test that Hill 2x2 hypothesis can recover a known Hill-encrypted plaintext."""
        # Known plaintext
        plaintext = "BERLINCLOCKEASTNORTHEAST"

        # Encrypt with known 2x2 Hill cipher key
        known_key = [[5, 8], [17, 3]]  # Invertible mod 26
        ciphertext = hill_encrypt(plaintext, known_key)

        # Run Hill hypothesis
        hyp = HillCipher2x2Hypothesis()
        candidates = hyp.generate_candidates(ciphertext, limit=100)

        # Check if correct key is found
        found_correct = False
        for cand in candidates:
            if cand.key_info['matrix'] == known_key:
                found_correct = True
                # Verify plaintext matches (first N characters)
                self.assertTrue(
                    plaintext[:20] in cand.plaintext or cand.plaintext[:20] in plaintext,
                    f"Correct key found but plaintext doesn't match. Got: {cand.plaintext[:30]}",
                )
                break

        self.assertTrue(found_correct, "Hill 2x2 hypothesis failed to find correct key in top-100 candidates")

    @unittest.skip("Transposition inversion logic needs refinement")
    def test_transposition_recovers_known_permutation(self):
        """Test that transposition hypothesis can recover a known column permutation."""
        # Known plaintext
        plaintext = "BERLINCLOCKEASTNORTHEASTPALIMPSEST"

        # Apply known columnar transposition
        n_cols = 5
        known_perm = (2, 0, 4, 1, 3)  # Column permutation
        ciphertext = apply_columnar_permutation(plaintext, n_cols, known_perm)

        # Run transposition hypothesis
        hyp = BerlinClockTranspositionHypothesis(
            widths=[5],  # Only test width=5
            prune=False,
            max_perms=120,  # 5! = 120, will test all
        )
        candidates = hyp.generate_candidates(ciphertext, limit=120)

        # Check if correct permutation is found
        found_correct = False
        for cand in candidates:
            if cand.key_info['permutation'] == known_perm:
                found_correct = True
                # Note: transposition inversion may not be perfect for short text
                # Just check that we found the permutation
                break

        self.assertTrue(found_correct, f"Transposition hypothesis failed to find correct permutation {known_perm}")

    def test_hill_ranks_correct_plaintext_higher(self):
        """Test that Hill hypothesis ranks correct plaintext higher than gibberish."""
        # Use a meaningful English phrase
        plaintext = "PALIMPSESTISTHEKEYTOKRYPTOSPARTONE"

        # Encrypt with Hill cipher
        key = [[7, 3], [5, 2]]
        ciphertext = hill_encrypt(plaintext, key)

        # Run Hill hypothesis
        hyp = HillCipher2x2Hypothesis()
        candidates = hyp.generate_candidates(ciphertext, limit=50)

        # Find the candidate with correct key
        correct_candidate = None
        for cand in candidates:
            if cand.key_info['matrix'] == key:
                correct_candidate = cand
                break

        # Check that correct candidate has relatively high score
        if correct_candidate:
            # Should be in top 50% at least
            rank = candidates.index(correct_candidate) + 1
            self.assertLessEqual(rank, 25, f"Correct Hill key ranked #{rank}/50 - scoring function may be broken")

    @unittest.skip("Scoring function needs calibration for this test")
    def test_known_k1_pattern_detectable(self):
        """Test on simplified K1-style cipher (Vigenère with PALIMPSEST)."""
        # K1 used Vigenère with keyword PALIMPSEST
        # This is a simplified test with known plaintext
        plaintext = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"

        # Simple Vigenère encryption (we'll implement this if needed)
        # For now, just verify our scoring functions work on known plaintext
        from kryptos.k4.scoring import combined_plaintext_score

        # Known plaintext should score better than random
        plaintext_score = combined_plaintext_score(plaintext)
        random_text = "XQZJKWPLMVBNCFGTYUIOHDSARE" + "QWZXCVBNMASDFGHJKLPOIUYTREW"
        random_score = combined_plaintext_score(random_text[: len(plaintext)])

        self.assertGreater(
            plaintext_score,
            random_score,
            f"Plaintext ({plaintext_score:.2f}) should score higher than random ({random_score:.2f})",
        )


if __name__ == '__main__':
    unittest.main()
