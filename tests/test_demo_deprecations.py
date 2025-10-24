from __future__ import annotations

import importlib
import warnings

DEMO_MODULES = [
    "scripts.demo.run_k4_demo",
    "scripts.demo.run_autopilot_demo",
    "scripts.demo.sample_composite_demo",
    "scripts.demo.sections_demo",
]


def test_demo_wrappers_emit_deprecation():
    for mod in DEMO_MODULES:
        with warnings.catch_warnings(record=True) as rec:
            warnings.simplefilter("always")
            importlib.import_module(mod)
            assert any(r.category is DeprecationWarning for r in rec), f"No DeprecationWarning for {mod}"
