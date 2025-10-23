"""Canonical K4 tuning utilities.

Authoritative home for crib weight sweep + param sweep helpers. Legacy
script duplicates under ``scripts/tuning`` are being deprecated; import
from this package instead of filesystem scripts.

Export list intentionally small: only pure functions without side-effects.
Artifact emission belongs in CLI wrappers.
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
