import pytest

from kryptos.k4.hypothesis_check import check_hypothesis, crib_verdict
from kryptos.k4.keystream_validator import K4_CRIBS


def test_crib_verdict_checks_overlapping_and_later_crib_positions():
    plaintext = ["X"] * 97
    for word, start in K4_CRIBS.values():
        plaintext[start : start + len(word)] = word

    assert len(plaintext) == 97
    assert crib_verdict("".join(plaintext)) == {label: True for label in K4_CRIBS}


def test_all_x_negative_control_matches_no_cribs():
    assert crib_verdict("X" * 97) == {label: False for label in K4_CRIBS}


def test_vigenere_hypothesis_returns_normalized_result():
    result = check_hypothesis("VIGENERE", "KRYPTOS")

    assert result["family"] == "vigenere"
    assert result["key"] == "KRYPTOS"
    assert result["plaintext"] == (
        "OAXXLKMOFFMGPKOJGCTPLFJZNJIWRMEWYRZTVYLYEHSOCWUQLAPHWGJTISUFIAYNRRNKZFZERWNBTKXVRFTTIFXMDJRUDXSPV"
    )
    assert result["hit_count"] == 0
    assert result["all_cribs_match"] is False


def test_beaufort_accepts_mixed_case_family_and_key():
    result = check_hypothesis("BeAuFoRt", "kRyPtOs")

    assert result["family"] == "beaufort"
    assert result["key"] == "KRYPTOS"
    assert result["plaintext"] == (
        "UNYYCKBUHHBGWKUDGLVWCHDRADEPZBIPXZRVTXCXIFQULPOSCNWFPGDVEQOHENXAZZAKRHRIZPAMVKYTZHVVEHYBJDZOJYQWT"
    )
    assert result["hit_count"] == 0
    assert result["all_cribs_match"] is False


def test_unknown_family_is_rejected():
    with pytest.raises(ValueError, match="Unknown family: atbash"):
        check_hypothesis("Atbash", "KRYPTOS")


def test_empty_key_uses_existing_cipher_validation():
    with pytest.raises(ValueError, match="Key must contain at least one alphabetic character"):
        check_hypothesis("vigenere", "")
