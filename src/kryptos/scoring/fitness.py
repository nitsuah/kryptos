"""Scoring functions (ngram, crib bonuses, structural checks).

Canonical implementation replacing prior duplicate under `src/scoring/fitness.py`.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from typing import Any

__all__ = ["load_ngram_data", "score_candidate", "compute_meta_and_score", "compute_crib_bonus"]


def load_ngram_data(source: str | None = None) -> dict[str, float]:
    """Load simple token weights from a file.

    Format: TOKEN [WEIGHT]
    Missing or unreadable file -> empty dict (caller decides fallback).
    """
    if not source:
        return {}
    if not os.path.isfile(source):
        return {}
    data: dict[str, float] = {}
    try:
        with open(source, encoding="utf-8") as fh:
            for line in fh:
                part = line.strip()
                if not part:
                    continue
                pieces = part.split()
                token = pieces[0]
                weight = float(pieces[1]) if len(pieces) > 1 else 1.0
                data[token] = weight
    except (OSError, ValueError):  # narrow exception scope
        return {}
    return data


def _score_ngram(text: str, ngram_map: dict[str, float] | None) -> float:
    if not ngram_map:
        return len(text) * 0.01  # uniform proxy
    return sum(ngram_map.get(ch, 0.0) for ch in text)


def compute_crib_bonus(text: str, cribs: Iterable[str] | None) -> float:
    """Naive crib bonus: +1.0 per exact occurrence of each crib.

    TODO: Replace with positional weighting + partial matches.
    """
    if not cribs:
        return 0.0
    bonus = 0.0
    for crib in cribs:
        if not crib:
            continue
        start = text.find(crib)
        while start != -1:
            bonus += 1.0
            start = text.find(crib, start + 1)
    return bonus


def compute_clock_valid(text: str) -> float:
    """Stub Berlin clock structural validation.

    Returns 1.0 if length divisible by 5 else 0.0.
    """
    return 1.0 if len(text) % 5 == 0 else 0.0


def score_candidate(text: str, meta: dict[str, Any], weights: dict[str, float]) -> float:
    """Aggregate weighted score.

    meta may include precomputed components; missing ones are computed lazily.
    """
    ngram_score = _score_ngram(text, meta.get("ngrams"))
    crib_score = meta.get("crib_bonus")
    if crib_score is None:
        crib_score = compute_crib_bonus(text, meta.get("cribs"))
    clock_score = meta.get("clock_valid")
    if clock_score is None:
        clock_score = compute_clock_valid(text)
    return (
        weights.get("ngram", 1.0) * ngram_score
        + weights.get("crib", 0.4) * crib_score
        + weights.get("clock", 0.6) * clock_score
    )


def compute_meta_and_score(text: str, weights: dict[str, float]) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "ngrams": None,
        "cribs": None,
        "crib_bonus": None,
        "clock_valid": None,
    }
    meta["score"] = score_candidate(text, meta, weights)
    return meta
