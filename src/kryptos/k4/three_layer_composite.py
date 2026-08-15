"""3-layer composite attack for K4 — Frontier P1.

Encryption hypothesis: plaintext → mono-subst(keyed) → clock-Vigenère → columnar → K4
Decryption:           K4 → inv-columnar → inv-clock-Vigenère → inv-mono-subst → candidate

Two priority clock states are tested first (CIA dedication timestamp):
  - 13:00 EST  (Nov 3 1990, CIA unveiling, local time)
  - 19:00 CET  (same moment, Berlin local time)

Then a full 24-state hourly sweep.  Search space at 6 cols, 3 alphabets:
  3 × 24 × 720 = 51,840 candidates per grid size.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import datetime, timezone
from itertools import permutations
from pathlib import Path
from typing import Any

from .berlin_clock import enumerate_clock_shift_sequences, full_berlin_clock_shifts
from .eureka import DEFAULT_SNAPSHOT_PATH, EurekaSignal, write_breakthrough_snapshot
from .inverse_transposition_sweep import K4_GRID_GEOMETRIES
from .keystream_validator import K4_CRIBS
from .scoring_instructional import combined_instructional_score
from .transposition_analysis import apply_columnar_permutation_reverse
from .vigenere_key_recovery import KNOWN_KEYED_ALPHABETS

logger = logging.getLogger(__name__)

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_NULL_ARTIFACT_PATH = "K4_3LAYER_NULL.json"
_EUREKA_WORDS: frozenset[str] = frozenset({"EAST", "NORTHEAST", "BERLIN", "CLOCK"})

# CIA dedication timestamp clock states (tested before the full sweep).
CIA_PRIORITY_TIMES = ["13:00:00", "19:00:00"]


def _mono_subst_decrypt(text: str, alphabet: str) -> str:
    """Undo a monoalphabetic substitution that encrypted standard→alphabet."""
    out: list[str] = []
    for c in text.upper():
        if c.isalpha() and c in alphabet:
            out.append(STANDARD[alphabet.index(c)])
        else:
            out.append(c)
    return "".join(out)


def _vigenere_decrypt_std(text: str, shifts: list[int]) -> str:
    """Standard Vigenère decrypt: subtract clock shifts mod 26."""
    out: list[str] = []
    pos = 0
    n = len(shifts)
    for c in text.upper():
        if c.isalpha():
            out.append(STANDARD[(STANDARD.index(c) - shifts[pos % n]) % 26])
            pos += 1
        else:
            out.append(c)
    return "".join(out)


def _keyword_hits(text: str) -> int:
    upper = text.upper()
    return sum(1 for w in _EUREKA_WORDS if w in upper)


def _decrypt_three_layer(
    ciphertext: str,
    n_cols: int,
    perm: tuple[int, ...],
    clock_shifts: list[int],
    subst_alphabet: str,
) -> str:
    """Apply full inverse 3-layer pipeline to ciphertext."""
    step1 = apply_columnar_permutation_reverse(ciphertext, n_cols, list(perm))
    step2 = _vigenere_decrypt_std(step1, clock_shifts)
    return _mono_subst_decrypt(step2, subst_alphabet)


def _build_clock_sequence(
    priority_times: list[str],
    clock_step_seconds: int,
) -> list[dict[str, Any]]:
    """Priority CIA timestamps first, then remaining hourly states (no duplicates)."""
    from datetime import time as dtime

    def _parse(ts: str) -> dict[str, Any]:
        h, m, s = (int(x) for x in ts.split(":"))
        t = dtime(h, m, s)
        shifts = full_berlin_clock_shifts(t)
        return {"time": ts, "shifts": shifts, "priority": True}

    priority = [_parse(ts) for ts in priority_times]
    priority_set = {ts for ts in priority_times}

    full = enumerate_clock_shift_sequences(step_seconds=clock_step_seconds)
    rest = [{"time": e["time"], "shifts": e["shifts"], "priority": False} for e in full if e["time"] not in priority_set]
    return priority + rest


def run_three_layer_composite(
    ciphertext: str = K4,
    subst_alphabets: dict[str, str] | None = None,
    grid_sizes: list[int] | None = None,
    clock_step_seconds: int = 3600,
    priority_clock_times: list[str] | None = None,
    max_perms_per_grid: int | None = 720,
    keyword_eureka_threshold: int = 4,
    eureka_snapshot_path: str | Path = "K4_3LAYER_BREAKTHROUGH.md",
    null_artifact_path: str | Path = _NULL_ARTIFACT_PATH,
    progress_cb: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Run the P1 3-layer composite attack against K4.

    Args:
        ciphertext:             K4 ciphertext string.
        subst_alphabets:        Name→alphabet dict for monoalphabetic layer.
        grid_sizes:             Column counts to sweep (default: K4_GRID_GEOMETRIES).
        clock_step_seconds:     Granularity for clock state enumeration.
        priority_clock_times:   Clock states tested first (CIA timestamps).
        max_perms_per_grid:     Cap per (grid, clock, alphabet) combo.
        keyword_eureka_threshold: Cribs required to fire Eureka (max 4).
        eureka_snapshot_path:   Breakthrough snapshot destination.
        null_artifact_path:     Null-result provenance artifact.
        progress_cb:            Optional callback(dict) fired every clock state.

    Returns:
        Summary dict. Raises EurekaSignal on keyword_eureka_threshold hit.
    """
    if subst_alphabets is None:
        subst_alphabets = KNOWN_KEYED_ALPHABETS
    if grid_sizes is None:
        grid_sizes = K4_GRID_GEOMETRIES
    if priority_clock_times is None:
        priority_clock_times = CIA_PRIORITY_TIMES

    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    clock_sequence = _build_clock_sequence(priority_clock_times, clock_step_seconds)
    ts_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    total_candidates = 0
    best_candidates: list[dict[str, Any]] = []

    total_clock = len(clock_sequence)
    logger.info(
        "P1 3-layer composite: %d clock states, %d alphabets, grids=%s, max_perms=%s",
        total_clock,
        len(subst_alphabets),
        grid_sizes,
        max_perms_per_grid,
    )

    try:
        for clock_idx, clock in enumerate(clock_sequence):
            clock_shifts = clock["shifts"]
            clock_time = clock["time"]
            is_priority = clock.get("priority", False)

            if is_priority:
                logger.info("P1: priority clock state %s (CIA timestamp)", clock_time)

            for alpha_name, alphabet in subst_alphabets.items():
                for n_cols in grid_sizes:
                    perm_gen = permutations(range(n_cols))
                    perm_count = 0

                    for perm in perm_gen:
                        if max_perms_per_grid is not None and perm_count >= max_perms_per_grid:
                            break
                        perm_count += 1

                        candidate = _decrypt_three_layer(ct, n_cols, perm, clock_shifts, alphabet)
                        total_candidates += 1

                        kw_hits = _keyword_hits(candidate)
                        if kw_hits >= keyword_eureka_threshold:
                            key_info = {
                                "alpha_name": alpha_name,
                                "n_cols": n_cols,
                                "perm": list(perm),
                                "clock_time": clock_time,
                                "clock_shifts": list(clock_shifts),
                                "attack": "P1_three_layer",
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
                                    "clock_time": clock_time,
                                }
                            )

            if progress_cb is not None:
                progress_cb(
                    {
                        "clock_idx": clock_idx + 1,
                        "total_clock": total_clock,
                        "clock_time": clock_time,
                        "is_priority": is_priority,
                        "total_candidates": total_candidates,
                        "top_candidates": sorted(
                            best_candidates,
                            key=lambda r: (-r["keyword_hits"], -r["instructional_score"]),
                        )[:5],
                    }
                )

    except EurekaSignal:
        raise

    best_candidates.sort(key=lambda r: (-r["keyword_hits"], -r["instructional_score"]))

    run_params = {
        "attack": "P1_three_layer_composite",
        "subst_alphabets": list(subst_alphabets.keys()),
        "grid_sizes": grid_sizes,
        "clock_step_seconds": clock_step_seconds,
        "clock_states_count": len(clock_sequence),
        "priority_clock_times": priority_clock_times,
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
        "null_artifact_path": str(Path(null_artifact_path).resolve()),
    }

    logger.info(
        "P1 3-layer composite complete: %d candidates checked, %d near-misses",
        total_candidates,
        len(best_candidates),
    )
    Path(null_artifact_path).write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary


__all__ = [
    "K4",
    "CIA_PRIORITY_TIMES",
    "run_three_layer_composite",
    "_mono_subst_decrypt",
    "_vigenere_decrypt_std",
    "_decrypt_three_layer",
]
