"""Canonical hypothesis graph for the K4 physical/geometric pivot.

A small, file-persisted graph (not a database) mirroring the research
brief's flow diagram::

    KRYPTOS_PHYSICAL_STRUCTURE -> COMPASS_LODESTONE
    KRYPTOS_PHYSICAL_STRUCTURE -> FRONT_BACK_LAYERS
    KRYPTOS_PHYSICAL_STRUCTURE -> VIGENERE_TABLEAU_REVERSE
    KRYPTOS_PHYSICAL_STRUCTURE -> K4_CIPHERTEXT
    K4_CIPHERTEXT -> EASTNORTHEAST -> DIRECTIONAL_TRAVERSAL
        -> BERLIN_WORLD_CLOCK -> COORD_SYSTEM_24 -> GRID_4X24_PLUS_1
        -> GEOMETRIC_POSITIONAL_TRANSFORM -> SUBSTITUTION_LAYER

Each edge carries a status (``untested`` / ``null`` / ``partial_null`` /
``confirmed`` / ``eureka``) and an evidence pointer (an artifact path or a
short note). ``record_result`` updates an edge; ``save``/``load`` persist the
graph as JSON (the same append/update-artifact convention used by every
other K4 attack module); ``to_mermaid``/``to_markdown_table`` render it for
inclusion in ``docs/analysis/K4_ACTIVE_RESEARCH.md``.

The graph is seeded from results this repo already has — it starts accurate,
not empty.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NODES: list[str] = [
    "KRYPTOS_PHYSICAL_STRUCTURE",
    "COMPASS_LODESTONE",
    "FRONT_BACK_LAYERS",
    "VIGENERE_TABLEAU_REVERSE",
    "K4_CIPHERTEXT",
    "EASTNORTHEAST",
    "DIRECTIONAL_TRAVERSAL",
    "BERLIN_WORLD_CLOCK",
    "COORD_SYSTEM_24",
    "GRID_4X24_PLUS_1",
    "GEOMETRIC_POSITIONAL_TRANSFORM",
    "SUBSTITUTION_LAYER",
    # Phase 2 (item 13): does a clock-derived Vigenere layer, combined with
    # the Phase 1 geometric permutation, complete a 3-layer composite?
    "CLOCK_VIGENERE_LAYER",
    "THREE_LAYER_GEOMETRIC_COMPOSITE",
]

EDGES: list[tuple[str, str]] = [
    ("KRYPTOS_PHYSICAL_STRUCTURE", "COMPASS_LODESTONE"),
    ("KRYPTOS_PHYSICAL_STRUCTURE", "FRONT_BACK_LAYERS"),
    ("KRYPTOS_PHYSICAL_STRUCTURE", "VIGENERE_TABLEAU_REVERSE"),
    ("KRYPTOS_PHYSICAL_STRUCTURE", "K4_CIPHERTEXT"),
    ("K4_CIPHERTEXT", "EASTNORTHEAST"),
    ("EASTNORTHEAST", "DIRECTIONAL_TRAVERSAL"),
    ("DIRECTIONAL_TRAVERSAL", "BERLIN_WORLD_CLOCK"),
    ("BERLIN_WORLD_CLOCK", "COORD_SYSTEM_24"),
    ("COORD_SYSTEM_24", "GRID_4X24_PLUS_1"),
    ("GRID_4X24_PLUS_1", "GEOMETRIC_POSITIONAL_TRANSFORM"),
    ("GEOMETRIC_POSITIONAL_TRANSFORM", "SUBSTITUTION_LAYER"),
    ("SUBSTITUTION_LAYER", "CLOCK_VIGENERE_LAYER"),
    ("CLOCK_VIGENERE_LAYER", "THREE_LAYER_GEOMETRIC_COMPOSITE"),
]

VALID_STATUSES = {"untested", "null", "partial_null", "confirmed", "eureka"}

# Ordering used by record_result_preserving_strongest: higher wins.
STATUS_PRIORITY: dict[str, int] = {"untested": 0, "null": 1, "partial_null": 2, "confirmed": 3, "eureka": 4}

DEFAULT_GRAPH_PATH = "K4_HYPOTHESIS_GRAPH.json"

# Seeded from results already recorded in docs/analysis/K4_ACTIVE_RESEARCH.md.
_SEED: dict[str, dict[str, str]] = {
    "K4_CIPHERTEXT->EASTNORTHEAST": {
        "status": "confirmed",
        "evidence": "Sanborn-confirmed crib; kryptos.k4.keystream_validator.K4_CRIBS",
    },
    "GEOMETRIC_POSITIONAL_TRANSFORM->SUBSTITUTION_LAYER": {
        # "null", not "partial_null": physical_grid.py reached a definitive
        # null conclusion for the identity-permutation case it tested; the
        # narrower *scope* (no permutation front-end) is a fact about what
        # was tested, not a weaker/less-confident result. "partial_null"
        # is reserved for geometry_combined_sweep's own, unrelated meaning:
        # a threshold-crossing candidate that failed strict validation (a
        # stronger signal than a clean null, ranked above it in
        # STATUS_PRIORITY). Conflating the two previously caused this seed
        # to incorrectly outrank and suppress a genuine fresh null result.
        "status": "null",
        "evidence": (
            "kryptos.k4.physical_grid.run_physical_grid_attack — tableau-keystream "
            "substitution tested null, but without a geometric permutation front-end "
            "(see geometry_combined_sweep for the combined test)"
        ),
    },
}


def _edge_key(edge: tuple[str, str]) -> str:
    return f"{edge[0]}->{edge[1]}"


def new_graph() -> dict[str, Any]:
    """Build a freshly-seeded graph (nodes, edges, per-edge status)."""
    edges: dict[str, dict[str, str]] = {}
    for edge in EDGES:
        key = _edge_key(edge)
        edges[key] = dict(_SEED.get(key, {"status": "untested", "evidence": ""}))
    return {"nodes": list(NODES), "edges": edges}


def load(path: str | Path = DEFAULT_GRAPH_PATH) -> dict[str, Any]:
    """Load a persisted graph, or seed a fresh one if the file doesn't exist."""
    p = Path(path)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return new_graph()


