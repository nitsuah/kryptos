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

    def test_reversed_is_exact_path_reversal(self):
        forward = er.trace_route("ENE", 0)
        reverse = er.trace_route("ENE_REVERSED", 0)
        assert reverse == list(reversed(forward))
        assert forward != reverse

    @pytest.mark.parametrize("direction", ["ENE", "NE"])
    def test_route_order_reversed_is_exact_full_order_reversal(self, direction):
        forward = er.route_order(direction)
        reverse = er.route_order(f"{direction}_REVERSED")
        assert reverse == list(reversed(forward))

    @pytest.mark.parametrize(
        ("a", "b"),
        [("N", "S"), ("NE", "SW"), ("ENE", "WSW"), ("NNE", "SSW")],
    )
    def test_opposite_bearings_produce_distinct_routes(self, a, b):
        # Before the fix, dcol/drow was direction-blind for any 180-degree
        # pair (both components flip sign, so the ratio doesn't change) —
        # opposite bearings collapsed onto the identical route.
        route_a = er.trace_route(a, 5)
        route_b = er.trace_route(b, 5)
        assert route_a != route_b

    def test_north_south_route_order_is_row_reversal(self):
        north = er.trace_route("N", 5)
        south = er.trace_route("S", 5)
        assert south == list(reversed(north))

    def test_pure_east_west_trace_route_raises(self):
        with pytest.raises(ValueError):
            er.trace_route("E", 0)
        with pytest.raises(ValueError):
            er.trace_route("W", 0)
