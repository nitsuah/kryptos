"""Combined geometry attack for K4 — the physical/geometric pivot's integration point.

Chains every primitive built for this pivot into one pipeline, matching the
research brief's "Combined Geometry Attack" section exactly::

    K4 -> 24-col grid -> fill order (or ENE/NE route) -> reflection
       -> clock/Berlin-Langley column rotation
       -> composed 97-length permutation (encrypt-direction gather)
       -> apply_inverse (attack-direction scatter) on the real K4 ciphertext
       -> physical tableau keystream (reused from physical_grid, not reimplemented)
       -> Quagmire III decrypt (reused from quagmire, not reimplemented)
       -> positional_crib_hits / keyword_hits gate
       -> EurekaSignal on threshold, else accumulate into best_candidates

This is the permutation front-end that ``physical_grid.py`` never had: that
module already showed varying only the *keystream* against the untouched
K4 ordering is a null result. This module additionally varies the
*ciphertext ordering itself* before the same tableau substitution step.

Every candidate that crosses the eureka threshold is also run through
:mod:`kryptos.k4.validation` (independent reproduction + overfitting-guard
score) and recorded into the canonical hypothesis graph
(:mod:`kryptos.k4.hypothesis_graph`); a null result updates the graph too.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from typing import Any

from . import clock_rotation, ene_routes, geometry24, hypothesis_graph, reflection, validation
from .eureka import DEFAULT_SNAPSHOT_PATH, EurekaSignal, write_breakthrough_snapshot
from .physical_grid import K4, candidate_keystreams
from .quagmire import quagmire3_decrypt
from .quagmire_sweep import _keyword_hits, positional_crib_hits

DEFAULT_ORDER_NAMES: list[str] = [*geometry24.ORDER_NAMES, *(f"route_{d}" for d in ene_routes.PRIORITY_DIRECTIONS)]
DEFAULT_REFLECTIONS: list[str] = reflection.SHAPE_PRESERVING
DEFAULT_OFFSETS: list[int] = clock_rotation.PRIORITY_OFFSETS
DEFAULT_REMAINDER_MODES: list[str] = list(geometry24.REMAINDER_MODES)

_TRANSFORM_EDGE = ("GEOMETRIC_POSITIONAL_TRANSFORM", "SUBSTITUTION_LAYER")


def _order_coords(order_name: str) -> geometry24.Coords:
    if order_name.startswith("route_"):
        direction = order_name[len("route_") :]
        return ene_routes.route_order(direction)
    return geometry24.order_coords(order_name)


def composed_flat_indices(
    order_name: str,
    reflection_name: str,
    rotation_offset: int,
    remainder_mode: str,
) -> list[int]:
    """Compose fill-order/route -> reflection -> column rotation into flat source indices."""
    coords = _order_coords(order_name)
    reflect_fn = reflection.TRANSFORMS[reflection_name]
    coords = [reflect_fn(r, c) for (r, c) in coords]
    coords = [(r, clock_rotation.rotated_column(c, rotation_offset)) for (r, c) in coords]
    return geometry24.coords_to_flat(coords, remainder_mode)


def _reproduce_candidate(key_info: dict[str, Any], ciphertext: str) -> str:
    """Independently re-derive a candidate from its key_info (used by validation)."""
    flat_idx = composed_flat_indices(
        key_info["order"], key_info["reflection"], key_info["rotation_offset"], key_info["remainder_mode"]
    )
    ct_source = ciphertext if key_info["remainder_mode"] != "drop" else ciphertext[: geometry24.CORE_LEN]
    permuted_ct = geometry24.apply_inverse(ct_source, flat_idx)
    keystream = candidate_keystreams(key_info["alphabet_keyword"])[key_info["tableau_route"]]
    return quagmire3_decrypt(permuted_ct, keystream, key_info["alphabet_keyword"], key_info["indicator_base"])


def run_geometry_combined_sweep(
    ciphertext: str = K4,
    order_names: list[str] | None = None,
    reflection_names: list[str] | None = None,
    rotation_offsets: list[int] | None = None,
    remainder_modes: list[str] | None = None,
    alphabet_keyword: str = "KRYPTOS",
    eureka_snapshot_path: str | Path = DEFAULT_SNAPSHOT_PATH,
    null_artifact_path: str | Path = "K4_GEOMETRY_COMBINED_NULL.json",
    graph_path: str | Path = hypothesis_graph.DEFAULT_GRAPH_PATH,
    positional_eureka_threshold: int = 3,
    keyword_eureka_threshold: int = 4,
) -> dict[str, Any]:
    """Run the combined geometric-permutation + tableau-keystream sweep against K4.

    Returns a summary dict (status, run_params, best_candidates) and always
    writes it to ``null_artifact_path``. Raises EurekaSignal on a crib
    breakthrough (matching every other attack module's convention).
    """
    order_names = order_names if order_names is not None else DEFAULT_ORDER_NAMES
    reflection_names = reflection_names if reflection_names is not None else DEFAULT_REFLECTIONS
    rotation_offsets = rotation_offsets if rotation_offsets is not None else DEFAULT_OFFSETS
    remainder_modes = remainder_modes if remainder_modes is not None else DEFAULT_REMAINDER_MODES

    ts_start = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    tableau_streams = candidate_keystreams(alphabet_keyword)

    total_tested = 0
    best_candidates: list[dict[str, Any]] = []

    for order_name in order_names:
        for reflection_name in reflection_names:
            for offset in rotation_offsets:
                for remainder_mode in remainder_modes:
                    flat_idx = composed_flat_indices(order_name, reflection_name, offset, remainder_mode)
                    ct_source = ciphertext if remainder_mode != "drop" else ciphertext[: geometry24.CORE_LEN]
                    if len(ct_source) != len(flat_idx):
                        continue
                    permuted_ct = geometry24.apply_inverse(ct_source, flat_idx)

                    for route, keystream in tableau_streams.items():
                        for base in (None, "A"):
                            total_tested += 1
                            candidate = quagmire3_decrypt(permuted_ct, keystream, alphabet_keyword, base)
                            pos_hits = positional_crib_hits(candidate)
                            kw_hits = _keyword_hits(candidate)

                            if pos_hits >= positional_eureka_threshold or kw_hits >= keyword_eureka_threshold:
                                key_info = {
                                    "attack": "geometry_combined_sweep",
                                    "order": order_name,
                                    "reflection": reflection_name,
                                    "rotation_offset": offset,
                                    "remainder_mode": remainder_mode,
                                    "tableau_route": route,
                                    "alphabet_keyword": alphabet_keyword,
                                    "indicator_base": base,
                                }
                                check = validation.validate_candidate(
                                    candidate,
                                    key_info,
                                    partial(_reproduce_candidate, ciphertext=ciphertext),
                                    param_count=4,  # order, reflection, rotation_offset, tableau_route
                                    exceptions=0,
                                )

                                graph = hypothesis_graph.load(graph_path)
                                evidence = (
                                    f"geometry_combined_sweep candidate "
                                    f"(crib_hits={pos_hits}, reproduced={check['reproduced']})"
                                )
                                hypothesis_graph.record_result(
                                    graph,
                                    _TRANSFORM_EDGE,
                                    "eureka" if check["promote"] else "partial_null",
                                    evidence=evidence,
                                )
                                hypothesis_graph.save(graph, graph_path)

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
                                        "reflection": reflection_name,
                                        "rotation_offset": offset,
                                        "remainder_mode": remainder_mode,
                                        "tableau_route": route,
                                        "indicator_base": base,
                                    }
                                )

    best_candidates.sort(key=lambda r: (-r["positional_crib_hits"], -r["keyword_hits"]))

    summary: dict[str, Any] = {
        "status": "null_result",
        "attack": "geometry_combined_sweep",
        "timestamp": ts_start,
        "run_params": {
            "alphabet_keyword": alphabet_keyword,
            "order_names": order_names,
            "reflection_names": reflection_names,
            "rotation_offsets": rotation_offsets,
            "remainder_modes": remainder_modes,
            "tableau_routes": list(tableau_streams.keys()),
            "total_tested": total_tested,
            "positional_eureka_threshold": positional_eureka_threshold,
            "keyword_eureka_threshold": keyword_eureka_threshold,
            "ts_start": ts_start,
        },
        "best_candidates": best_candidates[:10],
        "null_artifact_path": str(Path(null_artifact_path).resolve()),
    }
    Path(null_artifact_path).write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")

    graph = hypothesis_graph.load(graph_path)
    hypothesis_graph.record_result(graph, _TRANSFORM_EDGE, "null", evidence=str(Path(null_artifact_path).resolve()))
    hypothesis_graph.save(graph, graph_path)

    return summary


__all__ = [
    "DEFAULT_OFFSETS",
    "DEFAULT_ORDER_NAMES",
    "DEFAULT_REFLECTIONS",
    "DEFAULT_REMAINDER_MODES",
    "composed_flat_indices",
    "run_geometry_combined_sweep",
]
