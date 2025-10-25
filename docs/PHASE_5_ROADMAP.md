# Phase 5+ Roadmap

**Current Status:** Phase 5.2 Complete **Branch:** `phase-5` **Last Updated:** October 25, 2025

## Completed Phases

### ✅ Phase 5.1: Attack Generation Engine
- AttackGenerator class (667 lines)
- Q-Research hint conversion
- Coverage-gap targeting
- 100% deduplication
- 24 tests passing

### ✅ Phase 5.2: OPS Integration
- Extended OPS Agent with attack generation methods
- Parallel execution with batching
- AttackLogger integration
- Placeholder execution
- 6 integration tests
- Demo scripts created

## Phase 5.3: Real Cipher Execution (Next)

**Goal:** Replace placeholder execution with real cipher implementations

### Tasks

#### 1. Implement Real Cipher Execution
- [ ] Modify `OpsAgent._execute_single_attack()` to call real ciphers
- [ ] Map cipher types to functions:
  - `vigenere` → `vigenere_decrypt()`
  - `transposition/columnar` → `columnar_transpose_decrypt()`
  - `transposition/rail_fence` → `rail_fence_decrypt()`
  - `transposition/route` → `route_cipher_decrypt()`
  - `hill` → `hill_decrypt()`
- [ ] Parse `key_or_params` dict into function arguments
- [ ] Handle cipher-specific parameter formats

#### 2. Integrate SPY Agent Scoring
- [ ] Call SPY agent on each decryption result
- [ ] Store confidence scores in `AttackResult`
- [ ] Filter candidates below threshold (e.g., 0.3)
- [ ] Return top N candidates per attack

#### 3. Result Storage
- [ ] Save promising candidates to JSON
- [ ] Export results in human-readable format
- [ ] Update AttackLogger with real success/failure
- [ ] Add result visualization tools

#### 4. Performance Optimization
- [ ] Parallel cipher execution (multiprocessing pool)
- [ ] Early termination on high-confidence find
- [ ] Memory limits per attack
- [ ] Timeout handling for slow ciphers

#### 5. Testing
- [ ] Integration tests with real ciphers
- [ ] Performance benchmarks
- [ ] K1/K2/K3 validation (known plaintexts)
- [ ] Error handling tests

**Estimated Effort:** 2-3 days **Deliverables:**
- Real decryption results from attack queue
- SPY-scored candidates
- Updated test suite (add ~10 tests)

---

## Phase 5.4: Validation Pipeline

**Goal:** Multi-stage filtering to reduce 100K candidates → 10 reviewable

### Architecture

```
OPS Attack Execution (100K candidates)
        ↓
    SPY Scoring (filter to top 1K)
        ↓
    LINGUIST Grammar Check (filter to 100)
        ↓
    Q Statistical Validation (filter to 10)
        ↓
    Human Review
```

### Tasks

#### 1. SPY Stage (Pattern Recognition)
- [ ] Batch scoring for performance
- [ ] Configurable threshold (default: 0.3)
- [ ] Return confidence breakdown by metric

#### 2. LINGUIST Stage (Grammar Validation)
- [ ] Part-of-speech tagging
- [ ] Sentence structure validation
- [ ] Grammar likelihood scores
- [ ] Filter grammatically invalid candidates

#### 3. Q Stage (Statistical Validation)
- [ ] Chi-squared test on digraph frequencies
- [ ] IC verification
- [ ] Entropy analysis
- [ ] Known-pattern matching (if applicable)

#### 4. Human Review Interface
- [ ] Export top 10 to formatted report
- [ ] Show attack parameters that produced each candidate
- [ ] Confidence scores from all agents
- [ ] Side-by-side comparison tool

#### 5. Testing
- [ ] End-to-end pipeline tests
- [ ] K1/K2/K3 should pass all stages
- [ ] Performance benchmarks (time per stage)

**Estimated Effort:** 3-4 days **Deliverables:**
- Multi-stage filtering pipeline
- Human review reports
- Updated test suite (add ~15 tests)

---

## Phase 5.5: Adaptive Learning

**Goal:** Learn from successful attacks to improve future generation

### Features

#### 1. Success Pattern Analysis
- [ ] Track which parameter combinations succeed
- [ ] Build success probability model
- [ ] Weight future generation toward successful patterns

#### 2. Failure Pruning
- [ ] Identify consistently failing parameter ranges
- [ ] Reduce priority for similar attacks
- [ ] Save compute by avoiding known failures

#### 3. Dynamic Priority Adjustment
- [ ] Adjust priority scores based on recent results
- [ ] Boost related attacks when one succeeds
- [ ] Reduce priority for exhausted parameter spaces

