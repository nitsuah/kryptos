"""Crib / weight sweep helpers.

Pure functions to support tuning experiments formerly implemented only in
scripts. These functions deliberately avoid direct filesystem I/O (aside
from optional explicit write helpers) so they are easy to test.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from statistics import mean

from .. import scoring

DEFAULT_SAMPLE_SET = [
    "BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT LIES THE NUANCE OF ILLUSION",
    "IT WAS TOTALLY INVISIBLE HOWS THAT POSSIBLE THEY USED THE EARTHS MAGNETIC FIELD",
    "SLOWLY DESPARATLY SLOWLY THE REMAINS OF PASSAGE DEBRIS THAT ENCUMBERED THE LOWER",
]


@dataclass(frozen=True)
class WeightSweepRow:
    weight: float
    sample: str
    baseline: float
    with_cribs: float
    delta: float


def run_crib_weight_sweep(
    samples: Sequence[str] | None = None,
    cribs: Iterable[str] | None = None,
    weights: Sequence[float] | None = None,
) -> list[WeightSweepRow]:
    """Compute baseline vs crib‑augmented scores for each sample and weight.

    Returns a list of rows (unsorted). Consumers can persist as CSV.
    """
    if samples is None:
        samples = DEFAULT_SAMPLE_SET
    if weights is None:
        weights = (0.1, 0.5, 1.0)
    cribs_list = [c.upper() for c in (cribs or []) if c and c.isalpha() and len(c) >= 3]
    rows: list[WeightSweepRow] = []
    for w in weights:
        for s in samples:
            base = scoring.combined_plaintext_score(s)
            withc = scoring.combined_plaintext_score_with_external_cribs(s, cribs_list, crib_weight=w)
            rows.append(WeightSweepRow(weight=float(w), sample=s, baseline=base, with_cribs=withc, delta=withc - base))
    return rows


def summarize_weight_sweep_rows(rows: Iterable[WeightSweepRow]) -> dict[float, dict[str, float]]:
    """Aggregate mean delta per weight.

    Returns mapping weight -> {mean_delta: float, count: int}.
    """
    buckets: dict[float, list[float]] = {}
    for r in rows:
        buckets.setdefault(r.weight, []).append(r.delta)
    return {w: {"mean_delta": mean(deltas), "count": float(len(deltas))} for w, deltas in buckets.items() if deltas}


def pick_best_weight_from_rows(rows: Iterable[WeightSweepRow]) -> float:
    """Pick weight with highest mean delta (ties -> smallest weight for determinism)."""
    summary = summarize_weight_sweep_rows(rows)
    if not summary:
        return 0.0
    # sorted by (-mean_delta, weight) so we pick highest improvement, then lowest weight
    ranked = sorted(((meta["mean_delta"], w) for w, meta in summary.items()), key=lambda t: (-t[0], t[1]))
    return float(ranked[0][1])


def tiny_param_sweep(
    samples: Sequence[str] | None = None,
    param_grid: Sequence[dict] | None = None,
) -> list[dict]:
    """Replicate the previous tiny deterministic sweep returning structured results.

    Each result dict contains: run_id, chi_weight, ngram_weight, crib_bonus, top_sample, top_score.
    """
    if samples is None:
        samples = DEFAULT_SAMPLE_SET
    if param_grid is None:
        param_grid = [
            {"chi_weight": 1.0, "ngram_weight": 1.0, "crib_bonus": 0.0},
            {"chi_weight": 1.5, "ngram_weight": 0.8, "crib_bonus": 0.0},
            {"chi_weight": 0.8, "ngram_weight": 1.2, "crib_bonus": 0.5},
        ]
    out: list[dict] = []
    for i, params in enumerate(param_grid, start=1):
        scores: list[tuple[str, float]] = []
        for s in samples:
            stats = scoring.baseline_stats(s)
            ngram_sum = stats["bigram_score"] + stats["trigram_score"] + stats["quadgram_score"]
            score = (
                params["ngram_weight"] * ngram_sum
                - params["chi_weight"] * (0.05 * stats["chi_square"])
                + params["crib_bonus"] * stats["crib_bonus"]
            )
            scores.append((s, score))
        scores.sort(key=lambda x: x[1], reverse=True)
        top_sample, top_score = scores[0]
        out.append(
            {
                "run_id": f"r{i:03d}",
                "chi_weight": params["chi_weight"],
                "ngram_weight": params["ngram_weight"],
                "crib_bonus": params["crib_bonus"],
                "top_sample": top_sample,
                "top_score": float(top_score),
            },
        )
    return out


def compare_crib_integration(
    samples: Sequence[str] | None = None,
    cribs: Iterable[str] | None = None,
) -> list[dict]:
    """Return rows comparing baseline vs baseline+crib_bonus for visibility.

    Each row dict: sample, baseline_combined, with_cribs_combined, crib_count.
    """
    if samples is None:
        samples = DEFAULT_SAMPLE_SET
    cribs_list = [c.upper() for c in (cribs or []) if c and c.isalpha() and len(c) >= 3]
    rows: list[dict] = []
    upper_samples = ["".join(c for c in s.upper() if c.isalpha()) for s in samples]
    for s, upper in zip(samples, upper_samples):
        base_stats = scoring.baseline_stats(s)
        baseline = base_stats.get("combined_score", 0.0)
        crib_bonus = 0.0
        for crib in cribs_list:
            if crib in upper:
                crib_bonus += 5.0 * len(crib)
        rows.append(
            {
                "sample": s,
                "baseline_combined": float(baseline),
                "with_cribs_combined": float(baseline + crib_bonus),
                "crib_count": len(cribs_list),
            },
        )
    return rows
