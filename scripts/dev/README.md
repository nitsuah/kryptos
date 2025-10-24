# Autopilot dev README

This small README explains the local "autopilot" flow and how the SPY extractor threshold is chosen.

## Overview

- The autopilot orchestrator runs three logical components: Q (question/planner), OPS (operational
tuner/sweep), and SPY (conservative crib extractor).
- `scripts/dev/ask_triumverate.py` is a small driver that can run the autopilot loop in dry-run or
full-auto.

## SPY threshold selection

- The SPY extractor accepts a minimum confidence threshold via the environment variable
`SPY_MIN_CONF` or CLI `--min-conf`.
- If `SPY_MIN_CONF` is not set, the autopilot will call the SPY evaluation harness to compute a
recommended threshold from labeled tuning runs.
- The evaluation harness lives at `kryptos/scripts/tuning/spy_eval.py` and evaluates
precision/recall/F1 across thresholds.
- By default the harness now prefers a threshold that maximizes precision (conservative extraction).
If multiple thresholds have identical precision, it picks the one with the higher F1 score as a tie- breaker.

## Running locally

- To run the autopilot in dry-run mode:

```powershell
Set-Location 'C:\Users\<you>\code\kryptos'
python scripts/dev/ask_triumverate.py --dry-run
```

- To run full autopilot and allow SPY to run automatically (writes to `agents/LEARNED.md`):

```powershell
python scripts/dev/ask_triumverate.py
```

## Daemons (autonomous runs)

- `scripts/dev/autopilot_daemon.py` — periodically invokes the triumverate
(`ask_triumverate.run_plan_check`) and stops when a safe decision is produced. Useful for continuous background tuning
when you want the system to run unattended.
- `scripts/dev/cracker_daemon.py` — repeatedly runs the K4 pipeline against ciphertext(s) and writes
a decision artifact when a candidate exceeds a plausibility score threshold.

Examples:

```powershell
# Run the autopilot loop in dry-run mode every 5 minutes
python scripts/dev/autopilot_daemon.py --interval 300 --dry-run

# Run the cracker daemon against a ciphertext, stopping when candidate score >= 0.9
python scripts/dev/cracker_daemon.py --cipher 'OBKRUOXOGHULBSOLIFB' --score-threshold 0.9
```

## Safety / No-user-decision guarantee

- The autopilot will not auto-apply changes unless safety checks pass. By default the safety gate
requires `AUTOPILOT_SAFE_PREC=0.9` (90% precision) and no negative regression on the holdout set
(`AUTOPILOT_MAX_REGRESSION=0.0`).
- All automated decisions are written as JSON under `artifacts/decisions/decision_<timestamp>.json`
for audit and review.
- If you want manual control, run `scripts/dev/ask_triumverate.py --no-autopilot` to prevent any
autopilot actions.

- To override the computed threshold explicitly:

```powershell
$env:SPY_MIN_CONF = '0.5'
python scripts/dev/ask_triumverate.py
```

## Local editable install (recommended for development)

Install the project in editable mode so imports like `kryptos.scripts.tuning.spy_eval` resolve consistently:

```powershell
Set-Location 'C:\Users\<you>\code\kryptos'
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

After that you can run tests and demos normally (pytest, demo runner, etc.).

## Notes

- The evaluation harness expects labeled CSV in `data/spy_eval_labels.csv` with rows `run_dir,token`
and tuning runs under `artifacts/tuning_runs/run_<ts>/`.
- If you prefer to bias threshold selection to maximize recall (less conservative), we can change
the selection strategy in `kryptos/scripts/tuning/spy_eval.py`.