def save(graph: dict[str, Any], path: str | Path = DEFAULT_GRAPH_PATH) -> str:
    """Write the graph to disk as JSON. Returns the resolved path as a string."""
    out_path = Path(path)
    out_path.write_text(json.dumps(graph, indent=2, sort_keys=True), encoding="utf-8")
    return str(out_path.resolve())


def record_result(
    graph: dict[str, Any],
    edge: tuple[str, str],
    status: str,
    evidence: str = "",
) -> dict[str, Any]:
    """Update one edge's status/evidence in place. Returns the graph."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Unknown status: {status!r} (expected one of {sorted(VALID_STATUSES)})")
    key = _edge_key(edge)
    if key not in graph["edges"]:
        raise KeyError(f"Unknown edge: {edge!r}")
    graph["edges"][key] = {
        "status": status,
        "evidence": evidence,
        "updated": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    return graph


def record_result_preserving_strongest(
    graph: dict[str, Any],
    edge: tuple[str, str],
    status: str,
    evidence: str = "",
) -> dict[str, Any]:
    """Like record_result, but never downgrades an edge to a weaker status.

    Guards against a later, narrower-scope null run silently erasing an
    earlier genuine eureka/confirmed finding recorded on the same shared
    edge (status priority: untested < null < partial_null < confirmed <
    eureka). A same-or-stronger status still updates evidence/timestamp
    normally.
    """
    if status not in VALID_STATUSES:
        raise ValueError(f"Unknown status: {status!r} (expected one of {sorted(VALID_STATUSES)})")
    key = _edge_key(edge)
    if key not in graph["edges"]:
        raise KeyError(f"Unknown edge: {edge!r}")
    current_status = graph["edges"][key]["status"]
    if STATUS_PRIORITY[status] < STATUS_PRIORITY[current_status]:
        return graph
    return record_result(graph, edge, status, evidence)


def to_mermaid(graph: dict[str, Any]) -> str:
    """Render the graph as a Mermaid flowchart, styled by edge status."""
    status_arrow = {
        "untested": "-.->",
        "null": "-- null -->",
        "partial_null": "-- partial null -->",
        "confirmed": "==>",
        "eureka": "== EUREKA ==>",
    }
    lines = ["flowchart TD"]
    for src, dst in EDGES:
        info = graph["edges"][_edge_key((src, dst))]
        arrow = status_arrow.get(info["status"], "-->")
        lines.append(f"    {src} {arrow} {dst}")
    return "\n".join(lines)


def to_markdown_table(graph: dict[str, Any]) -> str:
    """Render the graph's edges as a Markdown table."""
    rows = [
        "| Edge | Status | Evidence |",
        "|------|--------|----------|",
    ]
    for src, dst in EDGES:
        info = graph["edges"][_edge_key((src, dst))]
        rows.append(f"| `{src}` -> `{dst}` | {info['status']} | {info.get('evidence', '')} |")
    return "\n".join(rows)


__all__ = [
    "DEFAULT_GRAPH_PATH",
    "EDGES",
    "NODES",
    "STATUS_PRIORITY",
    "VALID_STATUSES",
    "load",
    "new_graph",
    "record_result",
    "record_result_preserving_strongest",
    "save",
    "to_markdown_table",
    "to_mermaid",
]
