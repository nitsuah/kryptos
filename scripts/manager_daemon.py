"""Minimal daemon/manager to orchestrate tuning sweeps and archive results.

Usage: import and call run() or execute as a script. Contains a dry-run mode
that doesn't execute heavy jobs (useful for tests).

This file intentionally avoids network calls and runs the existing tuning
script via its Python entrypoint if present.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import shutil
import time
from collections.abc import Iterable, Mapping
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "tuning_runs"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def default_param_grid() -> Iterable[Mapping[str, int]]:
    # Very small deterministic grid for quick runs; expand later.
    for prune in (10, 15):
        for cap in (20, 40):
            yield {"pruning_top_n": prune, "candidate_cap": cap}


def run_sweep(params: Mapping[str, int], dry_run: bool = False) -> Path:
    """Run a single tuning sweep with params and write a CSV summary.

    Returns the path to the written CSV file.
    """
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_dir = ARTIFACT_DIR / f"run_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Assemble a fake result if dry-run, otherwise try to call the tuning script
    results = []
    if dry_run:
        # produce deterministic fake rows
        for i in range(4):
            results.append({"param_set": json.dumps(params), "run": i, "best_score": 0.1 * (i + 1)})
    else:
        # If scripts/tune_pipeline.py exists and provides a run_sweep function, call it.
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location("tune_pipeline", str(ROOT / "scripts" / "tune_pipeline.py"))
            mod = importlib.util.module_from_spec(spec) if spec else None
            if spec and mod:
                spec.loader.exec_module(mod)  # type: ignore
                # Expect mod.run_sweep to accept params and return iterable of dict rows
                raw = getattr(mod, "run_sweep", None)
                if raw:
                    for row in raw(params):
                        results.append(row)
                else:
                    # fallback: write a small placeholder
                    results.append({"param_set": json.dumps(params), "run": 0, "best_score": 0.0})
            else:
                results.append({"param_set": json.dumps(params), "run": 0, "best_score": 0.0})
        except Exception:
            # Do not allow daemon to crash; record an error row
            results.append({"param_set": json.dumps(params), "run": 0, "best_score": -1.0, "error": "exception"})

    csv_path = out_dir / "summary.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = None
        for row in results:
            if writer is None:
                writer = csv.DictWriter(fh, fieldnames=list(row.keys()))
                writer.writeheader()
            writer.writerow(row)

    # Basic archival: keep only last 20 runs
    runs = sorted(ARTIFACT_DIR.glob("run_*"), key=lambda p: p.name, reverse=True)
    for old in runs[20:]:
        try:
            shutil.rmtree(old)
        except Exception:
            pass

    return csv_path


def filter_top_candidates(csv_path: Path, top_n: int = 5) -> Path:
    """Simple filter that reads summary CSV and writes top_n rows by best_score."""
    rows = []
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            try:
                score = float(r.get("best_score") or 0.0)
            except Exception:
                score = -9999.0
            r["_score_f"] = score
            rows.append(r)
    rows.sort(key=lambda r: r["_score_f"], reverse=True)
    out = csv_path.with_name(csv_path.stem + "_top.csv")
    with out.open("w", encoding="utf-8", newline="") as fh:
        if not rows:
            fh.write("")
            return out
        keys = [k for k in rows[0].keys() if not k.startswith("_")]
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writeheader()
        for r in rows[:top_n]:
            writer.writerow({k: r.get(k, "") for k in keys})
    return out


def run(loop_delay: int = 10, dry_run: bool = True):
    """Main loop: iterate param grid and run sweep for each set.

    loop_delay: seconds between param sets (keeps loop friendly).
    dry_run: when True, do not execute heavy operations.
    """
    try:
        while True:
            for params in default_param_grid():
                csvp = run_sweep(params, dry_run=dry_run)
                filter_top_candidates(csvp, top_n=3)
                # friendly sleep between runs
                time.sleep(loop_delay)
            # one pass completed; brief pause
            time.sleep(loop_delay)
    except KeyboardInterrupt:
        print("Daemon stopped by user")


def _main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true", help="Do not execute heavy jobs; produce deterministic output.")
    p.add_argument("--delay", type=int, default=2, help="Seconds delay between runs (default: 2).")
    args = p.parse_args()
    run(loop_delay=args.delay, dry_run=args.dry_run)


if __name__ == "__main__":
    _main()
