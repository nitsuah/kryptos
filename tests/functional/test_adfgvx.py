"""Tests for the ADFGVX fractionating cipher (K4 hypothesis module)."""

import pytest

from kryptos.k4.adfgvx import ADFGVX_CHARS, adfgvx_decrypt, adfgvx_encrypt, build_polybius_square, square_index


class TestBuildPolybius:
    def test_returns_6x6(self):
        sq = build_polybius_square("KRYPTOS")
        assert len(sq) == 6
        assert all(len(row) == 6 for row in sq)

    def test_36_unique_chars(self):
        sq = build_polybius_square("KRYPTOS")
        flat = [c for row in sq for c in row]
        assert len(set(flat)) == 36

    def test_keyword_chars_appear_first(self):
        sq = build_polybius_square("KRYPTOS")
        flat = [c for row in sq for c in row]
        # First unique chars of KRYPTOS in order
        assert flat[:7] == list("KRYPTOS")

    def test_wrong_alphabet_raises(self):
        with pytest.raises(ValueError):
            build_polybius_square("KRYPTOS", alphabet="ABCD")  # too short


class TestSquareIndex:
    def test_finds_char(self):
        sq = build_polybius_square("KRYPTOS")
        r, c = square_index(sq, "K")
        assert sq[r][c] == "K"

    def test_missing_raises(self):
        sq = build_polybius_square("KRYPTOS")
        with pytest.raises(KeyError):
            square_index(sq, "!")


class TestADFGVXRoundtrip:
    def test_basic_roundtrip(self):
        pt = "HELLO"
        ct = adfgvx_encrypt(pt, "KRYPTOS", "BERLIN")
        recovered = adfgvx_decrypt(ct, "KRYPTOS", "BERLIN")
        assert recovered == "HELLO"

    def test_longer_text(self):
        pt = "FINDTHEEASTWALL"
        ct = adfgvx_encrypt(pt, "PALIMPSEST", "NORTHEAST")
        recovered = adfgvx_decrypt(ct, "PALIMPSEST", "NORTHEAST")
        assert recovered == "FINDTHEEASTWALL"

    def test_ciphertext_only_adfgvx_chars(self):
        ct = adfgvx_encrypt("KRYPTOS", "KRYPTOS", "KEY")
        assert all(c in ADFGVX_CHARS for c in ct)

    def test_ciphertext_is_even_length(self):
        ct = adfgvx_encrypt("HELLO", "KRYPTOS", "BERLIN")
        # Fractionation doubles length, transposition preserves it
        assert len(ct) % 2 == 0

    def test_different_keys_different_output(self):
        ct1 = adfgvx_encrypt("TEST", "KRYPTOS", "KEYONE")
        ct2 = adfgvx_encrypt("TEST", "KRYPTOS", "KEYTWO")
        assert ct1 != ct2

    def test_different_square_keys(self):
        ct1 = adfgvx_encrypt("TEST", "KRYPTOS", "KEY")
        ct2 = adfgvx_encrypt("TEST", "ABSCISSA", "KEY")
        assert ct1 != ct2

    def test_digits_in_plaintext(self):
        pt = "ABC123"
        ct = adfgvx_encrypt(pt, "KRYPTOS", "CLOCK")
        recovered = adfgvx_decrypt(ct, "KRYPTOS", "CLOCK")
        assert recovered == pt

    def test_odd_length_ciphertext_raises(self):
        # "ADF" has 3 ADFGVX chars — odd length must raise
        with pytest.raises(ValueError):
            adfgvx_decrypt("ADF", "KRYPTOS", "KEY")
