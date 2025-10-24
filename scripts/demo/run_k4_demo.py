"""Tiny K4 demo runner.

Runs a short, fast composite pipeline using existing stage factories in kryptos.k4
and writes artifacts under artifacts/demo/run_<ts>/.

This is intended to be fast and safe for CI/local experimentation.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from kryptos.k4 import make_hill_constraint_stage, make_masking_stage, persist_attempt_logs, run_composite_pipeline
from kryptos.logging import setup_logging


def run_demo(limit: int = 10):
    """Run a very small K4 composite pipeline and persist attempt logs.

    Returns the artifact directory path as a string.
    """
    setup_logging(level=logging.INFO, logger_name="kryptos.demo")
    log = logging.getLogger("kryptos.demo")

    # tiny cipher and minimal stages for demo speed
    cipher = 'OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTW'
    stages = [make_hill_constraint_stage(partial_len=30, partial_min=-200.0), make_masking_stage(limit=5)]

    run_composite_pipeline(
        cipher,
        stages,
        report=False,
        weights=None,
        normalize=True,
        adaptive=False,
        limit=limit,
    )

    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    out_dir = Path('artifacts') / 'demo' / f'run_{ts}'
    out_dir.mkdir(parents=True, exist_ok=True)

    # persist attempt logs into the demo directory
    persist_attempt_logs(out_dir=str(out_dir), label='K4-DEMO', clear=False)
    log.info('Demo complete. Artifacts written to: %s', out_dir)
    return str(out_dir)


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(description='Run a tiny K4 demo pipeline')
    p.add_argument('--limit', type=int, default=10, help='Result limit to produce')
    args = p.parse_args()
    run_demo(limit=args.limit)
