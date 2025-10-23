# Kryptos Technical Debt & Cleanup Plan

> Policy: No more shims, fallback import ladders, or duplicate modules. We delete, migrate, and
unify. Every item below either gets implemented properly or removed.

## Guiding Principles
- Single canonical namespace: all library code lives under `kryptos/` (including K4 logic under
`kryptos/k4/`).
- No duplicate modules or parallel implementations.
- No script contains core logic: scripts become thin CLI wrappers delegating to package functions.
- Imports are stable (`from kryptos...`). No `from src.k4`, no `from k4`, no `from kryptos.src.k4`.
- Library modules NEVER call `logging.basicConfig` or print; use a logger configured externally.
- Broad `except Exception:` is forbidden. Catch explicit exceptions or let them surface.
- Artifacts managed via helper functions, not ad-hoc path concatenation.
- Documentation consolidated. Plans and deprecated notes move to one location with lifecycle
policies.
- Deprecations use `warnings.warn(DeprecationWarning)` until removal.

## High Impact Debt (Tackle First)
1. Split namespace (`src/k4/` vs `src/kryptos/`). 2. Duplicate scoring modules
(`src/scoring/fitness.py` & `src/kryptos/scoring/fitness.py`). 3. Reporting duplication
(`src/report.py` + shim `src/kryptos/report.py`). 4. Re-export / fallback import shims in
`kryptos/__init__.py`. 5. Logging side-effects in library (e.g. `kryptos/ciphers.py`). 6. Hardcoded
root/artifact paths sprinkled in scripts. 7. Build artifacts (`kryptos.egg-info/`) residing under
`src/`. 8. Cryptographic stub functions (`polybius_decrypt`, `transposition_decrypt`) with no
roadmap.

## Medium Impact Debt
- Script proliferation (daemon variants, tuning scripts with near-identical logic).
- Spy extractor logic living only in script form.
- Multiple pipeline sample / demo wrappers.
- Unimplemented scoring TODOs (positional crib weighting, partial matches, external ngram + crib
supply).
- Sleep-based daemon loops (`time.sleep`) instead of structured scheduling/backoff.
- Stage adapter TODOs and `mock_stage.py` placeholder.
- Mixed dependency declarations (`pyproject.toml` & `requirements.txt`).
- Unstructured config objects and argument parsing spread across scripts.
- Print statements in package code (e.g. tuning evaluation output).
- Empty / placeholder package dirs (`src/kryptos/stages/`, unused `scripts/tuning` shim
directories).

## Lower Impact / Polish
- Deprecated inline comments vs formal deprecation warnings.
- Experimental tools with unclear relevance (`aggregate_spy_phrases.py`, `summarize_crib_hits.py`,
`holdout_score.py`, `k3_double_rotation.py`).
- Missing centralized logging setup helper.
- Lack of a consolidated CLI entry point grouping subcommands.
- Scattered plan & reorg docs; need README + CONTRIBUTING + DEPRECATIONS + API section.
- Missing K4 canonical ciphertext test fixture.
- Absent pre-commit & CI baseline.
- Lack of error-path test coverage for scoring fallbacks and parsing failures.

## Concrete Action Items
(Reflects current TODO list; updated here for clarity. Each item results in code or deletion — no
new shims.)

### Phase A: Structural Consolidation (Single PR target)
- Move `src/k4/` → `src/kryptos/k4/`; update all imports. Remove all multi-path import fallbacks.
- Keep only one scoring module: adopt richer implementation; delete duplicate.
- Migrate `src/report.py` into `kryptos/reporting.py`; delete shim.
- Purge re-export blocks from `kryptos/__init__.py`; expose explicit curated API.
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
- Provide `pipeline.build_default()` and use across demo/daemon/tuning.
- Remove pipeline sample wrappers after verifying parity.

### Phase C: Scoring & Adapter Enhancements
- Implement positional crib weighting & partial match scoring.
- Externalize ngram & crib sources; make loader explicit.
- Add comprehensive tests for scoring error paths & improvements.
- Implement stage adapters (hill, transposition, masking, berlin clock) or prune the interface TODO.

### Phase D: Quality & Tooling
- Introduce `kryptos/logging.py` with setup helper and documented usage.
- Replace prints with logging across package.
- Pre-commit configuration (ruff/black/mdformat, tests).
- CI workflow (install, lint, test, coverage, artifact summary).
- Add `tests/data/k4_sample.txt` fixture.
- Formalize deprecation workflow (`DEPRECATIONS.md`).
- Consolidate docs (archive old plan files in `docs/archive/`).
- Document final public API surface in README.

### Phase E: Operational Refinements
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
Proceed with Phase A migration (move `src/k4` into `src/kryptos/k4`, update imports, delete
duplicate scoring & reporting shim) WITHOUT adding compatibility shims.

--- Last updated: 2025-10-23
