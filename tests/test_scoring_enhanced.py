"""Tests for enhanced linguistic scoring functions."""

import unittest

from kryptos.k4.scoring_enhanced import (
    combined_linguistic_score,
    enhanced_combined_score,
    linguistic_diagnostics,
    phonetic_rules_score,
    syllable_structure_score,
    vowel_consonant_alternation_score,
    word_boundary_score,
)


class TestEnhancedScoring(unittest.TestCase):
    def test_english_text_scores_higher_than_gibberish(self):
        """English text should score significantly higher than random gibberish."""
        english = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
        gibberish = "XQZVBKJWPMTHGLFDNRSCYXQZVBKJWPMTH"

        eng_score = combined_linguistic_score(english)
        gib_score = combined_linguistic_score(gibberish)

        self.assertGreater(
            eng_score,
            gib_score,
            f"English ({eng_score:.2f}) should score higher than gibberish ({gib_score:.2f})",
        )

    def test_word_boundary_detects_common_words(self):
        """Should detect common short words."""
        # Contains: THE, AND, FOR, THE, IS, AN
        text = "THEANDFORTHEISANEXAMPLE"
        score = word_boundary_score(text)

        self.assertGreater(score, 0.0, "Should detect some common words")

    def test_phonetic_rules_penalize_bad_clusters(self):
        """Should penalize impossible consonant clusters."""
        # Contains bad clusters: QZ, XQ, ZB
        bad_text = "QZXQZBPWMTHGLF"
        good_text = "THEBRIGHTSTAR"

        bad_score = phonetic_rules_score(bad_text)
        good_score = phonetic_rules_score(good_text)

        self.assertLess(
            bad_score,
            good_score,
            f"Bad clusters ({bad_score:.2f}) should score lower than good text ({good_score:.2f})",
        )

    def test_syllable_structure_recognizes_patterns(self):
        """Should recognize valid CV/CVC syllable patterns."""
        # CVCV pattern throughout
        good_syllables = "BANANA"  # BA-NA-NA (CV-CV-CV)
        # All consonants
        bad_syllables = "BCDFGH"

        good_score = syllable_structure_score(good_syllables)
        bad_score = syllable_structure_score(bad_syllables)

        self.assertGreater(
            good_score,
            bad_score,
            f"Good syllables ({good_score:.2f}) should score higher than bad ({bad_score:.2f})",
        )

    def test_vc_alternation_prefers_balanced(self):
        """Should prefer balanced vowel-consonant alternation."""
        # Good alternation
        balanced = "BANANA"  # CVCVCV
        # Poor alternation (all vowels then all consonants)
        unbalanced = "AEIOUYBCDFGH"

        balanced_score = vowel_consonant_alternation_score(balanced)
        unbalanced_score = vowel_consonant_alternation_score(unbalanced)

        self.assertGreater(
            balanced_score,
            unbalanced_score,
            f"Balanced ({balanced_score:.2f}) should score higher than unbalanced ({unbalanced_score:.2f})",
        )

    def test_enhanced_combined_score_works(self):
        """Enhanced score should run without errors and return reasonable values."""
        english = "THEBERLINCLOCKISANINTERESTINGPUZZLE"
        score = enhanced_combined_score(english)

        self.assertIsInstance(score, float, "Should return a float")
        # Should be less negative than pure gibberish
        self.assertGreater(score, -500.0, "Should not be extremely negative for English text")

    def test_linguistic_diagnostics_returns_all_metrics(self):
        """Diagnostic function should return all component scores."""
        text = "THEBERLINCLOCKISHERE"
        diag = linguistic_diagnostics(text)

        expected_keys = {
            'syllable_structure',
            'word_boundary',
            'phonetic_rules',
            'vc_alternation',
            'position_frequency',
            'combined_linguistic',
        }

        self.assertEqual(set(diag.keys()), expected_keys, "Should return all expected metrics")
        for key, value in diag.items():
            self.assertIsInstance(value, float, f"{key} should be a float")

    def test_known_plaintext_scores_well(self):
        """K1-K3 known plaintexts should score well with enhanced scoring."""
        # K1 plaintext (first 50 chars)
        k1_fragment = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHE"

        score = combined_linguistic_score(k1_fragment)

        # Should get substantial linguistic bonus
        self.assertGreater(score, 0.0, "K1 plaintext should get positive linguistic score")


if __name__ == '__main__':
    unittest.main()
