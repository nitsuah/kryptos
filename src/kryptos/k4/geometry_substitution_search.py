"""Simulated-annealing substitution-key search over the Phase-1 geometric
permutation front-end — P15 (optional / lower priority).

The existing heuristic-search infrastructure covers two narrow key spaces:
:mod:`kryptos.k4.hill_genetic` (a genetic algorithm over Hill 3x3 matrices)
and :mod:`kryptos.k4.transposition_analysis` (SA/GA over columnar
*transposition permutations*). Neither searches the general monoalphabetic
substitution key space (26! possible keys) heuristically, and every
composite sweep that already pairs a geometric-permutation front-end with a
substitution layer (:mod:`kryptos.k4.geometry_combined_sweep`,
:func:`kryptos.k4.three_layer_composite.run_three_layer_composite_geometric`)
only ever tries a handful of *named* keyed alphabets (KRYPTOS, PALIMPSEST,
ABSCISSA, Berlin-Clock-derived indicators, ...) for that layer — never a
heuristic search over the full substitution key space. That is the genuine,
non-redundant gap this module fills.

:mod:`kryptos.k4.substitution_solver` already implements a plain
restart-based hill-climb over substitution mappings, but it is a bare
utility — never composed with a transposition-inversion front end, and
"accept only strict improvement" hill-climbing (unlike a temperature-based
SA) gets stuck in local optima more easily. This module instead runs a
proper simulated annealing search (same accept-worse-with-decreasing-
probability structure as
:func:`kryptos.k4.transposition_analysis.solve_columnar_permutation_simulated_annealing`,
just over a 26-letter substitution alphabet instead of a column
permutation) on the text obtained after inverting one of Phase 1's named
24-column geometric permutations.

Scope is deliberately bounded: the fill-order x reflection x rotation x
remainder-mode *permutation*-parameter combinatorics are already
exhaustively covered by :mod:`kryptos.k4.geometry_combined_sweep`,
so this module only varies the geometry24 base fill order (identity
reflection, zero rotation, trailing remainder) and lets the expensive,
stochastic part of the search — the substitution layer — do the actual
heuristic work.

Every candidate that crosses the eureka threshold is run through
:func:`kryptos.k4.validation.validate_candidate`; only a ``promote``-passing
candidate raises :class:`~kryptos.k4.eureka.EurekaSignal`. The winning
substitution alphabet is captured verbatim in ``key_info``, so independent
reproduction re-applies that *exact fixed* mapping deterministically — it
never re-runs the stochastic search itself (which would not be
reproducible run to run).
"""

from __future__ import annotations

import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import geometry24
from .eureka import EurekaSignal, write_breakthrough_snapshot
from .quagmire_sweep import _keyword_hits, positional_crib_hits
from .scoring import combined_plaintext_score
from .validation import validate_candidate

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

_NULL_ARTIFACT_PATH = "K4_GEOMETRY_SUBSTITUTION_SA_NULL.json"

# Bounded, curated scope: the 8 base geometry24 fill orders (not the
# reversed variants — the permutation-parameter space is already
# exhaustively covered elsewhere), identity reflection, zero rotation,
# trailing remainder mode. See module docstring for why this stays narrow.
DEFAULT_ORDER_NAMES: list[str] = list(geometry24.BASE_ORDERS)
DEFAULT_REMAINDER_MODE = "trailing"


def _mono_subst_decrypt(text: str, alphabet: str) -> str:
    """Undo a monoalphabetic substitution that encrypted standard->alphabet.

    Same convention as
    :func:`kryptos.k4.three_layer_composite._mono_subst_decrypt`: ``alphabet``
    is a 26-letter permutation of :data:`STANDARD`, and ``alphabet[i]`` is
    the ciphertext letter standing in for ``STANDARD[i]``.
    """
    out: list[str] = []
    for c in text.upper():
        if c.isalpha() and c in alphabet:
            out.append(STANDARD[alphabet.index(c)])
        else:
            out.append(c)
    return "".join(out)


def simulated_annealing_substitution_search(
    ciphertext: str,
    max_iterations: int = 3000,
    initial_temp: float = 15.0,
    cooling_rate: float = 0.999,
    rng: random.Random | None = None,
    seed_alphabet: str | None = None,
) -> tuple[str, float]:
    """SA search over the 26-letter monoalphabetic substitution key space.

    Mirrors
    :func:`kryptos.k4.transposition_analysis.solve_columnar_permutation_simulated_annealing`'s
    structure (temperature/cooling schedule, random-swap neighbor moves,
    Metropolis-criterion acceptance of worse moves) with the search variable
    swapped from a column permutation to a substitution alphabet.

    Returns ``(best_alphabet, best_score)``.
    """
    rng_obj = rng if rng is not None else random.Random()
    text = "".join(c for c in ciphertext.upper() if c.isalpha())

    if seed_alphabet is not None:
        if sorted(seed_alphabet.upper()) != list(STANDARD):
            raise ValueError("seed_alphabet must be a permutation of the standard alphabet")
        current = list(seed_alphabet.upper())
    else:
        current = list(STANDARD)
        rng_obj.shuffle(current)

    current_score = combined_plaintext_score(_mono_subst_decrypt(text, "".join(current)))

    best = current[:]
    best_score = current_score

    temperature = initial_temp
    for _ in range(max_iterations):
        neighbor = current[:]
        i, j = rng_obj.sample(range(26), 2)
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]

        neighbor_score = combined_plaintext_score(_mono_subst_decrypt(text, "".join(neighbor)))
        delta = neighbor_score - current_score

        if delta > 0:
            current = neighbor
            current_score = neighbor_score
            if current_score > best_score:
                best = current[:]
                best_score = current_score
        else:
            acceptance_prob = math.exp(delta / temperature) if temperature > 0 else 0
            if rng_obj.random() < acceptance_prob:
                current = neighbor
                current_score = neighbor_score

        temperature *= cooling_rate
        if temperature < 0.01:
            break

    return "".join(best), best_score


