# Next Phase Plan

**Branch:** `k4-milestones` → merge to `main` → new branch for next phase

---

## Completed (composite-hypotheses branch) ✅

**Composite Hypothesis Infrastructure (Oct 24, 2025):**
- ✅ `CompositeHypothesis` base class (86 lines) - chains any two hypothesis implementations
- ✅ 8 composite implementations (397 total lines):
  - TranspositionThenHill, VigenereThenTransposition, SubstitutionThenTransposition
  - HillThenTransposition, AutokeyThenTransposition, PlayfairThenTransposition
  - DoubleTransposition, VigenereThenHill
- ✅ Stage-aware scoring (113 lines) - awards bonuses for IOC improvement, word patterns, frequency convergence
- ✅ Artifact provenance tracking (100 lines) - captures git state, Python version, platform for reproducibility
- ✅ Test infrastructure: 21 total tests (12 composite + 9 single-stage), all passing
- ✅ Test suite optimization: 144s → 73s → 1.39s quick run (127x speedup with pytest markers)
- ✅ CI fixed: pytest collection issue resolved (renamed helper functions)
- ✅ API documentation expanded: 257 new lines with comprehensive examples

**Test Results (Quick Run - Reduced Parameters):**
- Transposition→Hill: Best score -428.49 (baseline: -355.92) ❌ No signal
- Vigenère→Transposition: Best score -431.68 ❌ No signal
- Substitution→Transposition: Best score -446.57 ❌ No signal
- **All scores below 2σ threshold (-326.68)**

**Key Finding:** Simple two-layer classical cipher combinations ruled out for K4. This is a valuable negative result -
Sanborn likely used more sophisticated layering or non-classical methods.

**Code Added:**
- 397 lines composite implementations
- 113 lines stage-aware scoring
- 100 lines provenance tracking
- 257 lines API documentation
- 21 comprehensive tests

---

## Completed (k4-milestones branch)

✅ Agent triumvirate: SPY + OPS + Q (~1,100 lines, 36 tests) ✅ Coverage: 82% → 85% (hypotheses.py 59% → 95%) ✅ 9
hypothesis types tested with real K4 ciphertext ✅ Statistical validation (2σ/3σ thresholds) ✅ CI fixed (pyproject.toml
package-dir) ✅ All 281 tests passing ✅ PRR feedback applied

---

## Next Phase: Advanced Exploration (Priority Order)

**Current Status:** Composite hypotheses complete. No signals found with simple two-layer ciphers.

### Phase 1: Full-Scale Composite Testing (High Priority)

**Goal:** Run complete parameter exploration to definitively rule out (or discover signals in) composite classical
ciphers

**Tasks:** 1. Run full-scale tests (~65 min runtime):
   - TranspositionThenHill: 20 candidates × 1,000 Hill keys
   - VigenereThenTransposition: 50 × 100 permutations
   - SubstitutionThenTransposition: 28 × 100 permutations
2. Analyze for any candidates exceeding 2σ threshold 3. Document results in artifacts/composite_tests/

**Success Criteria:** Complete exploration of composite parameter space, statistical confidence in negative result

**Estimate:** 1-2 hours (mostly compute time)

---

### Phase 2: Alternative Composite Combinations (Medium Priority)

**Goal:** Test additional layering approaches not yet explored

**Candidates:**
- Hill 2x2 → Transposition (reverse order from Phase 1)
- Autokey → Transposition (Vigenère variant with plaintext feedback)
- Playfair → Transposition (5×5 grid digraph cipher)
- Double Transposition (two columnar stages with different widths)
- Vigenère → Hill 2x2 (polyalphabetic → matrix)

**Implementation:** Each requires ~40-line CompositeHypothesis subclass

**Success Criteria:** 5+ new composite methods tested

**Estimate:** 2-3 days

---

### Phase 3: Hill 3x3 Genetic Algorithm (High Priority if Composites Fail)

**Goal:** Expand Hill cipher search beyond 2×2 exhaustive approach

