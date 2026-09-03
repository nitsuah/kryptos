"""Shadow/null masking variants for K4 — Frontier P2.

If any K4 characters are nulls (inserted by Sanborn as "physical shadows"),
every attack that assumes 97 solid message characters is attacking padded
input.  This module strips candidate null characters before feeding the
residue into the existing 2-layer composite pipeline.

After each masking step, crib positions are recalculated in the residue
text so the Eureka gate still applies correctly.

Six masking variants from K4_ATTACK_LANDSCAPE.md §P2:
  stride-2, stride-3, stride-4, clock-shadow, arc-fraction, block-8 skip
"""

from __future__ import annotations

from datetime import time

from .berlin_clock import full_clock_state
from .keystream_validator import K4_CRIBS

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Original crib positions (0-indexed in the 97-char K4).
#
# Previously duplicated K4_CRIBS as a separate, hand-maintained literal here
# (with EAST/NORTHEAST independently drifted 1 position too high -- the same
# bug fixed in keystream_validator.K4_CRIBS on 2026-09-02, see that module's
# note). Derived from the already-imported K4_CRIBS instead, so there is only
# one source of truth to keep correct.
ORIGINAL_CRIB_POSITIONS: dict[str, int] = {label: pos for label, (_, pos) in K4_CRIBS.items()}


def _recalc_cribs(residue_indices: list[int]) -> dict[str, int | None]:
    """Map original crib positions to new positions in the residue.

    residue_indices: list of original (0-based) char positions that survived masking.
    Returns dict of crib_name → new_position (None if any crib char was masked out).
    """
    idx_map = {orig: new for new, orig in enumerate(residue_indices)}
    result: dict[str, int | None] = {}
    for label, (plain, orig_pos) in K4_CRIBS.items():
        # Span must come from the plaintext word's own length, not the dict
        # key -- label and plain happen to be identical strings for all 4
        # current cribs, which hid this until it mattered.
        new_positions = [idx_map.get(orig_pos + i) for i in range(len(plain))]
        if None in new_positions:
            result[label] = None  # masked out
        else:
            result[label] = new_positions[0]  # type: ignore[assignment]
    return result


def mask_stride(ciphertext: str, stride: int) -> tuple[str, dict]:
    """Remove every stride-th character (0-indexed positions 0, stride, 2*stride, ...).

    Example: stride=2 removes positions 0, 2, 4, ... keeping 1, 3, 5, ...
    Landscape §P2: stride-2 → 49 chars, stride-3 → 65 chars, stride-4 → 73 chars.
    """
    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    kept_indices = [i for i in range(len(ct)) if i % stride != 0]
    residue = "".join(ct[i] for i in kept_indices)
    cribs = _recalc_cribs(kept_indices)
    return residue, {"mode": f"stride-{stride}", "original_len": len(ct), "residue_len": len(residue), "cribs": cribs}


def mask_block_skip(ciphertext: str, block: int = 8) -> tuple[str, dict]:
    """Remove every block-th character (KRYPTOS alphabet period = 8)."""
    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    kept_indices = [i for i in range(len(ct)) if (i + 1) % block != 0]
    residue = "".join(ct[i] for i in kept_indices)
    cribs = _recalc_cribs(kept_indices)
    return residue, {
        "mode": f"block-{block}-skip",
        "original_len": len(ct),
        "residue_len": len(residue),
        "cribs": cribs,
    }


def mask_clock_shadow(ciphertext: str, clock_time: time) -> tuple[str, dict]:
    """Remove chars at positions where the Berlin Clock lamp is OFF at clock_time.

    Uses the 24-element full_clock_state encoding. Position i mod 24 selects
    which lamp governs character i.  Positions where lamp == 0 are shadows.
    """
    from .berlin_clock import encode_clock_state

    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    state = full_clock_state(clock_time)
    lamps = encode_clock_state(state)  # 24 elements
    n_lamps = len(lamps)
    kept_indices = [i for i in range(len(ct)) if lamps[i % n_lamps] != 0]
    residue = "".join(ct[i] for i in kept_indices)
    cribs = _recalc_cribs(kept_indices)
    time_str = f"{clock_time.hour:02d}:{clock_time.minute:02d}:{clock_time.second:02d}"
    return residue, {
        "mode": f"clock-shadow@{time_str}",
        "original_len": len(ct),
        "residue_len": len(residue),
        "cribs": cribs,
    }


def mask_arc_fraction(ciphertext: str, clock_time: time, neighborhood: int = 4) -> tuple[str, dict]:
    """Remove chars at ⌊(clock-hand angle / 360°) × 97⌋ and its neighborhood."""
    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    n = len(ct)
    total_mins = (clock_time.hour * 60 + clock_time.minute) % (12 * 60)  # wrap to 12h
    angle_fraction = total_mins / (12 * 60)  # fraction of 12-hour clock face
    center = int(angle_fraction * n)
    shadow_set = set(range(max(0, center - neighborhood), min(n, center + neighborhood + 1)))
    kept_indices = [i for i in range(n) if i not in shadow_set]
    residue = "".join(ct[i] for i in kept_indices)
    cribs = _recalc_cribs(kept_indices)
    time_str = f"{clock_time.hour:02d}:{clock_time.minute:02d}"
    return residue, {
        "mode": f"arc-fraction@{time_str}±{neighborhood}",
        "original_len": len(ct),
        "residue_len": len(residue),
        "cribs": cribs,
    }


def all_masking_variants(ciphertext: str = K4) -> list[tuple[str, dict]]:
    """Return all six masking variants as (residue, metadata) pairs."""
    from datetime import time as dtime

    variants: list[tuple[str, dict]] = []
    # Stride variants
    for stride in (2, 3, 4):
        variants.append(mask_stride(ciphertext, stride))
    # Block-8 skip
    variants.append(mask_block_skip(ciphertext, 8))
    # Clock-shadow at CIA timestamps
    for h, m in ((13, 0), (19, 0)):
        variants.append(mask_clock_shadow(ciphertext, dtime(h, m, 0)))
    # Arc-fraction at CIA timestamps
    for h, m in ((13, 0), (19, 0)):
        variants.append(mask_arc_fraction(ciphertext, dtime(h, m, 0)))
    return variants


__all__ = [
    "mask_stride",
    "mask_block_skip",
    "mask_clock_shadow",
    "mask_arc_fraction",
    "all_masking_variants",
    "ORIGINAL_CRIB_POSITIONS",
]
