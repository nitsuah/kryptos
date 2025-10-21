"""Tuning harness for PipelineExecutor.

Sweeps selected parameters (pruning_top_n, candidate_cap_per_stage, parallel_hill_variants)
and records performance + best score metrics for comparison. Produces CSV summary in artifacts.

Usage (example):
    python scripts/tune_pipeline.py --cipher PATH --sweeps pruning_top_n=10,15 parallel_hill_variants=1,3

If no cipher path provided, uses a small synthetic ciphertext sample.
"""

from __future__ import annotations

import argparse
import csv
import os
import random
import string
import sys
import time
from dataclasses import replace
from typing import Any

# Ensure repository root on path when running as script
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PARENT = os.path.abspath(os.path.join(ROOT, '..'))
SRC_DIR = os.path.join(ROOT, 'src')
for path_candidate in (ROOT, SRC_DIR, PARENT):
    if path_candidate not in sys.path:
        sys.path.insert(0, path_candidate)

# Attempt import via src.k4 first then fallback to k4
try:  # pragma: no cover - import resolution logic
    from kryptos.src.k4.executor import PipelineConfig, PipelineExecutor  # type: ignore
    from kryptos.src.k4.pipeline import Stage, StageResult  # type: ignore
except ImportError:  # pragma: no cover
    try:
        from src.k4.executor import PipelineConfig, PipelineExecutor  # type: ignore
        from src.k4.pipeline import Stage, StageResult  # type: ignore
    except ImportError:
        from k4.executor import PipelineConfig, PipelineExecutor  # type: ignore
        from k4.pipeline import Stage, StageResult  # type: ignore

# --- Synthetic stage stubs (if real ones not wired here) ---


def _dummy_candidates(base_text: str, count: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i in range(count):
        mutated = list(base_text)
        if mutated:
            # random minor mutation for diversity
            idx = random.randrange(len(mutated))
            mutated[idx] = random.choice(string.ascii_uppercase)
        cand_text = ''.join(mutated)
        # pseudo score: length-based + random jitter
        score = len(cand_text) * 0.5 + random.uniform(-5, 5)
        out.append({'text': cand_text, 'score': score, 'source': 'stub', 'trace': f'm{i}'})
    return out


def stage_hill() -> Stage:  # simple factory returning Stage instance
    def _run(text: str):
        cands = _dummy_candidates(text, 25)
        best = max(cands, key=lambda c: c['score'])
        return StageResult(name='hill', output=best['text'], score=best['score'], metadata={'candidates': cands})

    return Stage(name='hill', func=_run)


def stage_transposition() -> Stage:
    def _run(text: str):
        cands = _dummy_candidates(text, 18)
        best = max(cands, key=lambda c: c['score'])
        return StageResult(
            name='transposition',
            output=best['text'],
            score=best['score'],
            metadata={'candidates': cands},
        )

    return Stage(name='transposition', func=_run)


def build_default_order() -> list[Stage]:
    return [stage_hill(), stage_transposition()]


# --- Tuning Sweep ---


def run_sweep(ciphertext: str, base_config: PipelineConfig, param_grid: dict[str, list[Any]], out_csv: str) -> None:
    headers = [
        'run_id',
        'pruning_top_n',
        'candidate_cap_per_stage',
        'parallel_hill_variants',
        'best_stage_score',
        'wall_clock_seconds',
    ]
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)
        run_id = 0
        for pruning_top_n in param_grid.get('pruning_top_n', [base_config.pruning_top_n]):
            for candidate_cap_per_stage in param_grid.get(
                'candidate_cap_per_stage',
                [base_config.candidate_cap_per_stage],
            ):
                for parallel_hill_variants in param_grid.get(
                    'parallel_hill_variants',
                    [base_config.parallel_hill_variants],
                ):
                    cfg = replace(
                        base_config,
                        pruning_top_n=int(pruning_top_n),
                        candidate_cap_per_stage=int(candidate_cap_per_stage),
                        parallel_hill_variants=int(parallel_hill_variants),
                        ordering=build_default_order(),  # rebuild ordering to ensure fresh stage closures
                    )
                    executor = PipelineExecutor(cfg)
                    start = time.perf_counter()
                    summary = executor.run(ciphertext)
                    elapsed = time.perf_counter() - start
                    writer.writerow(
                        [
                            run_id,
                            cfg.pruning_top_n,
                            cfg.candidate_cap_per_stage,
                            cfg.parallel_hill_variants,
                            summary.get('best_stage_score'),
                            elapsed,
                        ],
                    )
                    run_id += 1
    print(f"Sweep complete. Wrote {run_id} rows to {out_csv}")


# --- CLI ---


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Pipeline tuning sweep')
    parser.add_argument('--cipher', type=str, help='Path to ciphertext file', default='')
    parser.add_argument('--out', type=str, help='Output CSV path', default='artifacts/tuning/tuning_results.csv')
    parser.add_argument(
        '--sweeps',
        type=str,
        nargs='*',
        help='Param sweeps like pruning_top_n=10,15 candidate_cap_per_stage=30,50 parallel_hill_variants=1,3',
        default=[],
    )
    return parser.parse_args()


def parse_param_grid(specs: list[str]) -> dict[str, list[Any]]:
    grid: dict[str, list[Any]] = {}
    for spec in specs:
        if '=' not in spec:
            continue
        key, vals = spec.split('=', 1)
        grid[key.strip()] = [v.strip() for v in vals.split(',') if v.strip()]
    return grid


def load_cipher(path: str) -> str:
    if path and os.path.exists(path):
        with open(path, encoding='utf-8') as fh:
            return fh.read().strip()
    # fallback synthetic ciphertext
    return 'K4SYNTHETICPLACEHOLDER' * 3


def main() -> None:
    args = parse_args()
    ciphertext = load_cipher(args.cipher)
    base_cfg = PipelineConfig(ordering=build_default_order())
    param_grid = parse_param_grid(args.sweeps)
    run_sweep(ciphertext, base_cfg, param_grid, args.out)


if __name__ == '__main__':
    main()
