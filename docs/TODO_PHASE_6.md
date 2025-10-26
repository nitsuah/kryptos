# Phase 6 TODO List - Operational Readiness
**Goal:** Build a cryptanalysis system that **learns, adapts, and gets smarter with every attempt**

**Philosophy:** Stop trying random keys. Start learning from failures, tracking what works, and adapting strategy based
on evidence.

---

## 🎯 Core Objective

Build a system that: 1. **Never tries the same key twice** (cross-run memory) 2. **Learns from failures** (if Vigenère
fails 1000 times, try something else) 3. **Chains ciphers intelligently** (try V→T, T→V, H→T combinations) 4. **Adapts
search strategy** (prioritize unexplored regions, avoid saturated spaces) 5. **Gets faster over time** (caches
successful patterns, prunes dead ends)

---

## Priority 1: Learning & Memory System 🔴 CRITICAL

**Problem:** System retries failed attempts, wastes compute on explored spaces, doesn't learn from patterns.

### 1.1 Cross-Run Search Space Memory ⚡ HIGH IMPACT

**Current:** SA restarts within same run don't share memory **Target:** No duplicate key attempts across ANY runs

**Tasks:**
- [ ] **Extend `SearchSpaceTracker`** to persist tried keys (not just counts)
  - File: `src/kryptos/provenance/search_space.py`
  - Add `tried_keys: set[str]` to `KeySpaceRegion`
  - Serialize to JSONL for efficiency (1 key per line)

- [ ] **Integrate with Vigenère key recovery**
  - File: `src/kryptos/k4/vigenere_key_recovery.py`
  - Check `tracker.already_tried("vigenere", key)` before attempting
  - Add to exclusion set after attempt

- [ ] **Integrate with transposition SA**
  - File: `src/kryptos/k4/transposition_analysis.py`
  - Add `exclude_permutations: set[tuple]` parameter to SA solver
  - Load from tracker, update after each restart

- [ ] **Integrate with Hill cipher**
  - File: `src/kryptos/k4/hill_cipher.py`
  - Track matrix fingerprints (hash of normalized matrix)
  - Skip if already tried

**Success Metric:** After 1000 Vigenère attempts, next 1000 tries ZERO duplicates (verify with logs)

**Estimated Time:** 2-3 days

---

### 1.2 Adaptive Solver Strategy 🧠 HIGH IMPACT

**Current:** Fixed iteration counts, no learning from success/failure patterns **Target:** Solvers adapt parameters
based on what's working

**Tasks:**
- [ ] **Create `AdaptiveSolverConfig` class**
  - File: `src/kryptos/k4/adaptive_config.py` (NEW)
  - Tracks: success_rate_by_key_length, avg_iterations_to_success, last_N_attempts
  - Auto-adjusts: iteration counts, cooling schedules, restart counts

- [ ] **Implement success pattern detection**
  ```python
  # If length 5 keys succeed 10x more than length 8, prioritize length 5
  if tracker.success_rate("vigenere", "length_5") > 0.5:
      priority_boost("vigenere", "length_5")
  ```

- [ ] **Implement failure pattern detection**
  ```python
  # If Hill 2x2 fails 1000 times in a row, pause for 100 attempts
  if tracker.consecutive_failures("hill_2x2") > 1000:
      pause_strategy("hill_2x2", attempts=100)
  ```

- [ ] **Wire to OPS Director**
  - File: `src/kryptos/agents/ops_director.py`
  - OPS queries adaptive config for next attack priority
  - OPS adjusts resource allocation based on success rates

**Success Metric:** After 10K attempts, system automatically focuses on successful key spaces (visible in logs)

**Estimated Time:** 3-4 days

---

### 1.3 Coverage-Guided Exploration 🗺️ MEDIUM IMPACT

**Current:** Random/systematic search, no awareness of unexplored regions **Target:** Visual heatmaps, automatic
priority boost for virgin territory

