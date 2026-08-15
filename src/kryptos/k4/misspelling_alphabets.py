"""P12 — Misspelling-derived substitution alphabets for K4.

Sanborn intentionally misspelled two words across K1-K3:
  - K1: IQLUSION  (ILLUSION with I→L swap, producing IQL... instead of ILL...)
  - K3: DESPARATLY (DESPERATELY with an A used where E belongs)

Hypothesis: these misspellings encode partial substitution-alphabet constraints
for K4. Specifically, the K4 substitution alphabet may:
  a) Conflate I and L (treat them as equivalent letter slots)
  b) Swap A and E in the alphabet ordering
  c) Both — creating a 2-edit modification of the standard keyed alphabets

We test all 8 combinations:
  base alphabet ∈ {KRYPTOS, PALIMPSEST, ABSCISSA} × swap ∈ {IL, AE, both}

The alphabet-modification approach: if the sculptor intended certain letters to
appear as others in the output (the misspelling IS the intended text), then the
substitution cipher might map the "correct" letter to the "wrong" letter's slot
in the alphabet. For example, if I and L share one cipher slot, a plaintext I
would encipher the same as a plaintext L.

Concretely:
  build_swapped_alphabet(base_alpha, swaps):
    → swap the POSITIONS of the specified letters in the keyed alphabet
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .vigenere_key_recovery import KNOWN_KEYED_ALPHABETS, build_keyed_alphabet

logger = logging.getLogger(__name__)

_NULL_ARTIFACT_PATH = "K4_P12_MISSPELLING_NULL.json"

# Letters swapped in the confirmed misspellings
MISSPELLING_SWAPS: dict[str, tuple[str, str]] = {
    "IL": ("I", "L"),   # IQLUSION: I used where L expected
    "AE": ("A", "E"),   # DESPARATLY: A used where E expected
}

BASE_ALPHABETS: list[str] = ["KRYPTOS", "PALIMPSEST", "ABSCISSA"]


def build_swapped_alphabet(base_alpha: str, swaps: list[tuple[str, str]]) -> str:
    """Swap the positions of pairs of letters in a keyed alphabet.

    Args:
        base_alpha: 26-character keyed alphabet string.
        swaps:      List of (letter_a, letter_b) pairs to swap positions.

    Returns:
        Modified alphabet with the specified letter positions exchanged.
    """
    alpha = list(base_alpha.upper())
    for a, b in swaps:
        ia = alpha.index(a)
        ib = alpha.index(b)
        alpha[ia], alpha[ib] = alpha[ib], alpha[ia]
    return "".join(alpha)


def build_misspelling_alphabets() -> dict[str, str]:
    """Build all misspelling-derived alphabets.

    Returns a dict of {name: alphabet_string} for each combination of
    base keyword × swap set.
    """
    result: dict[str, str] = {}

    for kw in BASE_ALPHABETS:
        base = KNOWN_KEYED_ALPHABETS[kw]

        # Single swaps
        for swap_name, swap_pair in MISSPELLING_SWAPS.items():
            name = f"{kw}_swap_{swap_name}"
            result[name] = build_swapped_alphabet(base, [swap_pair])

        # Both swaps combined
        both_swaps = list(MISSPELLING_SWAPS.values())
        name = f"{kw}_swap_IL_AE"
        result[name] = build_swapped_alphabet(base, both_swaps)

    return result


MISSPELLING_ALPHABETS: dict[str, str] = build_misspelling_alphabets()


def run_misspelling_sweep(
    grid_sizes: list[int] | None = None,
    clock_step_seconds: int = 3600,
    max_perms_per_grid: int | None = 120,
    priority_only: bool = True,
    progress_cb: Any = None,
    null_artifact_path: str | Path = _NULL_ARTIFACT_PATH,
) -> dict[str, Any]:
    """Run the P1 3-layer composite with all P12 misspelling-derived alphabets.

    Tests 9 alphabets (3 base keywords × 3 swap combinations: IL, AE, both).

    Args:
        grid_sizes:            Column counts to sweep.
        clock_step_seconds:    Granularity for full clock sweep.
        max_perms_per_grid:    Permutation cap per combo.
        priority_only:         If True, only test CIA priority timestamps.
        progress_cb:           Optional callback forwarded to run_three_layer_composite.
        null_artifact_path:    Path for null-result artifact.
    """
    from .three_layer_composite import CIA_PRIORITY_TIMES, run_three_layer_composite

    clock_step = 86400 if priority_only else clock_step_seconds

    logger.info(
        "P12 misspelling sweep: %d alphabets, priority_only=%s",
        len(MISSPELLING_ALPHABETS),
        priority_only,
    )

    return run_three_layer_composite(
        subst_alphabets=MISSPELLING_ALPHABETS,
        grid_sizes=grid_sizes,
        clock_step_seconds=clock_step,
        priority_clock_times=CIA_PRIORITY_TIMES,
        max_perms_per_grid=max_perms_per_grid,
        null_artifact_path=null_artifact_path,
        progress_cb=progress_cb,
    )
