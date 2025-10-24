# Kryptos Technical Debt & Cleanup Plan
Breadcrumb: Architecture > Tech Debt > Cleanup Plan

> Policy: No more shims, fallback import ladders, or duplicate modules. We delete, migrate, and
## Other Docs

- REORG.md
- SECTIONS.md
- TOMORROW_PLAN.md
- EXPERIMENTAL_TOOLING.md
- 10KFT.md

## Guiding Principles

- Single canonical namespace: all library code lives under `kryptos/` (including K4 logic under
	`kryptos/k4/`).
- No duplicate modules or parallel implementations.
REORG.md SECTIONS.md EXPERIMENTAL_TOOLING.md 10KFT.md AUTOPILOT.md ROADMAP.md
- Documentation consolidated. Plans and deprecated notes move to one location with lifecycle
	policies.
- Deprecations use `warnings.warn(DeprecationWarning)` until removal.

## High Impact Debt (Tackle First)

1. Split namespace (historical `src/k4/` vs `kryptos/k4/`). (Completed) 2. Duplicate scoring modules
(`src/scoring/fitness.py` & `src/kryptos/scoring/fitness.py`). (Removed; single source) 3. Reporting duplication
(`src/report.py` + shim `src/kryptos/report.py`). (Completed; canonical
## Kryptos Technical Debt & Cleanup Plan
Breadcrumb: Architecture > Tech Debt > Cleanup Plan

> Policy: No more shims, fallback import ladders, or duplicate modules. We delete, migrate, and unify. Every item
results in code or deletion — no shims.

### High Impact Debt (Top Priority)
1. Positional letter deviation weight calibration & evaluation dataset. 2. Artifact provenance hashing & optional
compression. 3. Remaining hardcoded artifact paths (ensure all use `kryptos.paths`). 4. Eliminate any residual broad
exception handlers. 5. Centralize configuration validation & logging filters.

### Medium Impact Debt
- Script proliferation (ensure all logic lives in package; wrappers thin).
- Pending reporting consolidation edge cases.
- Expand scoring error-path tests (fallback data, malformed inputs).
- Remove lingering duplicate doc sections.

### Lower Impact / Polish
- Deprecation warnings for legacy demo wrappers.
- Pre-commit hooks & CI coverage gate.
- API surface documentation (planned API_REFERENCE.md).

### Structural Phases (Simplified)
- Phase A: Consolidation (completed major moves; validate no fallback import ladders).
- Phase B: CLI unification (subcommands stable; prune wrappers).
- Phase C: Scoring enhancements (positional calibration, rarity-weight integration).
- Phase D: Quality (logging cleanup, provenance, tests, coverage targets).
- Phase E: Operational (daemon safety, metrics placeholders).
- Phase F: Documentation (breadcrumbs, index, deprecations, API reference).

### No-Shim Enforcement Checklist
- No `shim` filenames or comments marking re-export.
- Single import path per module (no ladders).
- No duplicate Python filenames in different internal paths.
- Library modules free of `print()` and `logging.basicConfig`.

### Metrics Targets
| Metric | Target |
|--------|--------|
| Duplicate module pairs | 0 |
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