**Tasks:**
- [ ] **Implement gap analysis algorithm**
  - File: `src/kryptos/provenance/search_space.py`
  - `get_unexplored_regions()` returns list of untried key spaces
  - `get_oversaturated_regions()` returns list of exhausted spaces

- [ ] **Create coverage visualization**
  - File: `scripts/visualize_coverage.py` (NEW)
  - Matplotlib heatmap: key length vs attempts
  - Color-code: red=oversaturated, green=optimal, blue=virgin

- [ ] **Integrate with attack generator**
  - File: `src/kryptos/pipeline/attack_generator.py`
  - Query gap analysis before generating attacks
  - Boost priority for unexplored regions by 2-5x

**Success Metric:** Run 20K attacks, generate heatmap showing balanced exploration (no huge red blobs)

**Estimated Time:** 2 days

---

## Priority 2: K2/K3 Reliability Fixes 🟡 BLOCKERS

**Problem:** Can't crack ciphers we KNOW the solution to. Not ready for K4.

### 2.1 K2 Alphabet Variant Recovery ⚡ CRITICAL

**Current:** 3.8% success (ignores keyed alphabet `KRYPTOSABCDEFGHIJLMNQUVWXZ`) **Target:** 100% success with auto-
detection

**Tasks:**
- [ ] **Wire alphabet enumeration to orchestrator**
  - Code EXISTS in `vigenere_key_recovery.py` (lines 164-250)
  - Add `try_keyed_alphabets` parameter to `recover_key_by_frequency()`
  - Default: try standard alphabet, then KRYPTOS alphabet

- [ ] **Add alphabet detection heuristics**
  - If standard alphabet fails (score < -320), try keyed
  - If K123 patterns detected, auto-enable keyed alphabet

- [ ] **Update `k4_campaign.py` Vigenère attack**
  - File: `src/kryptos/pipeline/k4_campaign.py` (line 110-147)
  - Remove "placeholder" comment (code structure is there!)
  - Call `recover_key_by_frequency()` with both alphabets

- [ ] **Add comprehensive test**
  - File: `tests/test_vigenere_key_recovery.py`
  - Test: K2 auto-recovery without alphabet hint (should detect keyed)

**Success Metric:** `pytest tests/test_vigenere_key_recovery.py::test_k2_full_autonomous_solve` passes 100%

**Estimated Time:** 1-2 days

---

### 2.2 K3 Transposition Solver Reliability ⚡ CRITICAL

**Current:** 27.5% success on known plaintext (SA unreliable) **Target:** >95% success in <30 seconds

**Tasks:**
- [ ] **Increase SA iterations to 100K-200K**
  - File: `src/kryptos/k4/transposition_analysis.py`
  - Update `solve_columnar_permutation_simulated_annealing()` default
  - Add adaptive iteration count (increase if no improvement for N steps)

- [ ] **Tune cooling schedule**
  - Current: Linear cooling
  - Try: Exponential decay `T = T0 * (0.95 ** step)`
  - Add: Reheating when stuck (if no improvement for 1000 steps, reheat)

- [ ] **Add dictionary-guided constraints**
  - After each SA step, check if plaintext contains real words
  - Boost score if wordlist_hit_rate > 0.3 (partial English)

- [ ] **Implement hybrid solver**
  - For period ≤10: exhaustive search (guaranteed optimal)
  - For period >10: SA with 5 restarts, keep best

- [ ] **Add comprehensive tests**
  - File: `tests/test_transposition_reliability.py` (NEW)
  - Test: K3 auto-recovery (no hints) 100 times → >95% success
  - Test: Synthetic transpositions period 5-15 → all solvable

**Success Metric:** K3 solve succeeds >95% of attempts, avg runtime <30s

**Estimated Time:** 2-3 days

---

## Priority 3: Composite Attack Chains 🔗 HIGH VALUE

**Problem:** No V→T, T→V, H→T attack sequences. K4 likely uses layered cipher.

### 3.1 Implement Chain Execution Engine 🧩 HIGH IMPACT

**Current:** `composite.py` only fuses scores from parallel stages **Target:** Sequential cipher application (decrypt
outer, then inner)

