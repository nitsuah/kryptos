"""Composite parameter sweep for K4 — K4-ATTACK-4.

Exhaustively searches:
    alphabets × grid_sizes × Berlin Clock states × reading routes

Per combination, the decryption pipeline is:
    K4 ──[inverse_transposition(perm, n_cols)]──► intermediate
       ──[route_read(intermediate, n_cols)]──► routed
       ──[Vigenère_decrypt(clock_shifts, alphabet)]──► candidate_plaintext
       ──[keyword presence check + InstructionalScore]──► Eureka / record

A simultaneous appearance of all four Sanborn-confirmed words
(EAST, NORTHEAST, BERLIN, CLOCK) in the candidate plaintext triggers
the Eureka protocol and halts the sweep.

A null-result artifact is always written when the sweep ends without a
Eureka event so each run is fully provenance-tracked and reproducible.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from itertools import permutations
from pathlib import Path
from typing import Any

from .berlin_clock import enumerate_clock_shift_sequences
from .eureka import DEFAULT_SNAPSHOT_PATH, EurekaSignal, write_breakthrough_snapshot
from .inverse_transposition_sweep import K4_GRID_GEOMETRIES, SWEEP_ROUTES, invert_permutation
from .keystream_validator import K4_CRIBS
from .physical_grid import K4
from .scoring_instructional import combined_instructional_score
from .transposition_analysis import apply_columnar_permutation_reverse
from .vigenere_key_recovery import KNOWN_KEYED_ALPHABETS, check_keyed_alphabet_realignment

_NULL_ARTIFACT_PATH = "K4_COMPOSITE_SWEEP_NULL.json"
_EUREKA_WORDS: frozenset[str] = frozenset({"EAST", "NORTHEAST", "BERLIN", "CLOCK"})


def _vigenere_decrypt(text: str, shifts: list[int], alphabet: str) -> str:
    """Subtract clock shifts cyclically from text using the given alphabet."""
    n_alpha = len(alphabet)
    n_shifts = len(shifts)
    out: list[str] = []
    pos = 0
    for c in text.upper():
        if not c.isalpha():
            continue
        if c not in alphabet:
            out.append(c)
            pos += 1
            continue
        idx = alphabet.index(c)
        out.append(alphabet[(idx - shifts[pos % n_shifts]) % n_alpha])
        pos += 1
    return "".join(out)


def _keyword_hits(text: str) -> int:
    """Count how many of the 4 K4 confirmation words appear as substrings."""
    upper = text.upper()
    return sum(1 for w in _EUREKA_WORDS if w in upper)


def run_composite_sweep(
    ciphertext: str = K4,
    alphabets: dict[str, str] | None = None,
    grid_sizes: list[int] | None = None,
    clock_step_seconds: int = 3600,
    routes: tuple[str, ...] = ("ene_diagonal", "columnar"),
    max_perms_per_grid: int | None = 500,
    eureka_snapshot_path: str | Path = DEFAULT_SNAPSHOT_PATH,
    null_artifact_path: str | Path = _NULL_ARTIFACT_PATH,
    keyword_eureka_threshold: int = 4,
) -> dict[str, Any]:
    """Run composite parameter sweep over alphabets × grids × clock states × routes.

    Args:
        ciphertext:               K4 ciphertext.
        alphabets:                Dict of name→26-char alphabet (default: KNOWN_KEYED_ALPHABETS).
        grid_sizes:               Column counts to test (default: K4_GRID_GEOMETRIES).
        clock_step_seconds:       Berlin Clock granularity (3600 = 24 states/day).
        routes:                   Transposition reading routes from SWEEP_ROUTES.
        max_perms_per_grid:       Cap on permutations per (grid, clock, alphabet) combo.
        eureka_snapshot_path:     Breakthrough snapshot destination.
        null_artifact_path:       Null-result provenance artifact destination.
        keyword_eureka_threshold: K4 keywords required in plaintext to trigger Eureka (max 4).

    Returns:
        Summary dict. Raises EurekaSignal immediately on keyword hit ≥ threshold.
    """
    if alphabets is None:
        alphabets = KNOWN_KEYED_ALPHABETS
    if grid_sizes is None:
        grid_sizes = K4_GRID_GEOMETRIES

    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    clock_states = enumerate_clock_shift_sequences(step_seconds=clock_step_seconds)
    ts_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    alignment = check_keyed_alphabet_realignment(ct, K4_CRIBS, alphabets=alphabets)

    total_candidates = 0
    best_candidates: list[dict[str, Any]] = []

    try:
        for clock in clock_states:
            clock_shifts = clock["shifts"]
            clock_time = clock["time"]

            for alpha_name, alphabet in alphabets.items():
                clock_stripped = _vigenere_decrypt(ct, clock_shifts, alphabet)

                for n_cols in grid_sizes:
                    perm_gen = permutations(range(n_cols))
                    perm_count = 0
                    for perm in perm_gen:
                        if max_perms_per_grid is not None and perm_count >= max_perms_per_grid:
                            break
                        perm_count += 1

                        intermediate = apply_columnar_permutation_reverse(clock_stripped, n_cols, list(perm))

                        for route_name in routes:
                            route_fn = SWEEP_ROUTES.get(route_name)
                            if route_fn is None:
                                continue

                            candidate = route_fn(intermediate, n_cols)
                            total_candidates += 1

                            kw_hits = _keyword_hits(candidate)
                            if kw_hits >= keyword_eureka_threshold:
                                key_info = {
                                    "alpha_name": alpha_name,
                                    "n_cols": n_cols,
                                    "perm": list(perm),
                                    "inv_perm": list(invert_permutation(perm)),
                                    "route": route_name,
                                    "clock_time": clock_time,
                                    "clock_shifts": list(clock_shifts),
                                }
                                snap = write_breakthrough_snapshot(
                                    candidate,
                                    key_info,
                                    extra={"keyword_hits": kw_hits, "sweep_ts": ts_start},
                                    path=eureka_snapshot_path,
                                )
                                result = {
                                    "candidate_text": candidate,
                                    "key_info": key_info,
                                    "snapshot_path": snap,
                                    "keyword_hits": kw_hits,
                                }
                                raise EurekaSignal(snapshot_path=snap, result=result)

                            if kw_hits > 0:
                                score = combined_instructional_score(candidate, gate_entropy=False)
                                best_candidates.append(
                                    {
                                        "candidate_text": candidate,
                                        "keyword_hits": kw_hits,
                                        "instructional_score": score,
                                        "alpha_name": alpha_name,
                                        "n_cols": n_cols,
                                        "perm": list(perm),
                                        "route": route_name,
                                        "clock_time": clock_time,
                                    }
                                )

    except EurekaSignal:
        raise

    best_candidates.sort(key=lambda r: (-r["keyword_hits"], -r["instructional_score"]))

    run_params = {
        "alphabets": list(alphabets.keys()),
        "grid_sizes": grid_sizes,
        "clock_step_seconds": clock_step_seconds,
        "clock_states_count": len(clock_states),
        "routes": list(routes),
        "max_perms_per_grid": max_perms_per_grid,
        "total_candidates_checked": total_candidates,
        "keyword_eureka_threshold": keyword_eureka_threshold,
        "ts_start": ts_start,
    }
    summary = {
        "status": "null_result",
        "timestamp": ts_start,
        "run_params": run_params,
        "best_candidates": best_candidates[:10],
        "alphabet_alignment": alignment,
        "null_artifact_path": str(Path(null_artifact_path).resolve()),
    }

    Path(null_artifact_path).write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary


__all__ = [
    "K4",
    "run_composite_sweep",
]
