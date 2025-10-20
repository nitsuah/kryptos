"""Pipeline orchestrator for K4 hypothesis testing.

Defines modular transformation stages and execution framework.
"""
from dataclasses import dataclass
from typing import Callable, List, Dict, Any

@dataclass
class StageResult:
    name: str
    output: str
    metadata: Dict[str, Any]
    score: float

@dataclass
class Stage:
    name: str
    func: Callable[[str], StageResult]

class Pipeline:
    def __init__(self, stages: List[Stage]):
        self.stages = stages

    def run(self, ciphertext: str) -> List[StageResult]:
        results: List[StageResult] = []
        current = ciphertext
        for stage in self.stages:
            res = stage.func(current)
            results.append(res)
            current = res.output
        return results
