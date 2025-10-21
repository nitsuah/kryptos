"""Composite multi-stage pipeline runner and candidate aggregator for K4."""
from __future__ import annotations
from typing import List, Dict, Any
from .pipeline import Pipeline, Stage, StageResult
from .reporting import generate_candidate_artifacts

def aggregate_stage_candidates(results: List[StageResult]) -> List[Dict[str, Any]]:
    """Aggregate candidates from multiple StageResults, annotate with stage name."""
    agg: List[Dict[str, Any]] = []
    for res in results:
        cands = res.metadata.get('candidates', [])
        for c in cands:
            agg.append({
                'stage': res.name,
                'score': c.get('score', res.score),
                'text': c.get('text', res.output),
                'source': c.get('source', f'stage:{res.name}'),
                'key': c.get('key'),
                'time': c.get('time'),
                'mode': c.get('mode'),
                'shifts': c.get('shifts')
            })
    agg.sort(key=lambda x: x.get('score', 0.0), reverse=True)
    return agg

def run_composite_pipeline(ciphertext: str, stages: List[Stage], report: bool = True, report_dir: str = 'reports', limit: int = 100) -> Dict[str, Any]:
    """Run multiple stages, aggregate candidates, optionally write artifacts.
    Returns dict with 'results', 'aggregated', and optional 'artifacts'.
    """
    pipe = Pipeline(stages)
    stage_results = pipe.run(ciphertext)
    aggregated = aggregate_stage_candidates(stage_results)[:limit]
    out: Dict[str, Any] = {
        'results': stage_results,
        'aggregated': aggregated
    }
    if report:
        # Adapt candidates format to expected reporting schema fields
        candidates_for_artifact = [
            {
                'text': c['text'],
                'score': c['score'],
                'source': f"{c.get('stage')}|{c.get('source')}",
                'key': c.get('key')
            } for c in aggregated
        ]
        paths = generate_candidate_artifacts('composite', 'K4', ciphertext, candidates_for_artifact, out_dir=report_dir, limit=limit)
        out['artifacts'] = paths
    return out

__all__ = ['aggregate_stage_candidates','run_composite_pipeline']
