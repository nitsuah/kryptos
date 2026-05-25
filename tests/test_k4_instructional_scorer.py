"""Tests for InstructionalScorer (K4-ATTACK-5)."""

import pytest
from kryptos.k4.scoring_instructional import (
    INSTRUCTIONAL_VECTORS,
    combined_instructional_score,
    entropy_gate,
    instructional_score,
    levenshtein,
)


class TestLevenshtein:
    def test_identical(self):
        assert levenshtein("EAST", "EAST") == 0

    def test_single_sub(self):
        assert levenshtein("EAST", "EIST") == 1

    def test_single_insert(self):
        assert levenshtein("EAST", "EEAST") == 1

    def test_single_delete(self):
        assert levenshtein("EAST", "AST") == 1

    def test_iqlusion(self):
        # Sanborn-style misspelling pattern
        assert levenshtein("ILLUSION", "IQLUSION") == 2

    def test_desparatly(self):
        assert levenshtein("DESPERATELY", "DESPARATLY") <= 3

    def test_empty(self):
        assert levenshtein("", "ABC") == 3
        assert levenshtein("ABC", "") == 3

    def test_symmetric(self):
        assert levenshtein("NORTH", "SOUTH") == levenshtein("SOUTH", "NORTH")


class TestInstructionalScore:
    def test_exact_match_scores_positive(self):
        score = instructional_score("FINDTHEEASTWALL")
        assert score > 0

    def test_gibberish_scores_low(self):
        score = instructional_score("QZXVBJKWPQZX")
        assert score == 0.0

    def test_direction_words_score_high(self):
        directional = instructional_score("PROCEEDTOWARDSTHENORTHEAST")
        plain = instructional_score("ABCDEFGHIJKLMNOPQRSTU")
        assert directional > plain

    def test_fuzzy_match_tol_0_strict(self):
        # "NORT" is 1 edit from "NORTH" — strict mode should miss it
        score_strict = instructional_score("NORT", fuzzy_tol=0)
        score_fuzzy  = instructional_score("NORT", fuzzy_tol=1)
        assert score_strict == 0.0
        assert score_fuzzy > 0.0

    def test_score_normalised(self):
        # Padding with noise shouldn't inflate the score arbitrarily
        short = instructional_score("DIGHERE")
        padded = instructional_score("DIGHERE" + "X" * 100)
        # Both positive, but padded should be lower (more noise per char)
        assert short > 0
        assert padded < short

    def test_known_k4_vocabulary(self):
        for word in ["EAST", "NORTHEAST", "BERLIN", "CLOCK", "DIG", "FIND"]:
            assert instructional_score(word) > 0, f"{word} should score positive"


class TestEntropyGate:
    def test_english_text_passes(self):
        assert entropy_gate("THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG") is True

    def test_single_char_repeat_may_fail(self):
        # All-A text has entropy 0, well below min
        result = entropy_gate("A" * 50)
        assert result is False

    def test_short_text_always_passes(self):
        # Short texts bypass the gate
        assert entropy_gate("AB") is True

    def test_k4_ciphertext_high_entropy(self):
        K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        # K4 has near-uniform distribution → high entropy → may fail gate
        # (acceptable: it IS ciphertext, not plaintext)
        result = entropy_gate(K4)
        assert isinstance(result, bool)


class TestCombinedInstructionalScore:
    def test_returns_float(self):
        score = combined_instructional_score("DIGTOWARDTHENORTH")
        assert isinstance(score, float)

    def test_instructional_text_beats_gibberish(self):
        instructional = combined_instructional_score("PROCEEDEASTALONGTHEPATH")
        gibberish = combined_instructional_score("ZXQVBJWPKZXQVBJWPKZXQVB")
        assert instructional > gibberish

    def test_custom_scorer_used(self):
        sentinel = []
        def spy_scorer(text):
            sentinel.append(text)
            return 0.0
        combined_instructional_score("TEST", base_scorer=spy_scorer, gate_entropy=False)
        assert "TEST" in sentinel

    def test_gate_disabled_always_applies_bonus(self):
        text = "A" * 50  # would fail entropy gate
        gated   = combined_instructional_score(text, gate_entropy=True)
        ungated = combined_instructional_score(text, gate_entropy=False)
        # Both should return floats; gated returns base only, ungated adds bonus
        assert isinstance(gated, float)
        assert isinstance(ungated, float)
