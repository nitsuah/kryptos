# Archived & Classified Scripts

Exhaustive disposition for every file under `scripts/` (including experimental subdirs) as of
2025-10-23.

Status Legend:
- KEEP: Retained in current cycle.
- REMOVE: Logic superseded; script scheduled for deletion.
- STUB: Temporarily replaced with a stub raising SystemExit while docs propagate (intermediate state
before final removal).
- MIGRATE: Will be refactored into package module / CLI.
- AUDIT: Requires review (security, side-effects) prior to promotion or removal.
- HISTORICAL: Preserved for provenance (tagged, not executed in CI).

## Summary Counts
- KEEP: TBD (after stub pass)
- REMOVE (target): 9
- STUB (this pass): 9
- MIGRATE: 6
- AUDIT: 2
- HISTORICAL: 1

## Core Tuning Scripts (`scripts/tuning/`)
| File | Decision | Notes |
|------|----------|-------|
| crib_weight_sweep.py | KEEP | Canonical sweep implementation for CLI.
| pick_best_weight.py | MIGRATE | Fold into tuning CLI helper or artifacts module; keep until tests added.
| compare_crib_integration.py | AUDIT | Validate ongoing usefulness; consider merge into summarize run.
| tiny_tuning_sweep.py | KEEP | Deterministic test harness; consider param fixture.
| spy_eval.py (duplicate in src) | REMOVE (duplicate) | Eliminate duplication; ensure imported module path used by CLI.

## Lint Scripts (`scripts/lint/`)
All KEEP (tooling infra): run_lint.ps1, run_tests_coverage.ps1, reflow_md.py,
pep8_spacing_autofix.py, check_md.py.

## Examples (`scripts/examples/`)
| File | Decision | Notes |
|------|----------|-------|
| run_autopilot_demo.py | MIGRATE | Convert to `kryptos.examples.autopilot_demo` module & doc snippet.

## Experimental Examples (`scripts/experimental/examples/`)
| File | Decision | Notes |
|------|----------|-------|
| run_full_smoke.py | STUB → REMOVE | Replaced by chained CLI examples.
| run_autopilot_demo.py | MIGRATE | Consolidate with non-experimental version; remove duplicate.
| condensed_tuning_report.py | STUB → MIGRATE | Fold into report API (`kryptos.k4.report`).
| generate_top_candidates.py | MIGRATE | Integrate as report function.
| run_ops_tiny_sweep.py | MIGRATE | Replace with CLI example; then remove.
| sections_demo.py | KEEP | Educational; later move to docs/examples package.
| sample_composite_run.py | KEEP | Pipeline illustration; incorporate into README.

## Experimental Tools (`scripts/experimental/tools/`)
| File | Decision | Notes |
|------|----------|-------|
| run_hill_search.py | STUB → REMOVE | Hill logic in package.
| run_hill_canonical.py | STUB → REMOVE | Thin wrapper; superseded.
| run_pipeline_sample.py | STUB → REMOVE | Pipeline factories & CLI cover use case.
| holdout_score.py | STUB → REMOVE | Replaced by `tuning-holdout-score` CLI subcommand.
| run_sweep_on_artifact_samples.py | STUB → REMOVE | Superseded by CLI weight sweep with samples option (future enhancement).
| clean_and_summarize_matches.py | STUB → REMOVE | Artifacts end-to-end process covers.
| summarize_crib_hits.py | STUB → REMOVE | Crib hit counting integrated.
| aggregate_spy_phrases.py | MIGRATE | Merge into spy extract / aggregator CLI.
| extract_spy_cribs.py | AUDIT | Security & determinism review; then promote.
| collect_sanborn_sources.py | KEEP (External) | Network fetch; isolate; may move to data_prep/.
| k3_double_rotation.py | HISTORICAL | Tag & relocate to docs/archive/ later.
| remove_top_level_wrappers.py | KEEP (Maintenance) | Internal cleanup; run ad-hoc.
| auto_remove_compat_wrappers.py | KEEP (Maintenance) | Internal cleanup; run ad-hoc.

## Dev Scripts (`scripts/dev/`)
| File | Decision | Notes |
|------|----------|-------|
| ask_triumverate.py | KEEP | Autopilot core.
| ask_best_next.py | KEEP | Autopilot helper.
| autopilot_daemon.py | KEEP | Long-running persona orchestrator (daemon).
| cracker_daemon.py | KEEP | Worker daemon; consider packaging later.
| manager_daemon.py | KEEP | Supervisor logic; may consolidate.
| spy_extractor.py | MIGRATE | Fold into spy CLI & package; then remove.
| run_plan.py | KEEP | Plan execution harness.
| create_pr.py | AUDIT | Verify no secret leakage; potentially move to automation/.
| migrate_run_artifacts.py | KEEP (Temp) | Remove after migration completed & tests pass.
| migrate_misplaced_reports.py | KEEP (Temp) | Same as above.
| orchestrator.py | KEEP | Multi-stage coordination; candidate for packaging.
| README.md / README_pr.md | KEEP | Documentation; keep updated.

## Demo (`scripts/demo/`)
| File | Decision | Notes |
|------|----------|-------|
| run_k4_demo.py | MIGRATE | Convert to concise README usage & CLI example; may become `kryptos.examples.k4_demo`.
| README.md | KEEP | Demo index; update after migrations.

## Cross-repo / Non-Python
| games/scripts/download-sounds.js | KEEP (Unrelated) | Game assets helper; outside K4 scope.

## Duplicate / Redundant Files Detected
- `spy_eval.py` appears both under `scripts/tuning/` and `src/kryptos/scripts/tuning/`. Remove
script copy; retain package module.

## Immediate Execution Plan
1. Replace each REMOVE target with STUB raising SystemExit & pointing to replacement. 2. Delete
duplicate `scripts/tuning/spy_eval.py` if package version exists. 3. Update
`EXPERIMENTAL_TOOLING.md` & `REORG.md` dispositions to reflect STUB or MIGRATE accurately. 4. Add
CLI examples to README_CORE (decrypt, tuning sweep + pick, summarize, holdout score, spy
eval/extract). 5. Add minimal tests for `tuning-holdout-score` and `spy-eval` subcommands. 6. Second
pass: convert STUB → actual deletion once docs + tests merged.

Updated: 2025-10-23
