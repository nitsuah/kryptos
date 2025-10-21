"""Pipeline orchestrator for K4 hypothesis testing.

Defines modular transformation stages and execution framework.
"""
from dataclasses import dataclass
from typing import Callable, List, Dict, Any
from .hill_constraints import decrypt_and_score
from .scoring import combined_plaintext_score
from .berlin_clock import enumerate_clock_shift_sequences, apply_clock_shifts

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

def make_berlin_clock_stage(name: str = 'berlin-clock', step_seconds: int = 3600, limit: int = 50) -> Stage:
    """Create a stage that applies multiple Berlin Clock shift sequences and scores outputs.
    Enumerates times across a day at given step; applies shifts (decrypt-style) attempting to reveal plaintext.
    Returns best candidate text as stage output; all candidates stored in metadata.
    """
    def _run(ct: str) -> StageResult:
        seqs = enumerate_clock_shift_sequences(step_seconds=step_seconds)
        cands: List[Dict[str, Any]] = []
        for entry in seqs:
            shifts = entry['shifts']
            # Try both directions (encrypt-like and decrypt-like application)
            dec_forward = apply_clock_shifts(ct, shifts, decrypt=True)
            dec_backward = apply_clock_shifts(ct, shifts, decrypt=False)
            for mode, txt in [('forward', dec_forward), ('backward', dec_backward)]:
                score = combined_plaintext_score(txt)
                cands.append({'time': entry['time'], 'mode': mode, 'shifts': shifts, 'text': txt, 'score': score})
        cands.sort(key=lambda c: c['score'], reverse=True)
        top = cands[:limit]
        best = top[0] if top else {'text': ct, 'score': combined_plaintext_score(ct)}
        return StageResult(name=name, output=best['text'], metadata={'candidates': top}, score=best['score'])
    return Stage(name=name, func=_run)

__all__ = ['Stage','StageResult','Pipeline','make_hill_constraint_stage','make_berlin_clock_stage']
