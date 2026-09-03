"""Known-plaintext transposition inversion -- new attack surface once a candidate plaintext exists.

Every geometric sweep this project has run before this module (see
``geometry_combined_sweep.py``, ~2.4M candidates across Phases 6-7) works
the same way: hypothesize a transposition, invert it, apply a *hypothesized
substitution* (a keyed Quagmire III tableau), and score the result by
language quality / crib matches. That's the right approach when the
plaintext is unknown.

It is no longer the only approach available. `solvekryptos.com`'s
reconstructed plaintext (see ``plaintext_evidence.py`` -- 24 Sanborn-
CONFIRMED characters, 73 RECONSTRUCTED and independently unverified)
matches all 4 confirmed crib anchors exactly. Assuming it for the sake of
argument, this module asks a different, cheaper question: for each
already-enumerated candidate transposition, invert the real K4 ciphertext
through it, then instead of guessing a substitution and checking if the
result reads like English, directly compute what the *substitution shift*
at every position would have to be for that transposition to have produced
this specific reconstructed plaintext -- and check whether that implied
shift sequence shows any structure (a repeating period) at all.

This does not "cheat" or presuppose the answer: language-score-based
sweeps and this position-derived-shift approach are two independent tests
of the same transposition-hypothesis space, and a transposition that shows
no structure here is just as null a result as one that produced no
readable candidate before. The one discipline that matters, and that this
module enforces structurally rather than just by convention: any signal
found here rests entirely on the RECONSTRUCTED plaintext's unverified 73
characters, so it can only ever produce a *hypothesis to test
independently* (e.g. via ``key_csp.solve_key_csp`` against the real
ciphertext, or by checking whether the derived shift sequence matches a
real Berlin Clock state or keyed alphabet) -- never a promoted candidate
in its own right. Nothing here calls ``EurekaSignal``.
"""

from __future__ import annotations

from typing import Any

from . import geometry24, reflection
from .geometry_combined_sweep import DEFAULT_ORDER_NAMES, composed_flat_indices
from .physical_grid import K4
from .plaintext_evidence import STANDARD_ALPHABET, reconstructed_plaintext

DEFAULT_REFLECTION_NAMES: list[str] = [*reflection.SHAPE_PRESERVING, *reflection.SHAPE_CHANGING]
DEFAULT_ROTATION_OFFSETS: list[int] = list(range(geometry24.COLS))  # full 0-23, not just the priority subset
DEFAULT_REMAINDER_MODES: list[str] = list(geometry24.REMAINDER_MODES)


def implied_shifts(
    order_name: str,
    reflection_name: str,
    rotation_offset: int,
    remainder_mode: str,
    candidate_name: str = "solvekryptos_field_guide",
    alphabet: str = STANDARD_ALPHABET,
) -> list[int] | None:
    """The per-position Vigenère-equivalent shift a substitution layer would need,

    for this specific transposition hypothesis to turn the reconstructed
    plaintext into the real K4 ciphertext. Returns None if the reconstructed
    plaintext isn't available or lengths don't align after a "drop"
    remainder mode.
    """
    plaintext = reconstructed_plaintext(candidate_name)
    if plaintext is None:
        return None
    flat_idx = composed_flat_indices(order_name, reflection_name, rotation_offset, remainder_mode)
    ct_source = K4 if remainder_mode != "drop" else K4[: geometry24.CORE_LEN]
    if len(ct_source) != len(flat_idx):
        return None
    pre_transposition = geometry24.apply_inverse(ct_source, flat_idx)
    n = min(len(pre_transposition), len(plaintext))
    shifts: list[int] = []
    for i in range(n):
        p, c = plaintext[i], pre_transposition[i]
        if p not in alphabet or c not in alphabet:
            continue
        shifts.append((alphabet.index(c) - alphabet.index(p)) % len(alphabet))
    return shifts


def _consistent_periods(shifts: list[int], period_range: range) -> list[int]:
    """Which periods in ``period_range`` are consistent with ``shifts`` (same shift at every position mod L)?"""
    consistent: list[int] = []
    for period in period_range:
        by_slot: dict[int, set[int]] = {}
        for pos, shift in enumerate(shifts):
            by_slot.setdefault(pos % period, set()).add(shift)
        if all(len(vals) == 1 for vals in by_slot.values()):
            consistent.append(period)
    return consistent


def scan_transpositions(
    order_names: list[str] | None = None,
    reflection_names: list[str] | None = None,
    rotation_offsets: list[int] | None = None,
    remainder_modes: list[str] | None = None,
    candidate_name: str = "solvekryptos_field_guide",
    period_range: range = range(2, 21),
) -> dict[str, Any]:
    """Scan every candidate transposition already enumerated elsewhere in this project

    for one whose implied substitution shift (against the reconstructed
    plaintext) shows a repeating-key period. Reuses exactly the same
    transposition primitives ``geometry_combined_sweep.py`` already tests
    (same ``composed_flat_indices``), so this walks the identical
    transposition-hypothesis space that project's ~2.4M language-scored
    candidates already covered -- just judged a different way.
    """
    order_names = order_names if order_names is not None else DEFAULT_ORDER_NAMES
    reflection_names = reflection_names if reflection_names is not None else DEFAULT_REFLECTION_NAMES
    rotation_offsets = rotation_offsets if rotation_offsets is not None else DEFAULT_ROTATION_OFFSETS
    remainder_modes = remainder_modes if remainder_modes is not None else DEFAULT_REMAINDER_MODES

    total_tested = 0
    hits: list[dict[str, Any]] = []

    for order_name in order_names:
        for reflection_name in reflection_names:
            for rotation_offset in rotation_offsets:
                for remainder_mode in remainder_modes:
                    shifts = implied_shifts(
                        order_name, reflection_name, rotation_offset, remainder_mode, candidate_name
                    )
                    if not shifts:
                        continue
                    total_tested += 1
                    periods = _consistent_periods(shifts, period_range)
                    if periods:
                        hits.append(
                            {
                                "order": order_name,
                                "reflection": reflection_name,
                                "rotation_offset": rotation_offset,
                                "remainder_mode": remainder_mode,
                                "consistent_periods": periods,
                            }
                        )

    return {
        "attack": "known_plaintext_transposition_inversion",
        "candidate_name": candidate_name,
        "total_tested": total_tested,
        "period_range": [period_range.start, period_range.stop],
        "hits": hits,
        "status": "hypothesis_found" if hits else "null_result",
    }


__all__ = [
    "DEFAULT_REFLECTION_NAMES",
    "DEFAULT_ROTATION_OFFSETS",
    "DEFAULT_REMAINDER_MODES",
    "implied_shifts",
    "scan_transpositions",
]
