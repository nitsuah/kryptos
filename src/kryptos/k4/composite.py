"""Composite multi-stage pipeline runner and candidate aggregator for K4."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..paths import ensure_reports_dir
from .attempt_logging import persist_attempt_logs  # new import
from .pipeline import Pipeline, Stage, StageResult
from .reporting import generate_candidate_artifacts
from .scoring import trigram_entropy, wordlist_hit_rate  # ensure metrics imported


def aggregate_stage_candidates(results: list[StageResult]) -> list[dict[str, Any]]:
    """Aggregate candidates from multiple StageResults, annotate with stage name."""
    agg: list[dict[str, Any]] = []
    for res in results:
        cands = res.metadata.get('candidates', [])
        for c in cands:
            agg.append(
                {
                    'stage': res.name,
                    'score': c.get('score', res.score),
                    'text': c.get('text', res.output),
                    'source': c.get('source', f'stage:{res.name}'),
                    'key': c.get('key'),
                    'time': c.get('time'),
                    'mode': c.get('mode'),
                    'shifts': c.get('shifts'),
                    'trace': c.get('trace'),  # propagate trace
                },
            )
    agg.sort(key=lambda x: x.get('score', 0.0), reverse=True)
    return agg


# Weighted fusion utilities


def _min_max(values: list[float]) -> tuple[float, float]:
    return (min(values), max(values)) if values else (0.0, 0.0)


def normalize_scores(candidates: list[dict[str, Any]], key: str = 'score') -> list[dict[str, Any]]:
    """Return new list with added 'norm_score' using min-max normalization per stage grouping."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for c in candidates:
        grouped.setdefault(c['stage'], []).append(c)
    out: list[dict[str, Any]] = []
    for group in grouped.values():
        vals = [g.get(key, 0.0) for g in group]
        mn, mx = _min_max(vals)
        span = mx - mn if mx != mn else 1.0
        all_equal = mx == mn
        for g in group:
            ns = 0.5 if all_equal else (g.get(key, 0.0) - mn) / span
            new = dict(g)
            new['norm_score'] = ns
            out.append(new)
    return out


