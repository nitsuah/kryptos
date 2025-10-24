# Kryptos Technical Debt & Cleanup Plan

> Policy: No more shims, fallback import ladders, or duplicate modules. We delete, migrate, and
unify. Every item below either gets implemented properly or removed.

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
(`src/scoring/fitness.py` & `src/kryptos/scoring/fitness.py`). (Removed; single source) 3. Reporting
duplication (`src/report.py` + shim `src/kryptos/report.py`). (Completed; canonical
`kryptos/reporting.py`) 4. Section inconsistency (K1/K2 logic in `main.py` & `ciphers.py`, K3 inside
library). (Pending cleanup of residual references) 5. Positional letter deviation weight calibration
& evaluation dataset (new) — tune composite weight to avoid overfitting. 6. Artifact provenance
hashing & compression option (new) — ensure reproducibility & storage efficiency. 7. Hardcoded
root/artifact paths sprinkled in scripts. (Pending; standardize via helper) 8. Build artifacts
(`kryptos.egg-info/`) residing under `src/`. (Pending) 9. Cryptographic stub / legacy helpers
without roadmap (evaluate `transposition_decrypt`). (Pending decision)
## Medium Impact Debt

- Script proliferation (daemon variants, tuning scripts with near-identical logic).
- Spy extractor logic living only in script form. (Resolved: migrated to `kryptos.spy.*`)
- Multiple pipeline sample / demo wrappers.
- Unimplemented scoring TODOs (positional crib weighting, partial matches, external ngram + crib
	supply).
- Print statements in package code (e.g. tuning evaluation output).
- Central logging helper absent (plan: introduce `kryptos.logging.setup()` and replace prints).
(New)
- Removed legacy duplicate dirs (previous `src/k4/`, `src/scoring/`, `src/stages/`, stray
`kryptos/stages/`).
## Lower Impact / Polish

- Deprecated inline comments vs formal deprecation warnings.
	`holdout_score.py`, `k3_double_rotation.py`). Post-processing scripts (`summarize_crib_hits.py`,
	`clean_and_summarize_matches.py`) migrated into `kryptos.k4.tuning.artifacts` (schedule removal of
	legacy wrappers after deprecation window).
- Missing centralized logging setup helper.
- Demo runner legacy path (`scripts/demo/run_k4_demo.py`) pending migration to examples + CLI doc.
(New)
- Lack of a consolidated CLI entry point grouping subcommands.
- Scattered plan & reorg docs; need README + CONTRIBUTING + DEPRECATIONS + API section.
- Missing K4 canonical ciphertext test fixture.
- Absent pre-commit & CI baseline.
- Lack of error-path test coverage for scoring fallbacks and parsing failures.

## Concrete Action Items

(Reflects current TODO list; updated here for clarity. Each item results in code or deletion — no
new shims.)

### Phase A: Structural Consolidation (Single PR target)

- Move `src/k4/` → `kryptos/k4/`; update all imports. Remove all multi-path import fallbacks.
(Completed)
- Keep only one scoring module: adopt richer implementation; delete duplicate. (Completed)
- Migrate `src/report.py` into `kryptos/reporting.py`; delete shim. (Completed)
- Unify section layout: introduce `kryptos/k1/`, `kryptos/k2/`, `kryptos/k3/` packages each with
`decrypt()`; deprecate orchestration in `main.py` & raw `kryptos_k3_decrypt` exposure. (Completed)
- Provide `kryptos/sections.py` discovery mapping: `{'K1': k1.decrypt, 'K2': k2.decrypt, 'K3':
k3.decrypt, 'K4': k4.decrypt_best}`. (Completed placeholder for K4)
- Add `kryptos/k4/decrypt_best()` convenience wrapper over pipeline default. (Completed)
- Refactor `main.py` into example or CLI entrypoint (`examples/run_sections.py` or
`kryptos/cli/sections.py`). (Completed example refactor)
- Purge re-export blocks from `kryptos/__init__.py`; expose explicit curated API. (In progress)
- Remove `logging.basicConfig` calls from any library modules.
- Add `kryptos/paths.py` with `get_repo_root()` sentinel and `build_artifact_path()` helpers.
- Delete `kryptos.egg-info/` from version control; update `.gitignore`.
- Implement or delete crypto stubs; prefer delete if not on near roadmap.

