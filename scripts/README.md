# Scripts Directory

Organized scripts for Kryptos cryptanalysis system.

---

## Directory Structure

### `validation/` - K1-K3 Validation Scripts

**Purpose:** Verify our system can crack known Kryptos sections

- **`validate_known_kryptos.py`** - Comprehensive K1-K3 validation suite
- **`test_k123_unified_pipeline.py`** - Unified paradigm validation (shows current success rates)
- **`test_k3_transposition.py`** - Specific K3 transposition solver testing
- **`test_k4_execution.py`** - OPS agent attack execution testing

**Usage:**
```bash
# Run full K1-K3 validation
python scripts/validation/validate_known_kryptos.py

# Test unified pipeline (shows K1: 100%, K2: 3.8%, K3: 27.5%)
python scripts/validation/test_k123_unified_pipeline.py
```

**Current Status:**
- K1: ✅ 100% reliable
- K2: ⚠️ 3.8% (needs alphabet variant integration)
- K3: ⚠️ 27.5% (needs SA tuning)

---

### `benchmarks/` - Performance & Calibration

**Purpose:** Measure and optimize system performance

- **`benchmark_scoring.py`** - Benchmark dictionary scoring performance
- **`profile_scoring.py`** - Profile scoring functions for bottlenecks
- **`calibrate_scoring_weights.py`** - Tune validation pipeline weights
- **`tuning.py`** - General parameter tuning utilities

**Usage:**
```bash
python scripts/benchmarks/benchmark_scoring.py
python scripts/benchmarks/profile_scoring.py
```

---

### `experiments/` - Research & Prototypes

**Purpose:** Test new features and attack strategies

- **`test_exhaustive_search.py`** - Exhaustive permutation search (periods ≤8)
- **`test_attack_provenance.py`** - Attack logging and deduplication
- **`test_search_space.py`** - Coverage tracking validation
- **`test_attack_gen_simple.py`** - Attack generation from Q-hints
- **`demo_provenance.py`** - Demo of provenance logging system
- **`debug_word_detection.py`** - Debug dictionary scoring

**Usage:**
```bash
python scripts/experiments/test_exhaustive_search.py
python scripts/experiments/test_attack_provenance.py
```

---

### `archive/` - Historical Scripts

**Purpose:** Old test scripts kept for reference (no longer actively maintained)

---

### `lint/` - Code Quality

**Purpose:** Linting and formatting scripts

---

## Quick Start

### Validate System Works
```bash
# Full K1-K3 validation (recommended first step)
python scripts/validation/validate_known_kryptos.py

# See detailed success rates with explanations
python scripts/validation/test_k123_unified_pipeline.py
```

### Run Performance Benchmarks
```bash
python scripts/benchmarks/benchmark_scoring.py
```

### Test New Features
```bash
python scripts/experiments/test_attack_provenance.py
python scripts/experiments/test_search_space.py
```

---

## Phase 6 Priority Scripts

### Sprint 6.1: K2/K3 Fixes
Focus on these validation scripts:
- `validation/test_k123_unified_pipeline.py` - Track improvement
- `validation/test_k3_transposition.py` - Iterate on SA tuning
- `validation/validate_known_kryptos.py` - End-to-end validation

**Goal:** K2 to 100%, K3 to >95%

---

## Key Metrics to Track

### Validation Success Rates
- **K1 Vigenère:** Currently 100% ✅
- **K2 Vigenère:** Currently 3.8% (Target: 100%)
- **K3 Transposition:** Currently 27.5% (Target: >95%)
- **Composite V→T:** Currently 6.2% (Target: 100%)

### Performance Benchmarks
- **Attack throughput:** Currently 2.5/sec (Target: 10+/sec)
- **Dictionary scoring:** ~0.1ms per candidate
- **SA iterations:** 50k (Target: 100k-200k for K3)

---

## CLI Integration

Many functionalities are available via CLI:
- `kryptos k4-decrypt` - Run K4 attacks
- `kryptos autonomous` - Autonomous system
- `kryptos tuning-*` - Tuning operations

---

## References

- **Main docs:** `docs/PHASE_6_ROADMAP.md`
- **Gap analysis:** `docs/CRITICAL_GAP_ANALYSIS.md`
- **Phase 5 reference:** `docs/reference/phase5/`

---

**Last Updated:** October 25, 2025 **Phase:** 6.1 (K2/K3 Fixes) **Status:** Organized and ready for Sprint 6.1