def fuse_scores_weighted(
    candidates: list[dict[str, Any]],
    weights: dict[str, float],
    use_normalized: bool = True,
) -> list[dict[str, Any]]:
    """Fuse scores across stages using supplied weights.
    - If use_normalized True, use 'norm_score' (ensure normalize_scores called first).
    - Otherwise use raw 'score'.
    Returns new candidate list with 'fused_score' and sorted by it desc.
    """
    out: list[dict[str, Any]] = []
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
    stages: list[Stage],
    report: bool = True,
    report_dir: str | None = None,
    limit: int = 100,
    weights: dict[str, float] | None = None,
    normalize: bool = True,
    adaptive: bool = False,
) -> dict[str, Any]:
    """Run multiple stages, aggregate candidates, optionally write artifacts and apply
    weighted fusion.
    weights: mapping of stage name to multiplier; if provided fused ranking appended.
    normalize: apply per-stage min-max before fusion (balances different scoring scales).
    Returns dict with 'results', 'aggregated', optional 'fused', and optional 'artifacts'.
    """
    pipe = Pipeline(stages)
    stage_results = pipe.run(ciphertext)
    aggregated = aggregate_stage_candidates(stage_results)[:limit]
    out: dict[str, Any] = {
        'results': stage_results,
        'aggregated': aggregated,
        'profile': {
            'stage_durations': {r.name: r.metadata.get('duration') for r in stage_results},
        },
    }
    # Build lineage list (stage names in order)
    lineage = [r.name for r in stage_results]
    fused_candidates: list[dict[str, Any]] = []
    # If adaptive requested, compute weights dynamically (overrides provided weights)
    if adaptive:
        weights = adaptive_fusion_weights(aggregated)
        metrics_samples = [
            {
                'stage': c['stage'],
                'wl': wordlist_hit_rate(c['text']),
                'ent': trigram_entropy(c['text']),
            }
            for c in aggregated
        ]
        by_stage: dict[str, list[dict[str, float]]] = {}
        for m in metrics_samples:
            by_stage.setdefault(m['stage'], []).append(m)
        diag: dict[str, dict[str, float]] = {}
        for stage, arr in by_stage.items():
            if not arr:
                continue
            wls = sorted(v['wl'] for v in arr)
            ents = sorted(v['ent'] for v in arr)
            mid_wl = wls[len(wls) // 2]
            mid_ent = ents[len(ents) // 2]
            diag[stage] = {
                'median_wordlist_hit_rate': mid_wl,
                'median_trigram_entropy': mid_ent,
                'adaptive_weight': weights.get(stage, 1.0),
            }
        out['profile']['adaptive_diagnostics'] = diag
    if weights:
        candidates_for_fusion = normalize_scores(aggregated) if normalize else aggregated
        fused_candidates = fuse_scores_weighted(candidates_for_fusion, weights, use_normalized=normalize)
        out['fused'] = fused_candidates[:limit]
    if report:
        # Canonicalize report_dir; default now under artifacts/k4_runs
        if report_dir is None or report_dir == 'reports':
            base = Path(ensure_reports_dir()).parent  # points to artifacts/<timestamp> parent
            k4_root = base / 'k4_runs'
            k4_root.mkdir(parents=True, exist_ok=True)
            report_dir = str(k4_root)
        artifact_source = fused_candidates if fused_candidates else aggregated
        candidates_for_artifact = [
            {
                'text': c['text'],
                'score': c.get('fused_score', c['score']),
                'source': c.get('source'),
                'key': c.get('key'),
                'lineage': lineage,
                'trace': c.get('trace'),
            }
            for c in artifact_source
        ]
        paths = generate_candidate_artifacts(
            'composite',
            'K4',
            ciphertext,
            candidates_for_artifact,
            out_dir=report_dir,
            limit=limit,
            lineage=lineage,
        )
        out['artifacts'] = paths
        attempt_path = persist_attempt_logs(out_dir=report_dir, label='K4', clear=True)
        out['attempt_log'] = attempt_path
    return out


def adaptive_fusion_weights(candidates: list[dict[str, Any]]) -> dict[str, float]:
    """Compute dynamic stage weights from top candidate linguistic metrics.
    Heuristic:
      - Base weight = 1.0
      - +0.30 if top candidate wordlist_hit_rate > median of stage tops
      - +0.20 if trigram_entropy in [3.0, 5.2] (plausible English band)
      - -0.15 if trigram_entropy outside that band
      - +0.10 if candidate raw score in top 10% of all aggregated scores
      - Clamp weights to [0.3, 2.5]
    Returns mapping stage->weight.
    """
    if not candidates:
        return {}
    # Identify top candidate per stage (highest raw score)
    by_stage: dict[str, dict[str, Any]] = {}
    all_scores: list[float] = []
    for c in candidates:
        sc = c.get('score', 0.0)
        all_scores.append(sc)
        stage = c['stage']
        if stage not in by_stage or sc > by_stage[stage].get('score', -1e9):
            by_stage[stage] = c
    # Compute metrics
    tops = list(by_stage.values())
    wl_rates = [wordlist_hit_rate(t['text']) for t in tops]
    median_wl = sorted(wl_rates)[len(wl_rates) // 2]
    all_scores.sort(reverse=True)
    top_cutoff_index = max(1, int(0.1 * len(all_scores))) - 1
    top_cutoff_score = all_scores[top_cutoff_index]
    weights: dict[str, float] = {}
    for stage, cand in by_stage.items():
        w = 1.0
        wl = wordlist_hit_rate(cand['text'])
        ent = trigram_entropy(cand['text'])
        raw_score = cand.get('score', 0.0)
        if wl > median_wl:
            w += 0.30
        if 3.0 <= ent <= 5.2:
            w += 0.20
        else:
            w -= 0.15
        if raw_score >= top_cutoff_score:
            w += 0.10
        # clamp
        if w < 0.3:
            w = 0.3
        if w > 2.5:
            w = 2.5
        weights[stage] = round(w, 3)
    return weights


__all__ = [
    'aggregate_stage_candidates',
    'run_composite_pipeline',
    'normalize_scores',
    'fuse_scores_weighted',
    'adaptive_fusion_weights',
]
