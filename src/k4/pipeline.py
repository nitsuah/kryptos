"""Pipeline orchestrator for K4 hypothesis testing.

Defines modular transformation stages and execution framework.
"""
from dataclasses import dataclass
from typing import Callable, List, Dict, Any
import time  # profiling
from .hill_constraints import decrypt_and_score
from .scoring import combined_plaintext_score_cached as combined_plaintext_score  # switch to cached
from .berlin_clock import enumerate_clock_shift_sequences, apply_clock_shifts
from .transposition import search_columnar, search_columnar_adaptive
from .masking import score_mask_variants

@dataclass
class StageResult:
    """
    Represents the result of a processing stage in the pipeline.
    """
    name: str
    output: str
    metadata: Dict[str, Any]
    score: float

@dataclass
class Stage:
    """A processing stage in the pipeline."""
    name: str
    func: Callable[[str], StageResult]

class Pipeline:
    """Orchestrates execution of multiple stages on ciphertext."""
    def __init__(self, stages: List[Stage]):
        self.stages = stages

    def run(self, ciphertext: str) -> List[StageResult]:
        """
        Execute all stages on the given ciphertext.
        """
        results: List[StageResult] = []
        current = ciphertext
        for stage in self.stages:
            start = time.perf_counter()
            res = stage.func(current)
            duration = time.perf_counter() - start
            # attach duration profiling info
            res.metadata['duration'] = duration
            results.append(res)
            current = res.output
        return results

# New helper to build a Hill constraint stage

def make_hill_constraint_stage(name: str = 'hill-constraint') -> Stage:
    """Create a stage that applies Hill cipher constraints and scores outputs.
    Uses decrypt_and_score to generate candidates; returns best candidate text as stage output.
    """
    def _run(ct: str) -> StageResult:
        candidates = decrypt_and_score(ct)
        best = candidates[0] if candidates else {'text': ct, 'score': combined_plaintext_score(ct), 'key': None, 'trace': []}
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
            dec_forward = apply_clock_shifts(ct, shifts, decrypt=True)
            dec_backward = apply_clock_shifts(ct, shifts, decrypt=False)
            for mode, txt in [('forward', dec_forward), ('backward', dec_backward)]:
                score = combined_plaintext_score(txt)
                trans_label = f"clock:{mode}:{entry['time']}"
                cands.append({'time': entry['time'], 'mode': mode, 'shifts': shifts, 'text': txt, 'score': score, 'trace': [{'stage': name, 'transformation': trans_label, 'shifts': shifts}]})
        cands.sort(key=lambda c: c['score'], reverse=True)
        top = cands[:limit]
        best = top[0] if top else {'text': ct, 'score': combined_plaintext_score(ct), 'trace': []}
        return StageResult(name=name, output=best['text'], metadata={'candidates': top}, score=best['score'])
    return Stage(name=name, func=_run)

# New transposition search stage

def make_transposition_stage(
    name: str = 'transposition',
    min_cols: int = 5,
    max_cols: int = 8,
    max_perms_per_width: int = 720,
    prune: bool = True,
    partial_length: int = 40,
    partial_min_score: float = -500.0,
    limit: int = 50
) -> Stage:
    """Create a stage performing columnar transposition search.
    Parameters mirror search_columnar; results are scored and best plaintext output returned.
    """
    def _run(ct: str) -> StageResult:
        cands = search_columnar(
            ct,
            min_cols=min_cols,
            max_cols=max_cols,
            max_perms_per_width=max_perms_per_width,
            prune=prune,
            partial_length=partial_length,
            partial_min_score=partial_min_score
        )
        # inject trace
        for c in cands:
            c['trace'] = [{'stage': name, 'transformation': f"colperm:{c['cols']}:{c['perm']}", 'cols': c['cols'], 'perm': c['perm']}]
        best = cands[0] if cands else {'text': ct, 'score': combined_plaintext_score(ct), 'trace': []}
        return StageResult(name=name, output=best['text'], metadata={'candidates': cands[:limit]}, score=best['score'])
    return Stage(name=name, func=_run)

# Adaptive transposition search stage

def make_transposition_adaptive_stage(
    name: str = 'transposition-adaptive',
    min_cols: int = 5,
    max_cols: int = 8,
    sample_perms: int = 500,
    partial_length: int = 50,
    prefix_len: int = 3,
    prefix_cache_max: int = 5000,
    early_stop_threshold: float = 1500.0,
    limit: int = 50
) -> Stage:
    """Create a stage using adaptive permutation sampling and prefix caching heuristics."""
    def _run(ct: str) -> StageResult:
        cands = search_columnar_adaptive(
            ct,
            min_cols=min_cols,
            max_cols=max_cols,
            sample_perms=sample_perms,
            partial_length=partial_length,
            prefix_len=prefix_len,
            prefix_cache_max=prefix_cache_max,
            early_stop_threshold=early_stop_threshold
        )
        for c in cands:
            c['trace'] = [{'stage': name, 'transformation': f"colperm-adapt:{c['cols']}:{c['perm']}", 'cols': c['cols'], 'perm': c['perm'], 'partial': c.get('partial')}]
        best = cands[0] if cands else {'text': ct, 'score': combined_plaintext_score(ct), 'trace': []}
        return StageResult(name=name, output=best['text'], metadata={'candidates': cands[:limit]}, score=best['score'])
    return Stage(name=name, func=_run)

def make_masking_stage(name: str = 'masking', null_chars=None, limit: int = 25) -> Stage:
    """Create a stage that generates and scores masking/null-removal variants."""
    def _run(ct: str) -> StageResult:
        cands = score_mask_variants(ct, null_chars)
        for c in cands:
            c['trace'] = [{'stage': name, 'transformation': f"mask:{c.get('removed','')}"}]
        best = cands[0] if cands else {'text': ct, 'score': combined_plaintext_score(ct), 'trace': []}
        return StageResult(name=name, output=best['text'], metadata={'candidates': cands[:limit]}, score=best['score'])
    return Stage(name=name, func=_run)

__all__ = ['Stage','StageResult','Pipeline','make_hill_constraint_stage','make_berlin_clock_stage','make_transposition_stage','make_transposition_adaptive_stage','make_masking_stage']
