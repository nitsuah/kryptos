"""Cross-vector consensus scoring -- Frontier Phase 7.

Idea (ROADMAP.md, 2026-08-28): P16 (:mod:`kryptos.k4.corpus_miner`) already
mines recurring positional fragments from the *merged pool* of every
attack vector's null-result candidates, but it does not track which
attack vector produced a given candidate. A fragment that happens to
repeat many times within one vector's own large sweep can outweigh a
fragment that appears in several *structurally independent* vectors even
once each -- but the latter is the much stronger signal, since it would
take coincidence across unrelated cryptographic models (different
substitution/transposition assumptions entirely) rather than just
within a single model's own parameter sweep.

This module re-scans the same ``K4_*_NULL.json`` artifacts P16 uses, but
groups candidates by their *source artifact* (one artifact == one attack
vector's run) first, and only flags a positional fragment as a consensus
anchor if it appears in candidates from at least
:data:`MIN_DISTINCT_VECTORS` separate artifacts -- not just N times
overall.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from .corpus_miner import ANCHOR_WINDOW, ENGLISH_WORDS_4_PLUS, NGRAM_RANGE, _extract_candidates, _load_artifact

logger = logging.getLogger(__name__)

MIN_DISTINCT_VECTORS = 3  # a fragment must appear in candidates from >=3 separate artifacts


def score_cross_vector_consensus(
    artifact_glob: str = "K4_*_NULL.json",
    search_dir: str | None = None,
    min_distinct_vectors: int = MIN_DISTINCT_VECTORS,
) -> dict[str, Any]:
    """Scan every null-result artifact and flag fragments shared across distinct vectors.

    Args:
        artifact_glob: Glob pattern matching null-artifact files.
        search_dir: Directory to search (defaults to cwd/artifacts/../artifacts).
        min_distinct_vectors: Minimum number of separate artifacts a
            (position, n-gram) must appear in to be flagged.

    Returns:
        Analysis dict listing every (position, n-gram) found in candidates
        from >= ``min_distinct_vectors`` distinct artifacts, sorted by
        vector count then English-word status.
    """
    search_dirs = [Path(search_dir)] if search_dir else [Path("."), Path("artifacts"), Path("../artifacts")]

    artifact_files: list[Path] = []
    for d in search_dirs:
        if d.exists():
            artifact_files.extend(d.glob(artifact_glob))

    # (position, n, ngram) -> set of artifact filenames it was seen in
    ngram_vectors: dict[tuple[int, int, str], set[str]] = {}
    vector_candidate_counts: dict[str, int] = {}
    anchor_start, anchor_end = ANCHOR_WINDOW

    for fpath in artifact_files:
        artifact = _load_artifact(fpath)
        if artifact is None:
            continue
        texts = _extract_candidates(artifact)
        if not texts:
            continue
        vector_candidate_counts[fpath.name] = len(texts)

        # Per-vector dedup: a fragment repeated many times *within* one
        # vector's own sweep must still only count as ONE vector's worth
        # of evidence -- that's exactly the distinction this module adds
        # over P16's flat frequency count.
        seen_this_vector: set[tuple[int, int, str]] = set()
        for text in texts:
            for n in range(NGRAM_RANGE[0], NGRAM_RANGE[1] + 1):
                for pos in range(anchor_start, min(anchor_end, len(text) - n + 1)):
                    gram = text[pos : pos + n]
                    if gram.isalpha():
                        seen_this_vector.add((pos, n, gram))
        for key in seen_this_vector:
            ngram_vectors.setdefault(key, set()).add(fpath.name)

    if not vector_candidate_counts:
        return {
            "status": "no_candidates",
            "attack": "cross_vector_consensus",
            "artifact_files_found": len(artifact_files),
            "message": "No candidates extracted. Run attack sweeps first to generate artifacts.",
        }

    consensus_anchors: list[dict[str, Any]] = [
        {
            "position": pos,
            "ngram": gram,
            "length": n,
            "distinct_vector_count": len(vectors),
            "vectors": sorted(vectors),
            "is_english_word": gram in ENGLISH_WORDS_4_PLUS,
        }
        for (pos, n, gram), vectors in ngram_vectors.items()
        if len(vectors) >= min_distinct_vectors
    ]
    consensus_anchors.sort(key=lambda x: (-x["distinct_vector_count"], -x["is_english_word"], x["position"]))

    return {
        "status": "complete",
        "attack": "cross_vector_consensus",
        "artifacts_scanned": len(artifact_files),
        "vectors_with_candidates": len(vector_candidate_counts),
        "vector_candidate_counts": vector_candidate_counts,
        "min_distinct_vectors": min_distinct_vectors,
        "consensus_anchors_found": len(consensus_anchors),
        "consensus_anchors": consensus_anchors[:20],
    }


def run_cross_vector_consensus_attack(
    artifact_glob: str = "K4_*_NULL.json",
    null_artifact_path: str = "K4_CROSS_VECTOR_CONSENSUS_NULL.json",
) -> dict[str, Any]:
    """Run cross-vector consensus scoring and persist results."""
    result = score_cross_vector_consensus(artifact_glob=artifact_glob)
    try:
        Path(null_artifact_path).write_text(json.dumps(result, indent=2), encoding="utf-8")
    except OSError:
        logger.warning("cross_vector_consensus: failed to write %s", null_artifact_path)
    return result


__all__ = [
    "MIN_DISTINCT_VECTORS",
    "run_cross_vector_consensus_attack",
    "score_cross_vector_consensus",
]
