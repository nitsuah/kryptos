"""Tests for K4 candidate gate checks."""

import pytest

from kryptos.k4.candidate_checks import check_candidate
from kryptos.k4.hypothesis_check import check_hypothesis


def test_vigenere_kryptos_reproduces_but_cribs_fail():
    """Plaintext from Vigenère/KRYPTOS reproduces with same key but cribs fail."""
    hypothesis = check_hypothesis("vigenere", "KRYPTOS")
    plaintext = hypothesis["plaintext"]

    result = check_candidate(plaintext, "vigenere", "KRYPTOS")

    assert result["normalised"] == plaintext
    assert result["length_ok"] is True
    assert result["reproduces"] is True
    assert result["cribs_ok"] is False
    assert result["all_checks_pass"] is False


def test_vigenere_kryptos_wrong_key_does_not_reproduce():
    """Same plaintext with different key does not reproduce."""
    hypothesis = check_hypothesis("vigenere", "KRYPTOS")
    plaintext = hypothesis["plaintext"]

    result = check_candidate(plaintext, "vigenere", "WRONGKEY")

    assert result["normalised"] == plaintext
    assert result["length_ok"] is True
    assert result["reproduces"] is False
    assert result["all_checks_pass"] is False


def test_short_string_length_fails():
    """Short string fails length check."""
    result = check_candidate("SHORT", "vigenere", "KEY")

    assert result["normalised"] == "SHORT"
    assert result["length_ok"] is False
    assert result["reproduces"] is False
    assert result["all_checks_pass"] is False


def test_unknown_family_raises_value_error():
    """Unknown family raises ValueError."""
    with pytest.raises(ValueError, match="Unknown family"):
        check_candidate("A" * 97, "unknown_family", "KEY")


def test_all_checks_pass_false_in_all_cases():
    """all_checks_pass is false in all tested cases."""
    # Case 1: reproduces but cribs fail
    hypothesis = check_hypothesis("vigenere", "KRYPTOS")
    result1 = check_candidate(hypothesis["plaintext"], "vigenere", "KRYPTOS")
    assert result1["all_checks_pass"] is False

    # Case 2: wrong key
    result2 = check_candidate(hypothesis["plaintext"], "vigenere", "WRONGKEY")
    assert result2["all_checks_pass"] is False

    # Case 3: short string
    result3 = check_candidate("SHORT", "vigenere", "KEY")
    assert result3["all_checks_pass"] is False
