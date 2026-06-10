"""Functional tests for kryptos.k4.vigenere_stress_tests utilities.

Covers the pure helper functions (noise injection, match-ratio scoring) and
the K1/K2 constants. The expensive recover_key_by_frequency-based stress
runs are exercised in tests/e2e/test_k1_k2_stress_suite.py.
"""

from __future__ import annotations

import random

from kryptos.ciphers import vigenere_decrypt
from kryptos.k4.vigenere_stress_tests import (
    K1_CIPHERTEXT,
    K1_KEY,
    K1_PLAINTEXT,
    K2_CIPHERTEXT,
    K2_KEY,
    K2_PLAINTEXT,
    _match_ratio,
    inject_noise,
)


def test_constants_round_trip():
    assert vigenere_decrypt(K1_CIPHERTEXT, K1_KEY) == K1_PLAINTEXT
    assert vigenere_decrypt(K2_CIPHERTEXT, K2_KEY) == K2_PLAINTEXT
    assert len(K1_CIPHERTEXT) == len(K1_PLAINTEXT)
    assert len(K2_CIPHERTEXT) == len(K2_PLAINTEXT)


def test_inject_noise_zero_rate_is_identity():
    rng = random.Random(0)
    assert inject_noise(K1_CIPHERTEXT, 0.0, rng) == K1_CIPHERTEXT


def test_inject_noise_full_rate_only_touches_alpha_chars():
    text = "AB12 CD"
    rng = random.Random(0)
    noisy = inject_noise(text, 1.0, rng)
    assert len(noisy) == len(text)
    for original, replaced in zip(text, noisy, strict=True):
        if original.isalpha():
            assert replaced.isalpha()
        else:
            assert replaced == original


def test_match_ratio_identical():
    assert _match_ratio("ABCDEF", "ABCDEF") == 1.0


def test_match_ratio_partial():
    assert _match_ratio("ABCD", "ABXY") == 0.5


def test_match_ratio_length_mismatch_or_empty():
    assert _match_ratio("ABC", "AB") == 0.0
    assert _match_ratio("", "") == 0.0
