"""Directional (compass-route) generator for K4's 24-column grid.

Treats EASTNORTHEAST as a possible spatial traversal instruction rather than
only a numeric key. Sixteen-point compass bearings are converted to
*discrete rational* column-per-row slopes (via ``fractions.Fraction``) so a
route can be traced across the 4x24 grid without floating-point angle drift
— the existing ``transposition_routes.read_ene_diagonal`` uses a single
floating constant (``tan(67.5 deg) ~= 2.414``); this module generalizes that
idea to all 16 compass points and grounds it in exact rational arithmetic.

For a fixed step ``i``, walking the grid at rational column-slope ``s`` from
starting column ``start_col`` lands on column
``(start_col + floor(i * s)) % COLS`` — an integer modular translation of
``start_col``. That makes each step's 24 starting columns a bijection onto
the 24 grid columns, so the 24-ribbon family (one ribbon per starting
column) tiles the whole 4x24 grid with no gaps or overlaps. That family is
exposed as ``route_order`` so it can be used as an alternate grid "reader",
interchangeable with :mod:`kryptos.k4.geometry24`'s fill orders.

The row-per-step vertical component and the column-per-step slope are
tracked *separately* (``_trace_params`` returns a signed row direction plus
an unsigned-drow column slope), not collapsed into a single ``dcol/drow``
ratio: that ratio is direction-blind whenever a bearing pair is 180 degrees
apart (``sin``/``cos`` both flip sign, so the ratio — and therefore the
route — would otherwise be identical for e.g. N/S or NE/SW). Pure E/W
bearings have zero row progression and cannot be represented by this
one-step-per-row model at all; ``trace_route``/``route_order`` raise for
them rather than silently producing a degenerate route. ``rational_slope``
itself (the plain ``dcol/drow`` ratio) is unaffected and still used directly
for the informational sanity checks against ``tan(67.5)`` etc.
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


def _trace_params(bearing: str | float, max_denominator: int = 24) -> tuple[int, Fraction]:
    """Signed row direction and column-slope magnitude for tracing a bearing.

    Unlike ``rational_slope`` (a plain ``dcol/drow`` ratio, which is the same
    for opposite bearings whenever both components flip sign together), this
    keeps the row direction as an explicit sign so N vs S, NE vs SW, etc.
    trace genuinely different routes.
    """
    deg = _bearing_degrees(bearing)
    theta = math.radians(deg)
    drow = math.cos(theta)
    dcol = math.sin(theta)
    if abs(drow) < 1e-9:
        raise ValueError(f"bearing {deg} has no row progression (due E/W); trace_route cannot represent it")
    row_direction = 1 if drow > 0 else -1
    col_slope = Fraction(dcol / abs(drow)).limit_denominator(max_denominator)
    return row_direction, col_slope


def trace_route(
    bearing: str | float,
    start_col: int,
    rows: int = ROWS,
    cols: int = COLS,
    max_denominator: int = 24,
) -> list[Coord]:
    """Walk the grid one row at a time along a rational-slope compass bearing.

    ``bearing`` may be a named 16-point compass direction, a
    ``"_REVERSED"``-suffixed name (traces the same angle then reverses the
    resulting sequence — literally retracing the path backward, i.e.
    ``trace_route(f"{X}_REVERSED", c) == list(reversed(trace_route(X, c)))``),
    or a raw float degree value (e.g. an exact geographic bearing that
    doesn't land on a named compass point — see
    :func:`kryptos.k4.clock_rotation.geography_derived_bearings`).
    """
    row_direction, col_slope = _trace_params(bearing, max_denominator)
    coords: list[Coord] = []
    col_accum = Fraction(start_col)
    for step in range(rows):
        r = step if row_direction == 1 else (rows - 1 - step)
        c = math.floor(col_accum) % cols
        coords.append((r, c))
        col_accum += col_slope
    if isinstance(bearing, str) and bearing.endswith("_REVERSED"):
        coords = list(reversed(coords))
    return coords


def route_order(
    direction: str | float,
    rows: int = ROWS,
    cols: int = COLS,
    max_denominator: int = 24,
) -> list[Coord]:
    """Concatenate one ribbon per starting column into a full grid coordinate order.

    The result is a bijection over all ``rows * cols`` grid cells (see
    module docstring), so it can be used anywhere a
    :mod:`kryptos.k4.geometry24` fill order is used.

    For a ``"_REVERSED"`` direction, both the ribbon order *and* each
    ribbon's own internal order must flip for this to be the true reverse
    of the forward route (``reversed(A + B + ... + Z) == reversed(Z) + ...
    + reversed(A)``) — ``trace_route`` already reverses each ribbon
    internally; iterating starting columns backward here supplies the other
    half.
    """
    coords: list[Coord] = []
    reversed_ = isinstance(direction, str) and direction.endswith("_REVERSED")
    start_columns = range(cols - 1, -1, -1) if reversed_ else range(cols)
    for start_col in start_columns:
        coords.extend(trace_route(direction, start_col, rows, cols, max_denominator))
    return coords


__all__ = [
    "COMPASS_BEARINGS",
    "PRIORITY_DIRECTIONS",
    "rational_slope",
    "route_order",
    "trace_route",
]
