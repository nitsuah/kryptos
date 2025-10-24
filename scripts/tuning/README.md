# Tuning

Single consolidated tool: `scripts/tuning.py`

## Usage

```bash
# Crib weight sweep
python scripts/tuning.py sweep --weights 0.1,0.5,1.0

# Analyze sweep results
python scripts/tuning.py analyze                    # Use latest run
python scripts/tuning.py analyze artifacts/tuning_runs/run_20251024T120000

# Rarity calibration (when implemented)
python scripts/tuning.py calibrate --k-values 1.0,3.0,5.0

# Quick parameter test
python scripts/tuning.py quick
```

## Commands

| Command | Purpose | Output |
|---------|---------|--------|
| `sweep` | Crib weight impact measurement | `crib_weight_sweep.csv` + detail CSVs |
| `analyze` | Recommend best weight from sweep | Prints best weight to stdout |
| `calibrate` | Rarity/positional deviation sweep | `calibration_<timestamp>.json` |
| `quick` | Fast deterministic param test | `summary.csv` + per-run CSVs |

## Artifacts

All runs write to `artifacts/tuning_runs/run_<timestamp>/`

## Why One File?

Previously 5 separate scripts:

- `crib_weight_sweep.py`
- `pick_best_weight.py`
- `tiny_tuning_sweep.py`
- `compare_crib_integration.py`
- `run_rarity_calibration.py`

**Consolidated to `scripts/tuning.py`** with subcommands. All logic delegates to `kryptos.k4.tuning` package APIs.

**Result:** 1 CLI tool instead of 5 separate scripts.
