from __future__ import annotations

import os
import unittest
from collections.abc import Iterable
from typing import Any

from src.stages.interface import StageContext
from src.stages.mock_stage import MockStage

__all__ = [
    "load_ngram_data",
    "score_candidate",
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


def score_candidate(text: str, meta: dict[str, Any], weights: dict[str, float]) -> float:
    """
    Aggregate score using weighted components.
    meta may provide:
      - ngrams (dict or None)
      - crib_bonus (float or None)
      - clock_valid (float or None)
      - cribs (iterable of strings) if crib_bonus absent
    """
    ngram_score = _score_ngram(text, meta.get("ngrams"))
    crib_score = meta.get("crib_bonus")
    if crib_score is None:
        crib_score = compute_crib_bonus(text, meta.get("cribs"))
    clock_score = meta.get("clock_valid")
    if clock_score is None:
        clock_score = compute_clock_valid(text)
    total = (
        weights.get("ngram", 1.0) * ngram_score
        + weights.get("crib", 0.4) * crib_score
        + weights.get("clock", 0.6) * clock_score
    )
    return total


# Convenience wrapper for stages


def compute_meta_and_score(text: str, weights: dict[str, float]) -> dict[str, Any]:
    meta = {
        "ngrams": None,  # TODO: populate via loader
        "cribs": None,  # TODO: supply crib list externally
        "crib_bonus": None,  # computed if None
        "clock_valid": None,  # computed if None
    }
    meta["score"] = score_candidate(text, meta, weights)
    return meta


class TestStageInterface(unittest.TestCase):
    def setUp(self):
        self.stage = MockStage()

    def test_mock_stage_basic(self):
        ctx = StageContext(ciphertext="ABCDEFG", params={}, prior_results={})
        results = self.stage.run(ctx)
        self.assertTrue(results)
        self.assertTrue(any(r.text == "ABC" for r in results))

    def test_mock_stage_empty_ciphertext(self):
        ctx = StageContext(ciphertext="", params={}, prior_results={})
        results = self.stage.run(ctx)
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
