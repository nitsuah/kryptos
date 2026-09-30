"""Pin the K4 facts the docs quote, so a doc number can't drift from the ciphertext again.

Each test here corresponds to a claim in docs/analysis/K4_ACTIVE_RESEARCH.md or
K4_KEYSTREAM_ANALYSIS.md that was previously wrong (IC ~0.062, a fabricated local-IC
table, EAST "released 2023") or only partly checked (periods 2-20, Vigenère only).
"""

from __future__ import annotations

import pytest

from kryptos.k4.ic_profile import RANDOM_IC, ic_profile, segment_ics, segment_spread_p_value
from kryptos.k4.key_csp import CRIB_SHIFTS, periodic_family_consistency, solve_key_csp
from kryptos.k4.keystream_validator import K4_CRIB_RELEASES, K4_CRIBS, K4_EXPECTED_KEYSTREAMS
from kryptos.k4.physical_grid import K4


class TestIndexOfCoincidence:
    def test_k4_ic_is_near_random_not_english(self):
        ic = ic_profile()["ic"]
        assert ic == pytest.approx(0.0361, abs=5e-4)
        assert abs(ic - RANDOM_IC) < 0.005

    def test_segment_ics_match_docs(self):
        assert segment_ics() == pytest.approx([0.0464, 0.0464, 0.0341], abs=5e-4)

    def test_segment_spread_is_ordinary_noise(self):
        # The old "non-uniform local IC => substitution before transposition" argument
        # needs this to be small. It isn't.
        assert segment_spread_p_value(trials=1000) > 0.2


class TestCribProvenance:
    def test_release_ciphertext_matches_positions(self):
        for label, (word, start) in K4_CRIBS.items():
            ct = K4_CRIB_RELEASES[label]["ciphertext"]
            assert len(ct) == len(word)
            assert K4[start : start + len(ct)] == ct

    def test_release_dates(self):
        assert K4_CRIB_RELEASES["BERLIN"]["released"] == "2010-11"
        assert K4_CRIB_RELEASES["CLOCK"]["released"] == "2014-11"
        assert K4_CRIB_RELEASES["NORTHEAST"]["released"] == "2020-01"
        assert K4_CRIB_RELEASES["EAST"]["released"] == "2020-08"


class TestCribShifts:
    def test_crib_shifts_derived_from_canonical_cribs(self):
        expected = []
        for label, (_word, start) in K4_CRIBS.items():
            expected += [(start + i, s) for i, s in enumerate(K4_EXPECTED_KEYSTREAMS[label])]
        assert CRIB_SHIFTS == sorted(expected)

    def test_no_periodic_key_up_to_26_in_any_direct_family(self):
        result = periodic_family_consistency(max_period=26)
        assert set(result) == {"vigenere", "beaufort", "variant_beaufort", "quagmire3_kryptos"}
        assert all(periods == [] for periods in result.values())

    def test_first_consistent_period_is_27(self):
        result = periodic_family_consistency(max_period=27)
        assert all(periods == [27] for periods in result.values())

    def test_solve_key_csp_agrees(self):
        assert solve_key_csp(key_lengths=range(1, 27)) == {}


def test_periodic_consistency_positive_control():
    std = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    plain = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGWHILEASMALLBIRDWATCHESFROMTHEOLDOAKTREENEARTHERIVERBANKTODAYXX"
    key = [5, 17, 2, 21, 9, 0, 13]
    ct = "".join(std[(std.index(c) + key[i % 7]) % 26] for i, c in enumerate(plain))
    cribs = {label: (plain[start : start + len(word)], start) for label, (word, start) in K4_CRIBS.items()}
    result = periodic_family_consistency(max_period=10, ciphertext=ct, cribs=cribs)
    assert 7 in result["vigenere"]
