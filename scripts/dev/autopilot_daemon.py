#!/usr/bin/env python3
"""DEPRECATED Autopilot daemon.

Use unified forthcoming CLI subcommand (planned: `kryptos cli autopilot --loop`).
Will be removed after daemon merge. Tracks decisions in `artifacts/decisions`.
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
    import importlib.util

    ask_path = repo_root / 'scripts' / 'dev' / 'ask_triumverate.py'
    spec = importlib.util.spec_from_file_location('ask_triumverate_mod', str(ask_path))
    if not (spec and spec.loader):
        logging.error('Failed to load ask_triumverate at %s', ask_path)
        return 2
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    run_plan_check_obj = getattr(mod, 'run_plan_check', None)
    if not callable(run_plan_check_obj):
        logging.error('run_plan_check missing from ask_triumverate module')
        return 2

    SAFE_PREC = float(__import__("os").environ.get("AUTOPILOT_SAFE_PREC", "0.9"))

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    it = 0
    while True:
        it += 1
        logging.info("Autopilot iteration %d starting", it)
        try:
            run_plan_check_obj(plan_text=args.plan, autopilot=True, dry_run=(not args.force and args.dry_run))
        except (RuntimeError, ValueError) as exc:  # expected operational errors
            logging.exception("run_plan_check failed: %s", exc)
        except Exception as exc:  # noqa: BLE001 keep daemon alive for any unforeseen issue
            logging.exception('Unexpected error in run_plan_check: %s', exc)

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
                    except (TypeError, ValueError):
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
