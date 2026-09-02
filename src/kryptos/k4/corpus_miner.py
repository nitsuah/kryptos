"""P16 — Candidate corpus fragment mining from null-result artifacts.

Every P1-P7 sweep writes *_NULL.json artifacts. This module loads them all,
extracts best_candidates[].candidate_text, and runs a sliding-window n-gram
frequency analysis over positions 0-21 (before the EAST crib at position 21;
see keystream_validator.K4_CRIBS's 2026-09-02 fix note -- this module's own
ANCHOR_WINDOW already used the correct boundary, only this docstring was off
by one).

Any English fragment appearing in >3% of candidates at a consistent position
across multiple attack types is treated as a partial-plaintext anchor.
"""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

NGRAM_RANGE = (4, 6)  # n-gram sizes to analyze
ANCHOR_WINDOW = (0, 21)  # positions to analyze (before EAST crib)
MIN_FREQUENCY_PCT = 3.0  # minimum % of candidates to flag as anchor

ENGLISH_WORDS_4_PLUS = frozenset(
    {
        "EAST",
        "WEST",
        "NORTH",
        "SOUTH",
        "NORT",
        "SOUT",
        "LOOK",
        "FIND",
        "SEEK",
        "TURN",
        "WALK",
        "MOVE",
        "STEP",
        "FEET",
        "YARD",
        "MILE",
        "INCH",
        "METER",
        "DEEP",
        "CLUE",
        "CODE",
        "HINT",
        "SIGN",
        "MARK",
        "DARK",
        "LIGHT",
        "SHADOW",
        "BELOW",
        "ABOVE",
        "UNDER",
        "GOLD",
        "STONE",
        "ROCK",
        "SAND",
        "DUST",
        "DIRT",
        "DOOR",
        "GATE",
        "WALL",
        "ROOM",
        "HALL",
        "ARCH",
        "TIME",
        "DATE",
        "YEAR",
        "HOUR",
        "NOON",
        "DAWN",
        "LAND",
        "AREA",
        "ZONE",
        "SITE",
        "SPOT",
        "NEAR",
        "JUST",
        "THEN",
        "FROM",
        "INTO",
        "WITH",
        "THAT",
        "THIS",
        "THEY",
        "HAVE",
        "BEEN",
        "WERE",
        "WHEN",
        "WHERE",
        "WHAT",
        "HERE",
        "THERE",
        "BETWEEN",
        "BURIED",
        "HIDDEN",
        "LOCATED",
        "FOUND",
        "IQLUSION",
        "DIGETAL",
        "SANBORN",
        "LANGLEY",
    }
)


def _load_artifact(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except Exception:  # noqa: BLE001
        return None


def _extract_candidates(artifact: dict[str, Any]) -> list[str]:
    texts: list[str] = []
    for key in ("best_candidates", "top_candidates", "candidates"):
        items = artifact.get(key, [])
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    text = item.get("candidate_text") or item.get("text") or item.get("plaintext", "")
                    if text and isinstance(text, str) and len(text) >= 22:
                        texts.append(text.upper())
    return texts


def mine_candidate_corpus(
    artifact_glob: str = "K4_*_NULL.json",
    search_dir: str | None = None,
) -> dict[str, Any]:
    """Load all null-result artifacts and mine for recurring positional fragments.

    Args:
        artifact_glob: Glob pattern matching null-artifact files.
        search_dir: Directory to search (defaults to cwd and common artifact paths).

    Returns:
        Analysis dict with top positional anchors, sorted by frequency.
    """
    search_dirs = []
    if search_dir:
        search_dirs.append(Path(search_dir))
    else:
        search_dirs.extend(
            [
                Path("."),
                Path("artifacts"),
                Path("../artifacts"),
            ]
        )

    artifact_files: list[Path] = []
    for d in search_dirs:
        if d.exists():
            artifact_files.extend(d.glob(artifact_glob))

    logger.info("P16: found %d artifact files matching %s", len(artifact_files), artifact_glob)

    all_candidates: list[str] = []
    attack_sources: dict[str, int] = {}  # artifact_name → candidate_count

    for fpath in artifact_files:
        artifact = _load_artifact(fpath)
        if artifact is None:
            continue
        texts = _extract_candidates(artifact)
        all_candidates.extend(texts)
        attack_sources[fpath.name] = len(texts)

    if not all_candidates:
        return {
            "status": "no_candidates",
            "attack": "P16_corpus_mining",
            "artifact_files_found": len(artifact_files),
            "message": "No candidates extracted. Run P1-P7 sweeps first to generate artifacts.",
        }

    n_candidates = len(all_candidates)
    logger.info("P16: %d total candidates from %d artifacts", n_candidates, len(artifact_files))

    # Sliding-window n-gram frequency at each position
    anchor_start, anchor_end = ANCHOR_WINDOW
    ngram_counts: dict[tuple[int, int, str], int] = {}  # (pos, n, ngram) → count

    for text in all_candidates:
        for n in range(NGRAM_RANGE[0], NGRAM_RANGE[1] + 1):
            for pos in range(anchor_start, min(anchor_end, len(text) - n + 1)):
                gram = text[pos : pos + n]
                if gram.isalpha():
                    key = (pos, n, gram)
                    ngram_counts[key] = ngram_counts.get(key, 0) + 1

    min_count = max(1, math.ceil(n_candidates * MIN_FREQUENCY_PCT / 100))
    frequent_grams: list[dict[str, Any]] = [
        {
            "position": pos,
            "ngram": gram,
            "length": n,
            "count": count,
            "frequency_pct": round(count / n_candidates * 100, 2),
            "is_english_word": gram in ENGLISH_WORDS_4_PLUS,
        }
        for (pos, n, gram), count in ngram_counts.items()
        if count >= min_count
    ]

    frequent_grams.sort(key=lambda x: (-x["frequency_pct"], -x["is_english_word"], x["position"]))
    english_anchors = [g for g in frequent_grams if g["is_english_word"]]

    # Per-position summary: top fragment at each position 0-21
    position_summary: dict[int, dict[str, Any]] = {}
    for g in frequent_grams:
        pos = g["position"]
        if pos not in position_summary or g["frequency_pct"] > position_summary[pos]["frequency_pct"]:
            position_summary[pos] = g

    return {
        "status": "complete",
        "attack": "P16_corpus_mining",
        "artifacts_scanned": len(artifact_files),
        "artifact_sources": attack_sources,
        "total_candidates": n_candidates,
        "min_frequency_pct": MIN_FREQUENCY_PCT,
        "frequent_grams_found": len(frequent_grams),
        "english_anchors": english_anchors[:20],
        "top_positional_anchors": sorted(position_summary.values(), key=lambda x: x["position"])[:22],
        "top_frequent_grams": frequent_grams[:20],
    }


def run_corpus_miner_attack(
    artifact_glob: str = "K4_*_NULL.json",
    null_artifact_path: str = "K4_P16_CORPUS_MINE_NULL.json",
) -> dict[str, Any]:
    """Run the P16 corpus miner and persist results."""
    result = mine_candidate_corpus(artifact_glob=artifact_glob)
    result["attack"] = "P16_corpus_mining"

    try:
        from pathlib import Path as _Path

        _Path(null_artifact_path).write_text(json.dumps(result, indent=2))
    except Exception:  # noqa: BLE001
        pass

    return result


__all__ = [
    "NGRAM_RANGE",
    "ANCHOR_WINDOW",
    "MIN_FREQUENCY_PCT",
    "mine_candidate_corpus",
    "run_corpus_miner_attack",
]
