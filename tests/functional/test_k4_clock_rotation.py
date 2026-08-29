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
