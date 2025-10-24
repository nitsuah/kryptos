# Kryptos Technical Debt & Cleanup Status

**Last Updated:** 2025-10-24 **Status:** Major cleanup completed, infrastructure phase ahead

---

## 🎉 Completed Cleanup (Oct 2024)

### Files Deleted

**scripts/experimental/** - Entire folder removed (100% bloat)

- `examples/run_autopilot_demo.py` → moved to `src/kryptos/examples/`
- `examples/run_ops_tiny_sweep.py` → redundant
- `examples/generate_top_candidates.py` → covered by package API
- `tools/` - 10+ utility scripts superseded by package APIs

**scripts/dev/** - Cleaned 8 → 3 files

- ❌ `berlin_clock_vig.py` - temp test file (integrated)
- ❌ `create_pr.py` - use GitHub CLI instead
- ❌ `README.md` + `README_pr.md` - unnecessary docs
- ❌ `archived/` - 6 old hypothesis runners (obsolete)
- ✅ KEPT: `orchestrator.py`, `test_new_ciphers.py`, `test_vigenere_expanded.py`

**scripts/demo/** - Moved to proper location

- All `.py` files → `src/kryptos/examples/`
- Folder deleted after migration

**docs/** - Consolidated 20 → 6 files (70% reduction)

- ❌ `10KFT.md` - merged into README.md
- ❌ `AUTOPILOT.md` - merged into AGENTS_ARCHITECTURE.md
- ❌ `CONSOLIDATION_PLAN.md` - obsolete (work done)
- ❌ `DEPRECATIONS.md` - merged into CHANGELOG.md
- ❌ `EXPANSION_PLAN.md` - merged into K4_MASTER_PLAN.md
- ❌ `EXPERIMENTAL_TOOLING.md` - merged into ARCHIVED_SCRIPTS.md
- ❌ `INDEX.md` - redundant with README.md
- ❌ `K4_PROGRESS_TRACKER.md` - merged into K4_MASTER_PLAN.md
- ❌ `K4_V1_SPINE_SUMMARY.md` - archived (dated milestone)
- ❌ `LOGGING.md` - moved to API_REFERENCE.md
- ❌ `MASTER_AGENT_PROMPT.md` - moved to AGENTS_ARCHITECTURE.md
- ❌ `PERF.md` - moved to TECHDEBT.md (this file)
- ❌ `ARCHIVED_SCRIPTS.md` - no longer needed

### Metrics

| Category | Before | After | Reduction |
|----------|--------|-------|-----------|
| Docs | 20 files | 6 files | 70% |
| Scripts (dev/) | 8 files | 3 files | 63% |
| Scripts (experimental/) | ~15 files | 0 files | 100% |
| Total LOC | ~20,000 | ~15,000 | 25% |

### Final Structure

```text
kryptos/
├── src/kryptos/
│   ├── agents/
│   │   └── spy.py (✅ 435 lines)
│   ├── examples/ (NEW - moved from scripts/demo/)
│   └── ...
├── scripts/
│   ├── run_hypothesis.py (✅ unified runner)
│   ├── run_random_baseline.py
│   ├── dev/ (3 files only)
│   ├── tuning/ (4 core scripts)
│   └── lint/ (tooling)
├── docs/ (6 core files)
│   ├── README.md
│   ├── K4_MASTER_PLAN.md
│   ├── AGENTS_ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── CHANGELOG.md
│   └── TECHDEBT.md (this file)
└── tests/ (249 passing)
```

---

## 🚧 Remaining High Priority Debt

### 1. Agent Implementation Gap (CRITICAL)

**Problem:** SPY is fully implemented (435 lines), but OPS and Q are just text prompts

**Impact:** Cannot scale to thousands of hypotheses or validate results at scale

**Solution:**

- Implement `src/kryptos/agents/ops.py` (~1,000 lines)
  - Multiprocessing orchestrator
  - Queue management
  - Resource monitoring
  - Timeout enforcement
- Implement `src/kryptos/agents/q.py` (~800 lines)
  - Statistical validation
  - Anomaly detection
  - False positive filtering
  - Result sanity checks

**Estimate:** 2-3 days of focused work

### 2. Tuning Scripts Consolidation

**Problem:** 4 scripts in `scripts/tuning/` with potential redundancy

**Files:**

- `crib_weight_sweep.py`
- `pick_best_weight.py`
- `compare_crib_integration.py`
- `tiny_tuning_sweep.py`
- `run_rarity_calibration.py`

**Action Needed:** Review for duplicate logic, ensure all use package APIs, create single README

**Estimate:** 2-3 hours

### 3. Performance & Profiling

**Weight Calibration:**

- Positional letter deviation weight needs calibration
- Rarity-weighted crib bonus evaluation
- Stage timing collection standardization

**Profiling Targets:**

- Hill 3x3 key assembly loops
- Transposition route enumeration
- Scoring aggregation hotspots

**Tools:** cProfile or pyinstrument for composite runs

### 4. Artifact Provenance

**Missing:**

- Provenance hashing for run reproducibility
- Standardized timing metadata
- Optional artifact compression

**Implementation:** Expand `kryptos.paths` module with `provenance_hash()` helper

---

## 📋 Medium Priority Debt

### Code Quality

- [ ] Eliminate remaining broad exception handlers
- [ ] Add error-path tests for scoring (fallback data, malformed inputs)
- [ ] Centralize configuration validation
- [ ] Add pre-commit hooks

### Documentation

- [ ] Expand API_REFERENCE.md with all public functions
- [ ] Add docstring examples for key modules
- [ ] Create CONTRIBUTING.md with guidelines

### Testing

- [ ] Increase coverage targets (currently good but not measured)
- [ ] Add integration tests for agent coordination
- [ ] Add performance regression tests

---

## ✅ Debt Elimination Checklist

**Structural (DONE):**

- [x] Consolidate docs/ (20 → 6 files)
- [x] Delete scripts/experimental/ (100% removal)
- [x] Clean scripts/dev/ (8 → 3 files)
- [x] Move demos to package (scripts/demo/ → src/kryptos/examples/)
- [x] Single hypothesis runner (run_hypothesis.py working)

**Agents (IN PROGRESS):**

- [x] SPY agent implementation (435 lines, 10 tests passing)
- [ ] OPS agent implementation (text prompt → Python code)
- [ ] Q agent implementation (text prompt → Python code)

**Performance (TODO):**

- [ ] Weight calibration sweep
- [ ] Profiling harness for hotspots
- [ ] Artifact provenance hashing

**Quality (TODO):**

- [ ] Exception handling audit
- [ ] Scoring edge case tests
- [ ] Pre-commit hooks
- [ ] Coverage measurement

---

## 🎯 Next Actions

**Immediate (This Sprint):**

1. Implement OPS agent (parallel execution orchestrator) 2. Implement Q agent (statistical validation) 3. Review tuning/
scripts for redundancy 4. Add profiling to hypothesis runner

**Short Term (Next Sprint):**

1. Weight calibration studies 2. Artifact provenance system 3. API documentation expansion 4. Pre-commit hooks setup

**Long Term:**

1. SPY LLM/NLP upgrade (Phase 1: spaCy/NLTK) 2. Embedding-based pattern matching 3. Metrics export
(Prometheus/OpenTelemetry) 4. MCP server for agent state exposure

---

## 📊 Tech Debt Burn Down

| Sprint | Files Deleted | LOC Removed | Agent Progress |
|--------|---------------|-------------|----------------|
| Oct 24 | 30+ files | ~5,000 | SPY ✅ |
| Next   | TBD | TBD | OPS ⏳ Q ⏳ |

**Goal:** Zero redundant files, all agents implemented, <5% tech debt overhead

---

**Last Updated:** 2025-10-24
| Script files with core logic | <5 |
| Broad `except Exception:` occurrences | 0 |
| Library prints | 0 |
| Fallback import ladders | 0 |
| Unimplemented scoring TODOs | 0 |

### Next Immediate Steps
1. Calibrate positional deviation weight. 2. Add provenance hash to attempt/decision metadata. 3. Remove deprecated demo
wrappers post CI module usage. 4. Introduce `DEPRECATIONS.md` (added) and implement warning emission. 5. Draft
`API_REFERENCE.md`.

Last updated: 2025-10-24T01:03Z
## Test & Verification Additions

- New tests for: root/path helpers, artifact path builder, logging setup idempotence, scoring new
features, stage adapters, deprecation warnings emission.
- Coverage gate ensures removed duplicates do not leave untested gaps.

## Metrics We Will Track Post-Cleanup

| Metric | Current (est.) | Target |
| ------ | -------------- | ------ |
| Duplicate module pairs | 2+ | 0 |
| Script files with core logic | >15 | <5 (all wrappers) |
| Broad `except Exception:` occurrences | >4 | 0 |
| Library prints | >1 | 0 |
| Fallback import ladders | >10 | 0 |
| Unimplemented TODOs in scoring | 3 | 0 |

### Logging Rollout Status (2025-10-23)

Completed:

- Central logging helper `kryptos.logging.setup_logging` implemented and adopted by CLI.
- CLI subcommands migrated from print-only to mixed logging + JSON (with `--quiet` suppression).
- Legacy shim scripts (`spy_eval`, autopilot demo) now minimal and slated for eventual removal.
- Public API export gap (`k3_decrypt`) restored to satisfy tests.

Outstanding script migrations (prints remain; convert to logging in phased order):

1. Dev operational scripts (`scripts/dev/*`): retry loops, daemon orchestration, plan execution. 2. Tuning scripts
(`scripts/tuning/*`): artifact path/status lines; change prints to logger.info and add `--json`/`--quiet` parity. 3.
Experimental examples/tools: educational output acceptable; introduce optional `--log-level` to silence in automated
runs. 4. Demo scripts: convert status messages to `kryptos.demo` logger for consistency. 5. Lint/check tooling: keep
direct prints (they are user-facing diagnostics) but annotate as intentional.

Target migration sequence:

- Phase 1 (Dev): spy_extractor, orchestrator, ask_triumverate, create_pr.
- Phase 2 (Tuning): pick_best_weight, crib_weight_sweep, compare_crib_integration,
run_rarity_calibration.
- Phase 3 (Demos/Examples): run_k4_demo, sample_composite_demo, sections_demo.
- Phase 4 (Experimental tools optional): aggregate_spy_phrases, generate_top_candidates.

Policy: After Phase 2 completion, metric "Library prints" must be 0 (only scripts allowed). After Phase 3, all remaining
prints are either test fixtures or interactive tools.

Follow-up Tasks:

- Add `tests/test_dev_logging.py` verifying orchestrator and spy_extractor logging usage.
- Document logging usage patterns in `README.md` / new `LOGGING.md`.
- Schedule removal of shim scripts (spy_eval, autopilot demo stub) after two minor releases once CI
confirms unused.

Risks & Mitigations:

- Excessive log volume during brute-force runs: add rate-limited progress logger or periodic
summaries.
- Accidental double handlers: existing idempotent marker `_kryptos_handler` prevents duplication.

Success Criteria:

- All dev/tuning scripts accept `--log-level` and optionally `--quiet`.
- No prints remain in package modules (excluding deliberate stdout JSON emission in CLI).
- Logging documentation and deprecation timeline published.

## Open Questions (Resolve During Phase A)

- Keep or remove unfinished Berlin clock scoring stub? (Decide: integrate or delete.)
- Implement cryptographic stubs vs future roadmap? (Delete now; reintroduce when spec defined.)
- Argparse vs click for CLI? (Default argparse unless complex UX required.)

## Immediate Next Step

Reporting & paths consolidation: migrate any remaining reporting shim to `kryptos/reporting.py`, introduce
`kryptos/paths.py` + `kryptos/logging.py`, then delete stale references.

Verification note: Physical duplicate directories under `src/` removed; legacy duplicate modules purged; reporting
consolidated; spy extractor migrated; positional letter deviation metric integrated; artifact path standardized under
`artifacts/k4_runs/`. Spy eval shims physically deleted (former `scripts/tuning/spy_eval.py` and
`src/kryptos/scripts/tuning/spy_eval.py`); canonical harness lives only at `src/kryptos/tuning/spy_eval.py`. Any future
reintroduction of script-level spy eval must be a thin CLI wrapper calling the canonical module.

--- Last updated: 2025-10-23T23:57Z (spy namespace, artifact path consolidation, positional deviation metric, new
calibration & provenance tasks) --- Last updated: 2025-10-23T24:30Z (CLI logging rollout; compatibility shims; logging
migration plan added)

## Organizational Refactor Plan (Proposed)

Goal: Reduce root-level module clutter and clarify separation between infrastructure (core), domain logic (sections,
scoring), and public API exports.

Target structure: 1. `kryptos/core/` — move `logging.py`, `paths.py`, `deprecation.py`. 2. `kryptos/sections/` — retain
existing `k1/`, `k2/`, `k3/`, `k4/` plus a lightweight `sections.py` mapping. 3. Optional `kryptos/analysis/` — migrate
heavier analytical helpers from `analysis.py` if expansion continues. 4. Keep `reporting.py` root-level (user-facing).
5. Evaluate `ciphers.py` constants; if minimal keep, otherwise relocate into `core/constants.py`.

Phased tasks:
- Phase 1: Introduce `core/` package with copies of modules; add deprecation warnings in old
locations.
- Phase 2: Update internal imports & tests; remove fallback ladders.
- Phase 3: Document changes (README + DEPRECATIONS.md) and remove old stubs after one minor release.

Backward compatibility strategy:
- Old root modules emit `DeprecationWarning` for one minor version.
- Public API (`kryptos.__init__`) continues to re-export stable names like `setup_logging`.

Risks & mitigations:
- External code relying on deep imports: mitigate with deprecation window.
- Over-segmentation: limit new packages to `core/` unless justified by growth.

Success metrics:
- Root-level Python files (excluding `__init__.py`) reduced to <=3.
- Zero import fallback ladders.
- All deprecation warnings removed after window.
