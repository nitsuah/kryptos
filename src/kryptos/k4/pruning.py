"""Candidate pruning utilities (replacing legacy PipelineExecutor._prune).

Public prune_candidates replicates previous logic:
    - Rank candidates descending by 'score'.
    - Keep top_n always.
    - Include any remaining candidates whose crib_bonus >= crib_bonus_threshold.
    - Cap final list to candidate_cap.

Each candidate is a dict with at minimum 'text' and 'score'. If 'crib_bonus' missing it will be
computed via kryptos.k4.scoring.crib_bonus.
"""

from __future__ import annotations

from collections.abc import Iterable

from .scoring import crib_bonus


def prune_candidates(
    candidates: Iterable[dict],
    top_n: int = 15,
    candidate_cap: int = 40,
    crib_bonus_threshold: float = 1.0,
) -> list[dict]:
    """Return pruned candidate list using score + crib bonus threshold.

    Args:
        candidates: iterable of candidate dicts (score, text, optional crib_bonus).
        top_n: number of highest scoring candidates always retained.
        candidate_cap: upper bound on returned candidate count.
        crib_bonus_threshold: include any extra candidate whose crib_bonus >= threshold.

    Behavior mirrors legacy executor for test continuity while removing dependency on
    PipelineExecutor.
    """
    items = [dict(c) for c in candidates]
    if not items:
        return []
    for c in items:
        if 'crib_bonus' not in c:
            c['crib_bonus'] = crib_bonus(c.get('text', ''))
    ranked = sorted(items, key=lambda d: d.get('score', 0.0), reverse=True)
    base = ranked[:top_n]
    extras = [d for d in ranked[top_n:] if d.get('crib_bonus', 0.0) >= crib_bonus_threshold]
    pruned = base + extras
    return pruned[:candidate_cap]


__all__ = ['prune_candidates']
