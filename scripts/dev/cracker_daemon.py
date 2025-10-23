#!/usr/bin/env python3
"""Autonomous K4 cracker daemon.

Runs a lightweight K4 pipeline (constructed inline, no deprecated wrapper
imports) against one or more ciphertexts and exits when a candidate passes a
plausibility score threshold.

All former wrapper indirection (`run_pipeline_sample.py`) removed to enforce
explicit pipeline composition using public factories under `kryptos.k4.pipeline`.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

from kryptos.k4.executor import PipelineConfig, PipelineExecutor
from kryptos.k4.pipeline import (
    make_hill_constraint_stage,
    make_masking_stage,
    make_transposition_adaptive_stage,
    make_transposition_stage,
)


def build_pipeline(parallel_variants: int = 0) -> PipelineExecutor:
    """Construct a default exploratory pipeline executor.

    (Formerly loaded from deprecated wrapper.)
    """
    stages = [
        make_hill_constraint_stage(name="hill", prune_3x3=True, partial_len=50, partial_min=-850.0),
        make_transposition_adaptive_stage(),
        make_transposition_stage(),
        make_masking_stage(name="masking", null_chars=["X"], limit=15),
    ]
    cfg = PipelineConfig(
        ordering=stages,
        candidate_cap_per_stage=30,
        pruning_top_n=12,
        crib_bonus_threshold=5.0,
        adaptive_thresholds={"hill": -500.0},
        artifact_root="artifacts",
        label="daemon-run",
        enable_attempt_log=True,
        parallel_hill_variants=parallel_variants,
    )
    return PipelineExecutor(cfg)


def find_latest_run_artifact(artifact_root: Path) -> Path | None:
    if not artifact_root.exists():
        return None
    runs = [p for p in artifact_root.iterdir() if p.is_dir() and p.name.startswith('run_')]
    if not runs:
        return None
    return sorted(runs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def read_top_candidates(run_dir: Path) -> list[dict]:
    csvp = run_dir / 'stage_top_candidates.csv'
    if not csvp.exists():
        return []
    out: list[dict] = []
    with csvp.open('r', encoding='utf-8', newline='') as fh:
        rdr = csv.reader(fh)
        # skip header row (not used)
        next(rdr, None)
        for row in rdr:
            # writer writes: stage, rank, score, crib_bonus, text_prefix
            out.append(
                {
                    'stage': row[0],
                    'rank': int(row[1]),
                    'score': float(row[2]) if row[2] else None,
                    'crib_bonus': row[3],
                    'text_prefix': row[4],
                },
            )
    return out


def write_decision(repo_root: Path, decision: dict) -> None:
    droot = repo_root / 'artifacts' / 'decisions'
    droot.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    fname = droot / f'decision_{ts}.json'
    with fname.open('w', encoding='utf-8') as fh:
        json.dump(decision, fh, indent=2)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description='Autonomous K4 cracker daemon')
    parser.add_argument('--cipher', type=str, default=None, help='Single ciphertext string to try')
    parser.add_argument('--cipher-file', type=Path, default=None, help='File with one ciphertext per line')
    parser.add_argument('--interval', type=int, default=60, help='Seconds between runs')
    parser.add_argument('--score-threshold', type=float, default=0.9, help='Plausibility score threshold to accept')
    parser.add_argument('--parallel-variants', type=int, default=0, help='Set PipelineExecutor.parallel_hill_variants')
    parser.add_argument(
        '--artifact-root',
        type=Path,
        default=Path('artifacts'),
        help='Artifact root',
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[2]
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    # Build executor directly
    try:
        ex = build_pipeline(parallel_variants=int(args.parallel_variants))
    except Exception as exc:  # noqa: BLE001
        logging.exception('Failed to construct pipeline: %s', exc)
        return 2

    # configure
    ex.config.artifact_root = str(args.artifact_root)
    # parallel variants already set during build

    # prepare ciphertexts
    ciphers: list[str] = []
    if args.cipher:
        ciphers.append(args.cipher)
    if args.cipher_file and args.cipher_file.exists():
        with args.cipher_file.open('r', encoding='utf-8') as fh:
            for ln in fh:
                t = ln.strip()
                if t:
                    ciphers.append(t)
    if not ciphers:
        # default sample ciphertexts (small set)
        ciphers = [
            'OBKRUOXOGHULBSOLIFB',
        ]

    # scoring helper import (prefer installed/editable kryptos.k4, fallback to adding src to path)
    try:
        from kryptos.k4 import scoring as scoring_mod  # type: ignore
    except ImportError:
        sys.path.insert(0, str(repo_root / 'src'))
        try:
            from kryptos.k4 import scoring as scoring_mod  # type: ignore
        except ImportError:
            scoring_mod = None

    it = 0
    while True:
        it += 1
        logging.info('Cracker loop iteration %d', it)
        for c in ciphers:
            logging.info('Running pipeline on ciphertext: %s...', c[:40])
            try:
                summary = ex.run(c)
            except Exception:  # noqa: BLE001 (robust daemon loop)
                logging.exception('Pipeline run failed for cipher: %s', c[:40])
                continue

            # find latest run dir under artifact_root
            run_dir = find_latest_run_artifact(Path(ex.config.artifact_root))
            if not run_dir:
                logging.warning('No run artifacts found; continuing')
                continue

            tops = read_top_candidates(run_dir)
            logging.info('Top candidates (first 3): %s', tops[:3])

            # compute plausibility for the top candidate using combined_plaintext_score
            if tops:
                top = tops[0]
                # top stores text_prefix; try to recover more by reading attempt_log if needed
                candidate_text = top.get('text_prefix', '')
                try:
                    if scoring_mod is None:
                        raise RuntimeError('scoring module not available')
                    score = scoring_mod.combined_plaintext_score(candidate_text)
                except Exception:  # noqa: BLE001 (scoring robustness)
                    logging.exception('Scoring failed or module missing; skipping')
                    score = 0.0

                logging.info('Top candidate score=%.3f threshold=%.3f', score, args.score_threshold)
                if score >= args.score_threshold:
                    decision = {
                        'time': datetime.utcnow().isoformat(),
                        'cipher': c,
                        'candidate_prefix': candidate_text,
                        'score': score,
                        'run_dir': str(run_dir),
                        'summary': summary,
                    }
                    write_decision(repo_root, decision)
                    logging.info('Acceptable candidate found; decision written and exiting')
                    return 0

        logging.info('No acceptable candidate yet; sleeping %d seconds', args.interval)
        time.sleep(args.interval)


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
