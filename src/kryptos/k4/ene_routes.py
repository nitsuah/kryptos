"""Directional (compass-route) generator for K4's 24-column grid.

Treats EASTNORTHEAST as a possible spatial traversal instruction rather than
only a numeric key. Sixteen-point compass bearings are converted to
*discrete rational* column-per-row slopes (via ``fractions.Fraction``) so a
route can be traced across the 4x24 grid without floating-point angle drift
— the existing ``transposition_routes.read_ene_diagonal`` uses a single
floating constant (``tan(67.5 deg) ~= 2.414``); this module generalizes that
idea to all 16 compass points and grounds it in exact rational arithmetic.

For a fixed row ``r``, walking the grid at rational slope ``s`` from
starting column ``start_col`` lands on column
``(start_col + floor(r * s)) % COLS`` — an integer modular translation of
``start_col``. That makes each row's 24 starting columns a bijection onto
the 24 grid columns, so the 24-ribbon family (one ribbon per starting
column) tiles the whole 4x24 grid with no gaps or overlaps. That family is
exposed as ``route_order`` so it can be used as an alternate grid "reader",
interchangeable with :mod:`kryptos.k4.geometry24`'s fill orders.
"""

from __future__ import annotations

import math
from fractions import Fraction

from .geometry24 import COLS, ROWS

COMPASS_BEARINGS: dict[str, float] = {
    "N": 0.0,
    "NNE": 22.5,
    "NE": 45.0,
    "ENE": 67.5,
    "E": 90.0,
    "ESE": 112.5,
    "SE": 135.0,
    "SSE": 157.5,
    "S": 180.0,
    "SSW": 202.5,
    "SW": 225.0,
    "WSW": 247.5,
    "W": 270.0,
    "WNW": 292.5,
    "NW": 315.0,
    "NNW": 337.5,
}

# Priority per the research brief: ENE / NE and their reverse-traversal forms.
PRIORITY_DIRECTIONS: list[str] = ["ENE", "NE", "ENE_REVERSED", "NE_REVERSED"]

Coord = tuple[int, int]


def _bearing_degrees(bearing: str | float) -> float:
    if isinstance(bearing, str):
        name = bearing.removesuffix("_REVERSED")
        if name not in COMPASS_BEARINGS:
            raise ValueError(f"Unknown compass direction: {bearing!r}")
        return COMPASS_BEARINGS[name]
    return float(bearing)


def rational_slope(bearing: str | float, max_denominator: int = 24) -> Fraction:
    """Discrete rational dcol/drow approximation for a compass bearing.

    North (0 deg) advances straight down the grid with no column drift;
    ENE (67.5 deg) yields ~2.414 (matching the existing ``tan(67.5)``
    constant used elsewhere), NE (45 deg) yields 1.
    """
    deg = _bearing_degrees(bearing)
    theta = math.radians(deg)
    drow = math.cos(theta)
    dcol = math.sin(theta)
    if abs(drow) < 1e-9:
        raise ValueError(f"bearing {deg} has no row progression (due E/W)")
    return Fraction(dcol / drow).limit_denominator(max_denominator)


def trace_route(
    bearing: str,
    start_col: int,
    rows: int = ROWS,
    cols: int = COLS,
    max_denominator: int = 24,
) -> list[Coord]:
    """Walk the grid one row at a time along a rational-slope compass bearing.

    A ``"_REVERSED"``-suffixed bearing name negates the slope (reverse
    traversal direction) while keeping the same underlying compass angle.
    """
    reversed_ = isinstance(bearing, str) and bearing.endswith("_REVERSED")
    slope = rational_slope(bearing, max_denominator)
    if reversed_:
        slope = -slope
    coords: list[Coord] = []
    col_accum = Fraction(start_col)
    for r in range(rows):
        c = math.floor(col_accum) % cols
        coords.append((r, c))
        col_accum += slope
    return coords


def route_order(
    direction: str,
    rows: int = ROWS,
    cols: int = COLS,
    max_denominator: int = 24,
) -> list[Coord]:
    """Concatenate one ribbon per starting column into a full grid coordinate order.

    The result is a bijection over all ``rows * cols`` grid cells (see
    module docstring), so it can be used anywhere a
    :mod:`kryptos.k4.geometry24` fill order is used.
    """
    coords: list[Coord] = []
    for start_col in range(cols):
        coords.extend(trace_route(direction, start_col, rows, cols, max_denominator))
    return coords


__all__ = [
    "COMPASS_BEARINGS",
    "PRIORITY_DIRECTIONS",
    "rational_slope",
    "route_order",
    "trace_route",
]
