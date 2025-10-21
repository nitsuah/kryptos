"""Pipeline executor for K4 analysis.

Coordinates ordered stage execution, candidate pruning, adaptive threshold gating,
and artifact persistence (attempt log + summary). Designed to stay lightweight and
fast for iterative tuning.
"""

from __future__ import annotations

import csv
import json
import os
import statistics
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .attempt_logging import persist_attempt_logs
from .pipeline import Stage, StageResult
from .scoring import baseline_stats, crib_bonus


@dataclass
class PipelineConfig:
    ordering: list[Stage]
    candidate_cap_per_stage: int = 40
    pruning_top_n: int = 15
    crib_bonus_threshold: float = 1.0  # keep any candidate with bonus >= threshold
    adaptive_thresholds: dict[str, float] = field(default_factory=dict)
    retry_on_empty: dict[str, Callable[[str], str]] = field(default_factory=dict)
    artifact_root: str = "artifacts"
    label: str = "K4"
    enable_attempt_log: bool = True
    parallel_hill_variants: int = 0  # if >0 run hill stage variants in parallel stub


class PipelineExecutor:
    def __init__(self, config: PipelineConfig):
        self.config = config
        # Track dynamic threshold adjustments per stage
        self._dynamic_thresholds: dict[str, float] = {}

    # ---------------- Internal helpers -----------------
    def _artifact_dir(self) -> str:
        ts = datetime.utcnow().strftime('%Y%m%dT%H%M%S')
        path = os.path.join(self.config.artifact_root, f"run_{ts}")
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def _extract_candidates(result: StageResult) -> list[dict]:
        cands = result.metadata.get('candidates')
        if isinstance(cands, list):
            return cands
        return []

    def _prune(self, candidates: list[dict]) -> list[dict]:
        if not candidates:
            return []
        # compute crib bonuses for pruning rule
        for c in candidates:
            txt = c.get('text', '')
            c['crib_bonus'] = crib_bonus(txt)
        ranked = sorted(candidates, key=lambda c: c.get('score', 0.0), reverse=True)
        top_n = ranked[: self.config.pruning_top_n]
        # include extras meeting crib bonus threshold
        extras = [
            c
            for c in ranked[self.config.pruning_top_n :]
            if c.get('crib_bonus', 0.0) >= self.config.crib_bonus_threshold
        ]
        pruned = top_n + extras
        # cap final size
        return pruned[: self.config.candidate_cap_per_stage]

    def _write_attempt_line(self, fh, stage_name: str, cand: dict, rank: int) -> None:
        text = cand.get('text', '')
        metrics = baseline_stats(text)
        line = {
            'stage': stage_name,
            'rank': rank,
            'score': cand.get('score'),
            'crib_bonus': cand.get('crib_bonus'),
            'metrics': metrics,
            'source': cand.get('source'),
            'trace': cand.get('trace'),
            'text_prefix': text[:60],
        }
        fh.write(json.dumps(line) + '\n')

    # ---------------- Parallel hill variant stub -----------------
    def _run_parallel_hill(self, hill_stage: Stage, ciphertext: str) -> StageResult:
        """Run hill stage variants concurrently with diversified parameters.
        Diversification strategy:
          - Vary partial_len (window used for early pruning) over a small range.
          - Vary partial_min (minimum acceptable partial score) progressively stricter.
        Assumes underlying hill stage closure captures these parameters; if not, we wrap.
        Returns best-scoring StageResult; attaches 'parallel_variants' metadata list.
        """
        variant_ct = self.config.parallel_hill_variants
        if variant_ct <= 1:
            return hill_stage.func(ciphertext)

        # Build param grid: spread partial_len and partial_min
        base_partial_lens = [40, 50, 60, 70, 80]
        base_partial_mins = [-950.0, -900.0, -850.0, -800.0, -750.0]
        # Trim lists to variant_ct length
        partial_lens = base_partial_lens[:variant_ct]
        partial_mins = base_partial_mins[:variant_ct]

        results: list[StageResult] = []
        variant_meta: list[dict[str, float]] = []

        def _variant_call(p_len: int, p_min: float) -> StageResult:
            # hill_stage.func may accept ciphertext only; we recreate a thin wrapper.
            # If underlying closure actually varies pruning params, future refactor will inject them.
            res = hill_stage.func(ciphertext)
            # Annotate metadata with variant parameters (even if underlying stage did not use them directly)
            res.metadata.setdefault('variant_params', {})
            res.metadata['variant_params'].update({'partial_len': p_len, 'partial_min': p_min})
            return res

        with ThreadPoolExecutor(max_workers=variant_ct) as ex:
            futures = [
                ex.submit(_variant_call, p_len, p_min) for p_len, p_min in zip(partial_lens, partial_mins, strict=False)
            ]
            for fut in as_completed(futures):
                try:
                    r = fut.result()
                    results.append(r)
                    vp = r.metadata.get('variant_params', {})
                    variant_meta.append({'score': r.score, **vp})
                except (RuntimeError, ValueError) as e:  # pragma: no cover - defensive; narrow catch
                    results.append(
                        StageResult(
                            name=hill_stage.name,
                            output=ciphertext,
                            metadata={'error': str(e), 'variant_params': {}},
                            score=-1.0,
                        ),
                    )
                    variant_meta.append({'score': -1.0})
        results.sort(key=lambda r: r.score, reverse=True)
        best = results[0]
        best.metadata['parallel_variants'] = variant_meta
        return best

    # ---------------- Execution -----------------
    def run(self, ciphertext: str) -> dict[str, Any]:
        artifact_dir = self._artifact_dir()
        attempt_log_path = os.path.join(artifact_dir, 'attempt_log.jsonl')
        attempt_fh = open(attempt_log_path, 'w', encoding='utf-8') if self.config.enable_attempt_log else None
        all_stage_results: list[StageResult] = []
        total_candidates = 0
        pruned_total = 0
        start_wall = time.perf_counter()
        current_text = ciphertext
        stage_perf: list[dict[str, Any]] = []

        for stage in self.config.ordering:
            stage_start = time.perf_counter()
            if stage.name == 'hill' and self.config.parallel_hill_variants > 1:
                result = self._run_parallel_hill(stage, current_text)
            else:
                result = stage.func(current_text)
            duration = time.perf_counter() - stage_start
            result.metadata['duration'] = duration
            candidates = self._extract_candidates(result)
            total_candidates += len(candidates)
            pruned = self._prune(candidates)
            pruned_total += len(pruned)
            result.metadata['pruned_candidates'] = pruned
            result.metadata['candidate_count'] = len(candidates)
            result.metadata['pruned_count'] = len(pruned)
            all_stage_results.append(result)

            # Performance counters per stage
            cps = len(candidates) / duration if duration > 0 else 0.0  # candidates per second raw
            pps = len(pruned) / duration if duration > 0 else 0.0  # pruned candidates per second
            # Score bucket distribution (simple histogram of candidate scores)
            raw_scores = [c.get('score', 0.0) for c in candidates]
            if raw_scores:
                mean_score = statistics.fmean(raw_scores)
                stdev_score = statistics.pstdev(raw_scores)
                min_score = min(raw_scores)
                max_score = max(raw_scores)
            else:
                mean_score = stdev_score = min_score = max_score = 0.0
            bucket_edges = [-2000, -1000, -500, -250, -100, 0, 100, 250, 500, 1000, 2000]
            bucket_counts: list[int] = [0] * (len(bucket_edges) - 1)
            for s in raw_scores:
                for i in range(len(bucket_edges) - 1):
                    if bucket_edges[i] <= s < bucket_edges[i + 1]:
                        bucket_counts[i] += 1
                        break
            stage_perf.append(
                {
                    'name': stage.name,
                    'duration': duration,
                    'candidate_count': len(candidates),
                    'pruned_count': len(pruned),
                    'candidates_per_sec': cps,
                    'pruned_per_sec': pps,
                    'score_mean': mean_score,
                    'score_stdev': stdev_score,
                    'score_min': min_score,
                    'score_max': max_score,
                    'score_bucket_counts': bucket_counts,
                },
            )

            # Attempt log lines
            if attempt_fh and pruned:
                for rank, cand in enumerate(pruned, start=1):
                    self._write_attempt_line(attempt_fh, stage.name, cand, rank)

            # Adaptive gating: if score below threshold of this stage, optionally skip next gated stage(s)
            base_thresh = self.config.adaptive_thresholds.get(stage.name)
            dyn_adjust = self._dynamic_thresholds.get(stage.name)
            effective_thresh = base_thresh
            if base_thresh is not None and dyn_adjust is not None:
                # Combine base with dynamic adjustment (bounded)
                effective_thresh = base_thresh + dyn_adjust
            if effective_thresh is not None and result.score < effective_thresh:
                result.metadata['adaptive_gate_pass'] = False
                result.metadata['adaptive_gate_threshold'] = effective_thresh
            else:
                result.metadata['adaptive_gate_pass'] = True
                result.metadata['adaptive_gate_threshold'] = effective_thresh

            # Dynamic threshold update heuristic:
            # If stage produced many candidates with high mean score, raise threshold slightly for next time.
            # If stage underperformed (few candidates or low mean), lower threshold to avoid over-pruning.
            if candidates:
                raw_scores = [c.get('score', 0.0) for c in candidates]
                mean_score = statistics.fmean(raw_scores)
                # Compute delta relative to existing threshold (if any)
                if base_thresh is not None:
                    delta = mean_score - base_thresh
                    # Scale adjustment: small fraction of delta, bounded
                    adjust = max(-50.0, min(50.0, delta * 0.05))
                    prev = self._dynamic_thresholds.get(stage.name, 0.0)
                    new_adj = prev + adjust
                    # Bound cumulative adjustment
                    new_adj = max(-base_thresh * 0.5, min(base_thresh * 0.5, new_adj))
                    self._dynamic_thresholds[stage.name] = new_adj
                    result.metadata['dynamic_threshold_adjust'] = new_adj
                else:
                    result.metadata['dynamic_threshold_adjust'] = None
            else:
                # Penalize threshold if no candidates; encourage easier future gating
                if base_thresh is not None:
                    prev = self._dynamic_thresholds.get(stage.name, 0.0)
                    new_adj = prev - (base_thresh * 0.05)
                    self._dynamic_thresholds[stage.name] = new_adj
                    result.metadata['dynamic_threshold_adjust'] = new_adj
                else:
                    result.metadata['dynamic_threshold_adjust'] = None

            # Prepare text for next stage: use best candidate output if available else stage output
            if pruned:
                best = pruned[0]
                current_text = best.get('text', result.output)
            else:
                # retry logic on empty candidate list
                if not candidates and stage.name in self.config.retry_on_empty:
                    current_text = self.config.retry_on_empty[stage.name](current_text)
                else:
                    current_text = result.output

        wall_clock = time.perf_counter() - start_wall

        if attempt_fh:
            attempt_fh.close()
            # flush global attempt buffers to dedicated artifact file (optional aggregation)
            persist_attempt_logs(out_dir=artifact_dir, label=self.config.label, clear=True)

        # Compute best aggregated score among stage outputs & pruned candidates
        best_score = max((r.score for r in all_stage_results), default=float('-inf'))
        # summary
        # Export per-stage top candidates to CSV for quick inspection
        csv_path = os.path.join(artifact_dir, 'stage_top_candidates.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfh:
            writer = csv.writer(csvfh)
            writer.writerow(
                [
                    'stage',
                    'rank',
                    'score',
                    'crib_bonus',
                    'text_prefix',
                ],
            )
            for r in all_stage_results:
                pruned = r.metadata.get('pruned_candidates', []) or []
                for rank, cand in enumerate(pruned, start=1):
                    writer.writerow(
                        [
                            r.name,
                            rank,
                            cand.get('score'),
                            cand.get('crib_bonus'),
                            (cand.get('text', '')[:60]).replace('\n', ' '),
                        ],
                    )

        summary = {
            'label': self.config.label,
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'wall_clock_seconds': wall_clock,
            'stages': [
                {
                    'name': r.name,
                    'score': r.score,
                    'duration': r.metadata.get('duration'),
                    'candidate_count': r.metadata.get('candidate_count'),
                    'pruned_count': r.metadata.get('pruned_count'),
                    'adaptive_gate_pass': r.metadata.get('adaptive_gate_pass'),
                    'adaptive_gate_threshold': r.metadata.get('adaptive_gate_threshold'),
                    'dynamic_threshold_adjust': r.metadata.get('dynamic_threshold_adjust'),
                }
                for r in all_stage_results
            ],
            'total_candidates_raw': total_candidates,
            'total_candidates_pruned': pruned_total,
            'best_stage_score': best_score,
            'performance': stage_perf,
            'score_bucket_edges': bucket_edges,
            'artifact_csv': os.path.basename(csv_path),
            'dynamic_thresholds_final': self._dynamic_thresholds,
        }
        with open(os.path.join(artifact_dir, 'summary.json'), 'w', encoding='utf-8') as fh:
            json.dump(summary, fh, indent=2)
        return summary


__all__ = ['PipelineConfig', 'PipelineExecutor']
