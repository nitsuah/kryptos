"""The scoring word list is a real dictionary and separates English from random text."""

from __future__ import annotations

import random
import statistics

import pytest

from kryptos.k4 import scoring
from kryptos.k4.running_key import K3_PLAINTEXT_FULL
from kryptos.k4.vigenere_stress_tests import K1_PLAINTEXT, K2_PLAINTEXT

pytest.importorskip("english_words")


def test_wordlist_is_a_dictionary():
    assert len(scoring.WORDLIST) > 100_000
    assert scoring.WORDLIST_SOURCE.startswith("english-words")
    assert {"THE", "CLOCK", "BERLIN", "PASSAGE"} <= scoring.WORDLIST


def test_hit_rate_separates_english_from_frequency_matched_random():
    eng = K1_PLAINTEXT + K2_PLAINTEXT + K3_PLAINTEXT_FULL
    windows = [eng[i : i + 97] for i in range(0, len(eng) - 97, 20)]
    letters = list(scoring.LETTER_FREQ)
    weights = [scoring.LETTER_FREQ[c] for c in letters]
    rng = random.Random(0)
    randoms = ["".join(rng.choices(letters, weights, k=97)) for _ in range(len(windows))]
    e = [scoring.wordlist_hit_rate(t) for t in windows]
    r = [scoring.wordlist_hit_rate(t) for t in randoms]
    assert statistics.mean(e) > 4 * statistics.mean(r)
    assert min(e) > statistics.mean(r)
