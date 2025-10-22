from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


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


# Default weights placeholder (shared by scoring)
DEFAULT_WEIGHTS = {
    "ngram": 1.0,
    "crib": 0.4,
    "clock": 0.6,
}

# TODO: Add concrete stage adapters (hill, transposition, masking, berlin clock).
