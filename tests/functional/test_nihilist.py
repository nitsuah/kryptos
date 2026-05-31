"""Tests for the Nihilist cipher module."""

import pytest
from kryptos.k4.nihilist import (
    build_square,
    format_ciphertext,
    nihilist_decrypt,
    nihilist_encrypt,
    parse_ciphertext,
)


class TestBuildSquare:
    def test_returns_5x5(self):
        sq = build_square("KRYPTOS")
        assert len(sq) == 5
        assert all(len(row) == 5 for row in sq)

    def test_25_unique_chars(self):
        sq = build_square("KRYPTOS")
        flat = [c for row in sq for c in row]
        assert len(set(flat)) == 25

    def test_no_j_in_square(self):
        sq = build_square("KRYPTOS")
        flat = [c for row in sq for c in row]
        assert "J" not in flat

    def test_keyword_chars_first(self):
        sq = build_square("KRYPTOS")
        flat = [c for row in sq for c in row]
        # K, R, Y, P, T, O, S appear before remaining alphabet chars
        for ch in "KRYPTOS":
            if ch == "J":
                continue
            assert flat.index(ch) < flat.index("Z")


class TestNihilistRoundtrip:
    def test_basic_roundtrip(self):
        ct = nihilist_encrypt("HELLO", "KRYPTOS", "SECRET")
        pt = nihilist_decrypt(ct, "KRYPTOS", "SECRET")
        assert pt == "HELLO"

    def test_longer_text(self):
        pt = "FINDTHEEASTWALL"
        ct = nihilist_encrypt(pt, "PALIMPSEST", "NORTHEAST")
        recovered = nihilist_decrypt(ct, "PALIMPSEST", "NORTHEAST")
        assert recovered == pt

    def test_ciphertext_is_list_of_ints(self):
        ct = nihilist_encrypt("HELLO", "KRYPTOS", "KEY")
        assert isinstance(ct, list)
        assert all(isinstance(v, int) for v in ct)

    def test_same_length_as_plaintext(self):
        pt = "KRYPTOS"
        ct = nihilist_encrypt(pt, "KRYPTOS", "KEY")
        assert len(ct) == len(pt)

    def test_j_treated_as_i(self):
        # J and I should decrypt to the same character (I)
        ct_i = nihilist_encrypt("I", "KRYPTOS", "KEY")
        ct_j = nihilist_encrypt("J", "KRYPTOS", "KEY")
        assert ct_i == ct_j
        assert nihilist_decrypt(ct_i, "KRYPTOS", "KEY") == "I"

    def test_different_keys_differ(self):
        ct1 = nihilist_encrypt("TEST", "KRYPTOS", "KEYONE")
        ct2 = nihilist_encrypt("TEST", "KRYPTOS", "KEYTWO")
        assert ct1 != ct2

    def test_cyclic_key(self):
        # Single-char key: shifts by same amount throughout
        ct = nihilist_encrypt("AAAA", "KRYPTOS", "K")
        # All values should be equal (same offset repeated)
        assert len(set(ct)) == 1

    def test_empty_key_raises(self):
        with pytest.raises(ValueError):
            nihilist_encrypt("HELLO", "KRYPTOS", "123")  # no alpha

    def test_format_and_parse_roundtrip(self):
        ct = nihilist_encrypt("HELLO", "KRYPTOS", "KEY")
        formatted = format_ciphertext(ct)
        parsed = parse_ciphertext(formatted)
        assert parsed == ct
