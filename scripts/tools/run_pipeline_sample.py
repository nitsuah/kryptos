#!/usr/bin/env python3
"""Minimal executable sample to exercise PipelineExecutor.

Creates a small pipeline (hill constraint + masking) and runs it on a short
slice of the K4 ciphertext. Produces artifacts under artifacts/run_<timestamp>/.

Usage (PowerShell):
    python scripts/tools/run_pipeline_sample.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure repository root on path when executing as a script.
ROOT = Path(__file__).resolve().parents[2]  # kryptos project root
SRC_DIR = ROOT / 'src'
# Ensure both repo root and src are importable depending on environment
for p in (str(ROOT), str(SRC_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Try a few import fallbacks depending on how the workspace is invoked
try:  # pragma: no cover - import resolution logic
    from src.k4.executor import PipelineConfig, PipelineExecutor  # type: ignore
    from src.k4.pipeline import make_hill_constraint_stage, make_masking_stage  # type: ignore
except ImportError:  # pragma: no cover
    try:
        from k4.executor import PipelineConfig, PipelineExecutor  # type: ignore
        from k4.pipeline import make_hill_constraint_stage, make_masking_stage  # type: ignore
    except ImportError:  # pragma: no cover
        from kryptos.src.k4.executor import PipelineConfig, PipelineExecutor  # type: ignore
        from kryptos.src.k4.pipeline import make_hill_constraint_stage, make_masking_stage  # type: ignore

# Short slice of K4 for quick run
CIPHERTEXT = "OBKRUOXOGHULBSOLIFB"


def build_pipeline() -> PipelineExecutor:
    stages = [
        make_hill_constraint_stage(name="hill", prune_3x3=True, partial_len=40, partial_min=-900.0),
        make_masking_stage(name="masking", null_chars=["X"], limit=15),
    ]
    cfg = PipelineConfig(
        ordering=stages,
        candidate_cap_per_stage=25,
        pruning_top_n=10,
        crib_bonus_threshold=5.0,
        adaptive_thresholds={"hill": -500.0},
        artifact_root="artifacts",
        label="sample-run",
        enable_attempt_log=True,
        parallel_hill_variants=0,
    )
    return PipelineExecutor(cfg)


def main() -> None:
    executor = build_pipeline()
    summary = executor.run(CIPHERTEXT)
    # Find most recent artifact dir (created inside executor)
    art_dir_parent = Path("artifacts")
    run_dirs = sorted([d for d in art_dir_parent.glob("run_*") if d.is_dir()], reverse=True)
    latest = run_dirs[0] if run_dirs else None
    print("Pipeline summary:")
    print(summary)
    if latest:
        print(f"Artifacts in: {latest}")
        print(f" - attempt_log.jsonl exists: {os.path.exists(latest / 'attempt_log.jsonl')}")
        print(f" - summary.json exists: {os.path.exists(latest / 'summary.json')}")


if __name__ == "__main__":
    main()
