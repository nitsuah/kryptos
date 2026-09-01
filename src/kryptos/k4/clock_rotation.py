"""24-position permutation library for K4 — clock coordinates + Berlin/Langley rotation.

Unifies two closely related hypotheses from the research brief into one
primitive, since both reduce to "a cyclic permutation of 24 columns":

  * The Berlin World Clock as a *coordinate system* (24 positions / origin
    selection / direction) rather than as a lamp-state -> Vigenere-shift
    source (that direct-keying form is already tested and ruled out — see
    ``kryptos.k4.berlin_clock`` and the null-result table in
    ``docs/analysis/K4_ACTIVE_RESEARCH.md``).
  * The +/-6 hour Berlin<->CIA-Langley timezone offset as a *positional*
    rotation of a 24-column grid, not a Caesar/Vigenere shift of letters.

``rotate``/``rotated_column`` are pure column-index permutations — they never
touch letters. ``geography_priority_offsets`` reuses (does not re-derive) the
geography this repo already computed in :mod:`kryptos.k4.bearing_attack` and
:mod:`kryptos.k4.k2_clock_states`, exposing those values as additional named
rotation-offset candidates with full provenance.
"""

from __future__ import annotations

from .geometry24 import COLS as N

# k2_clock_states.TIMEZONE_OFFSET_HOURS is the same Berlin(CET)<->CIA(EST)
# 6-hour offset the brief calls out; reused directly rather than redefined.
from .k2_clock_states import TIMEZONE_OFFSET_HOURS as BERLIN_LANGLEY_OFFSET_HOURS

PRIORITY_OFFSETS: list[int] = [0, BERLIN_LANGLEY_OFFSET_HOURS, -BERLIN_LANGLEY_OFFSET_HOURS]


def rotated_column(c: int, offset: int, direction: int = 1, n: int = N) -> int:
    """Map column ``c`` to its rotated position.

    ``direction=1``  -> simple cyclic rotation: (c + offset) % n.
    ``direction=-1`` -> reversed orientation ("23 22 21 ... 0") plus offset.
    """
    if direction == 1:
        return (c + offset) % n
    if direction == -1:
        return (n - 1 - c + offset) % n
    raise ValueError(f"direction must be 1 or -1, got {direction!r}")


def rotate(offset: int, n: int = N, direction: int = 1) -> list[int]:
    """Return the full column permutation for a given offset/direction."""
    return [rotated_column(c, offset, direction, n) for c in range(n)]


def origin_from_hour(hour: int, n: int = N) -> int:
    """Map a 24-hour clock hour directly onto a grid column (origin selection)."""
    return hour % n


def geography_priority_offsets() -> dict[str, int]:
    """Concrete rotation-offset candidates derived from already-computed geography.

    Reuses ``bearing_attack.CIA_BERLIN_BEARING_INT`` (great-circle bearing,
    CIA HQ -> Berlin) and ``k2_clock_states`` (K2-coordinate-derived clock
    times, the Berlin/Langley timezone offset, and the magnetic-declination
    offset) rather than re-deriving any geography here.
    """
    from .bearing_attack import CIA_BERLIN_BEARING_INT
    from .k2_clock_states import K2_CLOCK_TIMES, MAGNETIC_DECLINATION_MINUTES, TIMEZONE_OFFSET_HOURS

    offsets: dict[str, int] = {
        "cia_berlin_bearing_mod24": CIA_BERLIN_BEARING_INT % N,
        "timezone_offset_hours": TIMEZONE_OFFSET_HOURS % N,
        "magnetic_declination_minutes_mod24": MAGNETIC_DECLINATION_MINUTES % N,
    }
    for hhmm, _label in K2_CLOCK_TIMES:
        hour = int(hhmm.split(":")[0])
        offsets[f"k2_hour_{hhmm.replace(':', '')}"] = origin_from_hour(hour)
    return offsets