**Tasks:**
- [ ] **Create `CompositeChainExecutor` class**
  - File: `src/kryptos/k4/composite.py` (extend existing)
  - `execute_chain(ciphertext, cipher_sequence)` applies ciphers in order
  - Example: `execute_chain(K4, ["transposition", "vigenere"])` → decrypt T first, then V

- [ ] **Implement V→T chain**
  ```python
  # Hypothesis: K4 = Vigenère(Transposition(plaintext))
  # To decrypt: T→V (reverse order)
  candidates = []
  for v_key in vigenere_keys:
      decrypted_v = vigenere_decrypt(K4, v_key)
      for t_perm in transposition_perms:
          decrypted_t = transposition_decrypt(decrypted_v, t_perm)
          score = quadgram_score(decrypted_t)
          candidates.append((decrypted_t, score, f"V:{v_key}|T:{t_perm}"))
  ```

- [ ] **Implement T→V chain**
  - Similar but reverse order

- [ ] **Implement H→T chain** (Hill then Transposition)

- [ ] **Add provenance tracking**
  - Each candidate stores full chain: `lineage: ["hill_2x2:KEY", "transposition:PERM"]`
  - Enables replay: "This candidate came from Hill key X, then transposition Y"

**Success Metric:** Create synthetic V→T cipher, system auto-discovers chain and decrypts

**Estimated Time:** 3-4 days

---

### 3.2 Smart Chain Selection 🤖 MEDIUM IMPACT

**Current:** No guidance on which chains to try **Target:** Use K123 patterns to prioritize likely chains

**Tasks:**
- [ ] **Analyze K123 cipher progression**
  - K1: Vigenère
  - K2: Vigenère + encoding
  - K3: Transposition
  - K4: ??? (likely combination)

- [ ] **Build chain priority model**
  - High priority: V→T, T→V (K2+K3 combination)
  - Medium priority: H→T, H→V (Hill + other)
  - Low priority: V→V, T→T (unlikely double same cipher)

- [ ] **Implement early termination**
  - If V→T chain finds score > -300, immediately report
  - Don't waste time on other chains if one succeeds

**Success Metric:** Chain selection tries most likely combinations first (visible in attack logs)

**Estimated Time:** 2 days

---

## Priority 4: Test Coverage & Validation 🧪 QUALITY

**Problem:** 65% coverage, missing critical autonomous solve tests, no edge cases

### 4.1 Autonomous Solve Tests ⚡ CRITICAL

**Current:** K1/K2 autonomous tests exist but incomplete **Target:** Comprehensive end-to-end validation

**Tasks:**
- [ ] **Expand K1 autonomous test**
  - File: `tests/test_vigenere_key_recovery.py`
  - Test: No key provided, no alphabet hint → recovers PALIMPSEST
  - Test: Partial crib (first 10 chars) → completes key
  - Test: Wrong alphabet hint → auto-corrects

- [ ] **Expand K2 autonomous test**
  - Test: No key, no alphabet → discovers ABSCISSA + keyed alphabet
  - Test: With BERLIN crib → faster recovery

- [ ] **Create K3 autonomous test**
  - File: `tests/test_transposition_autonomous.py` (NEW)
  - Test: No hints → detects period, solves transposition
  - Test: With partial plaintext crib → anchors solution

- [ ] **Multi-cipher attempt test**
  - File: `tests/integration/test_multi_cipher_attempts.py` (NEW)
  - Test: Unknown cipher → tries V, fails → tries T, succeeds
  - Test: V→T composite → detects chain, decrypts both layers

**Success Metric:** All autonomous tests pass 100 consecutive runs (proves reliability)

**Estimated Time:** 3-4 days

---

### 4.2 Edge Case & Adversarial Tests 🔬 MEDIUM PRIORITY

**Current:** No edge case testing, no adversarial inputs **Target:** Robust handling of unusual inputs

