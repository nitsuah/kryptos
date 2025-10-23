#!/usr/bin/env python3
"""Autopilot daemon: periodically run the triumverate and stop on a safe decision.

This script imports and calls `run_plan_check` from `scripts/dev/ask_triumverate.py`.
It watches `artifacts/decisions` for the latest decision JSON and exits when the
decision meets safety criteria (holdout_pass True and spy_precision >= SAFE_PREC if
precision is available).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path


def find_latest_decision(repo_root: Path) -> Path | None:
    droot = repo_root / "artifacts" / "decisions"
    if not droot.exists():
        return None
    files = [p for p in droot.iterdir() if p.is_file()]
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def read_decision(path: Path) -> dict | None:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Run the autopilot triumverate in a loop")
    parser.add_argument("--iterations", type=int, default=0, help="Number of loops to run (0=infinite)")
    parser.add_argument("--interval", type=int, default=300, help="Seconds between runs")
    parser.add_argument("--plan", type=str, default=None, help="Optional plan text to pass to Q")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--force", dest="force", action="store_true", help="Allow destructive/non-dry runs")
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[2]

    # import the runner via file path to avoid package import issues
    try:
        import importlib.util

        ask_path = repo_root / 'scripts' / 'dev' / 'ask_triumverate.py'
        spec = importlib.util.spec_from_file_location('ask_triumverate_mod', str(ask_path))
        if spec is None or spec.loader is None:
            raise ImportError('Could not load ask_triumverate')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
        run_plan_check = mod.run_plan_check
    except Exception:
        # last resort: try package-style import
        try:
            from scripts.dev.ask_triumverate import run_plan_check  # type: ignore
        except Exception:
            raise

    SAFE_PREC = float(__import__("os").environ.get("AUTOPILOT_SAFE_PREC", "0.9"))

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    it = 0
    while True:
        it += 1
        logging.info("Autopilot iteration %d starting", it)
        try:
            run_plan_check(plan_text=args.plan, autopilot=True, dry_run=(not args.force and args.dry_run))
        except Exception as exc:  # keep the loop alive on unexpected errors
            logging.exception("run_plan_check failed: %s", exc)

        # check for latest decision
        latest = find_latest_decision(repo_root)
        if latest:
            d = read_decision(latest)
            if d:
                logging.info("Found decision: %s", latest.name)
                hold_ok = bool(d.get("holdout_pass"))
                prec = d.get("spy_precision")
                prec_ok = True
                if prec is not None:
                    try:
                        prec_ok = float(prec) >= SAFE_PREC
                    except Exception:
                        prec_ok = False

                if hold_ok and prec_ok:
                    logging.info("Decision meets safety criteria; exiting daemon.")
                    return 0
                logging.info("Decision not yet safe (holdout=%s, prec=%s); continuing.", hold_ok, prec)

        if args.iterations and it >= args.iterations:
            logging.info("Reached iteration limit (%d); stopping.", args.iterations)
            return 0

        logging.info("Sleeping %d seconds before next iteration", args.interval)
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
