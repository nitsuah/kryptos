#!/usr/bin/env python3
"""DEPRECATED: minimal pipeline sample wrapper.

Scheduled for removal once docs updated. Prefer:

    from kryptos.k4.pipeline import make_hill_constraint_stage, make_masking_stage
    from kryptos.k4.executor import PipelineConfig, PipelineExecutor

No module-level path mutations; safe to import without side effects.
"""

from __future__ import annotations

import os
from pathlib import Path

from kryptos.k4.executor import PipelineConfig, PipelineExecutor  # type: ignore
from kryptos.k4.pipeline import make_hill_constraint_stage, make_masking_stage  # type: ignore

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
