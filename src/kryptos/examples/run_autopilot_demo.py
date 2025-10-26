"""Deprecated wrapper: use `python -m kryptos.examples.autopilot_demo`.

Retained briefly for migration; will be removed.
"""

from __future__ import annotations

import warnings

from kryptos.examples import run_autopilot_demo as _run

warnings.warn(
    ("Importing scripts.demo.run_autopilot_demo is deprecated; use " "python -m kryptos.examples.autopilot_demo"),
    DeprecationWarning,
    stacklevel=1,
)


def main():
    warnings.warn(
        ("scripts/demo/run_autopilot_demo.py deprecated; use " "python -m kryptos.examples.autopilot_demo"),
        DeprecationWarning,
        stacklevel=2,
    )
    _run()


if __name__ == "__main__":
    main()
