# Autopilot, SPY Tuning, and OPS Overview

This document summarizes the offline autopilot flow (Q / OPS / SPY), the conservative
SPY extractor, the SPY evaluation harness, and CI demo wiring added to the project.

## Components

- Q (Planner): produces a short plan or single-line recommended next action. Implemented in `scripts/dev/ask_triumverate.py` and helpers.
- OPS (Operational Tuner): runs tuning sweeps to measure sensitivity to crib weights and other parameters. Key scripts: `scripts/tuning/crib_weight_sweep.py`, `scripts/tuning/tiny_tuning_sweep.py`.
- SPY (Conservative Extractor): scans tuning run CSV artifacts and extracts high-confidence quoted tokens present in `docs/sources/sanborn_crib_candidates.txt`. Implemented in `scripts/dev/spy_extractor.py`.

## SPY threshold selection

- The SPY extractor accepts a minimum confidence via `SPY_MIN_CONF` env var or `--min-conf` CLI.
- If unset, the autopilot will call `kryptos.scripts.tuning.spy_eval.select_best_threshold` which evaluates precision/recall/F1 across thresholds and now *prefers precision* (conservative extraction). Tie-breaker is F1.

## Artifacts

- Tuning runs: `artifacts/tuning_runs/run_<timestamp>/` containing `crib_weight_sweep.csv` and `weight_*_details.csv`.
- Demo runs: `artifacts/demo/run_<timestamp>/` produced by `scripts/demo/run_k4_demo.py`.

## CI

- Fast CI (`.github/workflows/ci-fast.yml`) runs tests quickly and installs the package in editable mode.
- Slow CI (`.github/workflows/ci-slow.yml`) runs the K4 demo smoke test and uploads artifacts for debugging; it runs on pushes to `main` and manual dispatch.

## How to run locally

1. Install dev dependencies and the package in editable mode:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

2. Run the autopilot in dry-run:

```powershell
python scripts/dev/ask_triumverate.py --dry-run
```

3. Run the demo:

```powershell
python scripts/demo/run_k4_demo.py --limit 5
```
