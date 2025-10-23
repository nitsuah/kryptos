"""Tuning utilities for K4 scoring heuristics.

This subpackage centralizes lightweight experimental helpers that were
previously implemented as ad-hoc scripts under ``scripts/tuning``.

Only stable, side‑effect free functions are exported here so they can be
unit tested and (optionally) wired into the CLI. File / artifact emitting
logic stays thin and is orchestrated by wrappers or future CLI commands.
"""

from .crib_sweep import (
    compare_crib_integration,
    pick_best_weight_from_rows,
    run_crib_weight_sweep,
    summarize_weight_sweep_rows,
    tiny_param_sweep,
)

__all__ = [
    'run_crib_weight_sweep',
    'summarize_weight_sweep_rows',
    'pick_best_weight_from_rows',
    'tiny_param_sweep',
    'compare_crib_integration',
]
