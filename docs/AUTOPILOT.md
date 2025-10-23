# Autopilot, SPY Tuning, and OPS Overview

This document summarizes the offline autopilot flow (Q / OPS / SPY), the conservative SPY extractor,
the SPY evaluation harness, and CI demo wiring added to the project.

Related documents / breadcrumbs:

- Project core: `README_CORE.md`
- K4 strategy: `K4_STRATEGY.md`
- Plan: `PLAN.md`
- Roadmap: `../ROADMAP.md`

## Components

- Q (Planner): produces a short plan or single-line recommended next action. Implemented in
`scripts/dev/ask_triumverate.py` and helpers.
- OPS (Operational Tuner): runs tuning sweeps to measure sensitivity to crib weights and other
parameters. Canonical APIs: `kryptos.k4.tuning.run_crib_weight_sweep`,
`kryptos.k4.tuning.tiny_param_sweep`, and artifact helpers in `kryptos.k4.tuning.artifacts` (legacy
script wrappers pending CLI promotion).
- SPY (Conservative Extractor): scans tuning run CSV artifacts and extracts high-confidence quoted
tokens present in `docs/sources/sanborn_crib_candidates.txt`. Implemented presently as
`scripts/dev/spy_extractor.py` (will migrate to a CLI subcommand `kryptos spy extract`).

## SPY threshold selection

- The SPY extractor accepts a minimum confidence via `SPY_MIN_CONF` env var or `--min-conf` CLI.
- If unset, the autopilot will call `kryptos.scripts.tuning.spy_eval.select_best_threshold` which
evaluates precision/recall/F1 across thresholds and now *prefers precision* (conservative
extraction). Tie-breaker is F1.

Notes and defaults:

- If `SPY_MIN_CONF` is not set and `select_best_threshold` cannot determine a threshold (no labels
or runs available), the autopilot will fall back to a conservative default of `0.25`.
- The SPY extractor computes a per-token confidence as `delta / max_delta` where `delta` is the run-
specific match delta and `max_delta` is the maximum delta observed in that run's scan. The `--min-
conf` threshold is applied to that normalized confidence to decide which tokens to emit.

Example: evaluating thresholds (package API):

```powershell
python - <<'PY'
from pathlib import Path
from kryptos.tuning import spy_eval
labels = Path('data/spy_eval_labels.csv')
runs = Path('artifacts/tuning_runs')
print('Eval summary:', spy_eval.evaluate(labels, runs))
print('Best threshold:', spy_eval.select_best_threshold(labels, runs))
PY
```

Programmatic selection (precision-first):

```python
from pathlib import Path
from kryptos.tuning import spy_eval

labels = Path('data/spy_eval_labels.csv')
runs = Path('artifacts/tuning_runs')
best = spy_eval.select_best_threshold(labels, runs)
print('Best threshold:', best)
```

## Artifacts

- Tuning runs: `artifacts/tuning_runs/run_<timestamp>/` containing `crib_weight_sweep.csv` and
per-weight detail CSVs.
- Demo runs: `artifacts/demo/run_<timestamp>/` (legacy demo script; consider CLI `k4-demo`).
- Decision artifacts: `artifacts/decisions/decision_<timestamp>.json`.

## Autonomous daemons

- `scripts/dev/autopilot_daemon.py` — periodically invokes the triumverate
(`ask_triumverate.run_plan_check`) and exits when a safe decision artifact is created. Useful for
background tuning and sweep automation.
- `scripts/dev/cracker_daemon.py` — runs the K4 pipeline repeatedly against ciphertext(s) and writes
a decision artifact when a candidate passes a plausibility threshold.

All decisions are written to:

```powershell
artifacts/decisions/decision_<timestamp>.json
```

Each decision JSON includes: time, run_dir, best_weight, spy_min_conf, spy_precision, holdout
results and `holdout_pass`.

## Safety: no user decisions required

- The autopilot will not auto-apply changes unless safety checks pass. Default safety policy:

  - `AUTOPILOT_SAFE_PREC` (env var): minimum required SPY precision to auto-apply (default `0.9`).
  - `AUTOPILOT_MAX_REGRESSION` (env var): allowed negative mean delta on holdout (default `0.0`).

- If precision cannot be computed because no labeled matches exist, the system will not auto-apply
and will instead write a decision JSON for human review.

- If you prefer manual control, call the driver with `--no-autopilot` or run `ask_triumverate.py`
directly and inspect the decision JSONs under `artifacts/decisions/`.

## CI

- Fast CI (`.github/workflows/ci-fast.yml`) runs tests quickly and installs the package in editable
mode.
- Slow CI (`.github/workflows/ci-slow.yml`) runs the K4 demo smoke test and uploads artifacts for
debugging; it runs on pushes to `main` and manual dispatch.

## How to run locally

1. Install dev dependencies and the package in editable mode:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

1. Run the autopilot in dry-run:

```powershell
python scripts/dev/ask_triumverate.py --dry-run  # (CLI subcommand forthcoming: kryptos autopilot)
```

1. Run the demo:

```powershell
python scripts/demo/run_k4_demo.py --limit 5  # or: kryptos k4-decrypt --limit 5 --report
```

Try a quick smoke-run (demo → tiny OPS sweep → SPY extractor → condensed report):

```powershell
# Deprecated: replace with direct package tuning & artifacts API calls (forthcoming CLI)
python scripts/experimental/examples/run_full_smoke.py
```

## Forthcoming CLI Enhancements

Planned subcommands to replace legacy scripts:

- `kryptos tuning crib-weight-sweep` → `run_crib_weight_sweep`
- `kryptos tuning summarize-run` → `kryptos.k4.tuning.artifacts.end_to_end_process`
- `kryptos spy extract` → conservative SPY token extraction
- `kryptos spy eval` → threshold evaluation (`kryptos.tuning.spy_eval`)

--- Last updated: 2025-10-23 (tuning API promotion + CLI roadmap)