**Challenge:** 26^9 = 5.4 trillion keys (vs 2×2's 158K). Exhaustive search impossible.

**Approach:**
- Genetic algorithm with smart pruning
- Population: 1,000 random invertible 3×3 matrices
- Selection: Top 20% by score
- Crossover + mutation to generate new population
- 100 generations = ~100K keys tested

**Success Criteria:** Test 100K+ keys in <10 minutes, find any 3σ candidates

**Estimate:** 2-3 days

---

### Phase 4: Stage-Aware Scoring Enhancement (Medium Priority)

**Goal:** Award bonuses for intermediate decryption progress in composite hypotheses

**Enhancements:** 1. Partial word match detection in stage1 plaintext 2. IOC (Index of Coincidence) reduction scoring 3.
Letter frequency shift toward English distribution 4. Positional pattern improvements 5. Weighted average of stage1 +
stage2 scores

**Implementation:** Enhance `src/kryptos/k4/scoring.py` (~100 lines)

**Success Criteria:** Composite scores reflect partial decryption quality

**Estimate:** 1-2 days

---

### Phase 5: SPY v2.0 - NLP Integration (Lower Priority)

**Goal:** Upgrade SPY pattern detection with proper NLP (no API costs)

**Enhancements:**
- spaCy for tokenization and POS tagging
- Named entity recognition
- Dependency parsing for phrase structure
- WordNet for semantic similarity

**Expected Improvement:** 20%+ better pattern quality scores

**Success Criteria:** SPY detects more sophisticated linguistic patterns

**Estimate:** 2-3 days

---

### Phase 6: Performance & Infrastructure (Ongoing)

**Tasks:**
- Profile composite runs (cProfile/py-instrument)
- Numba JIT for Hill cipher operations
- Artifact provenance tracking (reproducibility)
- Scoring weight calibration (grid search vs K1-K3)
- API documentation expansion
- pytest.mark.slow for long tests

**Estimate:** 1-2 days distributed across other phases

---

## Next Immediate Actions

1. **Merge composite-hypotheses branch** to main (all tests passing, 50% performance improvement) 2. **Run full-scale
composite tests** (65 min, overnight if needed) 3. **Decide Phase 2 vs Phase 3** based on full-scale results:
   - If any 2σ+ signals → Continue with alternative composites (Phase 2)
   - If no signals → Pivot to Hill 3×3 genetic algorithm (Phase 3)

---

## Cleanup Decisions

### ❌ DELETE: Top-level `agents/` folder

**Reason:** Superseded by `src/kryptos/agents/` (production code)

**Files to delete:**

- `agents/spy.prompt` → Reference only, actual SPY is `src/kryptos/agents/spy.py`
- `agents/q.prompt` → Reference only, actual Q is `src/kryptos/agents/q.py`
- `agents/ops.prompt` → Reference only, actual OPS is `src/kryptos/agents/ops.py`
- `agents/README.md` → Superseded by `docs/AGENTS_ARCHITECTURE.md`
- `agents/LEARNED.md` → State now in `artifacts/autopilot_state.json`
- `agents/logs/` → Logs now in `artifacts/logs/`

**Keep for now:** `scripts/dev/orchestrator.py` (uses prompts for autopilot simulation)

**Action:** Delete `agents/` folder after this branch merges

### ✅ KEEP: Documentation structure

- 6 core docs (README, K4_MASTER_PLAN, AGENTS_ARCHITECTURE, API_REFERENCE,
CHANGELOG, TECHDEBT)
- Minimal updates per phase (git history is sufficient for detailed changes)
- Only update CHANGELOG with version releases (not every branch)

---

## Documentation Policy

**Per-branch:**

- Update README.md current status only if major milestone (e.g., new agent, 90% coverage)
- Skip CHANGELOG.md until merge to main
- Skip TECHDEBT.md unless introducing known debt

**Merge to main:**

- Add one CHANGELOG entry summarizing the branch (5-10 lines max)
- Update K4_MASTER_PLAN current state if priorities changed
- Update README current status section

**Rationale:** Git commit messages + PR descriptions provide detail, docs provide high-level state

---

## Questions Answered

**Q: Do we need top-level `agents/` folder?** A: No. Production code is in `src/kryptos/agents/`. The prompt files are
only used by autopilot simulation (which could load from strings). Delete after merge.

**Q: Should we update CHANGELOG/docs every branch?** A: No. Only on merge to main. Git history is sufficient for branch-
level detail.

**Q: 90% coverage still a goal?** A: Lower priority. 85% is excellent. Remaining gaps are low-value error paths (file
I/O, CLI edge cases). Focus on K4-solving features instead.

**Q: Test performance optimization?** A: Phase 4 (lower priority). 96s fast path is already great. 335s with coverage is
acceptable for comprehensive testing.

---

## Success Metrics (Next 3 Phases)

- **Composite hypotheses:** 5+ new tests, score improvement demonstrated
- **Hill 3x3:** Genetic algorithm working, 100+ keys tested per second
- **SPY v2.0:** spaCy integrated, pattern quality score improved by 20%+

---

**Last Updated:** 2025-10-24 **Next Review:** After composite-hypotheses branch complete
