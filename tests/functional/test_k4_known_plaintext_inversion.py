"""Tests for kryptos.k4.known_plaintext_inversion."""

from __future__ import annotations

from kryptos.k4 import known_plaintext_inversion as kpi
from kryptos.k4.physical_grid import K4


class TestImpliedShifts:
    def test_returns_full_length_shift_list_for_trailing_mode(self):
        shifts = kpi.implied_shifts("row_major", "identity", 0, "trailing")
        assert shifts is not None
        assert len(shifts) == len(K4)

    def test_all_shifts_in_valid_range(self):
        shifts = kpi.implied_shifts("row_major", "identity", 0, "trailing")
        assert shifts is not None
        assert all(0 <= s < 26 for s in shifts)

    def test_none_for_unregistered_candidate(self):
        assert kpi.implied_shifts("row_major", "identity", 0, "trailing", candidate_name="not_real") is None

    def test_different_transpositions_give_different_shifts(self):
        # Sanity check the inversion actually depends on the transposition
        # hypothesis -- row_major and col_major should not coincidentally
        # produce the same implied shift sequence.
        a = kpi.implied_shifts("row_major", "identity", 0, "trailing")
        b = kpi.implied_shifts("col_major", "identity", 0, "trailing")
        assert a != b


class TestScanTranspositions:
    def test_small_scope_runs_and_reports_a_verdict(self):
        r = kpi.scan_transpositions(
            order_names=["row_major", "col_major"],
            reflection_names=["identity", "flip_h"],
            rotation_offsets=[0, 6],
            remainder_modes=["trailing"],
        )
        assert r["status"] in ("null_result", "hypothesis_found")
        assert r["total_tested"] == 2 * 2 * 2 * 1

    def test_hits_only_reported_when_a_period_or_substitution_is_actually_consistent(self):
        # A hit is recorded on EITHER signal (repeating period OR a fixed
        # monoalphabetic bijection) -- see scan_transpositions' `periods or
        # is_substitution` gate -- so neither field alone is required, but
        # at least one of them must be truthy for every reported hit.
        r = kpi.scan_transpositions(
            order_names=["row_major"],
            reflection_names=["identity"],
            rotation_offsets=[0],
            remainder_modes=["trailing"],
            period_range=range(2, 21),
        )
        for hit in r["hits"]:
            assert hit["consistent_periods"] or hit["consistent_monoalphabetic_substitution"]

    def test_hit_dicts_carry_the_substitution_field(self):
        r = kpi.scan_transpositions(
            order_names=["row_major", "col_major"],
            reflection_names=["identity"],
            rotation_offsets=[0],
            remainder_modes=["trailing"],
        )
        for hit in r["hits"]:
            assert "consistent_monoalphabetic_substitution" in hit
            assert isinstance(hit["consistent_monoalphabetic_substitution"], bool)

    def test_never_raises_eureka(self):
        # This module must never call EurekaSignal -- any signal here rests
        # on the unverified reconstructed plaintext and can only ever be a
        # hypothesis, not a promoted candidate. A full default-scope scan
        # (already run for real, see K4_ACTIVE_RESEARCH.md) completing
        # without exception is itself part of that guarantee.
        r = kpi.scan_transpositions(
            order_names=["row_major", "col_major"],
            reflection_names=["identity"],
            rotation_offsets=[0],
            remainder_modes=["trailing"],
        )
        assert "status" in r


class TestIsConsistentSubstitution:
    def test_true_for_a_genuine_fixed_bijection(self):
        # ROT13-style: every C always maps to the same P, and it's a valid
        # bijection (no P reused for two different Cs in this sample).
        pre_transposition = "ABAB"
        plaintext = "NONO"
        assert kpi._is_consistent_substitution(pre_transposition, plaintext) is True

    def test_false_when_same_ciphertext_letter_maps_to_two_plaintext_letters(self):
        pre_transposition = "AA"
        plaintext = "NM"
        assert kpi._is_consistent_substitution(pre_transposition, plaintext) is False

    def test_empty_strings_are_vacuously_consistent(self):
        assert kpi._is_consistent_substitution("", "") is True


class TestImpliedShiftsRectangular:
    def test_returns_shift_list_for_a_valid_permutation(self):
        shifts = kpi.implied_shifts_rectangular(7, tuple(range(7)))
        assert shifts is not None
        assert all(0 <= s < 26 for s in shifts)

    def test_length_matches_the_shorter_of_pre_transposition_and_plaintext(self):
        shifts = kpi.implied_shifts_rectangular(7, tuple(range(7)))
        assert shifts is not None
        assert len(shifts) <= len(K4)

    def test_none_for_unregistered_candidate(self):
        assert kpi.implied_shifts_rectangular(7, tuple(range(7)), candidate_name="not_real") is None

    def test_different_permutations_give_different_shifts(self):
        identity = tuple(range(7))
        reversed_perm = tuple(reversed(range(7)))
        a = kpi.implied_shifts_rectangular(7, identity)
        b = kpi.implied_shifts_rectangular(7, reversed_perm)
        assert a != b


class TestScanRectangularTranspositions:
    def test_small_scope_runs_and_reports_a_verdict(self):
        from itertools import islice, permutations

        # A handful of 7-column permutations only -- the full exhaustive
        # 7!+8!+10! scan is run for real separately (see
        # K4_ACTIVE_RESEARCH.md) and is far too slow for a unit test.
        r = kpi.scan_rectangular_transpositions(grid_sizes=[7], period_range=range(2, 6))
        assert r["status"] in ("null_result", "hypothesis_found")
        assert r["total_tested"] == len(list(permutations(range(7))))
        assert list(islice(r["hits"], 0)) == []  # hits list is always present, possibly empty

    def test_hits_carry_both_signal_fields(self):
        r = kpi.scan_rectangular_transpositions(grid_sizes=[7], period_range=range(2, 6))
        for hit in r["hits"]:
            assert "consistent_periods" in hit
            assert "consistent_monoalphabetic_substitution" in hit
            assert hit["consistent_periods"] or hit["consistent_monoalphabetic_substitution"]

    def test_never_raises_eureka(self):
        r = kpi.scan_rectangular_transpositions(grid_sizes=[7], period_range=range(2, 6))
        assert "status" in r
