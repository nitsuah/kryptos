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


def _aligned_pre_transposition(
    order_name: str,
    reflection_name: str,
    rotation_offset: int,
    remainder_mode: str,
    candidate_name: str,
) -> tuple[str, str] | None:
    """(pre_transposition_text, reconstructed_plaintext), both position-aligned. None if unavailable."""
    plaintext = reconstructed_plaintext(candidate_name)
    if plaintext is None:
        return None
    flat_idx = composed_flat_indices(order_name, reflection_name, rotation_offset, remainder_mode)
    ct_source = K4 if remainder_mode != "drop" else K4[: geometry24.CORE_LEN]
    if len(ct_source) != len(flat_idx):
        return None
    pre_transposition = geometry24.apply_inverse(ct_source, flat_idx)
    n = min(len(pre_transposition), len(plaintext))
    return pre_transposition[:n], plaintext[:n]


def _shifts_from_pair(pre_transposition: str, plaintext: str, alphabet: str) -> list[int]:
    shifts: list[int] = []
    for c, p in zip(pre_transposition, plaintext, strict=True):
        if p not in alphabet or c not in alphabet:
            continue
        shifts.append((alphabet.index(c) - alphabet.index(p)) % len(alphabet))
    return shifts


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
    pair = _aligned_pre_transposition(order_name, reflection_name, rotation_offset, remainder_mode, candidate_name)
    if pair is None:
        return None
    return _shifts_from_pair(*pair, alphabet)


def _is_consistent_substitution(pre_transposition: str, plaintext: str) -> bool:
    """Would a single, fixed monoalphabetic substitution (any 26-letter mapping,

    not just a Caesar shift) turn ``plaintext`` into ``pre_transposition``?
    True only if every ciphertext-side letter maps to exactly one
    plaintext-side letter everywhere it occurs, AND that mapping is a true
    bijection (no two distinct ciphertext letters collapse onto the same
    plaintext letter) -- a monoalphabetic substitution cipher must be
    invertible in both directions, or it isn't a valid substitution at all.
    The forward-only check originally here would have accepted "AB"/"NN" as
    consistent, which no real substitution cipher can produce (found via
    CodeRabbit review on PR #203, verified against current code before
    fixing) -- the same test this project already used to *disprove*
    monoalphabetic substitution on the 24 confirmed crib characters (see
    K4_ACTIVE_RESEARCH.md's Ruled Out table), now run against the full
    reconstructed text under each transposition hypothesis. Broader than
    `_consistent_periods` with period=1 (a fixed shift): this allows any
    bijection, not just addition mod 26.
    """
    mapping: dict[str, str] = {}
    reverse_mapping: dict[str, str] = {}
    for c, p in zip(pre_transposition, plaintext, strict=False):
        if c in mapping and mapping[c] != p:
            return False
        if p in reverse_mapping and reverse_mapping[p] != c:
            return False
        mapping[c] = p
        reverse_mapping[p] = c
    return True


