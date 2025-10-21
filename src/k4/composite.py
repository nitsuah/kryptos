"""Composite multi-stage pipeline runner and candidate aggregator for K4."""
from __future__ import annotations
from typing import List, Dict, Any, Tuple
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

# Weighted fusion utilities

def _min_max(values: List[float]) -> Tuple[float, float]:
    return (min(values), max(values)) if values else (0.0, 0.0)

def normalize_scores(candidates: List[Dict[str, Any]], key: str = 'score') -> List[Dict[str, Any]]:
    """Return new list with added 'norm_score' using min-max normalization per stage grouping."""
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for c in candidates:
        grouped.setdefault(c['stage'], []).append(c)
    out: List[Dict[str, Any]] = []
    for group in grouped.values():
        vals = [g.get(key, 0.0) for g in group]
        mn, mx = _min_max(vals)
        span = mx - mn if mx != mn else 1.0
        for g in group:
            ns = (g.get(key, 0.0) - mn) / span
            new = dict(g)
            new['norm_score'] = ns
            out.append(new)
    return out

def fuse_scores_weighted(candidates: List[Dict[str, Any]], weights: Dict[str, float], use_normalized: bool = True) -> List[Dict[str, Any]]:
    """Fuse scores across stages using supplied weights.
    - If use_normalized True, use 'norm_score' (ensure normalize_scores called first).
    - Otherwise use raw 'score'.
    Returns new candidate list with 'fused_score' and sorted by it desc.
    """
    out: List[Dict[str, Any]] = []
    for c in candidates:
        base = c.get('norm_score') if use_normalized else c.get('score')
        w = weights.get(c['stage'], 1.0)
        fused = (base or 0.0) * w
        new = dict(c)
        new['fused_score'] = fused
        out.append(new)
    out.sort(key=lambda x: x.get('fused_score', 0.0), reverse=True)
    return out

def run_composite_pipeline(
    ciphertext: str,
    stages: List[Stage],
    report: bool = True,
    report_dir: str = 'reports',
    limit: int = 100,
    weights: Dict[str, float] | None = None,
    normalize: bool = True
) -> Dict[str, Any]:
    """Run multiple stages, aggregate candidates, optionally write artifacts and apply weighted fusion.
    weights: mapping of stage name to multiplier; if provided fused ranking appended.
    normalize: apply per-stage min-max before fusion (recommended to balance different scoring scales).
    Returns dict with 'results', 'aggregated', optional 'fused', and optional 'artifacts'.
    """
    pipe = Pipeline(stages)
    stage_results = pipe.run(ciphertext)
    aggregated = aggregate_stage_candidates(stage_results)[:limit]
    out: Dict[str, Any] = {
        'results': stage_results,
        'aggregated': aggregated
    }
    fused_candidates: List[Dict[str, Any]] = []
    if weights:
        candidates_for_fusion = normalize_scores(aggregated) if normalize else aggregated
        fused_candidates = fuse_scores_weighted(candidates_for_fusion, weights, use_normalized=normalize)
        out['fused'] = fused_candidates[:limit]
    if report:
        # Choose artifact source list: fused if available else aggregated
        artifact_source = fused_candidates if fused_candidates else aggregated
        candidates_for_artifact = [
            {
                'text': c['text'],
                'score': c.get('fused_score', c['score']),
                'source': f"{c.get('stage')}|{c.get('source')}",
                'key': c.get('key')
            } for c in artifact_source
        ]
        paths = generate_candidate_artifacts('composite', 'K4', ciphertext, candidates_for_artifact, out_dir=report_dir, limit=limit)
        out['artifacts'] = paths
    return out

__all__ = ['aggregate_stage_candidates','run_composite_pipeline','normalize_scores','fuse_scores_weighted']