**Tasks:**
- [ ] **Create edge case test suite**
  - File: `tests/test_edge_cases.py` (NEW)
  - Empty ciphertext → graceful failure
  - Single character → returns unchanged
  - All same letter (AAAA...) → low score but no crash
  - Extremely long text (100K chars) → handles efficiently
  - Non-alphabetic characters → filters correctly

- [ ] **Create adversarial test suite**
  - File: `tests/test_adversarial.py` (NEW)
  - Random gibberish → low scores, no false positives
  - Real text with single cipher applied → detects cipher type
  - Real text with NO cipher → returns original (score best)

- [ ] **Performance boundary tests**
  - Period 1 (no transposition) → instant solve
  - Period 30 (huge) → timeout handling
  - Key length 1 (Caesar) → instant solve
  - Key length 50 (unrealistic) → rejects or handles

**Success Metric:** All edge cases handled gracefully, no crashes on adversarial inputs

**Estimated Time:** 2 days

---

### 4.3 Coverage Push to 90%+ 📊 MEDIUM PRIORITY

**Current:** ~65% coverage, missing key modules **Target:** 90%+ coverage with quality tests

**Tasks:**
- [ ] **Add tests for uncovered modules**
  - `src/kryptos/k4/period_detection.py` → NO TESTS (critical!)
  - `src/kryptos/k4/beaufort.py` → minimal tests
  - `src/kryptos/k4/transposition_routes.py` → no route tests

- [ ] **Add tests for scoring functions**
  - `src/kryptos/k4/scoring.py` → test all linguistic metrics
  - Test: `wordlist_hit_rate()` with known English text → >0.8
  - Test: `trigram_entropy()` with random text → high entropy

- [ ] **Add tests for provenance system**
  - `src/kryptos/provenance/search_space.py` → test persistence
  - Test: Write coverage → restart → load persisted data
  - Test: Deduplication → no duplicate attack logs

**Success Metric:** `pytest --cov=src --cov-report=html` shows >90% coverage

**Estimated Time:** 3-4 days

---

## Priority 5: Production Ready 🚀 POLISH

**Problem:** Placeholder comments, deprecated code, not wired together, slow performance

### 5.1 Remove Placeholders & Wire Execution ⚡ HIGH PRIORITY

**Current:** 27 placeholder comments, misleading docs **Target:** All code paths functional, no placeholders

**Tasks:**
- [ ] **Validate & fix OPS execution**
  - File: `src/kryptos/agents/ops.py` (line 360)
  - **UPDATE MISLEADING COMMENT** - code IS implemented (lines 490-530)
  - Test `_execute_vigenere()`, `_execute_hill()`, `_execute_transposition()`
  - Verify parameter parsing works correctly

- [ ] **Remove k4_campaign placeholders**
  - File: `src/kryptos/pipeline/k4_campaign.py` (lines 110-147)
  - Vigenère attack structure exists, remove "placeholder" markers
  - Wire to `vigenere_key_recovery.py` functions
  - Add attack result collection

- [ ] **Delete deprecated code**
  - File: `src/kryptos/k4/executor.py` (entire file marked DEPRECATED)
  - Verify no imports elsewhere: `grep -r "from.*executor import" src/`
  - Delete if truly unused

- [ ] **Fix autopilot placeholders**
  - File: `src/kryptos/autopilot.py` (lines 80-82)
  - Replace Q/OPS/SPY placeholder strings with real function calls

- [ ] **Clean up todos**
  - Search codebase for `TODO`, `FIXME`, `XXX`
  - Convert to GitHub issues or fix immediately

**Success Metric:** `grep -r "PLACEHOLDER\|TODO\|FIXME" src/` returns <5 results (only future enhancements)

**Estimated Time:** 2-3 days

---

### 5.2 Performance Optimization 🏎️ MEDIUM PRIORITY

**Current:** 2.5 attacks/sec sequential **Target:** 10-15 attacks/sec with parallel execution

**Tasks:**
- [ ] **Implement multiprocessing in OPS**
  - File: `src/kryptos/agents/ops.py`
  - Use `ProcessPoolExecutor` (already imported but not fully utilized)
  - Run N attacks in parallel where N = CPU cores

