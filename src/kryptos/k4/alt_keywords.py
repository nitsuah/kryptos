"""P11 — Alternative keyed-alphabet keyword sweep for K4.

Tests sculptor/location/plaintext-derived keywords as substitution-alphabet
seeds instead of the Phase 1 set (KRYPTOS, PALIMPSEST, ABSCISSA).

Candidate rationale:
  SANBORN   — sculptor who built Kryptos
  LANGLEY   — CIA HQ location (appears in K2 plaintext)
  SCHEIDT   — Ed Scheidt, CIA cryptographer who designed K4 with Sanborn
  WENDELL   — Sanborn's middle name; used in some Kryptos analyses
  NORTHEAST — confirmed K4 crib at positions 25-33
  BERLIN    — confirmed K4 crib at positions 63-68
  CLOCK     — confirmed K4 crib at positions 69-73
  SHADOW    — public Sanborn clue: "go between the lines" / shadow direction
  BETWEEN   — Sanborn clue word
  COMPASS   — Sanborn's compass-rose imagery in Kryptos sculpture
  DIGETAL   — Sanborn clue: "digital interpretation"
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .vigenere_key_recovery import KNOWN_KEYED_ALPHABETS, build_keyed_alphabet

logger = logging.getLogger(__name__)

_NULL_ARTIFACT_PATH = "K4_P11_ALT_KEYWORDS_NULL.json"

P11_KEYWORDS: list[str] = [
    "SANBORN",
    "LANGLEY",
    "SCHEIDT",
    "WENDELL",
    "NORTHEAST",
    "BERLIN",
    "CLOCK",
    "SHADOW",
    "BETWEEN",
    "COMPASS",
    "DIGETAL",
]

ALT_KEYED_ALPHABETS: dict[str, str] = {kw: build_keyed_alphabet(kw) for kw in P11_KEYWORDS}

COMBINED_ALPHABETS: dict[str, str] = {**KNOWN_KEYED_ALPHABETS, **ALT_KEYED_ALPHABETS}


def run_alt_keyword_sweep(
    grid_sizes: list[int] | None = None,
    clock_step_seconds: int = 3600,
    max_perms_per_grid: int | None = 120,
    priority_only: bool = True,
    progress_cb: Any = None,
    null_artifact_path: str | Path = _NULL_ARTIFACT_PATH,
) -> dict[str, Any]:
    """Run the P1 3-layer composite with the P11 alternative-keyword alphabet set.

    Args:
        grid_sizes:            Column counts to sweep (default: K4_GRID_GEOMETRIES).
        clock_step_seconds:    Granularity for full clock sweep.
        max_perms_per_grid:    Permutation cap per (grid, clock, alpha) combo.
        priority_only:         If True, only test CIA priority timestamps.
        progress_cb:           Optional callback forwarded to run_three_layer_composite.
        null_artifact_path:    Path for null-result provenance artifact.
    """
    from .three_layer_composite import CIA_PRIORITY_TIMES, run_three_layer_composite

    clock_step = 86400 if priority_only else clock_step_seconds

    logger.info(
        "P11 alt-keyword sweep: %d alphabets, priority_only=%s",
        len(ALT_KEYED_ALPHABETS),
        priority_only,
    )

    return run_three_layer_composite(
        subst_alphabets=ALT_KEYED_ALPHABETS,
        grid_sizes=grid_sizes,
        clock_step_seconds=clock_step,
        priority_clock_times=CIA_PRIORITY_TIMES,
        max_perms_per_grid=max_perms_per_grid,
        null_artifact_path=null_artifact_path,
        progress_cb=progress_cb,
    )
