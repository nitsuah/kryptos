"""Deprecated wrapper: use `python -m kryptos.examples.sections_demo`.

Will be removed; see DEPRECATIONS.md.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "Importing scripts.demo.sections_demo is deprecated; use python -m kryptos.examples.sections_demo",
    DeprecationWarning,
    stacklevel=1,
)

try:
    from kryptos.examples import run_sections_demo as _run
except ImportError:  # pragma: no cover
    _run = None


def main():  # pragma: no cover
    warnings.warn(
        "scripts/demo/sections_demo.py deprecated; use kryptos.examples.sections_demo",
        DeprecationWarning,
        stacklevel=2,
    )
    if _run is None:
        raise SystemExit("examples.sections_demo missing; update package")
    _run()


if __name__ == "__main__":  # pragma: no cover
    main()
