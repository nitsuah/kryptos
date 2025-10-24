#!/usr/bin/env python3
"""Autonomous K4 cracker daemon (refactored to composite API).

Runs a lightweight multi-stage K4 composite pipeline using `run_composite_pipeline` and exits
when a candidate passes a plausibility score threshold.

DEPRECATED NOTE: Former PipelineExecutor usage removed. This script will be merged into a unified
CLI subcommand (`kryptos cli autopilot --cracker`) and then removed after the deprecation window.
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

from kryptos.k4 import persist_attempt_logs, run_composite_pipeline
from kryptos.k4.pipeline import (
    make_hill_constraint_stage,
    make_masking_stage,
    make_transposition_adaptive_stage,
    make_transposition_stage,
)


def _build_stages() -> list:
    """Construct default exploratory composite stage list."""
    return [
        make_hill_constraint_stage(name="hill", prune_3x3=True, partial_len=50, partial_min=-850.0),
        make_transposition_adaptive_stage(),
        make_transposition_stage(),
        make_masking_stage(name="masking", null_chars=["X"], limit=15),
    ]


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
    parser.add_argument('--adaptive', action='store_true', help='Enable adaptive fusion weighting')
    parser.add_argument(
        '--artifact-root',
        type=Path,
        default=Path('artifacts'),
        help='Artifact root',
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[2]
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    stages = _build_stages()

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
            logging.info('Running composite pipeline on ciphertext: %s...', c[:40])
            try:
                comp = run_composite_pipeline(
                    c,
                    stages,
                    report=True,
                    report_dir=str(args.artifact_root),
                    limit=50,
                    adaptive=args.adaptive,
                    normalize=True,
                )
            except Exception:  # noqa: BLE001 keep daemon alive
                logging.exception('Composite run failed for cipher: %s', c[:40])
                continue

            # aggregated or fused candidates
            fused = comp.get('fused') or []
            aggregated = comp.get('aggregated') or []
            ranking = fused if fused else aggregated
            logging.info('Top candidates (first 3): %s', [r.get('text')[:25] for r in ranking[:3]])

            if not ranking:
                logging.info('No candidates produced; continuing')
                continue

            best = ranking[0]
            candidate_text = best.get('text', '')
            try:
                if scoring_mod is None:
                    raise RuntimeError('scoring module unavailable')
                score = scoring_mod.combined_plaintext_score(candidate_text)
            except Exception:  # noqa: BLE001
                logging.exception('Scoring failed; assigning score=0.0')
                score = 0.0

            logging.info('Best candidate score=%.3f threshold=%.3f', score, args.score_threshold)
            if score >= args.score_threshold:
                # Persist attempt logs (already in composite artifacts) and write decision
                persist_attempt_logs(out_dir=str(args.artifact_root), label='CRACKER', clear=False)
                decision = {
                    'time': datetime.utcnow().isoformat(),
                    'cipher': c,
                    'candidate_prefix': candidate_text[:80],
                    'score': score,
                    'artifact_root': str(args.artifact_root),
                    'adaptive': bool(args.adaptive),
                    'provenance_hash': comp.get('profile', {}).get('provenance_hash'),
                }
                write_decision(repo_root, decision)
                logging.info('Acceptable candidate found; decision written and exiting')
                return 0

        logging.info('No acceptable candidate yet; sleeping %d seconds', args.interval)
        time.sleep(args.interval)


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
