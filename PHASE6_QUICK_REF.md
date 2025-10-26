# Phase 6 Quick Reference
**Mission:** Build a cryptanalysis system that learns and adapts

## Top 5 Priorities (Start Here)

### 0. 🔴 Fix Data Paths FIRST (5.3) - 2 HOURS
**Impact:** Stops creating folders in wrong locations, unblocks all provenance work **Files:**
`src/kryptos/provenance/*.py`, `src/kryptos/agents/*.py` **Action:** Move all runtime data from `data/` to `artifacts/`,
use centralized paths

### 1. 🔴 Cross-Run Memory (1.1)
**Impact:** Eliminates duplicate attempts, 50%+ efficiency gain **Files:** `src/kryptos/provenance/search_space.py`
**Action:** Extend tracker to persist tried keys, integrate with all solvers

### 2. 🔴 K2 Alphabet Fix (2.1)
**Impact:** 3.8% → 100% K2 success rate **Files:** `src/kryptos/k4/vigenere_key_recovery.py`,
`src/kryptos/pipeline/k4_campaign.py` **Action:** Wire existing alphabet enumeration code to orchestrator

### 3. 🔴 K3 Transposition Fix (2.2)
**Impact:** 27.5% → 95%+ K3 success rate **Files:** `src/kryptos/k4/transposition_analysis.py` **Action:** Increase SA
iterations, tune cooling, add dictionary constraints

### 4. 🟡 Composite Chains (3.1)
**Impact:** Enables V→T, T→V attack sequences for K4 **Files:** `src/kryptos/k4/composite.py` **Action:** Create
`CompositeChainExecutor`, implement sequential cipher decryption

### 5. 🟡 Adaptive Strategy (1.2)
**Impact:** System learns from failures, adapts search **Files:** `src/kryptos/k4/adaptive_config.py` (NEW) **Action:**
Build success/failure pattern detection, wire to OPS

## Critical Metrics to Watch

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| K1 Auto-Recovery | 100% | 100% | ✅ PASS |
| K2 Auto-Recovery | 3.8% | 100% | ❌ FAIL |
| K3 Auto-Recovery | 27.5% | >95% | ❌ FAIL |
| Test Coverage | ~65% | >90% | ⚠️ LOW |
| Attack Speed | 2.5/sec | 10+/sec | ⚠️ SLOW |
| Duplicate Attempts | High | 0% | ❌ FAIL |

## Quick Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_vigenere_key_recovery.py -v

# Check coverage
pytest --cov=src --cov-report=html

# Start autonomous system
python -m kryptos.cli.main autonomous --max-hours 1 --cycle-interval 5

# Find placeholders
grep -r "PLACEHOLDER\|TODO\|FIXME" src/ | wc -l

# Profile performance
python -m cProfile -o profile.stats -m kryptos.cli.main k4-decrypt --cipher data/k4_cipher.txt
```

## Sprint Breakdown

- **Sprint 1 (Week 1-2):** Memory, K2 fix, adaptive strategy
- **Sprint 2 (Week 3-4):** K3 fix, composite chains
- **Sprint 3 (Week 5-6):** Testing, coverage push
- **Sprint 4 (Week 7-8):** Production polish, performance

## Key Files to Understand

| File | Purpose | Priority |
|------|---------|----------|
| `src/kryptos/provenance/search_space.py` | Coverage tracking | HIGH |
| `src/kryptos/k4/vigenere_key_recovery.py` | Vigenère solver | HIGH |
| `src/kryptos/k4/transposition_analysis.py` | Transposition SA | HIGH |
| `src/kryptos/k4/composite.py` | Multi-stage fusion | HIGH |
| `src/kryptos/agents/ops_director.py` | Attack orchestration | MEDIUM |
| `src/kryptos/pipeline/k4_campaign.py` | Campaign execution | MEDIUM |

## Blocker Resolution

**If K2 fix blocked:** Work on 1.1 (Cross-Run Memory) instead **If K3 fix blocked:** Work on 3.1 (Composite Chains)
instead **If tests failing:** Work on 4.1 (Autonomous Tests) instead

## Success Checklist

- [ ] K2 tests pass 100%
- [ ] K3 tests pass >95%
- [ ] No duplicate attacks in logs
- [ ] Test coverage >90%
- [ ] Performance >10 attacks/sec
- [ ] All placeholders removed
- [ ] Can crack synthetic V→T ciphers

---

**See `TODO_PHASE_6.md` for complete detailed breakdown**
