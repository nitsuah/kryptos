"""Pipeline orchestrator for K4 hypothesis testing.

Defines modular transformation stages and execution framework.
"""
from dataclasses import dataclass
from typing import Callable, List, Dict, Any
from .hill_constraints import decrypt_and_score
from .scoring import combined_plaintext_score

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

# New helper to build a Hill constraint stage

def make_hill_constraint_stage(name: str = 'hill-constraint') -> Stage:
    def _run(ct: str) -> StageResult:
        candidates = decrypt_and_score(ct)
        best = candidates[0] if candidates else {'text': ct, 'score': combined_plaintext_score(ct), 'key': None}
        return StageResult(name=name, output=best['text'], metadata={'key': best.get('key'), 'candidates': candidates}, score=best['score'])
    return Stage(name=name, func=_run)
