"""Copy of manager_daemon for scripts/dev (shim content retained).

This file is a copy of the original `scripts/manager_daemon.py` and placed under
`scripts/dev/` as part of the reorganization. It will be the canonical location for
daemon tooling.
"""

from __future__ import annotations

import csv
import datetime
import json
import shutil
from collections.abc import Iterable, Mapping
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
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

            spec = importlib.util.spec_from_file_location(
                "tune_pipeline",
                str(ROOT / "scripts" / "tuning" / "tune_pipeline.py"),
            )
            mod = importlib.util.module_from_spec(spec) if spec else None
            if spec and mod:
                spec.loader.exec_module(mod)  # type: ignore
                # Expect mod.run_sweep to accept params and return iterable of dict rows
                raw = getattr(mod, "run_sweep", None)
                if raw:
                    # raw may be a callable returning rows or an iterable of rows
                    if callable(raw):
                        rows = raw(params)
                    else:
                        rows = list(raw)
                    for row in rows:
                        results.append(row)
                else:
                    # fallback: write a small placeholder
                    results.append({"param_set": json.dumps(params), "run": 0, "best_score": 0.0})
            else:
                results.append({"param_set": json.dumps(params), "run": 0, "best_score": 0.0})
        except (OSError, ImportError):
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
        except OSError:
            pass

    return csv_path
