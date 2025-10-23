from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

__all__ = ["StageContext", "CandidateResult", "Stage", "DEFAULT_WEIGHTS"]


@dataclass
class StageContext:
    ciphertext: str
    params: dict[str, Any]
    prior_results: dict[str, Any]


@dataclass
class CandidateResult:
    text: str
    score: float
    meta: dict[str, Any]


class Stage(Protocol):
    def run(self, ctx: StageContext) -> list[CandidateResult]: ...


DEFAULT_WEIGHTS = {
    "ngram": 1.0,
    "crib": 0.4,
    "clock": 0.6,
}
