"""Tests for keyed alphabet realignment — K4-ATTACK-3."""

from kryptos.k4.keystream_validator import K4_CRIBS
from kryptos.k4.vigenere_key_recovery import (
    ABSCISSA_ALPHABET,
    KEYED_ALPHABET,
    KNOWN_KEYED_ALPHABETS,
    PALIMPSEST_ALPHABET,
    STANDARD_ALPHABET,
    build_keyed_alphabet,
    check_keyed_alphabet_realignment,
    derive_keystream_under_alphabet,
)

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"


class TestBuildKeyedAlphabet:
    def test_kryptos_alphabet(self):
        alpha = build_keyed_alphabet("KRYPTOS")
        assert alpha == KEYED_ALPHABET
        assert len(alpha) == 26

    def test_palimpsest_alphabet(self):
        alpha = build_keyed_alphabet("PALIMPSEST")
        assert alpha == PALIMPSEST_ALPHABET
        assert len(alpha) == 26
        assert alpha.startswith("PALIMSE")  # unique chars from keyword in order

    def test_abscissa_alphabet(self):
        alpha = build_keyed_alphabet("ABSCISSA")
        assert alpha == ABSCISSA_ALPHABET
        assert len(alpha) == 26
        assert alpha.startswith("ABSCI")  # unique chars from keyword in order

    def test_all_26_chars_present(self):
        for name, alpha in KNOWN_KEYED_ALPHABETS.items():
            assert len(alpha) == 26, f"{name} alphabet has wrong length"
            assert len(set(alpha)) == 26, f"{name} alphabet has duplicates"

    def test_standard_alphabet_unchanged(self):
        alpha = build_keyed_alphabet("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        assert alpha == STANDARD_ALPHABET

    def test_empty_keyword_gives_standard(self):
        alpha = build_keyed_alphabet("")
        assert alpha == STANDARD_ALPHABET


class TestDeriveKeystreamUnderAlphabet:
    def test_standard_alphabet_matches_validator(self):
        from kryptos.k4.keystream_validator import K4_EXPECTED_KEYSTREAMS

        result = derive_keystream_under_alphabet(K4, K4_CRIBS, STANDARD_ALPHABET)
        assert result["EAST"] == K4_EXPECTED_KEYSTREAMS["EAST"]
        assert result["NORTHEAST"] == K4_EXPECTED_KEYSTREAMS["NORTHEAST"]

    def test_returns_all_crib_labels(self):
        result = derive_keystream_under_alphabet(K4, K4_CRIBS, KEYED_ALPHABET)
        assert set(result.keys()) == set(K4_CRIBS.keys())

    def test_shifts_in_range(self):
        for name, alpha in KNOWN_KEYED_ALPHABETS.items():
            result = derive_keystream_under_alphabet(K4, K4_CRIBS, alpha)
            for label, shifts in result.items():
                for s in shifts:
                    assert 0 <= s < 26, f"Shift {s} out of range for {name}/{label}"

    def test_correct_length_per_crib(self):
        result = derive_keystream_under_alphabet(K4, K4_CRIBS, STANDARD_ALPHABET)
        assert len(result["EAST"]) == 4  # EAST is 4 chars
        assert len(result["NORTHEAST"]) == 9  # NORTHEAST is 9 chars
        assert len(result["BERLIN"]) == 6
        assert len(result["CLOCK"]) == 5


class TestCheckKeyedAlphabetRealignment:
    def test_returns_all_alphabets(self):
        result = check_keyed_alphabet_realignment(K4, K4_CRIBS)
        assert set(result.keys()) == set(KNOWN_KEYED_ALPHABETS.keys())

    def test_standard_matches_known_keystreams(self):
        from kryptos.k4.keystream_validator import K4_EXPECTED_KEYSTREAMS

        result = check_keyed_alphabet_realignment(K4, K4_CRIBS)
        standard = result["STANDARD"]
        for label, shifts in K4_EXPECTED_KEYSTREAMS.items():
            assert standard[label] == shifts

    def test_keyed_alphabets_produce_different_shifts(self):
        result = check_keyed_alphabet_realignment(K4, K4_CRIBS)
        # KRYPTOS alphabet should differ from standard (different ordering)
        assert result["KRYPTOS"]["EAST"] != result["STANDARD"]["EAST"]

    def test_custom_alphabets_override(self):
        custom = {"MY_KEY": build_keyed_alphabet("SANBORN")}
        result = check_keyed_alphabet_realignment(K4, K4_CRIBS, alphabets=custom)
        assert "MY_KEY" in result
        assert "STANDARD" not in result
