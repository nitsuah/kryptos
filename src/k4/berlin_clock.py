"""Berlin Clock key stream generator for K4 hypothesis (simplified)."""
from __future__ import annotations
from typing import List, Sequence
from datetime import time

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def berlin_clock_shifts(t: time) -> List[int]:
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
    out: List[str] = []
    sign = -1 if decrypt else 1
    n = len(shifts)
    for i, c in enumerate(letters):
        idx = ALPHABET.index(c)
        shift = shifts[i % n] * sign
        out.append(ALPHABET[(idx + shift) % 26])
    return ''.join(out)

__all__ = ['berlin_clock_shifts','apply_clock_shifts']
