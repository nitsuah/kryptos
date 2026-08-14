"""K2 coordinate digits as clock state selectors — Frontier P3 + P4.

The K2 plaintext encodes WGS-84 coordinates that, read as HH:MM, produce
5–8 specific Berlin Clock states.  These states should be tested as the
clock key for any clock-based attack before sweeping all 720 states.

P4 adds the ±6-hour Berlin↔CIA timezone offset to double any sweep.
"""

from __future__ import annotations

from datetime import time

from .berlin_clock import full_berlin_clock_shifts

# K2 coordinate readings as potential HH:MM pairs (per landscape §P3)
K2_CLOCK_TIMES: list[tuple[str, str]] = [
    ("14:57", "38%24=14, 57min"),
    ("06:05", "6°N lat, 5sec → 06:05"),
    ("17:08", "77%24=17, 8min"),
    ("08:44", "8min, 44sec → 08:44"),
    ("13:57", "38%24 alt, 57min"),
]

# CIA timestamp: Nov 3 1990 13:00 EST = 18:00 UTC = 19:00 Berlin CET
CIA_TIMESTAMP_TIMES: list[tuple[str, str]] = [
    ("13:00", "CIA local time (EST, Nov 3 1990 dedication)"),
    ("19:00", "Berlin local time (CET = EST+6)"),
]

TIMEZONE_OFFSET_HOURS = 6  # Berlin (CET/UTC+1) vs CIA (EST/UTC-5)


def parse_hhmm(hhmm: str) -> time:
    """Parse 'HH:MM' or 'HH:MM:SS' into a time object."""
    parts = hhmm.split(":")
    h, m = int(parts[0]), int(parts[1])
    s = int(parts[2]) if len(parts) > 2 else 0
    return time(h % 24, m % 60, s)


def clock_state_for_time(hhmm: str) -> dict:
    """Return {'time': hhmm, 'shifts': [...]} for a given HH:MM string."""
    t = parse_hhmm(hhmm)
    return {"time": hhmm, "shifts": full_berlin_clock_shifts(t)}


def offset_time(hhmm: str, offset_hours: int) -> str:
    """Return HH:MM shifted by ±offset_hours."""
    t = parse_hhmm(hhmm)
    total_mins = t.hour * 60 + t.minute + offset_hours * 60
    total_mins %= 1440  # mod 24h
    h, m = divmod(total_mins, 60)
    return f"{h:02d}:{m:02d}"


def get_k2_clock_states(include_tz_offset: bool = True) -> list[dict]:
    """Return all K2-derived clock states, optionally doubled by ±6h offset.

    Each entry: {'time': 'HH:MM', 'shifts': [...], 'source': str, 'is_offset': bool}
    """
    states: list[dict] = []
    for hhmm, source in K2_CLOCK_TIMES + CIA_TIMESTAMP_TIMES:
        base = clock_state_for_time(hhmm)
        states.append({**base, "source": source, "is_offset": False})
        if include_tz_offset:
            for delta in (-TIMEZONE_OFFSET_HOURS, +TIMEZONE_OFFSET_HOURS):
                shifted = offset_time(hhmm, delta)
                s = clock_state_for_time(shifted)
                states.append({
                    **s,
                    "source": f"{source} (±{abs(delta)}h tz offset from {hhmm})",
                    "is_offset": True,
                })
    return states


def get_tz_offset_states(base_states: list[dict]) -> list[dict]:
    """Double a list of clock states by adding ±6h offset variants (P4 modifier)."""
    extra: list[dict] = []
    for state in base_states:
        for delta in (-TIMEZONE_OFFSET_HOURS, +TIMEZONE_OFFSET_HOURS):
            shifted_hhmm = offset_time(state["time"], delta)
            s = clock_state_for_time(shifted_hhmm)
            extra.append({
                **s,
                "source": f"{state.get('source', state['time'])} ±{abs(delta)}h",
                "is_offset": True,
            })
    return base_states + extra


__all__ = [
    "K2_CLOCK_TIMES",
    "CIA_TIMESTAMP_TIMES",
    "TIMEZONE_OFFSET_HOURS",
    "clock_state_for_time",
    "offset_time",
    "get_k2_clock_states",
    "get_tz_offset_states",
]
