"""Generalized two-stage grid-rotation transposition solver.

K3 is solved by two cascaded 90-degree grid rotations
(``kryptos.ciphers.double_rotational_transposition``: a 24x14 grid rotated,
producing an intermediate 24x14 layout, then re-gridded at width 8 and
rotated again). This module generalizes that construction to arbitrary
divisor-pair grid widths and all six rotation types from
:func:`kryptos.k4.transposition_analysis.apply_rotation`, and provides a
brute-force solver plus a Monte Carlo validation harness.

This is the "K3 double-transposition Monte Carlo" item from
ROADMAP.md (Phase 4: Validation & hardening): confirming that the
double-rotation attack vector reliably recovers plaintext for K3-length
(336-char) ciphertexts, independent of which divisor-width/rotation-type
pair was used for each stage.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from kryptos.k4.transposition_analysis import apply_rotation, score_combined, score_combined_with_words

# K3 ciphertext length: 24*14 == 8*42 == 336
K3_LENGTH = 336

ROTATION_TYPES: tuple[str, ...] = (
    "identity",
    "90cw",
    "90ccw",
    "180",
    "flip_h",
    "flip_v",
)

# Proper divisors of 336, excluding 1 and 336 (which give degenerate 1xN/Nx1
# grids). This set is closed under w -> 336 // w, so the inverse of any
# (width, rotation) pair tried during encryption is also a candidate during
# brute-force decryption.
DIVISORS_336: tuple[int, ...] = (
    2,
    3,
    4,
    6,
    7,
    8,
    12,
    14,
    16,
    21,
    24,
    28,
    42,
    48,
    56,
    84,
    112,
    168,
)


def apply_double_rotation(text: str, width_a: int, rotation_a: str, width_b: int, rotation_b: str) -> str:
    """Apply two cascaded grid rotations, as in K3's double rotational transposition."""
    stage_a = apply_rotation(text, width_a, rotation_a)
    return apply_rotation(stage_a, width_b, rotation_b)


@dataclass(frozen=True)
class RotationCandidate:
    width_a: int
    rotation_a: str
    width_b: int
    rotation_b: str
    text: str
    score: float


def brute_force_double_rotation_solve(
    ciphertext: str,
    widths: tuple[int, ...] = DIVISORS_336,
    rotations: tuple[str, ...] = ROTATION_TYPES,
    prefilter_n: int = 50,
    top_n: int = 5,
) -> list[RotationCandidate]:
    """Try every (width, rotation) pair for both stages, ranked by score.

    Candidates are first ranked by the cheap n-gram-only :func:`score_combined`
    across the full search space, then the top ``prefilter_n`` are re-ranked
    with the more discriminating (but slower) :func:`score_combined_with_words`.
    """
    length = len(ciphertext)
    valid_widths = [w for w in widths if length % w == 0]

    stage_a_results: list[tuple[int, str, str]] = []
    for width_a in valid_widths:
        for rotation_a in rotations:
            stage_a_results.append((width_a, rotation_a, apply_rotation(ciphertext, width_a, rotation_a)))

    prefiltered: list[RotationCandidate] = []
    for width_a, rotation_a, stage_a_text in stage_a_results:
        for width_b in valid_widths:
            for rotation_b in rotations:
                stage_b_text = apply_rotation(stage_a_text, width_b, rotation_b)
                score = score_combined(stage_b_text)
                prefiltered.append(RotationCandidate(width_a, rotation_a, width_b, rotation_b, stage_b_text, score))

    prefiltered.sort(key=lambda c: c.score, reverse=True)
    rescored = [
        RotationCandidate(
            c.width_a,
            c.rotation_a,
            c.width_b,
            c.rotation_b,
            c.text,
            score_combined_with_words(c.text),
        )
        for c in prefiltered[:prefilter_n]
    ]
    rescored.sort(key=lambda c: c.score, reverse=True)
    return rescored[:top_n]


def _match_ratio(a: str, b: str) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    return sum(1 for x, y in zip(a, b, strict=True) if x == y) / len(a)


def run_k3_double_rotation_monte_carlo(
    plaintext: str,
    num_runs: int = 20,
    widths: tuple[int, ...] = DIVISORS_336,
    rotations: tuple[str, ...] = ROTATION_TYPES,
    seed: int = 42,
    match_threshold: float = 0.95,
    top_n: int = 10,
    results_path: Path | str | None = None,
) -> dict:
    """Monte Carlo validation of the double-rotation attack vector.

    For ``num_runs`` random (width, rotation) pairs per stage, encrypt
    ``plaintext`` with :func:`apply_double_rotation`, then run
    :func:`brute_force_double_rotation_solve` against the resulting
    ciphertext and check whether any of the top-``top_n`` candidates
    recovers ``plaintext`` to within ``match_threshold``.

    The search space contains rotation/width combinations (notably ones
    involving ``'identity'``, which is a no-op for any width) that are
    score-equivalent to cyclic rearrangements of the true plaintext: same
    n-gram and word statistics, just a different start offset. These can
    outrank the exact match by floating-point noise, so the correct
    plaintext is not always the literal #1 candidate even when it is
    recovered. Both the strict top-1 and best-of-``top_n`` match ratios
    are recorded so this distinction is visible in the results.
    """
    rng = random.Random(seed)
    runs = []
    successes = 0

    for run in range(num_runs):
        width_a = rng.choice(widths)
        rotation_a = rng.choice(rotations)
        width_b = rng.choice(widths)
        rotation_b = rng.choice(rotations)

        ciphertext = apply_double_rotation(plaintext, width_a, rotation_a, width_b, rotation_b)

        candidates = brute_force_double_rotation_solve(ciphertext, widths=widths, rotations=rotations, top_n=top_n)
        ratios = [_match_ratio(c.text, plaintext) for c in candidates]

        top1_match = ratios[0] if ratios else 0.0
        best_index = max(range(len(ratios)), key=ratios.__getitem__) if ratios else None
        best = candidates[best_index] if best_index is not None else None
        best_match = ratios[best_index] if best_index is not None else 0.0

        success = best_match >= match_threshold

        if success:
            successes += 1

        runs.append(
            {
                "run": run,
                "encrypt_params": [width_a, rotation_a, width_b, rotation_b],
                "top1_params": (
                    [
                        candidates[0].width_a,
                        candidates[0].rotation_a,
                        candidates[0].width_b,
                        candidates[0].rotation_b,
                    ]
                    if candidates
                    else None
                ),
                "top1_match_ratio": top1_match,
                "best_match_params": ([best.width_a, best.rotation_a, best.width_b, best.rotation_b] if best else None),
                "best_match_ratio": best_match,
                "success": success,
            }
        )

    summary = {
        "attack": "k3_double_rotation_monte_carlo",
        "status": "validated" if successes == num_runs else "partial",
        "success_rate": successes / num_runs,
        "run_params": {
            "num_runs": num_runs,
            "plaintext_length": len(plaintext),
            "widths": list(widths),
            "rotations": list(rotations),
            "match_threshold": match_threshold,
            "top_n": top_n,
            "seed": seed,
        },
        "runs": runs,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if results_path is not None:
        path = Path(results_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(summary, indent=2))

    return summary
