"""Shadow-angle primitives for K4 -- Frontier Phase 7.

Sanborn: "the secret is the shadow of the word" and "who says it is even a
math solution?" Previously flagged in ``K4_ATTACK_LANDSCAPE.md`` as out of
scope for the automated pipeline because it seemed to require physical or
photographic site access. Re-examined 2026-08-31/2026-09-01: two distinct,
independently-computable readings turn out not to need that access at all.

  A. World Clock (Weltzeituhr, Alexanderplatz) topper rotation -- the
     rotating solar-system sculpture on top of the clock turns at a fixed,
     documented rate of 1 revolution/minute, decoupled from real solar
     position (https://en.wikipedia.org/wiki/World_Clock_(Alexanderplatz)).
     Its orientation at any moment is deterministic elapsed-time math from
     an assumed reference timestamp, not an ephemeris lookup. The reference
     timestamp itself is genuinely unknown, so this module treats it as a
     sweep parameter over a small set of *already-sourced* candidate
     moments this project treats as significant (the CIA dedication, the
     three Berlin Wall priority moments) rather than inventing new ones.

  B. Real solar position at CIA HQ, Langley -- a literal shadow cast by the
     Kryptos courtyard sculpture's own copper panel needs true solar
     azimuth/elevation at a given lat/lon/date/time. Computed here via the
     standard NOAA solar-position algorithm (Meeus, "Astronomical
     Algorithms"; ~0.01 degree precision, no atmospheric-refraction
     correction -- more than sufficient for a transposition-order
     parameter) against the CIA HQ coordinates ``bearing_attack.py``
     already uses, at the same already-sourced timestamps as (A).

Both hypotheses reduce to a single derived angle that the existing
``geometry_combined_sweep`` / ``three_layer_composite_geometric``
machinery already consumes (a rotation-offset mod 24, or a route-bearing
direction) -- no new attack pipeline needed, only these primitives.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

from .geometry24 import COLS as N

# CIA HQ, Langley -- reused (not re-derived) from bearing_attack.py.
CIA_LAT, CIA_LON = 38.957, -77.145

# Already-sourced, already-significant timestamps this project uses
# elsewhere (k2_clock_states.py, three_layer_composite.py) -- reused here,
# not invented, so this module's sweep doesn't fabricate new "significant
# moments" just to widen its own search space.
CIA_DEDICATION_UTC = datetime(1990, 11, 3, 18, 0, 0, tzinfo=timezone.utc)  # 13:00 EST / 19:00 CET
BERLIN_WALL_SCHABOWSKI_UTC = datetime(1989, 11, 9, 17, 53, 0, tzinfo=timezone.utc)  # 18:53 CET
BERLIN_WALL_AP_FLASH_UTC = datetime(1989, 11, 9, 18, 5, 0, tzinfo=timezone.utc)  # 19:05 CET
BERLIN_WALL_ARD_UTC = datetime(1989, 11, 9, 19, 0, 0, tzinfo=timezone.utc)  # 20:00 CET

# World Clock's own dedication (Erich John's design, unveiled 1969) -- a
# third, independent candidate "reference epoch" for hypothesis A, sourced
# separately from the Kryptos-side dates above.
WELTZEITUHR_DEDICATION_UTC = datetime(1969, 9, 30, 12, 0, 0, tzinfo=timezone.utc)

# Sub-minute-precision timestamps, sourced 2026-09-02 from
# chronik-der-mauer.de's word-for-word transcript of Hans-Hermann Hertle's
# own camera/audio recording of the press conference (citing Hertle, "Die
# Berliner Mauer. Biografie eines Bauwerks", 2nd ed. 2015, p. 194-195) --
# the single most authoritative timing source found for this event. The
# transcript excerpt containing the "sofort ... unverzuglich" exchange
# opens at 18:52:40 CET and the press conference itself ends at 19:00:54
# CET ("Ende der Pressekonferenz: 19:00:54 Uhr") -- the exact quote falls
# somewhere within this ~8m14s window, but both bounds are themselves
# genuine, non-round, sourced moments (unlike every other timestamp this
# project has used for K4, which are all whole-minute approximations).
BERLIN_WALL_PRESSER_START_UTC = datetime(1989, 11, 9, 17, 52, 40, tzinfo=timezone.utc)  # 18:52:40 CET
BERLIN_WALL_PRESSER_END_UTC = datetime(1989, 11, 9, 18, 0, 54, tzinfo=timezone.utc)  # 19:00:54 CET

QUERY_MOMENTS: dict[str, datetime] = {
    "cia_dedication": CIA_DEDICATION_UTC,
    "berlin_wall_schabowski": BERLIN_WALL_SCHABOWSKI_UTC,
    "berlin_wall_ap_flash": BERLIN_WALL_AP_FLASH_UTC,
    "berlin_wall_ard": BERLIN_WALL_ARD_UTC,
    "berlin_wall_presser_start": BERLIN_WALL_PRESSER_START_UTC,
    "berlin_wall_presser_end": BERLIN_WALL_PRESSER_END_UTC,
}

# The two precise (non-whole-minute) moments only -- these are what makes
# hypothesis A's topper-angle computation non-vacuous (see
# precise_topper_shadow_offsets below).
PRECISE_QUERY_MOMENTS: dict[str, datetime] = {
    "berlin_wall_presser_start": BERLIN_WALL_PRESSER_START_UTC,
    "berlin_wall_presser_end": BERLIN_WALL_PRESSER_END_UTC,
}

REFERENCE_EPOCHS: dict[str, datetime] = {
    "cia_dedication": CIA_DEDICATION_UTC,
    "weltzeituhr_dedication": WELTZEITUHR_DEDICATION_UTC,
}


def topper_rotation_angle_deg(query_dt_utc: datetime, reference_dt_utc: datetime) -> float:
    """World Clock topper's angle (degrees, 0-360) at ``query_dt_utc``.

    The topper turns a fixed 1 revolution/minute, independent of real solar
    position -- so this is deterministic elapsed-time math relative to an
    assumed reference moment (angle 0 at ``reference_dt_utc``), not an
    ephemeris lookup.
    """
    elapsed_seconds = (query_dt_utc - reference_dt_utc).total_seconds()
    revolutions = elapsed_seconds / 60.0
    return (revolutions * 360.0) % 360.0


def topper_shadow_offsets() -> dict[str, int]:
    """Named rotation-offset (mod 24) candidates from hypothesis A (whole-minute sources only).

    Every *whole-minute* historical timestamp this project has sourced (CIA
    dedication, the three original Berlin Wall moments, the World Clock's
    own dedication) is reported only to whole-minute precision. Because the
    topper's period is exactly 60 seconds, ``topper_rotation_angle_deg``
    between *any* two whole-minute moments is always 0 modulo 360 (their
    difference is always a whole number of minutes) -- verified directly
    below, not assumed. A single "derived" offset from this pairing would
    therefore be vacuous, not a genuine finding, no matter which sourced
    pair is chosen.

    Rather than fabricate precision that doesn't exist (or silently ship a
    parameter that always evaluates to the same trivial value), this
    operationalizes hypothesis A honestly as: since the topper's phase is
    genuinely unconstrained by any whole-minute-only source, test its full
    0-23 rotation-offset space exhaustively -- a slice Phase 6 never
    covered (its sweeps used only {0,+6,-6} or a handful of
    geography-derived values, never the complete range).

    See :func:`precise_topper_shadow_offsets` for the two sub-minute-
    precision timestamps sourced 2026-09-02 (excluded from this function's
    vacuity check -- they are the point of that function, not this one).
    """
    whole_minute_moments = {k: v for k, v in QUERY_MOMENTS.items() if k not in PRECISE_QUERY_MOMENTS}
    all_pairs_vacuous = all(
        topper_rotation_angle_deg(query_dt, ref_dt) == 0.0
        for ref_dt in REFERENCE_EPOCHS.values()
        for query_dt in whole_minute_moments.values()
    )
    if not all_pairs_vacuous:
        raise RuntimeError(
            "a whole-minute-labeled timestamp pair now differs by a non-whole-minute amount -- "
            "topper_shadow_offsets' vacuity finding no longer holds and should be revisited"
        )
    return {f"topper_full_rotation_{i}": i for i in range(N)}


def precise_topper_shadow_offsets() -> dict[str, int]:
    """Named rotation-offset (mod 24) candidates from the two sub-minute-precision timestamps.

    Unlike every other timestamp this project has sourced,
    :data:`BERLIN_WALL_PRESSER_START_UTC` (18:52:40 CET) and
    :data:`BERLIN_WALL_PRESSER_END_UTC` (19:00:54 CET) carry genuine,
    non-zero, sourced second values -- so the topper's angle *within its
    own minute* (``seconds/60*360``, no reference epoch needed: for a
    fixed 1-rev/min rotation, the position at second S past any minute is
    the same regardless of which minute) is a real, non-vacuous
    computation for these two moments specifically. This assumes the
    mechanism's phase-zero aligns with the top of each minute -- a
    reasonable default for a synchronized public clock display, but an
    assumption, not a verified fact; labeled as such rather than presented
    as certain.
    """
    return {
        f"topper_precise_{name}": round((dt.second + dt.microsecond / 1e6) / 60.0 * N) % N
        for name, dt in PRECISE_QUERY_MOMENTS.items()
    }


def solar_position(lat_deg: float, lon_deg: float, dt_utc: datetime) -> dict[str, float]:
    """Approximate solar azimuth/elevation (degrees) at ``dt_utc``.

    Standard NOAA/Meeus solar-position algorithm (~0.01 degree precision;
    no atmospheric-refraction correction). ``dt_utc`` must be timezone-aware
    UTC. Azimuth is measured clockwise from true north; elevation is
    degrees above the horizon (negative = below).
    """
    if dt_utc.tzinfo is None:
        raise ValueError("dt_utc must be timezone-aware")
    dt_utc = dt_utc.astimezone(timezone.utc)

    jd = _julian_day(dt_utc)
    t = (jd - 2451545.0) / 36525.0

    l0 = (280.46646 + t * (36000.76983 + t * 0.0003032)) % 360.0
    m = 357.52911 + t * (35999.05029 - 0.0001537 * t)
    e = 0.016708634 - t * (0.000042037 + 0.0000001267 * t)

    m_rad = math.radians(m)
    c = (
        math.sin(m_rad) * (1.914602 - t * (0.004817 + 0.000014 * t))
        + math.sin(2 * m_rad) * (0.019993 - 0.000101 * t)
        + math.sin(3 * m_rad) * 0.000289
    )
    true_long = l0 + c
    omega = 125.04 - 1934.136 * t
    app_long = true_long - 0.00569 - 0.00478 * math.sin(math.radians(omega))

    eps0 = 23.0 + (26.0 + (21.448 - t * (46.815 + t * (0.00059 - t * 0.001813))) / 60.0) / 60.0
    eps = eps0 + 0.00256 * math.cos(math.radians(omega))

    decl = math.degrees(math.asin(math.sin(math.radians(eps)) * math.sin(math.radians(app_long))))

    y = math.tan(math.radians(eps / 2.0)) ** 2
    eq_time = 4.0 * math.degrees(
        y * math.sin(2 * math.radians(l0))
        - 2 * e * math.sin(m_rad)
        + 4 * e * y * math.sin(m_rad) * math.cos(2 * math.radians(l0))
        - 0.5 * y * y * math.sin(4 * math.radians(l0))
        - 1.25 * e * e * math.sin(2 * m_rad)
    )

    time_utc_min = dt_utc.hour * 60.0 + dt_utc.minute + dt_utc.second / 60.0
    true_solar_time = (time_utc_min + eq_time + 4.0 * lon_deg) % 1440.0
    hour_angle = true_solar_time / 4.0 - 180.0

    lat_rad = math.radians(lat_deg)
    decl_rad = math.radians(decl)
    ha_rad = math.radians(hour_angle)

    zenith_cos = math.sin(lat_rad) * math.sin(decl_rad) + math.cos(lat_rad) * math.cos(decl_rad) * math.cos(ha_rad)
    zenith_cos = max(-1.0, min(1.0, zenith_cos))
    zenith = math.degrees(math.acos(zenith_cos))
    elevation = 90.0 - zenith

    zenith_rad = math.radians(zenith)
    if abs(math.sin(zenith_rad)) < 1e-9:
        azimuth = 0.0
    else:
        az_cos = (math.sin(lat_rad) * math.cos(zenith_rad) - math.sin(decl_rad)) / (
            math.cos(lat_rad) * math.sin(zenith_rad)
        )
        az_cos = max(-1.0, min(1.0, az_cos))
        az_raw = math.degrees(math.acos(az_cos))
        azimuth = (az_raw + 180.0) % 360.0 if hour_angle > 0 else (540.0 - az_raw) % 360.0

    return {"azimuth_deg": azimuth, "elevation_deg": elevation}


def _julian_day(dt_utc: datetime) -> float:
    y, mo = dt_utc.year, dt_utc.month
    d = dt_utc.day + (dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0) / 24.0
    if mo <= 2:
        y -= 1
        mo += 12
    a = y // 100
    b = 2 - a + a // 4
    return math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (mo + 1)) + d + b - 1524.5


def solar_shadow_bearings() -> dict[str, float]:
    """Named solar-azimuth bearings (hypothesis B) at CIA HQ, at each already-sourced moment."""
    bearings: dict[str, float] = {}
    for name, dt in QUERY_MOMENTS.items():
        azimuth = solar_position(CIA_LAT, CIA_LON, dt)["azimuth_deg"]
        bearings[f"solar_shadow_{name}"] = azimuth
        bearings[f"solar_shadow_{name}_reversed"] = (azimuth + 180.0) % 360.0
    return bearings


__all__ = [
    "BERLIN_WALL_AP_FLASH_UTC",
    "BERLIN_WALL_ARD_UTC",
    "BERLIN_WALL_PRESSER_END_UTC",
    "BERLIN_WALL_PRESSER_START_UTC",
    "BERLIN_WALL_SCHABOWSKI_UTC",
    "CIA_DEDICATION_UTC",
    "CIA_LAT",
    "CIA_LON",
    "PRECISE_QUERY_MOMENTS",
    "QUERY_MOMENTS",
    "REFERENCE_EPOCHS",
    "WELTZEITUHR_DEDICATION_UTC",
    "precise_topper_shadow_offsets",
    "solar_position",
    "solar_shadow_bearings",
    "topper_rotation_angle_deg",
    "topper_shadow_offsets",
]
