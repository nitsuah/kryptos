"""P19 — Sanborn advisory names as keyed-alphabet seeds.

Individuals directly involved with Kryptos:
  - ED SCHEIDT: CIA KGB officer who designed the encryption WITH Sanborn.
    Most important — Scheidt said "there's still something that needs to be
    worked out." His name is an untested keyed-alphabet keyword.
  - WILLIAM WEBSTER: DCI 1987-1991 (during Kryptos design & installation)
  - RICHARD KERR: DDCI (Deputy Director of Central Intelligence)
  - WILLIAM STUDEMAN: NSA Director
  - JIM SANBORN: the sculptor himself

Each name is deduplicated and used to build a keyed alphabet, then tested
as the substitution alphabet in the full 3-layer composite sweep.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

ADVISORY_KEYWORDS: list[str] = [
    "SCHEIDT",      # most important: designed the cipher with Sanborn
    "WEBSTER",      # DCI 1987-1991
    "STUDEMAN",     # NSA Director
    "KERR",         # DDCI
    "SANBORN",      # sculptor (also in alt_keywords.py — included here for completeness)
    "LANGLEY",      # CIA HQ location
    "ELONKA",       # Elonka Dunin, lead K4 researcher Sanborn has spoken with directly
    "OSHEA",        # William O'Shea (another frequently cited CIA contact)
    "KRYPTOS",      # the sculpture's own name
]


def build_keyed_alphabet(keyword: str) -> str:
    """Deduplicated keyword chars first, then remaining A-Z."""
    seen: set[str] = set()
    result: list[str] = []
    for c in keyword.upper():
        if c.isalpha() and c not in seen:
            result.append(c)
            seen.add(c)
    for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        if c not in seen:
            result.append(c)
            seen.add(c)
    return "".join(result)


ADVISORY_KEYED_ALPHABETS: dict[str, str] = {
    kw: build_keyed_alphabet(kw) for kw in ADVISORY_KEYWORDS
}


def run_advisory_keyword_sweep(
    grid_sizes: list[int] | None = None,
    clock_step_seconds: int = 3600,
    max_perms_per_grid: int = 120,
    priority_only: bool = True,
    progress_cb: Any = None,
    null_artifact_path: str = "K4_P19_ADVISORY_NULL.json",
) -> dict[str, Any]:
    """Run the 3-layer composite with advisory-name keyed alphabets.

    Args:
        grid_sizes: Column counts to sweep (default: [7, 8, 10]).
        clock_step_seconds: Seconds between clock states (86400 = priority only).
        max_perms_per_grid: Maximum permutations per grid size.
        priority_only: If True, only test CIA dedication timestamps.
        progress_cb: Optional callback(info_dict) for progress updates.
        null_artifact_path: Path to write null-result artifact.

    Returns:
        Summary dict from the composite sweep.
    """
    from .three_layer_composite import CIA_PRIORITY_TIMES, run_three_layer_composite

    clock_step = 86400 if priority_only else clock_step_seconds
    return run_three_layer_composite(
        subst_alphabets=ADVISORY_KEYED_ALPHABETS,
        grid_sizes=grid_sizes or [7, 8, 10],
        clock_step_seconds=clock_step,
        priority_clock_times=CIA_PRIORITY_TIMES,
        max_perms_per_grid=max_perms_per_grid,
        progress_cb=progress_cb,
        null_artifact_path=null_artifact_path,
        eureka_snapshot_path="K4_P19_ADVISORY_EUREKA.md",
    )


__all__ = [
    "ADVISORY_KEYWORDS",
    "ADVISORY_KEYED_ALPHABETS",
    "build_keyed_alphabet",
    "run_advisory_keyword_sweep",
]