### Phase B: CLI & Workflow Unification

- Introduce `kryptos/cli/` package with argparse (or click) subcommands: `pipeline`, `daemon`,
`tuning`, `spy`, `report`.
- Merge daemons into single configurable loop.
- Consolidate tuning scripts into subcommands (sweep, eval, pick-weight).
- Integrate spy extractor logic into `kryptos/spy/extractor.py`; script becomes trivial wrapper.
	(Completed — legacy script removed)
- Provide `pipeline.build_default()` and use across demo/daemon/tuning.
- Remove pipeline sample wrappers after verifying parity.

### Phase C: Scoring & Adapter Enhancements

- Implement positional crib weighting & partial match scoring.
- Positional letter deviation weight calibration & evaluation corpus build. (New)
- Externalize ngram & crib sources; make loader explicit.
- Add comprehensive tests for scoring error paths & improvements.
- Implement stage adapters (hill, transposition, masking, berlin clock) or prune the interface TODO.

### Phase D: Quality & Tooling

- Introduce `kryptos/logging.py` with setup helper and documented usage.
- Artifact provenance: add hash/version stamping to run metadata. (New)
- Replace prints with logging across package.
- Pre-commit configuration (ruff/black/mdformat, tests).
- CI workflow (install, lint, test, coverage, artifact summary).
- Add `tests/data/k4_sample.txt` fixture.
- Formalize deprecation workflow (`DEPRECATIONS.md`).
- Consolidate docs (archive old plan files in `docs/archive/`).
- Document final public API surface in README.

### Phase E: Operational Refinements

- tbd

### Phase F: Documentation Re-Org

- Create `docs/SECTIONS.md` (uniform K1–K4 API surface & usage examples). (Completed)
- Archive dated planning docs (`PLAN.md`, older strategy snapshots) into `docs/archive/` after
summarizing deltas.
- Relocate deep dive `K4_STRATEGY.md` to `docs/sections/K4.md`; keep top-level index lean.
- Add `DEPRECATIONS.md` capturing removal timeline (legacy `src/*`, shims, soon direct K3 decrypt
alias).
- (Completed) Autopilot usage details merged; `TOMORROW_PLAN.md` archived
(`archive/TOMORROW_PLAN_2025-10-23.md`).
- Update `10KFT.md` to reflect unified section packages, removal of legacy duplicates, and canonical
reporting.
- Introduce `docs/ARCHIVE/` index listing archived files with brief rationale.

- Replace raw sleeps with a scheduler/backoff helper.
- Unify configuration into `kryptos/config` with validation (dataclasses + type checks or pydantic).
- Eliminate any side-effect executing imports.
- Remove `mock_stage.py` if not upgraded to a proper example.

## No-Shim Enforcement Checklist

Before merging a structural PR:

- [ ] No file named `shim` or containing 're-export shim' comment.
- [ ] No import fallback ladders (single, direct import paths only).
- [ ] No duplicate filename existing in two library paths.
- [ ] All library modules free of `logging.basicConfig` & `print` (except explicit debug guarded by
logger).
- [ ] `.egg-info` not tracked.

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

## Open Questions (Resolve During Phase A)

- Keep or remove unfinished Berlin clock scoring stub? (Decide: integrate or delete.)
- Implement cryptographic stubs vs future roadmap? (Delete now; reintroduce when spec defined.)
- Argparse vs click for CLI? (Default argparse unless complex UX required.)

## Immediate Next Step

Reporting & paths consolidation: migrate any remaining reporting shim to `kryptos/reporting.py`,
introduce `kryptos/paths.py` + `kryptos/logging.py`, then delete stale references.

Verification note: Physical duplicate directories under `src/` removed; legacy duplicate modules
purged; reporting consolidated; spy extractor migrated; positional letter deviation metric
integrated; artifact path standardized under `artifacts/k4_runs/`.

--- Last updated: 2025-10-23T23:57Z (spy namespace, artifact path consolidation, positional
deviation metric, new calibration & provenance tasks)
