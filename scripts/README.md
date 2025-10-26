# Scripts Directory# Scripts Directory



**Status:** Cleaned up (January 27, 2025)Organized scripts for Kryptos cryptanalysis system.



------



## Current Contents## Directory Structure



### `lint/` - Code Quality Tools### `validation/` - K1-K3 Validation Scripts



Development utilities for code quality:**Purpose:** Verify our system can crack known Kryptos sections



- **`autofix_unused_vars.py`** - Automatically fix unused variable warnings- **`validate_known_kryptos.py`** -
Comprehensive K1-K3 validation suite

- **`mdlint.py`** - Markdown linting utility- **`test_k123_unified_pipeline.py`** - Unified paradigm validation (shows
current success rates)

- **`README.md`** - Lint tools documentation- **`test_k3_transposition.py`** - Specific K3 transposition solver testing

- **`test_k4_execution.py`** - OPS agent attack execution testing

**Usage:**

**Usage:**

```bash

python scripts/lint/autofix_unused_vars.py```bash

python scripts/lint/mdlint.py# Run full K1-K3 validation

```python scripts/validation/validate_known_kryptos.py



---# Test unified pipeline (shows K1: 100%, K2: 3.8%, K3: 27.5%)

python scripts/validation/test_k123_unified_pipeline.py

## Recent Cleanup (January 27, 2025)```



**Deleted 7 development/debugging scripts** - All functionality migrated to proper tests:**Current Status:**



- `test_k1_recovery.py` → Covered by `tests/test_k1_k2_monte_carlo.py`- K1: ✅ 100% reliable

- `test_k2_recovery.py` → Covered by `tests/test_k1_k2_monte_carlo.py`- K2: ⚠️ 3.8% (needs alphabet variant integration)

- `test_ranking.py` → Validated by Monte Carlo tests- K3: ⚠️ 27.5% (needs SA tuning)

- `test_raw_generation.py` → Validated by Monte Carlo tests

- `test_column_scoring.py` → Validated by Monte Carlo tests---

- `debug_k2_positions.py` → Validated by Monte Carlo tests

- `test_col_positions.py` → Broken import, functionality redundant### `lint/` - Code Quality



**Rationale:** All development/debugging work complete. Comprehensive test suite now provides better coverage than
manual scripts.**Purpose:** Linting and formatting scripts



**Documentation:** See `docs/audits/SCRIPTS_CLEANUP_2025-01-27.md` for detailed analysis.---



---## Quick Start



## Validation Results (Measured)### Validate System Works



**K1/K2/K3 autonomous solving validated with Monte Carlo testing:**```bash

# Full K1-K3 validation (recommended first step)

- **K1 Vigenère:** ✅ **100%** success (50/50 runs, deterministic)python scripts/validation/validate_known_kryptos.py

- **K2 Vigenère:** ✅ **100%** success (50/50 runs, deterministic) - 26.3x better than old claim

- **K3 Transposition (P5):** ✅ **68%** success (50 runs) - 2.5x better than claimed# See detailed success rates with
explanations

- **K3 Transposition (P6):** ✅ **83%** success (30 runs) - 3.0x better than claimedpython
scripts/validation/test_k123_unified_pipeline.py

- **K3 Transposition (P7):** ✅ **95%** success (20 runs) - 3.5x better than claimed```



**See:**### Run Performance Benchmarks



- `docs/analysis/K1_K2_VALIDATION_RESULTS.md` - Comprehensive K1/K2 analysis```bash

- `docs/analysis/K3_VALIDATION_RESULTS.md` - Comprehensive K3 analysispython scripts/benchmarks/benchmark_scoring.py

- `tests/test_k1_k2_monte_carlo.py` - K1/K2 Monte Carlo tests```

- `tests/test_k3_monte_carlo_comprehensive.py` - K3 Monte Carlo tests

### Test New Features

---

---

## Development Workflow

## Phase 6 Priority Scripts

### For New Features

### Sprint 6.1: K2/K3 Fixes

1. **Develop** - Write code in `src/kryptos/`

2. **Test** - Write tests in `tests/` (not scripts)Focus on these validation scripts:

3. **Validate** - Run pytest to verify

4. **Document** - Update docs if needed- `validation/test_k123_unified_pipeline.py` - Track improvement

- `validation/test_k3_transposition.py` - Iterate on SA tuning

### For Debugging- `validation/validate_known_kryptos.py` - End-to-end validation



1. **Use pytest** - Run existing tests with `-xvs` flags**Goal:** K2 to 100%, K3 to >95%

2. **Add temporary debug** - In test files (remove after)

3. **Write temp script if needed** - But delete when done---

4. **Never commit debug scripts** - They become technical debt

## Key Metrics to Track

### Following Maintenance Guide

### Validation Success Rates

**Read:** `docs/MAINTENANCE_GUIDE.md`

- **K1 Vigenère:** Currently 100% ✅

**Key principles:**- **K2 Vigenère:** Currently 3.8% (Target: 100%)

- **K3 Transposition:** Currently 27.5% (Target: >95%)

- Tests are sacred (understand before modifying)- **Composite V→T:** Currently 6.2% (Target: 100%)

- Scripts are temporary (production them or delete them)

- Docs decay (prune regularly)### Performance Benchmarks

- Knowledge preservation (keep context, delete clutter)

- **Attack throughput:** Currently 2.5/sec (Target: 10+/sec)

---- **Dictionary scoring:** ~0.1ms per candidate

- **SA iterations:** 50k (Target: 100k-200k for K3)

## What Happened to validation/?

---

**Old claim:** "K2: 3.8% success"

## CLI Integration

**Measured reality:** K2: 100% success (deterministic, perfect)

Many functionalities are available via CLI:

The `validation/` folder was deleted October 25, 2025 (commit ec01d2b). The proper solution is comprehensive Monte Carlo
tests in `tests/`, which:

- `kryptos k4-decrypt` - Run K4 attacks

- Run automatically in CI- `kryptos autonomous` - Autonomous system

- Are version controlled- `kryptos tuning-*` - Tuning operations

- Have clear pass/fail criteria

- Measure actual performance---

- Can't bitrot (pytest runs them regularly)

## References

**Bottom line:** Validation belongs in `tests/`, not `scripts/`.

- **Main docs:** `docs/PHASE_6_ROADMAP.md`

---

---

## References

**Last Updated:** October 25, 2025 **Phase:** 6.1 (K2/K3 Fixes) **Status:** Organized and ready for Sprint 6.1

- **Validation results:** `docs/analysis/K1_K2_VALIDATION_RESULTS.md`, `docs/analysis/K3_VALIDATION_RESULTS.md`
- **Test suite:** `tests/test_*_monte_carlo.py`
- **Maintenance guide:** `docs/MAINTENANCE_GUIDE.md`
- **Roadmap:** `docs/PHASE_6_ROADMAP.md` (needs update with measured metrics)

---

**Last Updated:** January 27, 2025 **Maintainer:** See `CONTRIBUTING.md`