- [ ] **Batch SPY validation**
  - File: `src/kryptos/agents/spy_nlp.py`
  - Process 10-100 candidates at once (vectorized operations)
  - Use spaCy's `nlp.pipe()` for batch processing

- [ ] **Add memory limits per worker**
  - Monitor RAM usage per process
  - Kill and restart if process exceeds 2GB
  - Prevents memory leaks from long-running attacks

- [ ] **Implement timeout handling**
  - Each attack gets 60s max execution time
  - If timeout, kill process, log failure, move to next attack

- [ ] **Profile and optimize hot paths**
  - File: `scripts/profile_pipeline.py` (NEW)
  - Use `cProfile` to find bottlenecks
  - Optimize scoring functions (most CPU time)

**Success Metric:** 4× speedup on 4-core system (10 attacks/sec sustained)

**Estimated Time:** 3-4 days

---

### 5.3 Data Path Configuration Fix 🗂️ ⚡ HIGH PRIORITY (MOVED UP)

**Current:** Data folders creating in wrong locations (parent dir, workspace root) **Target:** All runtime data in
`kryptos/artifacts/`, persistent config in `kryptos/data/`

**Critical Issues:**
- `artifacts/coverage_history/` being created in parent `code/` directory instead of `kryptos/`
- `data/search_space/` using relative paths (creates duplicates)
- All provenance data should be in `artifacts/` (git-ignored but inside build)

