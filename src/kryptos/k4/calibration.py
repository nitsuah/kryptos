"""Calibration harness utilities for rarity weighting (k sweep) and positional deviation weight.

This module provides pure functions that accept a list of candidate plaintext strings and
return structured calibration metrics without mutating global scoring state.

Artifacts can be written via `write_calibration_artifact`.
"""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from dataclasses import dataclass

from ..paths import ensure_reports_dir
from .scoring import (
    baseline_stats,
    berlin_clock_pattern_validator,
    combined_plaintext_score,
    positional_letter_deviation_score,
)

DEFAULT_K_VALUES: Sequence[float] = (1.0, 2.0, 5.0, 10.0)
DEFAULT_POS_WEIGHTS: Sequence[float] = (10.0, 20.0, 30.0, 40.0)


def _spearman(rank_a: list[str], rank_b: list[str]) -> float:
    """Compute Spearman correlation of two rankings (list of item IDs).

    Assumes both lists contain same items (set equality) and no ties (acceptable for our deterministic ordering).
    Implements rho = 1 - (6 * sum(d_i^2)) / (n*(n^2 - 1)). Returns 0.0 if n < 2.
    """
    if not rank_a or set(rank_a) != set(rank_b):
        return 0.0
    n = len(rank_a)
    if n < 2:
        return 0.0
    pos_a = {item: i for i, item in enumerate(rank_a)}
    pos_b = {item: i for i, item in enumerate(rank_b)}
    d2_sum = 0.0
    for item in rank_a:
        d = pos_a[item] - pos_b[item]
        d2_sum += d * d
    return 1.0 - (6.0 * d2_sum) / (n * (n * n - 1))


def _rank_items(score_map: dict[str, float]) -> list[str]:
    return [t for t, _ in sorted(score_map.items(), key=lambda kv: kv[1], reverse=True)]


def compute_alignment_frequencies(candidates: Sequence[str], cribs: Sequence[str]) -> dict[str, float]:
    """Compute simple alignment frequency: fraction of candidates containing each crib.
    Returns mapping crib->frequency in [0,1]. Cribs are matched case-insensitive alphabetical only.
    """
    freqs: dict[str, float] = {}
    if not candidates:
        return freqs
    total = float(len(candidates))
    for crib in cribs:
        if not crib or not crib.isalpha():
            continue
        up = crib.upper()
        count = sum(1 for c in candidates if up in ''.join(ch for ch in c.upper() if ch.isalpha()))
        freqs[up] = count / total
    return freqs


def rarity_alignment_weighted_bonus(text: str, alignment_freqs: dict[str, float], k: float) -> float:
    """Compute rarity-alignment-weighted crib bonus variant.

    rarity_weight = 1 / (1 + f * k) where f is alignment frequency across candidate set.
    Base bonus per crib occurrence = 5 * len(crib) * rarity_weight.
    Multiple occurrences multiply; overlapping permitted.
    """
    seq = ''.join(c for c in text.upper() if c.isalpha())
    if not seq or not alignment_freqs:
        return 0.0
    total = 0.0
    for crib, freq in alignment_freqs.items():
        if crib in seq:
            # Count occurrences
            start = seq.find(crib)
            occs = 0
            while start != -1:
                occs += 1
                start = seq.find(crib, start + 1)
            rarity_weight = 1.0 / (1.0 + freq * k)
            total += 5.0 * len(crib) * rarity_weight * occs
    return total


@dataclass(frozen=True)
class RarityCalibrationRow:
    k: float
    spearman_vs_baseline: float
    top10_overlap_ratio: float
    mean_rarity_weight_top_quartile: float
    mean_rarity_weight_all: float


