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

    def test_hits_only_reported_when_a_period_is_actually_consistent(self):
        r = kpi.scan_transpositions(
            order_names=["row_major"],
            reflection_names=["identity"],
            rotation_offsets=[0],
            remainder_modes=["trailing"],
            period_range=range(2, 21),
        )
        for hit in r["hits"]:
            assert hit["consistent_periods"]

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