def geography_derived_bearings() -> dict[str, float]:
    """Named compass bearings (degrees) derived from already-computed geography.

    Brief item 12 — "combine geographic vectors with grid orientation": the
    exact CIA HQ -> Berlin great-circle bearing (~44.4 deg, not snapped to a
    named 16-point compass direction) used directly as a route bearing via
    :func:`kryptos.k4.ene_routes.trace_route`, which already accepts a raw
    float degree value. Reuses ``bearing_attack.CIA_BERLIN_BEARING_DEG``
    rather than re-deriving it.
    """
    from .bearing_attack import CIA_BERLIN_BEARING_DEG
    from .solar_geometry import solar_shadow_bearings

    bearings = {
        "cia_berlin_bearing": CIA_BERLIN_BEARING_DEG,
        "cia_berlin_bearing_reversed": (CIA_BERLIN_BEARING_DEG + 180.0) % 360.0,
    }
    bearings.update(mengenlehreuhr_weltzeituhr_bearings())
    bearings.update(solar_shadow_bearings())
    return bearings


# Weltzeituhr (World Clock), Alexanderplatz — unmoved since 1969.
# https://en.wikipedia.org/wiki/World_Clock_(Alexanderplatz)
WELTZEITUHR_LAT, WELTZEITUHR_LON = 52.5211, 13.4133

# Mengenlehreuhr (Berlin Clock / Set Theory Clock).
# Current site (Europa-Center, since 1996 — six years AFTER Kryptos was
# dedicated in Nov 1990): https://latitude.to/articles-by-country/de/germany/37064/mengenlehreuhr
MENGENLEHREUHR_CURRENT_LAT, MENGENLEHREUHR_CURRENT_LON = 52.5032, 13.3367
# 1975-1995 site (Kurfurstendamm/Uhlandstrasse corner) — the location during
# Sanborn's entire design window. Approximate: nearest documented
# cross-street, not the exact historical pedestal — expect a few tenths of a
# degree of slack from this coordinate alone.
MENGENLEHREUHR_1990_LAT, MENGENLEHREUHR_1990_LON = 52.50250, 13.32556


def mengenlehreuhr_weltzeituhr_bearings() -> dict[str, float]:
    """Bearing from the Berlin Clock to the World Clock — both real locations.

    ``docs/sources/CLOCK.md`` claims a line from the Mengenlehreuhr heading
    ENE reaches the Weltzeituhr, but cites no source and uses the clock's
    *current* location. The Mengenlehreuhr didn't move to Europa-Center
    until 1996 — six years after Kryptos was dedicated. This computes the
    precise geodesic bearing from both the current site and the 1990
    (Sanborn-era) site, so the period-accurate figure is available alongside
    the easier-to-source current one rather than silently substituted for it.
    """
    from .geodesy import geodesic_bearing_distance

    current = geodesic_bearing_distance(
        MENGENLEHREUHR_CURRENT_LAT, MENGENLEHREUHR_CURRENT_LON, WELTZEITUHR_LAT, WELTZEITUHR_LON
    )
    historic = geodesic_bearing_distance(
        MENGENLEHREUHR_1990_LAT, MENGENLEHREUHR_1990_LON, WELTZEITUHR_LAT, WELTZEITUHR_LON
    )
    fwd_current = current["forward_azimuth_deg"]
    fwd_historic = historic["forward_azimuth_deg"]
    return {
        "mengenlehreuhr_weltzeituhr_1990": fwd_historic,
        "mengenlehreuhr_weltzeituhr_1990_reversed": (fwd_historic + 180.0) % 360.0,
        "mengenlehreuhr_weltzeituhr_current": fwd_current,
        "mengenlehreuhr_weltzeituhr_current_reversed": (fwd_current + 180.0) % 360.0,
    }


__all__ = [
    "BERLIN_LANGLEY_OFFSET_HOURS",
    "MENGENLEHREUHR_1990_LAT",
    "MENGENLEHREUHR_1990_LON",
    "MENGENLEHREUHR_CURRENT_LAT",
    "MENGENLEHREUHR_CURRENT_LON",
    "PRIORITY_OFFSETS",
    "WELTZEITUHR_LAT",
    "WELTZEITUHR_LON",
    "geography_derived_bearings",
    "geography_priority_offsets",
    "mengenlehreuhr_weltzeituhr_bearings",
    "origin_from_hour",
    "rotate",
    "rotated_column",
]
