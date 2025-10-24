# Tuning Scripts

Parameter calibration and scoring optimization tools for K4 cryptanalysis.

## 🎯 Purpose

These scripts help optimize scoring weights, crib bonuses, and other parameters to improve plaintext candidate ranking.
All scripts use package APIs from `kryptos.k4.tuning` and `kryptos.k4.scoring`.

## 📁 Scripts

### 1. `crib_weight_sweep.py`

**Purpose:** Measure impact of external crib weight on candidate scoring.

**What it does:**
- Tests multiple crib weight values (e.g., 0.1, 0.5, 1.0)
- Scores sample plaintexts with each weight
- Generates CSV artifacts showing score deltas

**Usage:**
```bash
python scripts/tuning/crib_weight_sweep.py --weights 0.1,0.5,1.0
```

**Outputs:**
- `artifacts/tuning_runs/run_<timestamp>/crib_weight_sweep.csv`
- `artifacts/tuning_runs/run_<timestamp>/<weight>_details.csv` (per weight)

**Delegates to:** `kryptos.k4.tuning.run_crib_weight_sweep()`

---

### 2. `pick_best_weight.py`

**Purpose:** Analyze crib weight sweep results and recommend best weight.

**What it does:**
- Reads `crib_weight_sweep.csv` from a run
- Computes mean delta for each weight
- Recommends weight with highest mean improvement

**Usage:**
```bash
# Use latest run
python scripts/tuning/pick_best_weight.py

# Specify run directory
python scripts/tuning/pick_best_weight.py artifacts/tuning_runs/run_20251024T120000
```

**Outputs:** Prints recommendation to stdout

---

### 3. `compare_crib_integration.py`

**Purpose:** Compare scoring with and without Sanborn-derived cribs.

**What it does:**
- Loads cribs from `docs/sources/sanborn_crib_candidates.txt`
- Scores samples with baseline (no cribs) vs augmented (with cribs)
- Shows before/after score differences

**Usage:**
```bash
python scripts/tuning/compare_crib_integration.py
```

**Outputs:**
- `artifacts/tuning_runs/run_<timestamp>/crib_integration.csv`

**Status:** Experimental - may be merged into main sweep

---

### 4. `tiny_tuning_sweep.py`

**Purpose:** Fast deterministic parameter sweep for local experimentation.

**What it does:**
- Tests small parameter grid (chi_weight, ngram_weight, crib_bonus)
- Scores 3 sample plaintexts
- Quick feedback on parameter sensitivity

**Usage:**
```bash
python scripts/tuning/tiny_tuning_sweep.py
```

**Outputs:**
- `artifacts/tuning_runs/run_<timestamp>/summary.csv`
- `artifacts/tuning_runs/run_<timestamp>/<runid>_top.csv`

**Use case:** Verify scoring changes before full sweep

---

### 5. `run_rarity_calibration.py`

**Purpose:** Calibrate rarity-weighted crib bonus and positional deviation weights.

**What it does:**
- Sweeps rarity k values (1.0, 2.0, 5.0, 10.0)
- Sweeps positional deviation weights (10.0, 20.0, 30.0, 40.0)
- Generates calibration report JSON

**Usage:**
```bash
# Default sweep
python scripts/tuning/run_rarity_calibration.py

# Custom ranges
python scripts/tuning/run_rarity_calibration.py \
    --k-values 1.0 3.0 5.0 \
    --pos-weights 15.0 25.0 35.0
```

**Outputs:**
- `artifacts/calibration/calibration_<timestamp>.json`

**Delegates to:** `kryptos.k4.calibration` module

---

## 🔄 Typical Workflow

1. **Initial calibration:**
   ```bash
   python scripts/tuning/run_rarity_calibration.py
   ```

2. **Crib weight sweep:**
   ```bash
   python scripts/tuning/crib_weight_sweep.py --weights 0.1,0.3,0.5,1.0
   ```

3. **Analyze results:**
   ```bash
   python scripts/tuning/pick_best_weight.py
   ```

4. **Quick sanity check:**
   ```bash
   python scripts/tuning/tiny_tuning_sweep.py
   ```

## 📊 Artifact Structure

All tuning runs write to `artifacts/tuning_runs/run_<timestamp>/`:

```text
artifacts/tuning_runs/
└── run_20251024T120000/
    ├── crib_weight_sweep.csv     # Main sweep results
    ├── 0.1_details.csv            # Per-weight details
    ├── 0.5_details.csv
    ├── 1.0_details.csv
    └── summary.csv                # Metadata
```

## 🔧 Adding New Tuning Scripts

**Best practice:** Implement logic in package (`kryptos.k4.tuning`), create thin CLI wrapper here.

**Template:**
```python
"""Short description."""
import argparse
from kryptos.k4.tuning import your_function

def main():
    parser = argparse.ArgumentParser()
    # add args
    args = parser.parse_args()
    results = your_function(args.param)
    print(f"Results: {results}")

if __name__ == '__main__':
    raise SystemExit(main())
```

## 🧹 Maintenance

**Status:** All scripts use package APIs (no duplicate logic) ✅

**Next improvements:**
- Consolidate `compare_crib_integration.py` into main sweep
- Add CLI subcommands to replace individual scripts
- Create unified tuning dashboard

---

**Last Updated:** 2025-10-24
