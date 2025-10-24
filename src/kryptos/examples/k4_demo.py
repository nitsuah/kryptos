"""K4 demo runner (migrated from scripts/demo/run_k4_demo.py).

Runs a tiny composite pipeline and writes artifacts under
    artifacts/demo/run_<timestamp>/
using the centralized path helpers.
"""

from __future__ import annotations

import logging
from datetime import datetime

from kryptos.k4.attempt_logging import persist_attempt_logs
from kryptos.k4.composite import run_composite_pipeline
from kryptos.k4.pipeline import make_hill_constraint_stage, make_masking_stage
from kryptos.logging import setup_logging
from kryptos.paths import get_artifacts_root


def run_demo(limit: int = 10) -> str:
    setup_logging(level=logging.INFO, logger_name="kryptos.demo")
    log = logging.getLogger("kryptos.demo")

    cipher = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTW"
    stages = [
        make_hill_constraint_stage(partial_len=30, partial_min=-200.0),
        make_masking_stage(limit=5),
    ]

    run_composite_pipeline(
        cipher,
        stages,
        report=False,
        weights=None,
        normalize=True,
        adaptive=False,
        limit=limit,
    )

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_dir = get_artifacts_root() / "demo" / f"run_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    persist_attempt_logs(out_dir=str(out_dir), label="K4-DEMO", clear=False)
    log.info("Demo complete. Artifacts written to: %s", out_dir)
    return str(out_dir)


def _main() -> None:  # pragma: no cover
    import argparse

    p = argparse.ArgumentParser(description="Run a tiny K4 demo pipeline")
    p.add_argument("--limit", type=int, default=10, help="Result limit to produce")
    args = p.parse_args()
    run_demo(limit=args.limit)


if __name__ == "__main__":  # pragma: no cover
    _main()
