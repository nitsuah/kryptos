"""Tests for kryptos.k4.ene_routes — directional (compass) route generator."""

from __future__ import annotations

import math

import pytest

from kryptos.k4 import ene_routes as er
from kryptos.k4.geometry24 import COLS, ROWS


class TestCompassBearings:
    def test_sixteen_points(self):
        assert len(er.COMPASS_BEARINGS) == 16

    def test_spacing_is_22_5_degrees(self):
        values = sorted(er.COMPASS_BEARINGS.values())
        assert values[0] == 0.0
        for i in range(1, len(values)):
            assert values[i] - values[i - 1] == pytest.approx(22.5)

    def test_priority_directions_are_known(self):
        for direction in er.PRIORITY_DIRECTIONS:
            base = direction.removesuffix("_REVERSED")
            assert base in er.COMPASS_BEARINGS


class TestRationalSlope:
    def test_ene_matches_tan_67_5(self):
        slope = er.rational_slope("ENE")
        assert float(slope) == pytest.approx(math.tan(math.radians(67.5)), abs=0.01)

    def test_ne_is_one(self):
        assert float(er.rational_slope("NE")) == pytest.approx(1.0, abs=0.01)

    def test_north_is_zero(self):
        assert er.rational_slope("N") == 0

    def test_pure_east_raises(self):
        with pytest.raises(ValueError):
            er.rational_slope("E")

    def test_unknown_bearing_raises(self):
        with pytest.raises(ValueError):
            er.rational_slope("NOTADIRECTION")


class TestTraceRouteAndRouteOrder:
    @pytest.mark.parametrize("direction", er.PRIORITY_DIRECTIONS)
    def test_trace_route_in_bounds(self, direction):
        for start_col in range(COLS):
            coords = er.trace_route(direction, start_col)
            assert len(coords) == ROWS
            for r, c in coords:
                assert 0 <= r < ROWS
                assert 0 <= c < COLS

    @pytest.mark.parametrize("direction", er.PRIORITY_DIRECTIONS)
    def test_route_order_is_bijection(self, direction):
        coords = er.route_order(direction)
        assert len(coords) == ROWS * COLS
        assert len(set(coords)) == ROWS * COLS

    def test_reversed_negates_slope(self):
        forward = er.trace_route("ENE", 0)
        reverse = er.trace_route("ENE_REVERSED", 0)
        assert forward[0] == reverse[0]  # same starting cell
        assert forward != reverse
