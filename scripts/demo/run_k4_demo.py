"""Deprecated wrapper: use `python -m kryptos.examples.k4_demo`.

Kept temporarily for backward compatibility; will be removed after migration window.
"""

from __future__ import annotations

import warnings

from kryptos.examples import run_demo as _run_demo


def run_demo(limit: int = 10):  # pragma: no cover
    warnings.warn(
        "scripts/demo/run_k4_demo.py is deprecated; use kryptos.examples.k4_demo",
        DeprecationWarning,
        stacklevel=2,
    )
    return _run_demo(limit=limit)


if __name__ == "__main__":  # pragma: no cover
    run_demo()