def _consistent_periods(shifts: list[int], period_range: range) -> list[int]:
    """Which periods in ``period_range`` are consistent with ``shifts`` (same shift at every position mod L)?

    Only periods in ``1 <= period < len(shifts)`` are evaluated: ``period ==
    0`` would raise ``ZeroDivisionError`` on ``pos % period``, and any period
    at or beyond ``len(shifts)`` puts every position in its own singleton
    slot, making it *trivially* "consistent" regardless of the actual shift
    sequence -- a false hypothesis, not a real repeating-key signal (found
    via CodeRabbit review on PR #203, verified against current code before
    fixing; a default `period_range=range(2, 21)` against this project's
    ~97-character shift sequences never triggered this, but the function
    must not silently accept an out-of-range period from any caller).
    """
    consistent: list[int] = []
    for period in period_range:
        if not (0 < period < len(shifts)):
            continue
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
                    pair = _aligned_pre_transposition(
                        order_name, reflection_name, rotation_offset, remainder_mode, candidate_name
                    )
                    if pair is None:
                        continue
                    total_tested += 1
                    shifts = _shifts_from_pair(*pair, STANDARD_ALPHABET)
                    periods = _consistent_periods(shifts, period_range) if shifts else []
                    is_substitution = _is_consistent_substitution(*pair)
                    if periods or is_substitution:
                        hits.append(
                            {
                                "order": order_name,
                                "reflection": reflection_name,
                                "rotation_offset": rotation_offset,
                                "remainder_mode": remainder_mode,
                                "consistent_periods": periods,
                                "consistent_monoalphabetic_substitution": is_substitution,
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


def _aligned_pre_transposition_rectangular(
    n_cols: int,
    permutation: tuple[int, ...],
    candidate_name: str,
) -> tuple[str, str] | None:
    """Same as `_aligned_pre_transposition`, for the rectangular-grid family.

    `apply_columnar_permutation_reverse` already returns text ordered by
    original (pre-transposition) position, exactly like
    `geometry24.apply_inverse` -- same semantics, different primitive.
    """
    from .transposition_analysis import apply_columnar_permutation_reverse

    plaintext = reconstructed_plaintext(candidate_name)
    if plaintext is None:
        return None
    pre_transposition = apply_columnar_permutation_reverse(K4, n_cols, list(permutation))
    n = min(len(pre_transposition), len(plaintext))
    return pre_transposition[:n], plaintext[:n]


def implied_shifts_rectangular(
    n_cols: int,
    permutation: tuple[int, ...],
    candidate_name: str = "solvekryptos_field_guide",
    alphabet: str = STANDARD_ALPHABET,
) -> list[int] | None:
    """Same idea as ``implied_shifts``, for the *other* transposition family this project

    has tested (`inverse_transposition_sweep.py`'s 10x10/7x14/8x13 rectangular
    grids with an arbitrary column permutation) rather than the 24-column
    geometry family.
    """
    pair = _aligned_pre_transposition_rectangular(n_cols, permutation, candidate_name)
    if pair is None:
        return None
    return _shifts_from_pair(*pair, alphabet)


def scan_rectangular_transpositions(
    grid_sizes: list[int] | None = None,
    candidate_name: str = "solvekryptos_field_guide",
    period_range: range = range(2, 21),
) -> dict[str, Any]:
    """Exhaustive known-plaintext scan over the rectangular-grid transposition family.

    This is the K4-T1 physical-geometric spec's original grid set
    (`inverse_transposition_sweep.K4_GRID_GEOMETRIES`), tested here the
    known-plaintext way for the first time -- every one of that module's
    own sweeps scored candidates by crib/language match, never by directly
    solving for the implied substitution shift the way this does. Genuinely
    exhaustive for all three grid widths (7! = 5,040, 8! = 40,320,
    10! = 3,628,800 permutations -- all enumerated, no sampling).
    """
    from itertools import permutations

    from .inverse_transposition_sweep import K4_GRID_GEOMETRIES

    grid_sizes = grid_sizes if grid_sizes is not None else K4_GRID_GEOMETRIES
    total_tested = 0
    hits: list[dict[str, Any]] = []

    for n_cols in grid_sizes:
        for perm in permutations(range(n_cols)):
            pair = _aligned_pre_transposition_rectangular(n_cols, perm, candidate_name)
            if pair is None:
                continue
            total_tested += 1
            shifts = _shifts_from_pair(*pair, STANDARD_ALPHABET)
            periods = _consistent_periods(shifts, period_range) if shifts else []
            is_substitution = _is_consistent_substitution(*pair)
            if periods or is_substitution:
                hits.append(
                    {
                        "n_cols": n_cols,
                        "permutation": perm,
                        "consistent_periods": periods,
                        "consistent_monoalphabetic_substitution": is_substitution,
                    }
                )

    return {
        "attack": "known_plaintext_rectangular_inversion",
        "candidate_name": candidate_name,
        "grid_sizes": grid_sizes,
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
    "implied_shifts_rectangular",
    "scan_transpositions",
    "scan_rectangular_transpositions",
]