def run_geometry_substitution_sa_sweep(
    ciphertext: str = K4,
    order_names: list[str] | None = None,
    remainder_mode: str = DEFAULT_REMAINDER_MODE,
    num_restarts: int = 3,
    max_iterations: int = 3000,
    rng_seed: int = 42,
    seed_alphabet: str | None = None,
    positional_eureka_threshold: int = 3,
    keyword_eureka_threshold: int = 4,
    eureka_snapshot_path: str | Path = "K4_GEOMETRY_SUBSTITUTION_SA_BREAKTHROUGH.md",
    null_artifact_path: str | Path = _NULL_ARTIFACT_PATH,
) -> dict[str, Any]:
    """P15 — SA substitution search behind a Phase-1 geometric permutation front-end.

    For each ``order_name``, inverts that geometry24 fill order on K4 (zero
    rotation, identity reflection, ``remainder_mode``), then runs
    :func:`simulated_annealing_substitution_search` (``num_restarts`` times,
    seeded from a single :class:`random.Random` for reproducibility) on the
    resulting text. Every restart's best candidate is gated the same way as
    every other module in this family: a candidate crossing the eureka
    threshold is passed to :func:`kryptos.k4.validation.validate_candidate`;
    only a ``promote``-passing candidate raises
    :class:`~kryptos.k4.eureka.EurekaSignal`. A null-result artifact is
    always written.

    ``seed_alphabet``, if given, seeds only the very first restart of the
    very first order tested (mirrors the ``seed_perm``-for-first-restart
    convention in
    :func:`kryptos.k4.transposition_analysis.solve_columnar_permutation_simulated_annealing_multi_start`)
    — mainly useful for deterministically exercising the eureka path in
    tests, since the search is otherwise stochastic.
    """
    if order_names is None:
        order_names = DEFAULT_ORDER_NAMES

    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    ts_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    rng = random.Random(rng_seed)

    total_tested = 0
    best_candidates: list[dict[str, Any]] = []

    def _reproduce(key_info: dict[str, Any], _ct: str = ct) -> str:
        flat_idx = geometry24.flat_indices_for_order(key_info["order"], key_info["remainder_mode"])
        ct_source = _ct if key_info["remainder_mode"] != "drop" else _ct[: geometry24.CORE_LEN]
        permuted = geometry24.apply_inverse(ct_source, flat_idx)
        return _mono_subst_decrypt(permuted, key_info["alphabet"])

    for order_idx, order_name in enumerate(order_names):
        flat_idx = geometry24.flat_indices_for_order(order_name, remainder_mode)
        ct_source = ct if remainder_mode != "drop" else ct[: geometry24.CORE_LEN]
        if len(ct_source) != len(flat_idx):
            continue
        permuted = geometry24.apply_inverse(ct_source, flat_idx)

        for restart in range(num_restarts):
            use_seed = seed_alphabet if (order_idx == 0 and restart == 0) else None
            alphabet, _sa_score = simulated_annealing_substitution_search(
                permuted, max_iterations=max_iterations, rng=rng, seed_alphabet=use_seed
            )
            candidate = _mono_subst_decrypt(permuted, alphabet)
            total_tested += 1

            pos_hits = positional_crib_hits(candidate)
            kw_hits = _keyword_hits(candidate)

            if pos_hits >= positional_eureka_threshold or kw_hits >= keyword_eureka_threshold:
                key_info = {
                    "attack": "geometry_substitution_sa",
                    "order": order_name,
                    "remainder_mode": remainder_mode,
                    "alphabet": alphabet,
                    "restart": restart,
                }
                # param_count is deliberately high: a 26-letter permutation
                # found by unconstrained search is exactly the kind of
                # high-degree-of-freedom mechanism the overfitting guard
                # exists to penalize relative to a small-parameter match.
                check = validate_candidate(candidate, key_info, _reproduce, param_count=27, exceptions=0)

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
                        "order": order_name,
                        "restart": restart,
                        "alphabet": alphabet,
                    }
                )

    best_candidates.sort(key=lambda r: (-r["positional_crib_hits"], -r["keyword_hits"]))

    summary: dict[str, Any] = {
        "status": "null_result",
        "attack": "P15_geometry_substitution_sa",
        "timestamp": ts_start,
        "run_params": {
            "order_names": order_names,
            "remainder_mode": remainder_mode,
            "num_restarts": num_restarts,
            "max_iterations": max_iterations,
            "rng_seed": rng_seed,
            "total_tested": total_tested,
            "positional_eureka_threshold": positional_eureka_threshold,
            "keyword_eureka_threshold": keyword_eureka_threshold,
            "ts_start": ts_start,
        },
        "best_candidates": best_candidates[:10],
        "null_artifact_path": str(Path(null_artifact_path).resolve()),
    }
    Path(null_artifact_path).write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary


__all__ = [
    "K4",
    "DEFAULT_ORDER_NAMES",
    "DEFAULT_REMAINDER_MODE",
    "simulated_annealing_substitution_search",
    "run_geometry_substitution_sa_sweep",
]
