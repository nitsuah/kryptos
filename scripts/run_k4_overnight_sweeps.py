#!/usr/bin/env python
"""Thin CLI entry point for kryptos.k4.overnight_runner.run_all_pending_sweeps.

Runs every registered K4 full-scope sweep in order, printing progress as
it goes, and exits non-zero (with a loud message) if any sweep raises a
EurekaSignal breakthrough -- reusable logic lives in
``kryptos.k4.overnight_runner``, not here (see scripts/README.md).

Usage:
    python scripts/run_k4_overnight_sweeps.py
"""

from __future__ import annotations

import sys

from kryptos.k4.overnight_runner import run_all_pending_sweeps


def _progress(name: str, status: str) -> None:
    print(f"[{name}] {status}", flush=True)


def main() -> int:
    result = run_all_pending_sweeps(progress_cb=_progress)
    if result["status"] == "breakthrough":
        print(f"\n*** BREAKTHROUGH in sweep '{result['breakthrough_sweep']}' -- see snapshot path above ***")
        return 1
    print(f"\nAll {len(result['sweeps_run'])} sweeps complete, all null.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