def calibrate_rarity_weight(
    candidates: Sequence[str],
    cribs: Sequence[str],
    k_values: Sequence[float] | None = None,
    top_n: int = 10,
) -> list[RarityCalibrationRow]:
    """Return rows of calibration metrics for each k in k_values.

    Baseline ranking uses combined_plaintext_score; adjusted ranking adds rarity alignment weighted bonus
    while subtracting original simple crib_bonus portion (to avoid double counting). For simplicity we
    treat baseline_stats['crib_bonus'] as the component replaced.
    """
    if k_values is None:
        k_values = DEFAULT_K_VALUES
    base_scores = {c: combined_plaintext_score(c) for c in candidates}
    base_rank = _rank_items(base_scores)
    alignment_freqs = compute_alignment_frequencies(candidates, cribs)
    rows: list[RarityCalibrationRow] = []
    # precompute simple crib bonuses
    simple_bonus = {c: baseline_stats(c)['crib_bonus'] for c in candidates}
    for k in k_values:
        adj_scores: dict[str, float] = {}
        rarity_weights_sample: list[float] = []
        for c in candidates:
            rarity_bonus = rarity_alignment_weighted_bonus(c, alignment_freqs, k)
            # Replace simple crib bonus with rarity-adjusted variant
            adj_scores[c] = base_scores[c] - simple_bonus[c] + rarity_bonus
            # Track mean rarity weight per crib occurrence (approx using first crib matched)
            for crib, freq in alignment_freqs.items():
                if crib in ''.join(ch for ch in c.upper() if ch.isalpha()):
                    rarity_weights_sample.append(1.0 / (1.0 + freq * k))
                    break
        adj_rank = _rank_items(adj_scores)
        spearman_corr = _spearman(base_rank, adj_rank)
        top_base = set(base_rank[:top_n])
        top_adj = set(adj_rank[:top_n])
        overlap_ratio = len(top_base & top_adj) / float(top_n) if top_n else 0.0
        if rarity_weights_sample:
            rarity_weights_sample.sort(reverse=True)
            top_quartile = rarity_weights_sample[: max(1, len(rarity_weights_sample) // 4)]
            mean_top_q = sum(top_quartile) / len(top_quartile)
            mean_all = sum(rarity_weights_sample) / len(rarity_weights_sample)
        else:
            mean_top_q = mean_all = 0.0
        rows.append(
            RarityCalibrationRow(
                k=float(k),
                spearman_vs_baseline=round(spearman_corr, 4),
                top10_overlap_ratio=round(overlap_ratio, 4),
                mean_rarity_weight_top_quartile=round(mean_top_q, 4),
                mean_rarity_weight_all=round(mean_all, 4),
            ),
        )
    return rows


@dataclass(frozen=True)
class PositionalWeightCalibrationRow:
    positional_weight: float
    spearman_vs_baseline: float
    top10_overlap_ratio: float


def calibrate_positional_weight(
    candidates: Sequence[str],
    weights: Sequence[float] | None = None,
    top_n: int = 10,
    pattern_bonus_weight: float = 25.0,
) -> list[PositionalWeightCalibrationRow]:
    """Sweep weights for positional letter deviation component.

    Baseline ranking uses combined_plaintext_score (without positional + pattern extras).
    Adjusted score = combined + pattern_bonus_weight * pattern_bonus + W_pos * positional_letter_deviation_score.
    """
    if weights is None:
        weights = DEFAULT_POS_WEIGHTS
    base_scores = {c: combined_plaintext_score(c) for c in candidates}
    base_rank = _rank_items(base_scores)
    rows: list[PositionalWeightCalibrationRow] = []
    for w in weights:
        adj_scores: dict[str, float] = {}
        for c in candidates:
            pattern_meta = berlin_clock_pattern_validator(c)
            pattern_bonus = pattern_meta['pattern_bonus']
            pos_score = positional_letter_deviation_score(c)
            adj_scores[c] = base_scores[c] + pattern_bonus_weight * pattern_bonus + w * pos_score
        adj_rank = _rank_items(adj_scores)
        spearman_corr = _spearman(base_rank, adj_rank)
        top_base = set(base_rank[:top_n])
        top_adj = set(adj_rank[:top_n])
        overlap_ratio = len(top_base & top_adj) / float(top_n) if top_n else 0.0
        rows.append(
            PositionalWeightCalibrationRow(
                positional_weight=float(w),
                spearman_vs_baseline=round(spearman_corr, 4),
                top10_overlap_ratio=round(overlap_ratio, 4),
            ),
        )
    return rows


def write_calibration_artifact(
    rarity_rows: Sequence[RarityCalibrationRow],
    positional_rows: Sequence[PositionalWeightCalibrationRow],
    label: str = 'K4',
    output_dir: str | None = None,
) -> str:
    """Write combined calibration results to JSON and return path."""
    if output_dir is None:
        output_dir = str(ensure_reports_dir())
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, 'calibration_results.json')
    payload = {
        'label': label,
        'rarity_weight_sweep': [row.__dict__ for row in rarity_rows],
        'positional_weight_sweep': [row.__dict__ for row in positional_rows],
    }
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2)
    return path


__all__ = [
    'calibrate_rarity_weight',
    'calibrate_positional_weight',
    'compute_alignment_frequencies',
    'rarity_alignment_weighted_bonus',
    'write_calibration_artifact',
    'RarityCalibrationRow',
    'PositionalWeightCalibrationRow',
]
