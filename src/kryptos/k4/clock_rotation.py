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
        return (-c + offset) % n
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


__all__ = [
    "BERLIN_LANGLEY_OFFSET_HOURS",
    "PRIORITY_OFFSETS",
    "geography_priority_offsets",
    "origin_from_hour",
    "rotate",
    "rotated_column",
]
