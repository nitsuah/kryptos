"""Tests for kryptos.k4.geometry24 — 24-column grid fill-order engine."""

from __future__ import annotations

import pytest

from kryptos.k4 import geometry24 as g24


class TestOrderCoords:
    @pytest.mark.parametrize("name", g24.ORDER_NAMES)
    def test_bijection_over_96_cells(self, name):
        coords = g24.order_coords(name)
        assert len(coords) == g24.CORE_LEN
        assert len(set(coords)) == g24.CORE_LEN
        for r, c in coords:
            assert 0 <= r < g24.ROWS
            assert 0 <= c < g24.COLS

    @pytest.mark.parametrize("base_name", list(g24.BASE_ORDERS))
    def test_reversed_is_true_reverse(self, base_name):
        base = g24.order_coords(base_name)
        reversed_ = g24.order_coords(f"{base_name}_reversed")
        assert reversed_ == list(reversed(base))

    def test_row_major_is_identity_flat(self):
        coords = g24.order_coords("row_major")
        flat = g24.coords_to_flat(coords, "drop")
        assert flat == list(range(g24.CORE_LEN))

    def test_unknown_order_raises(self):
        with pytest.raises(ValueError):
            g24.order_coords("nonsense")


class TestRemainderModes:
    @pytest.mark.parametrize("mode", g24.REMAINDER_MODES)
    def test_length(self, mode):
        flat = g24.flat_indices_for_order("row_major", mode)
        expected_len = g24.CORE_LEN if mode == "drop" else g24.TOTAL_LEN
        assert len(flat) == expected_len

    def test_trailing_places_remainder_last(self):
        flat = g24.flat_indices_for_order("row_major", "trailing")
        assert flat[-1] == g24.CORE_LEN
        assert sorted(flat) == list(range(g24.TOTAL_LEN))

    def test_leading_places_remainder_first(self):
        flat = g24.flat_indices_for_order("row_major", "leading")
        assert flat[0] == 0
        assert sorted(flat) == list(range(g24.TOTAL_LEN))

    def test_drop_excludes_remainder(self):
        flat = g24.flat_indices_for_order("row_major", "drop")
        assert g24.CORE_LEN not in flat
        assert sorted(flat) == list(range(g24.CORE_LEN))

    def test_unknown_mode_raises(self):
        with pytest.raises(ValueError):
            g24.coords_to_flat(g24.order_coords("row_major"), "bogus")


class TestApplyForwardInverse:
    @pytest.mark.parametrize("name", g24.ORDER_NAMES)
    @pytest.mark.parametrize("mode", ["trailing", "leading"])
    def test_round_trip(self, name, mode):
        text = "".join(chr(ord("A") + (i % 26)) for i in range(g24.TOTAL_LEN))
        flat = g24.flat_indices_for_order(name, mode)
        forward = g24.apply_forward(text, flat)
        assert len(forward) == g24.TOTAL_LEN
        recovered = g24.apply_inverse(forward, flat)
        assert recovered == text

    def test_drop_round_trip_recovers_core(self):
        text = "".join(chr(ord("A") + (i % 26)) for i in range(g24.TOTAL_LEN))
        flat = g24.flat_indices_for_order("row_major", "drop")
        forward = g24.apply_forward(text[: g24.CORE_LEN], flat)
        recovered = g24.apply_inverse(forward, flat)
        assert recovered == text[: g24.CORE_LEN]

    def test_apply_inverse_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            g24.apply_inverse("short", list(range(g24.TOTAL_LEN)))
