"""Shim to expose repository script `scripts/tuning/spy_eval.py` as a package module.

This avoids importing from the filesystem path directly in tests and makes the
script available as `kryptos.scripts.tuning.spy_eval`.
"""

from importlib import import_module

_mod = import_module('scripts.tuning.spy_eval')

# Re-export functions used by tests
load_labels = _mod.load_labels
select_best_threshold = _mod.select_best_threshold
run_extractor_on_run = _mod.run_extractor_on_run
evaluate = _mod.evaluate

__all__ = [
    'load_labels',
    'select_best_threshold',
    'run_extractor_on_run',
    'evaluate',
]
