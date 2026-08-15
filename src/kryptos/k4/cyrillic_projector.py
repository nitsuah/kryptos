"""P20 — Cyrillic Projector crossover: KGB keywords as K4 alphabet seeds.

Sanborn's 'Cyrillic Projector' sculpture (UNC Chapel Hill, 1997) encodes a
declassified KGB document. The sculpture uses a passage from 'The KGB's
Classified Manual for the Recruitment of Agents' (1984).

Key Roman-alphabet words from the projected KGB text that may cross-reference
K4's cipher key, based on community research and the declassified document
(original in Cyrillic, projected in transliterated Roman):

  AGENT, REZIDENT, RAZVEDKA, SLUZHBA, OPERATSIYA, KONTAKT, METOD,
  ZADACHA, TSELI, INOSTRANETS, RAZVEDCHIK

Additionally, Sanborn confirmed the Cyrillic Projector plaintext is a
translation of a KGB operations manual — the specific chapter projected
at UNC is about recruitment and contact methods.

This module tests these transliterated KGB keywords as keyed-alphabet seeds
for K4, following the same pattern as P11 and P19.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# KGB document keywords from the Cyrillic Projector, transliterated to Roman
# Only alphanumeric characters, uppercase, using standard transliteration
CYRILLIC_PROJECTOR_KEYWORDS: list[str] = [
    "AGENT",         # agent/operative
    "REZIDENT",      # resident intelligence officer
    "RAZVEDKA",      # intelligence/reconnaissance
    "SLUZHBA",       # service/department
    "KONTAKT",       # contact
    "METOD",         # method
    "ZADACHA",       # task/objective
    "RAZVEDCHIK",    # intelligence officer
    "OPERATSIYA",    # operation
    "INOSTRANETS",   # foreigner/foreign national
    "NAZNACHENIE",   # assignment/appointment
    "VOVLECHENIE",   # recruitment/involvement
    "SVYAZ",         # connection/liaison
    "PROVERKA",      # verification/check
    "LEGENDY",       # cover stories (legend)
    "KONSPIRATSIYA", # conspiracy/secrecy
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


CYRILLIC_KEYED_ALPHABETS: dict[str, str] = {
    kw: build_keyed_alphabet(kw) for kw in CYRILLIC_PROJECTOR_KEYWORDS
}


def run_cyrillic_projector_sweep(
    grid_sizes: list[int] | None = None,
    clock_step_seconds: int = 3600,
    max_perms_per_grid: int = 120,
    priority_only: bool = True,
    progress_cb: Any = None,
    null_artifact_path: str = "K4_P20_CYRILLIC_NULL.json",
) -> dict[str, Any]:
    """Run the 3-layer composite with Cyrillic Projector keyed alphabets.

    Args:
        grid_sizes: Column counts to sweep (default: [7, 8, 10]).
        clock_step_seconds: Seconds between clock states.
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
        subst_alphabets=CYRILLIC_KEYED_ALPHABETS,
        grid_sizes=grid_sizes or [7, 8, 10],
        clock_step_seconds=clock_step,
        priority_clock_times=CIA_PRIORITY_TIMES,
        max_perms_per_grid=max_perms_per_grid,
        progress_cb=progress_cb,
        null_artifact_path=null_artifact_path,
        eureka_snapshot_path="K4_P20_CYRILLIC_EUREKA.md",
    )


__all__ = [
    "CYRILLIC_PROJECTOR_KEYWORDS",
    "CYRILLIC_KEYED_ALPHABETS",
    "build_keyed_alphabet",
    "run_cyrillic_projector_sweep",
]
