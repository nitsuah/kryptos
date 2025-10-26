"""Deprecated wrapper: use `python -m kryptos.examples.composite_demo`.

Kept temporarily for backward compatibility; will be removed per timeline in DEPRECATIONS.md.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "Importing scripts.demo.sample_composite_demo is deprecated; use python -m kryptos.examples.composite_demo",
    DeprecationWarning,
    stacklevel=1,
)

try:
    from kryptos.examples import run_composite_demo as _run
except ImportError:
    _run = None


def main():
    warnings.warn(
        "scripts/demo/sample_composite_demo.py deprecated; use kryptos.examples.composite_demo",
        DeprecationWarning,
        stacklevel=2,
    )
    if _run is None:
        raise SystemExit("examples.composite_demo missing; update package")
    _run()


if __name__ == "__main__":
    main()
