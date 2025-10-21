"""Berlin Clock key stream generator for K4 hypothesis (expanded)."""
from __future__ import annotations

from collections.abc import Sequence
from datetime import time, datetime, timedelta

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def berlin_clock_shifts(t: time) -> list[int]:
    """Return a base shift pattern derived from Berlin Clock lamp counts.
    Lamps simplified to five numeric components:
      H5 = hours//5 (0-4)
      H1 = hours%5 (0-4)
      M5 = minutes//5 (0-11)
      M1 = minutes%5 (0-4)
      S = seconds%2 (0 or 1)
    Returns list of ints to be cycled as Vigenère-like shifts.
    """
    h5 = t.hour // 5
    h1 = t.hour % 5
    m5 = t.minute // 5
    m1 = t.minute % 5
    s = t.second % 2
    return [h5, h1, m5, m1, s]


def apply_clock_shifts(ciphertext: str, shifts: Sequence[int], decrypt: bool = False) -> str:
    """Apply cyclic Berlin Clock-derived shifts (encrypt/decrypt)."""
    letters = [c for c in ciphertext.upper() if c.isalpha()]
    out: list[str] = []
    sign = -1 if decrypt else 1
    n = len(shifts)
    for i, c in enumerate(letters):
        idx = ALPHABET.index(c)
        shift = shifts[i % n] * sign
        out.append(ALPHABET[(idx + shift) % 26])
    return ''.join(out)


def full_clock_state(t: time) -> dict[str, list[int]]:
    """Return full Berlin Clock lamp state as lists of ints.
    Top hours row: 4 lamps (5-hour blocks)
    Bottom hours row: 4 lamps (1-hour blocks)
    Top minutes row: 11 lamps (5-min blocks) with quarter markers
    Bottom minutes row: 4 lamps (1-min blocks)
    Seconds lamp: single value (1 lit on even seconds else 0)
    Lit standard lamp = 1, quarter marker lit = 2 (to differentiate weighting), unlit = 0.
    """
    h = t.hour
    m = t.minute
    s = t.second
    top_hours = [1 if i < h // 5 else 0 for i in range(4)]
    bottom_hours = [1 if i < h % 5 else 0 for i in range(4)]
    top_minutes = []
    five_blocks = m // 5
    quarter_positions = {2, 5, 8}  # 0-based indices for 15,30,45 markers
    for i in range(11):
        if i < five_blocks:
            top_minutes.append(2 if i in quarter_positions else 1)
        else:
            top_minutes.append(0)
    bottom_minutes = [1 if i < m % 5 else 0 for i in range(4)]
    seconds_lamp = [1 if s % 2 == 0 else 0]
    return {
        'top_hours': top_hours,
        'bottom_hours': bottom_hours,
        'top_minutes': top_minutes,
        'bottom_minutes': bottom_minutes,
        'seconds': seconds_lamp,
    }


def encode_clock_state(state: dict[str, list[int]]) -> list[int]:
    """Flatten clock state dict into a single shift sequence list."""
    return (
        state['top_hours']
        + state['bottom_hours']
        + state['top_minutes']
        + state['bottom_minutes']
        + state['seconds']
    )


def full_berlin_clock_shifts(t: time) -> list[int]:
    """Convenience wrapper returning encoded full lamp shift sequence for time t."""
    return encode_clock_state(full_clock_state(t))


def enumerate_clock_shift_sequences(
    start: str = '00:00:00',
    end: str = '23:59:59',
    step_seconds: int = 3600,
) -> list[dict]:
    """Enumerate encoded shift sequences over a time range.
    Returns list of dicts: {'time': 'HH:MM:SS', 'shifts': [...]}.
    Default step is 1 hour to keep output small; decrease step_seconds for finer granularity.
    """
    def _parse(ts: str) -> datetime:
        return datetime.strptime(ts, '%H:%M:%S')
    cur = _parse(start)
    end_dt = _parse(end)
    out: list[dict] = []
    while cur <= end_dt:
        t_obj = time(cur.hour, cur.minute, cur.second)
        out.append({'time': cur.strftime('%H:%M:%S'), 'shifts': full_berlin_clock_shifts(t_obj)})
        cur += timedelta(seconds=step_seconds)
    return out

__all__ = [
    'berlin_clock_shifts',
    'apply_clock_shifts',
    'full_clock_state',
    'encode_clock_state',
    'full_berlin_clock_shifts',
    'enumerate_clock_shift_sequences',
]