#### 4. Coverage-Guided Generation
- [ ] Track which parameter spaces have been explored
- [ ] Prioritize unexplored regions
- [ ] Balance exploration vs exploitation

**Estimated Effort:** 4-5 days **Deliverables:**
- Adaptive priority scoring
- Success pattern database
- Coverage-guided generation

---

## Phase 5.6: Literature Integration

**Goal:** Extract attack parameters from academic papers

### Tasks

#### 1. LiteratureGapAnalyzer Implementation
- [ ] Parse academic papers (PDF/text)
- [ ] Extract cipher recommendations
- [ ] Parse parameter ranges from papers
- [ ] Generate attacks from literature

#### 2. Paper Database
- [ ] Curate relevant K4 papers
- [ ] Tag papers by cipher type
- [ ] Extract key insights manually
- [ ] Build structured paper database

#### 3. Integration
- [ ] Wire LiteratureGapAnalyzer into AttackGenerator
- [ ] Test comprehensive queue with literature attacks
- [ ] Validate paper-based attacks on K1/K2/K3

**Estimated Effort:** 5-7 days **Deliverables:**
- LiteratureGapAnalyzer implementation
- Paper database
- Literature-based attacks

---

## Future Enhancements

### Performance Optimization
- [ ] GPU acceleration for cipher operations
- [ ] Distributed execution (multi-node)
- [ ] Result streaming (don't hold all in memory)
- [ ] Incremental checkpointing (resume from failure)

### User Experience
- [ ] Web dashboard for monitoring progress
- [ ] Real-time statistics updates
- [ ] Interactive attack queue editor
- [ ] Visualization of parameter space coverage

### Quality Assurance
- [ ] **Comprehensive test audit and improvement**
  - [ ] Review all test files for redundancy
  - [ ] Improve test naming and organization
  - [ ] Add missing edge case tests
  - [ ] Consolidate overlapping tests
  - [ ] Add performance regression tests
  - [ ] Improve test documentation
- [ ] Continuous integration improvements
- [ ] Automated performance benchmarking
- [ ] Code coverage analysis (aim for >90%)

### Documentation
- [ ] API reference documentation
- [ ] Architecture decision records
- [ ] Video tutorials
- [ ] Research paper writeup

---

## Timeline Estimate

| Phase | Effort | Status |
|-------|--------|--------|
| 5.1 Attack Generation | 3 days | ✅ Complete |
| 5.2 OPS Integration | 2 days | ✅ Complete |
| 5.3 Real Cipher Execution | 2-3 days | 🔜 Next |
| 5.4 Validation Pipeline | 3-4 days | ⏳ Planned |
| 5.5 Adaptive Learning | 4-5 days | ⏳ Planned |
| 5.6 Literature Integration | 5-7 days | ⏳ Planned |
| **Test Audit & QA** | **3-4 days** | **⏳ Planned** |

**Total Remaining:** ~20-27 days of focused work

---

## Success Metrics

### Phase 5.3
- [ ] All attack types execute successfully
- [ ] SPY scores match manual validation
- [ ] K1/K2/K3 produce correct plaintexts
- [ ] Performance: <1s per attack on average

### Phase 5.4
- [ ] Pipeline reduces 100K → 10 candidates
- [ ] All K1/K2/K3 plaintexts in final 10
- [ ] <5% false negative rate
- [ ] Total pipeline time <30 minutes

### Phase 5.5
- [ ] 20% improvement in attack success rate
- [ ] 30% reduction in duplicate attack generation
- [ ] Coverage-guided generation finds new parameter spaces

### Phase 5.6
- [ ] Literature attacks contribute 10-20% of queue
- [ ] Novel parameter combinations from papers
- [ ] At least 5 papers integrated

### Test Quality (Post-Audit)
- [ ] Test suite completes in <10 minutes
- [ ] >90% code coverage
- [ ] Zero redundant tests
- [ ] All tests well-documented
- [ ] Performance regression tests in place

---

## Notes

### Technical Debt
- Placeholder execution in Phase 5.2 (blocking real results)
- No literature integration yet (missing attack vectors)
- Manual test organization needs improvement
- Some tests could be faster

### Dependencies
- Phase 5.3 required before 5.4 (need real results to filter)
- Phase 5.4 required before 5.5 (need success data to learn)
- Test audit should happen before Phase 5.6 (establish quality baseline)

### Risks
- Real cipher execution may be slower than expected
- SPY agent may not filter effectively (need tuning)
- Literature parsing may be manual-intensive
- Test audit may reveal systemic issues requiring refactoring

---

**Next Action:** Begin Phase 5.3 - Real Cipher Execution
