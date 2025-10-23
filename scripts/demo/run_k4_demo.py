"""Tiny K4 demo runner.

Runs a short, fast composite pipeline using existing stage factories in src.k4
and writes artifacts under artifacts/demo/run_<ts>/.

This is intended to be fast and safe for CI/local experimentation.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path


def run_demo(limit: int = 10):
    # Prefer installed package import, fall back to src/ in workspace or adding project root
    try:
        from kryptos.src.k4 import (
            make_hill_constraint_stage,
            make_masking_stage,
            persist_attempt_logs,
            run_composite_pipeline,
        )
    except ImportError:
        try:
            from src.k4 import (
                make_hill_constraint_stage,
                make_masking_stage,
                persist_attempt_logs,
                run_composite_pipeline,
            )
        except ImportError:
            PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            if PROJECT_ROOT not in sys.path:
                sys.path.insert(0, PROJECT_ROOT)
            from src.k4 import (
                make_hill_constraint_stage,
                make_masking_stage,
                persist_attempt_logs,
                run_composite_pipeline,
            )

    # tiny cipher and minimal stages for demo speed
    cipher = 'OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTW'
    stages = [make_hill_constraint_stage(partial_len=30, partial_min=-200.0), make_masking_stage(limit=5)]

    weights = None
    run_composite_pipeline(
        cipher,
        stages,
        report=False,
        weights=weights,
        normalize=True,
        adaptive=False,
        limit=limit,
    )

    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    out_dir = Path('artifacts') / 'demo' / f'run_{ts}'
    out_dir.mkdir(parents=True, exist_ok=True)

    # persist attempt logs into the demo directory
    persist_attempt_logs(out_dir=str(out_dir), label='K4-DEMO', clear=False)
    print('Demo complete. Artifacts written to:', out_dir)
    return str(out_dir)


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(description='Run a tiny K4 demo pipeline')
    p.add_argument('--limit', type=int, default=10, help='Result limit to produce')
    args = p.parse_args()
    run_demo(limit=args.limit)
