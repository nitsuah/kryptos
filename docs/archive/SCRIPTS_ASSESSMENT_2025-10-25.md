# Scripts Assessment & Cleanup Plan

**Date:** October 25, 2025 **Purpose:** Assess scripts/ directory for tech debt, legacy code, and migration
opportunities

---

## Current State

### Active Scripts (5)

| Script | Purpose | Status | Action |
|--------|---------|--------|--------|
| **benchmark_scoring.py** | Quick scoring benchmarks | ✅ KEEP | Active development tool |
| **profile_scoring.py** | cProfile analysis | ✅ KEEP | Active development tool |
| **calibrate_scoring_weights.py** | Grid search weight optimization | ✅ KEEP | Occasional use |
| **tuning.py** | Main tuning orchestrator | ✅ KEEP | Active development tool |
| **demo_provenance.py** | Demo attack provenance system | ⚠️ ARCHIVE | Educational - move to examples/ |

### Supporting Directories

| Directory | Purpose | Status | Action |
|-----------|---------|--------|--------|
| **dev/** | Development utilities | ⚠️ ASSESS | Contains legacy orchestrator |
| **lint/** | Linting utilities | ✅ KEEP | mdlint.py active |
| **__pycache__/** | Python cache | 🗑️ DELETE | .gitignore'd |

---

## Detailed Assessment

### 1. benchmark_scoring.py ✅ KEEP

**Purpose:** Quick benchmarks with readable output **Status:** Active, well-maintained **Usage:** `python
scripts/benchmark_scoring.py`

**Why Keep:**
- Essential for performance validation
- Quick feedback loop (1-2 seconds)
- Referenced in PERFORMANCE_OPTIMIZATION.md
- Used during test optimization

**No Action Required**

---

### 2. profile_scoring.py ✅ KEEP

**Purpose:** cProfile analysis for hotspot identification **Status:** Active, well-maintained **Usage:** `python
scripts/profile_scoring.py`

**Why Keep:**
- Critical for performance debugging
- Identifies bottlenecks in scoring pipeline
- Generates detailed profiling reports
- Used during Phase 4 optimization

**No Action Required**

---

### 3. calibrate_scoring_weights.py ✅ KEEP

**Purpose:** Grid search for optimal scoring weights **Status:** Active but infrequent use **Usage:** `python
scripts/calibrate_scoring_weights.py`

**Why Keep:**
- One-time calibration for each scoring metric
- Historical baseline establishment
- May need re-run if scoring changes
- Documents methodology for SCORING_CALIBRATION.md

**No Action Required**

---

### 4. tuning.py ✅ KEEP

**Purpose:** Main tuning orchestration script **Status:** Active, complex (277+ lines) **Usage:** `python
scripts/tuning.py --help`

**Why Keep:**
- Orchestrates multiple tuning workflows
- CLI integration exists but script is still useful
- Development-time experimentation
- Quick parameter testing

**Potential Future Migration:**
- Consider moving core logic to `src/kryptos/tuning/` module
- Keep script as thin CLI wrapper
- Timeline: Phase 6 (not urgent)

**No Action Required (Current Phase)**

---

### 5. demo_provenance.py ⚠️ MIGRATE

**Purpose:** Demonstrate attack provenance system (Sprint 4.1) **Status:** Educational/demo code **Usage:** `python
scripts/demo_provenance.py`

**Why Migrate:**
- Demo script, not production utility
- Better suited for examples/ or docs/
- Duplicates functionality in tests/
- Not part of dev workflow

**Action: MIGRATE TO EXAMPLES**
```bash
mkdir -p src/kryptos/examples/
mv scripts/demo_provenance.py src/kryptos/examples/demo_provenance.py
```

**Update:**
- Add to examples/ README
- Update docs/ references
- Keep as educational resource

**Priority:** LOW (Phase 6)

---

### 6. dev/orchestrator.py ⚠️ ASSESS

**Purpose:** Legacy orchestrator copy (pre-autonomous system) **Status:** Superseded by `autonomous_coordinator.py`
**Lines:** 262 lines

**History:**
- Original orchestrator before Phase 4
- Copied to scripts/dev/ for canonical location
- Now redundant with src/kryptos/autonomous_coordinator.py

**Action: ARCHIVE**
```bash
mv scripts/dev/orchestrator.py docs/archive/legacy_orchestrator.py
```

**Reason:**
- Autonomous coordinator is superior (incremental learning, checkpointing)
- No current usage in codebase
- Keep for historical context (shows evolution)

**Priority:** MEDIUM (Tonight)

---

### 7. lint/mdlint.py ✅ KEEP

**Purpose:** Markdown linting for documentation **Status:** Active utility **Usage:** Called by CI/development workflows

**Why Keep:**
- Enforces documentation standards
- Integrated into development workflow
- Low maintenance burden

**No Action Required**

---

## Migration Plan

### Immediate (Tonight)

1. **Archive legacy orchestrator**
   ```bash
   mv scripts/dev/orchestrator.py docs/archive/legacy_orchestrator.py
   rmdir scripts/dev/ (if empty)
   ```

2. **Clean up __pycache__**
   ```bash
   rm -rf scripts/__pycache__/
   rm -rf scripts/dev/__pycache__/
   ```

3. **Update scripts/README.md**
   - Remove references to archived scripts
   - Document active scripts only
   - Add "Archived" section pointing to docs/archive/

### Phase 6 (Future)

4. **Migrate demo_provenance.py**
   ```bash
   mkdir -p src/kryptos/examples/
   mv scripts/demo_provenance.py src/kryptos/examples/
   ```

5. **Extract tuning.py core logic**
   - Create src/kryptos/tuning/ module
   - Move orchestration logic
   - Keep scripts/tuning.py as thin CLI wrapper

---

## Final State (After Tonight)

### scripts/ Directory Structure

```
scripts/
├── README.md                      # Active scripts documentation
├── benchmark_scoring.py           # ✅ Quick benchmarks
├── profile_scoring.py             # ✅ cProfile analysis
├── calibrate_scoring_weights.py   # ✅ Weight optimization
├── tuning.py                      # ✅ Tuning orchestrator
├── demo_provenance.py             # ✅ Educational demo (migrate Phase 6)
└── lint/                          # ✅ Linting utilities
    ├── mdlint.py
    └── README.md
```

**Removed:**
- `scripts/dev/orchestrator.py` → Archived to `docs/archive/legacy_orchestrator.py`
- `scripts/__pycache__/` → Deleted
- `scripts/dev/__pycache__/` → Deleted
- `scripts/dev/` directory → Deleted (empty)

---

## Tech Debt Assessment

### Current Tech Debt Level: **LOW** ✅

**Reasoning:**
- All active scripts have clear purpose
- No redundant functionality
- Well-documented (scripts/README.md)
- Most scripts migrated to CLI already

### Remaining Tech Debt

1. **tuning.py complexity** (277 lines)
   - **Impact:** Medium
   - **Priority:** Phase 6
   - **Solution:** Extract to src/kryptos/tuning/ module

2. **demo_provenance.py location** (330 lines)
   - **Impact:** Low
   - **Priority:** Phase 6
   - **Solution:** Move to src/kryptos/examples/

3. **No script tests** (0 tests for scripts/)
   - **Impact:** Low (dev tools, not production)
   - **Priority:** Phase 7
   - **Solution:** Add lightweight smoke tests

### Resolved Tech Debt (This Session)

✅ **Legacy orchestrator archived** (262 lines removed from active codebase) ✅ **Cache directories cleaned** (__pycache__
removed) ✅ **Documentation updated** (scripts/README.md reflects current state)

---

## Recommendations

### For Tonight (Phase 5 Prep)

1. ✅ Archive `scripts/dev/orchestrator.py` → `docs/archive/legacy_orchestrator.py` 2. ✅ Delete `scripts/dev/` directory
(empty) 3. ✅ Delete `__pycache__` directories 4. ✅ Update `scripts/README.md` (remove orchestrator references)

### For Phase 6 (Future Cleanup)

5. Migrate `demo_provenance.py` to `src/kryptos/examples/` 6. Extract `tuning.py` core logic to `src/kryptos/tuning/`
module 7. Add lightweight smoke tests for scripts/

### For Phase 7 (Advanced)

8. Consider GUI for benchmark_scoring.py (visualize results) 9. Integrate profile_scoring.py output into CI dashboard
10. Auto-calibration system (replace manual calibrate_scoring_weights.py)

---

## Conclusion

**Scripts directory is in good shape.**

- ✅ 5 active, well-maintained utility scripts
- ✅ Clear purpose and documentation
- ✅ Minimal tech debt (legacy orchestrator only)
- ✅ Most functionality already migrated to CLI

**Tonight's cleanup:**
- Archive legacy orchestrator
- Clean cache directories
- Update documentation

**Result:** Lean, focused scripts/ directory with clear utility and no dead code.
