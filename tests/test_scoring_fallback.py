from __future__ import annotations
from typing import Any

from collections.abc import Iterable
import os
import unittest
from src.scoring.fitness import score_candidate

__all__ = [
    "load_ngram_data",
    "compute_meta_and_score",
]


def load_ngram_data(source: str | None = None) -> dict[str, float]:
    """
    Load n-gram (or simple character) scores.
    Expected format if file provided: one token per line optionally with weight: TOKEN [WHITESPACE WEIGHT]
    Falls back to uniform tiny weights if file missing or unreadable.
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
                if len(pieces) == 1:
                    token, weight = pieces[0], 1.0
                else:
                    token, weight = pieces[0], float(pieces[1])
                data[token] = weight
    except Exception:
        return {}
    return data


def _score_ngram(text: str, ngram_map: dict[str, float] | None) -> float:
    if not ngram_map:
        # Fallback: uniform proxy proportional to length.
        return len(text) * 0.01
    return sum(ngram_map.get(ch, 0.0) for ch in text)


def compute_crib_bonus(text: str, cribs: Iterable[str] | None) -> float:
    """
    Placeholder crib positional bonus: +1.0 per exact crib occurrence.
    TODO: Replace with positional weighting and partial match scoring.
    """
    if not cribs:
        return 0.0
    bonus = 0.0
    for crib in cribs:
        if not crib:
            continue
        # Simple count occurrences
        idx = text.find(crib)
        while idx != -1:
            bonus += 1.0
            idx = text.find(crib, idx + 1)
    return bonus


def compute_clock_valid(text: str) -> float:
    """
    Placeholder Berlin clock validation.
    TODO: Implement pattern extraction + structural validation.
    Returns 0.0 (invalid/unknown) or 1.0 (passes naive stub).
    """
    # Stub condition: length divisible by 5
    return 1.0 if len(text) % 5 == 0 else 0.0


def compute_meta_and_score(text: str, weights: dict[str, float]) -> dict[str, Any]:
    meta = {
        "ngrams": None,        # TODO: populate via loader
        "cribs": None,         # TODO: supply crib list externally
        "crib_bonus": None,    # computed if None
        "clock_valid": None,   # computed if None
    }
    meta["score"] = score_candidate(text, meta, weights)
    return meta


class TestScoringFallback(unittest.TestCase):

    def test_uniform_fallback(self):
        meta = {"ngrams": None, "crib_bonus": 0.0, "clock_valid": 0.0}
        score = score_candidate("ABCDEF", meta, {"ngram": 1.0, "crib": 0.4, "clock": 0.6})
        self.assertGreater(score, 0.0)

    def test_crib_bonus_applied(self):
        meta = {"ngrams": None, "crib_bonus": 2.0, "clock_valid": 0.0}
        score = score_candidate("XYZ", meta, {"ngram": 1.0, "crib": 0.5, "clock": 0.0})
        self.assertGreaterEqual(score, 1.0)


if __name__ == "__main__":
    unittest.main()
