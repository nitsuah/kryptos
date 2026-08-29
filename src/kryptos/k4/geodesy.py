"""Precise WGS84 geodesic bearing/distance for K4 — v2 dashboard support.

``bearing_attack.py``'s ``great_circle_bearing`` treats the Earth as a
sphere (a single ``atan2``/``cos``/``sin`` formula) — good enough for the
degree-level Caesar-shift/clock-offset attacks it was built for, and its
existing null result is untouched here. This module wraps ``geographiclib``
(a pure-Python WGS84 ellipsoid geodesic engine — no compiled/system
dependencies, unlike ``pyproj``/``cartopy``) for sub-meter-precision
distance and forward/back azimuth, for use where that precision might
eventually matter (e.g. if a precise K2-offset coordinate for the Kryptos
site is ever sourced — see the Physical/Geometric Pivot's item 10/11
findings in ``docs/analysis/K4_ACTIVE_RESEARCH.md``, which found the
community's own measurements of the site are explicitly incomplete).

This module does not replace, call, or modify ``bearing_attack.py`` in any
way — it is a new, independent, more-precise primitive.
"""

from __future__ import annotations

from typing import Any

from geographiclib.geodesic import Geodesic

from .bearing_attack import BERLIN_LAT, BERLIN_LON, CIA_LAT, CIA_LON


def geodesic_bearing_distance(lat1_deg: float, lon1_deg: float, lat2_deg: float, lon2_deg: float) -> dict[str, Any]:
    """Precise forward azimuth, back azimuth, and distance between two WGS84 points.

    Returns a dict with ``forward_azimuth_deg`` (0-360, initial bearing at
    point 1), ``back_azimuth_deg`` (0-360, bearing at point 2 looking back
    at point 1), ``distance_m``, and ``distance_ft``.
    """
    result = Geodesic.WGS84.Inverse(lat1_deg, lon1_deg, lat2_deg, lon2_deg)
    forward = result["azi1"] % 360
    # geographiclib's azi2 is the forward azimuth *at* point 2; the back
    # azimuth (looking from point 2 back toward point 1) is its reciprocal.
    back = (result["azi2"] + 180) % 360
    distance_m = result["s12"]
    return {
        "forward_azimuth_deg": forward,
        "back_azimuth_deg": back,
        "distance_m": distance_m,
        "distance_ft": distance_m * 3.280839895,
    }


def cia_berlin_geodesic() -> dict[str, Any]:
    """Precise CIA HQ -> Berlin bearing/distance, for comparison against
    ``bearing_attack.CIA_BERLIN_BEARING_DEG``'s spherical approximation.
    """
    return geodesic_bearing_distance(CIA_LAT, CIA_LON, BERLIN_LAT, BERLIN_LON)


__all__ = [
    "cia_berlin_geodesic",
    "geodesic_bearing_distance",
]
