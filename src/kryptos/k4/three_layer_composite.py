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
from .eureka import EurekaSignal, write_breakthrough_snapshot
from .geometry24 import CORE_LEN, apply_inverse
from .geometry_combined_sweep import (
    DEFAULT_OFFSETS,
    DEFAULT_ORDER_NAMES,
    DEFAULT_REFLECTIONS,
    DEFAULT_REMAINDER_MODES,
    composed_flat_indices,
)
from .hypothesis_graph import DEFAULT_GRAPH_PATH
from .hypothesis_graph import load as load_graph
from .hypothesis_graph import record_result_preserving_strongest
from .hypothesis_graph import save as save_graph
from .inverse_transposition_sweep import K4_GRID_GEOMETRIES
from .physical_grid import K4
from .quagmire_sweep import positional_crib_hits
from .scoring_instructional import combined_instructional_score
from .transposition_analysis import apply_columnar_permutation_reverse
from .validation import validate_candidate
from .vigenere_key_recovery import KNOWN_KEYED_ALPHABETS

logger = logging.getLogger(__name__)
STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_NULL_ARTIFACT_PATH = "K4_3LAYER_NULL.json"
_EUREKA_WORDS: frozenset[str] = frozenset({"EAST", "NORTHEAST", "BERLIN", "CLOCK"})

# CIA dedication timestamp clock states (tested before the full sweep).
CIA_PRIORITY_TIMES = ["13:00:00", "19:00:00"]

# Fall of the Berlin Wall, Nov 9 1989 — the event docs/sources/CLOCK.md cites
# as most influential on Sanborn's design, but never previously tested as a
# clock state. Three sourced Berlin-local (CET) moments from that evening
# (Schabowski's key statement — including his "sofort, unverzüglich"
# ["as of now, immediately"] answer, both at 18:53; the AP flash reporting
# the border opening; and ARD's lead broadcast — see
# docs/analysis/K4_ACTIVE_RESEARCH.md for citations), plus their EST
# equivalents (-6h), mirroring how CIA_PRIORITY_TIMES tests both timezone
# framings of the same event rather than arbitrarily picking one.
BERLIN_WALL_PRIORITY_TIMES = [
    "18:53:00",  # Schabowski's statement + "as of now, immediately!" answer (Berlin/CET)
    "19:05:00",  # AP flash report: border opening (Berlin/CET)
    "20:00:00",  # ARD lead broadcast (Berlin/CET)
    "12:53:00",  # same moments, CIA/EST (-6h)
    "13:05:00",
    "14:00:00",
]


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
    rest = [
        {"time": e["time"], "shifts": e["shifts"], "priority": False} for e in full if e["time"] not in priority_set
    ]
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


_GEOMETRIC_TRANSFORM_EDGE = ("SUBSTITUTION_LAYER", "CLOCK_VIGENERE_LAYER")
_GEOMETRIC_COMPOSITE_EDGE = ("CLOCK_VIGENERE_LAYER", "THREE_LAYER_GEOMETRIC_COMPOSITE")


def _decrypt_three_layer_geometric(
    ciphertext: str,
    order_name: str,
    reflection_name: str,
    rotation_offset: int,
    remainder_mode: str,
    clock_shifts: list[int],
    subst_alphabet: str,
) -> str:
    """Invert geometric permutation -> clock-Vigenere -> mono-subst, in that order.

    Reuses this module's own ``_vigenere_decrypt_std``/``_mono_subst_decrypt``
    for the two classical layers, and Phase 1's
    :func:`kryptos.k4.geometry_combined_sweep.composed_flat_indices` +
    :func:`kryptos.k4.geometry24.apply_inverse` for the transposition layer
    — the 24-column named geometric permutation, not the brute-force
    arbitrary column permutation :func:`_decrypt_three_layer` uses.
    """
    flat_idx = composed_flat_indices(order_name, reflection_name, rotation_offset, remainder_mode)
    ct_source = ciphertext if remainder_mode != "drop" else ciphertext[:CORE_LEN]
    step1 = apply_inverse(ct_source, flat_idx)
    step2 = _vigenere_decrypt_std(step1, clock_shifts)
    return _mono_subst_decrypt(step2, subst_alphabet)


