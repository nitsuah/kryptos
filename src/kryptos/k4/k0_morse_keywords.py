"""K0 -- Morse-code entrance-slab words as keyed-alphabet seeds for K4.

The Kryptos installation is two zones: the courtyard copper screen (K1-K4)
and a separate entrance approach, where red granite slabs sandwich copper
sheets perforated with International Morse code. The community nicknames
this "K0." It has never been used as a keyword source anywhere in this
project before now.

Sourced and cross-checked against two independent community references
before use, per this project's own no-unverified-claims discipline:
- https://elonka.com/kryptos/wishlist.html (the same authoritative
  measurement-tracking page this project already cites for the compass
  bearing gap) documents the entrance slabs' existence and open questions
  about them.
- https://rumkin.com/reference/kryptos/k0/ gives the actual decoded Morse
  transcriptions, checked directly (not taken from a paraphrased summary):
  SOS, RQ/YR, LUCID MEMORY, SHADOW FORCES, WHAT IS YOUR POSITION, DIGITAL
  INTERPRETATION, VIRTUALLY INVISIBLE (two plates).

Words already covered by this project's existing keyword sources are
excluded: SHADOW, BETWEEN, DIGETAL, and POSITION are already in
`alt_keywords.P11_KEYWORDS` / `plaintext_evidence.RECONSTRUCTED_PLAINTEXT_
KEYWORDS`. WHAT/IS/YOUR are function words, excluded the same way this
project already excludes THE/HERE/THIS/YOUR/OF elsewhere (see
`plaintext_evidence.py`). SOS and RQ/YR are too short (2-3 letters) to be
a meaningful 26-letter keyed-alphabet seed. DIGITAL is kept distinct from
the already-tested DIGETAL: this project doesn't know which spelling (if
either) is Sanborn's own intentional-misspelling choice on this slab, so
both are worth testing rather than assuming the earlier one was right.

The remaining, genuinely new words -- VIRTUALLY, INVISIBLE, LUCID, MEMORY,
FORCES, INTERPRETATION, DIGITAL -- were already present in
`scoring_instructional.INSTRUCTIONAL_VECTORS` as language-scoring bonus
vocabulary (someone had already flagged them as K4-relevant), but were
never tested as keyed-alphabet seeds. That is a genuinely different,
previously-unbuilt capability, not a duplicate of the scoring bonus.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_NULL_ARTIFACT_PATH = "K4_K0_MORSE_KEYWORD_NULL.json"

K0_MORSE_KEYWORDS: list[str] = [
    "VIRTUALLY",
    "INVISIBLE",
    "LUCID",
    "MEMORY",
    "FORCES",
    "INTERPRETATION",
    "DIGITAL",
]


def k0_morse_keyed_alphabets() -> dict[str, str]:
    """Keyed alphabets built from `K0_MORSE_KEYWORDS`, same convention as alt_keywords.py."""
    from .vigenere_key_recovery import build_keyed_alphabet

    return {kw: build_keyed_alphabet(kw) for kw in K0_MORSE_KEYWORDS}


def run_k0_morse_keyword_sweep(
    grid_sizes: list[int] | None = None,
    clock_step_seconds: int = 3600,
    max_perms_per_grid: int | None = 120,
    priority_only: bool = True,
    progress_cb: Any = None,
    null_artifact_path: str | Path = _NULL_ARTIFACT_PATH,
) -> dict[str, Any]:
    """Run the P1 3-layer composite with the K0 Morse-slab keyword alphabet set.

    Mirrors `alt_keywords.run_alt_keyword_sweep` and `plaintext_evidence.
    run_reconstructed_plaintext_keyword_sweep` exactly -- same composite
    pipeline, only the keyword source differs.
    """
    from .three_layer_composite import CIA_PRIORITY_TIMES, run_three_layer_composite

    clock_step = 86400 if priority_only else clock_step_seconds

    logger.info(
        "K0 Morse-keyword sweep: %d alphabets, priority_only=%s",
        len(K0_MORSE_KEYWORDS),
        priority_only,
    )

    return run_three_layer_composite(
        subst_alphabets=k0_morse_keyed_alphabets(),
        grid_sizes=grid_sizes,
        clock_step_seconds=clock_step,
        priority_clock_times=CIA_PRIORITY_TIMES,
        max_perms_per_grid=max_perms_per_grid,
        null_artifact_path=null_artifact_path,
        progress_cb=progress_cb,
        eureka_snapshot_path="K4_K0_MORSE_KEYWORD_EUREKA.md",
    )


__all__ = [
    "K0_MORSE_KEYWORDS",
    "k0_morse_keyed_alphabets",
    "run_k0_morse_keyword_sweep",
]
