# Next Phase Plan

**Branch:** `k4-milestones` → merge to `main` → new branch for next phase

---

## Completed (k4-milestones branch)

✅ Agent triumvirate: SPY + OPS + Q (~1,100 lines, 36 tests) ✅ Coverage: 82% → 85% (hypotheses.py 59% → 95%) ✅ 9
hypothesis types tested with real K4 ciphertext ✅ Statistical validation (2σ/3σ thresholds) ✅ CI fixed (pyproject.toml
package-dir) ✅ All 281 tests passing ✅ PRR feedback applied

---

## Next Phase: Composite Hypotheses (Priority 1)

**Goal:** Test layered ciphers (most likely K4 approach)

**Branch:** `composite-hypotheses`

**Tasks:**

1. Implement `CompositeHypothesis` base class 2. Add Transposition → Hill 2x2 combinator 3. Add Vigenère → Transposition
combinator 4. Add Simple Substitution → Transposition combinator 5. Test with real K4 ciphertext 6. Update scoring for
multi-stage candidates

**Success:** Generate composite candidates with provable score improvement over single-stage

**Tests:** Add to `test_k4_hypotheses.py` (aim for 5+ new tests, minimal coverage impact)

**Estimate:** 3-5 days

---

## Future Phases (Priority Order)

### Phase 2: Hill 3x3 Genetic Algorithm

- Expand beyond 2x2 exhaustive search
- Implement smart pruning with partial scores
- 26^9 keyspace requires intelligent search
- **Estimate:** 2-3 days

### Phase 3: SPY v2.0 (NLP Phase 1 - No API)

- Integrate spaCy for proper tokenization
- Add semantic similarity with WordNet
- Improve pattern detection without API costs
- **Estimate:** 2-3 days

### Phase 4: Test Performance Optimization

- Profile slow hypothesis implementations
- Consider pytest-xdist for parallel testing
- Target: <180s full suite (current: 96-335s variable)
- **Estimate:** 1-2 days

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