def run_three_layer_composite_geometric(
    ciphertext: str = K4,
    subst_alphabets: dict[str, str] | None = None,
    order_names: list[str] | None = None,
    reflection_names: list[str] | None = None,
    rotation_offsets: list[int] | None = None,
    remainder_modes: list[str] | None = None,
    priority_clock_times: list[str] | None = None,
    clock_step_seconds: int = 3600,
    full_clock_sweep: bool = False,
    positional_eureka_threshold: int = 3,
    keyword_eureka_threshold: int = 4,
    eureka_snapshot_path: str | Path = "K4_3LAYER_GEOMETRIC_BREAKTHROUGH.md",
    null_artifact_path: str | Path = "K4_3LAYER_GEOMETRIC_NULL.json",
    graph_path: str | Path = DEFAULT_GRAPH_PATH,
) -> dict[str, Any]:
    """Item 13 — mono-subst(keyed) -> clock-Vigenere -> Phase-1 geometric permutation.

    A sibling of :func:`run_three_layer_composite` that swaps the brute-force
    arbitrary columnar transposition (grid widths ``[7, 8, 10]``) for Phase
    1's named 24-column geometric permutations (fill order/route +
    reflection + rotation) — a distinct search space (24 was never a tested
    grid width in the original P1 sweep).

    Default scope is bounded (2 priority CIA-timestamp clock states x 4
    keyed alphabets x 720 geometric-permutation combos ~= 5,760 candidates);
    pass ``full_clock_sweep=True`` for the full hourly clock sweep too,
    matching how ``run_three_layer_composite`` itself scopes its own
    default run.

    Like :mod:`kryptos.k4.geometry_combined_sweep`, only a candidate that
    passes :func:`kryptos.k4.validation.validate_candidate`'s ``promote``
    gate (all 4 cribs + independent reproduction) raises EurekaSignal; a
    threshold-level partial match is recorded but does not halt the sweep.
    Uses ``record_result_preserving_strongest`` so this run can never
    downgrade an earlier genuine finding on the shared graph edges.
    """
    if subst_alphabets is None:
        subst_alphabets = KNOWN_KEYED_ALPHABETS
    if order_names is None:
        order_names = DEFAULT_ORDER_NAMES
    if reflection_names is None:
        reflection_names = DEFAULT_REFLECTIONS
    if rotation_offsets is None:
        rotation_offsets = DEFAULT_OFFSETS
    if remainder_modes is None:
        remainder_modes = DEFAULT_REMAINDER_MODES
    if priority_clock_times is None:
        priority_clock_times = CIA_PRIORITY_TIMES

    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    all_clock_states = _build_clock_sequence(priority_clock_times, clock_step_seconds)
    clock_sequence = all_clock_states if full_clock_sweep else all_clock_states[: len(priority_clock_times)]
    ts_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    total_tested = 0
    best_candidates: list[dict[str, Any]] = []

    def _reproduce(key_info: dict[str, Any], _ct: str = ct) -> str:
        return _decrypt_three_layer_geometric(
            _ct,
            key_info["order"],
            key_info["reflection"],
            key_info["rotation_offset"],
            key_info["remainder_mode"],
            key_info["clock_shifts"],
            subst_alphabets[key_info["alpha_name"]],
        )

    for clock in clock_sequence:
        clock_shifts = clock["shifts"]
        clock_time = clock["time"]
        for alpha_name, alphabet in subst_alphabets.items():
            for order_name in order_names:
                for reflection_name in reflection_names:
                    for offset in rotation_offsets:
                        for remainder_mode in remainder_modes:
                            flat_idx = composed_flat_indices(order_name, reflection_name, offset, remainder_mode)
                            ct_source = ct if remainder_mode != "drop" else ct[:CORE_LEN]
                            if len(ct_source) != len(flat_idx):
                                continue
                            step1 = apply_inverse(ct_source, flat_idx)
                            step2 = _vigenere_decrypt_std(step1, clock_shifts)
                            candidate = _mono_subst_decrypt(step2, alphabet)
                            total_tested += 1

                            pos_hits = positional_crib_hits(candidate)
                            kw_hits = _keyword_hits(candidate)

                            if pos_hits >= positional_eureka_threshold or kw_hits >= keyword_eureka_threshold:
                                key_info = {
                                    "attack": "three_layer_composite_geometric",
                                    "alpha_name": alpha_name,
                                    "order": order_name,
                                    "reflection": reflection_name,
                                    "rotation_offset": offset,
                                    "remainder_mode": remainder_mode,
                                    "clock_time": clock_time,
                                    "clock_shifts": list(clock_shifts),
                                }
                                check = validate_candidate(candidate, key_info, _reproduce, param_count=5, exceptions=0)

                                graph = load_graph(graph_path)
                                status = "eureka" if check["promote"] else "partial_null"
                                evidence = (
                                    f"three_layer_composite_geometric candidate "
                                    f"(crib_hits={pos_hits}, reproduced={check['reproduced']})"
                                )
                                record_result_preserving_strongest(graph, _GEOMETRIC_TRANSFORM_EDGE, status, evidence)
                                record_result_preserving_strongest(graph, _GEOMETRIC_COMPOSITE_EDGE, status, evidence)
                                save_graph(graph, graph_path)

                                if check["promote"]:
                                    snap = write_breakthrough_snapshot(
                                        candidate,
                                        key_info,
                                        extra={
                                            "positional_crib_hits": pos_hits,
                                            "keyword_hits": kw_hits,
                                            "validation": check,
                                            "sweep_ts": ts_start,
                                        },
                                        path=eureka_snapshot_path,
                                    )
                                    raise EurekaSignal(
                                        snapshot_path=snap,
                                        result={
                                            "candidate_text": candidate,
                                            "key_info": key_info,
                                            "snapshot_path": snap,
                                            "positional_crib_hits": pos_hits,
                                            "keyword_hits": kw_hits,
                                            "validation": check,
                                        },
                                    )

                            if pos_hits > 0 or kw_hits > 0:
                                best_candidates.append(
                                    {
                                        "candidate_text": candidate,
                                        "positional_crib_hits": pos_hits,
                                        "keyword_hits": kw_hits,
                                        "alpha_name": alpha_name,
                                        "order": order_name,
                                        "reflection": reflection_name,
                                        "rotation_offset": offset,
                                        "remainder_mode": remainder_mode,
                                        "clock_time": clock_time,
                                    }
                                )

    best_candidates.sort(key=lambda r: (-r["positional_crib_hits"], -r["keyword_hits"]))

    summary: dict[str, Any] = {
        "status": "null_result",
        "attack": "three_layer_composite_geometric",
        "timestamp": ts_start,
        "run_params": {
            "subst_alphabets": list(subst_alphabets.keys()),
            "order_names": order_names,
            "reflection_names": reflection_names,
            "rotation_offsets": rotation_offsets,
            "remainder_modes": remainder_modes,
            "clock_states_tested": [c["time"] for c in clock_sequence],
            "full_clock_sweep": full_clock_sweep,
            "total_tested": total_tested,
            "positional_eureka_threshold": positional_eureka_threshold,
            "keyword_eureka_threshold": keyword_eureka_threshold,
            "ts_start": ts_start,
        },
        "best_candidates": best_candidates[:10],
        "null_artifact_path": str(Path(null_artifact_path).resolve()),
    }
    Path(null_artifact_path).write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    graph = load_graph(graph_path)
    record_result_preserving_strongest(
        graph, _GEOMETRIC_TRANSFORM_EDGE, "null", str(Path(null_artifact_path).resolve())
    )
    record_result_preserving_strongest(
        graph, _GEOMETRIC_COMPOSITE_EDGE, "null", str(Path(null_artifact_path).resolve())
    )
    save_graph(graph, graph_path)

    return summary


__all__ = [
    "BERLIN_WALL_PRIORITY_TIMES",
    "CIA_PRIORITY_TIMES",
    "K4",
    "_decrypt_three_layer",
    "_decrypt_three_layer_geometric",
    "_mono_subst_decrypt",
    "_vigenere_decrypt_std",
    "run_three_layer_composite",
    "run_three_layer_composite_geometric",
]