**Tasks:**
- [ ] **Fix coverage_history path**
  - Currently: `c:\Users\ajhar\code\artifacts\coverage_history\`
  - Should be: `c:\Users\ajhar\code\kryptos\artifacts\coverage_history\`
  - Update wherever this path is created (likely in test runners or coverage tools)

- [ ] **Move provenance data to artifacts/**
  - `data/search_space/` → `artifacts/search_space/`
  - `data/attack_logs/` → `artifacts/attack_logs/`
  - `data/ops_strategy/` → `artifacts/ops_strategy/`
  - `data/intel_cache/` → `artifacts/intel_cache/`
  - Reason: These are runtime state, not source data

- [ ] **Update search_space.py to use artifacts/**
  - File: `src/kryptos/provenance/search_space.py`
  - Change default: `cache_dir or (get_artifacts_root() / "search_space")`
  - Use centralized paths, not relative `./data/search_space`

- [ ] **Update attack_log.py to use artifacts/**
  - File: `src/kryptos/provenance/attack_log.py`
  - Change to: `get_artifacts_root() / "attack_logs"`

- [ ] **Update spy_web_intel.py to use artifacts/**
  - File: `src/kryptos/agents/spy_web_intel.py`
  - Change to: `get_artifacts_root() / "intel_cache"`

- [ ] **Update ops_director.py to use artifacts/**
  - File: `src/kryptos/agents/ops_director.py`
  - Change to: `get_artifacts_root() / "ops_strategy"`

- [ ] **Update .gitignore**
  - Add: `/artifacts/*` (ignore all runtime state)
  - Keep: `!/artifacts/.gitkeep` (preserve directory)
  - Remove old patterns that are now redundant

- [ ] **Add migration script**
  - File: `scripts/migrate_provenance_to_artifacts.py` (NEW)
  - Move existing data from `data/` to `artifacts/`
  - Update any hard-coded paths in JSON files
  - Dry-run mode for safety

**Directory Structure After Fix:**
```
kryptos/
├── data/                    # SOURCE DATA (committed to git)
│   ├── bigrams.tsv
│   ├── trigrams.tsv
│   └── quadgrams.tsv
├── artifacts/               # RUNTIME STATE (git-ignored)
│   ├── search_space/        # Exploration tracking
│   ├── attack_logs/         # Attack attempts
│   ├── ops_strategy/        # OPS decisions
│   ├── intel_cache/         # Web scraping cache
│   ├── coverage_history/    # Test coverage over time
│   └── logs/                # Runtime logs
```

**Success Metric:**
- All runtime data in `kryptos/artifacts/`
- No folders in parent `code/` directory
- `git status` shows no new provenance files

**Estimated Time:** 2 hours (high impact, low complexity)

**PRIORITY BUMP:** This is causing confusion and polluting the workspace. Fix early in Sprint 1.

---

## Sprint Schedule (6-8 weeks)

### Sprint 1: Learning Foundation (Week 1-2)
- [x] 5.3 Data Path Configuration Fix (DONE - 2 hours ✅)
- [ ] 1.1 Cross-Run Search Space Memory
- [ ] 2.1 K2 Alphabet Variant Recovery
- [ ] 1.2 Adaptive Solver Strategy (if time permits)

### Sprint 2: K3 Fix & Chains (Week 3-4)
- [ ] 2.2 K3 Transposition Solver Reliability
- [ ] 3.1 Implement Chain Execution Engine
- [ ] 3.2 Smart Chain Selection

### Sprint 3: Testing & Quality (Week 5-6)
- [ ] 4.1 Autonomous Solve Tests
- [ ] 4.2 Edge Case & Adversarial Tests
- [ ] 4.3 Coverage Push to 90%+

### Sprint 4: Production Polish (Week 7-8)
- [ ] 5.1 Remove Placeholders & Wire Execution
- [ ] 5.2 Performance Optimization
- [ ] 1.3 Coverage-Guided Exploration

---

## Success Criteria - Phase 6 Complete

### Functional Requirements
- [ ] K1 auto-recovery: 100% (currently ✅ 100%)
- [ ] K2 auto-recovery: 100% (currently ❌ 3.8%)
- [ ] K3 auto-recovery: >95% (currently ❌ 27.5%)
- [ ] Composite V→T: 100% on synthetics (currently ❌ not implemented)
- [ ] No duplicate attempts across runs (currently ❌ duplicates happen)

### Quality Requirements
- [ ] Test coverage: >90% (currently ❌ ~65%)
- [ ] All autonomous tests pass 100 consecutive runs
- [ ] No placeholders in production code paths
- [ ] Performance: >10 attacks/sec on 4-core system

### Learning Requirements
- [ ] System learns from failures (adapts strategy)
- [ ] Coverage-guided exploration (visual heatmaps)
- [ ] Success pattern detection (prioritizes what works)
- [ ] Cross-run memory (never tries same key twice)

### K4 Readiness
- [ ] Can crack all K1-K3 reliably (>95%)
- [ ] Chain attacks working (V→T, T→V, H→T)
- [ ] Adaptive learning reducing waste by 50%
- [ ] Full provenance for reproducibility

---

## Tracking Progress

**Update this file weekly:**
```bash
# Mark items complete with ✅
- [x] Task completed
- [ ] Task in progress
- [ ] Task not started

# Add notes on blockers
## Blocker: K3 SA still unreliable after tuning
- Tried exponential cooling → no improvement
- Next: Try genetic algorithm instead of SA
```

**Generate weekly reports:**
```bash
# Run coverage report
pytest --cov=src --cov-report=html

# Run performance benchmark
python scripts/benchmark_attacks.py

# Generate progress summary
python scripts/phase6_progress.py > docs/PHASE6_PROGRESS.md
```

---

## Notes & Discoveries

**2025-10-25:** Phase 6 kickoff
- Discovered: 688 test functions defined, only 564 passing (124 missing?)
- Discovered: OPS placeholder comment misleading - code IS implemented!
- Discovered: K2 alphabet code exists but not wired
- Discovered: Search space tracking EXISTS - need to extend for keys, not just counts

**Add discoveries here as we learn:**
```markdown
**YYYY-MM-DD:** Discovery title
- Finding: What we learned
- Impact: How it changes our approach
- Action: What we'll do differently
```

---

**Last Updated:** 2025-10-25 **Phase:** 6 - Operational Readiness **Status:** Ready to start Sprint 1

**Next Action:** Start with 1.1 Cross-Run Search Space Memory (highest impact, unblocks everything else)
