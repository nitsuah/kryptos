"""Tests for kryptos.k4.clock_rotation — 24-position permutation library."""

from __future__ import annotations

import pytest

from kryptos.k4 import clock_rotation as cr
from kryptos.k4.geometry24 import COLS as N


class TestRotate:
    def test_is_permutation(self):
        for offset in range(N):
            perm = cr.rotate(offset)
            assert sorted(perm) == list(range(N))

    def test_offset_zero_is_identity(self):
        assert cr.rotate(0) == list(range(N))

    def test_priority_offsets_are_permutations(self):
        for offset in cr.PRIORITY_OFFSETS:
            perm = cr.rotate(offset)
            assert sorted(perm) == list(range(N))

    def test_plus_and_minus_six_are_distinct(self):
        assert cr.rotate(6) != cr.rotate(-6)

    def test_rotated_column_matches_rotate(self):
        offset = 6
        perm = cr.rotate(offset)
        for c in range(N):
            assert cr.rotated_column(c, offset) == perm[c]

    def test_direction_reversed_differs_from_forward(self):
        assert cr.rotate(0, direction=-1) != cr.rotate(0, direction=1)
        assert sorted(cr.rotate(0, direction=-1)) == list(range(N))

    def test_direction_reversed_exact_order(self):
        # documented as "23 22 21 ... 0": c=0 maps to n-1 when offset=0
        assert cr.rotate(0, direction=-1) == list(range(N - 1, -1, -1))
        assert cr.rotated_column(0, offset=0, direction=-1) == N - 1

    def test_invalid_direction_raises(self):
        with pytest.raises(ValueError):
            cr.rotate(0, direction=0)


class TestOriginFromHour:
    def test_range(self):
        for hour in range(24):
            assert cr.origin_from_hour(hour) == hour

    def test_wraps_beyond_24(self):
        assert cr.origin_from_hour(25) == 1
        assert cr.origin_from_hour(-1) == N - 1


class TestGeographyPriorityOffsets:
    def test_returns_named_offsets(self):
        offsets = cr.geography_priority_offsets()
        assert len(offsets) > 0
        for name, value in offsets.items():
            assert isinstance(name, str)
            assert 0 <= value < N

    def test_includes_bearing_and_timezone(self):
        offsets = cr.geography_priority_offsets()
        assert "cia_berlin_bearing_mod24" in offsets
        assert "timezone_offset_hours" in offsets
        assert offsets["timezone_offset_hours"] == cr.BERLIN_LANGLEY_OFFSET_HOURS % N


class TestGeographyDerivedBearings:
    def test_returns_named_float_bearings(self):
        bearings = cr.geography_derived_bearings()
        assert "cia_berlin_bearing" in bearings
        assert "cia_berlin_bearing_reversed" in bearings
        for value in bearings.values():
            assert isinstance(value, float)
            assert 0.0 <= value < 360.0

    def test_reversed_is_opposite(self):
        bearings = cr.geography_derived_bearings()
        forward = bearings["cia_berlin_bearing"]
        reverse = bearings["cia_berlin_bearing_reversed"]
        assert reverse == pytest.approx((forward + 180.0) % 360.0)

    def test_matches_bearing_attack_source(self):
        from kryptos.k4.bearing_attack import CIA_BERLIN_BEARING_DEG

        bearings = cr.geography_derived_bearings()
        assert bearings["cia_berlin_bearing"] == CIA_BERLIN_BEARING_DEG

    def test_includes_mengenlehreuhr_weltzeituhr(self):
        bearings = cr.geography_derived_bearings()
        assert "mengenlehreuhr_weltzeituhr_1990" in bearings
        assert "mengenlehreuhr_weltzeituhr_current" in bearings


class TestMengenlehreuhrWeltzeituhrBearings:
    def test_four_named_bearings(self):
        b = cr.mengenlehreuhr_weltzeituhr_bearings()
        assert set(b) == {
            "mengenlehreuhr_weltzeituhr_1990",
            "mengenlehreuhr_weltzeituhr_1990_reversed",
            "mengenlehreuhr_weltzeituhr_current",
            "mengenlehreuhr_weltzeituhr_current_reversed",
        }

    def test_close_to_ene(self):
        # Exact ENE is 67.5 deg. Both the 1990 (Sanborn-era) and current
        # Mengenlehreuhr locations should land within a few degrees of it —
        # this is the whole point of the hypothesis.
        b = cr.mengenlehreuhr_weltzeituhr_bearings()
        assert abs(b["mengenlehreuhr_weltzeituhr_1990"] - 67.5) < 5.0
        assert abs(b["mengenlehreuhr_weltzeituhr_current"] - 67.5) < 5.0

    def test_reversed_pairs_are_opposite(self):
        b = cr.mengenlehreuhr_weltzeituhr_bearings()
        assert b["mengenlehreuhr_weltzeituhr_1990_reversed"] == pytest.approx(
            (b["mengenlehreuhr_weltzeituhr_1990"] + 180.0) % 360.0
        )
        assert b["mengenlehreuhr_weltzeituhr_current_reversed"] == pytest.approx(
            (b["mengenlehreuhr_weltzeituhr_current"] + 180.0) % 360.0
        )

    def test_1990_and_current_differ(self):
        # Different physical locations (pre/post 1996 move) must give a
        # different bearing -- otherwise the period-accuracy correction in
        # this module's docstring would be pointless.
        b = cr.mengenlehreuhr_weltzeituhr_bearings()
        assert b["mengenlehreuhr_weltzeituhr_1990"] != b["mengenlehreuhr_weltzeituhr_current"]
