"""Pipeline orchestrator for K4 hypothesis testing (moved under package)."""

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class StageResult:
    name: str
    output: str
    metadata: dict
    score: float


@dataclass
class Stage:
    name: str
    func: Any


class Pipeline:
    def __init__(self, stages: list[Stage]):
        self.stages = stages

    def run(self, ciphertext: str) -> list[StageResult]:
        results = []
        current = ciphertext
        for stage in self.stages:
            start = time.perf_counter()
            res = stage.func(current)
            duration = time.perf_counter() - start
            res.metadata['duration'] = duration
            results.append(res)
            current = res.output
        return results
