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

## Summary Counts (Post daemon & plan wrapper removal 2025-10-24)

- KEEP: 8
- REMOVE / REMOVED: 18 (added ask_best_next.py, run_plan.py, daemon set)
- STUB: 0 (all prior stubs cleared)
- MIGRATE: 5 (demo & autopilot examples, tiny sweep, run_ops_tiny_sweep, compare_crib_integration
decision)
- AUDIT: 2 (extract_spy_cribs.py, create_pr.py)
- HISTORICAL: 1 (k3_double_rotation.py)

## Core Tuning Scripts

| File | Decision | Notes |
|------|----------|-------|
| crib_weight_sweep.py | KEEP | Canonical sweep; CLI subcommand mirrors behavior. |
| pick_best_weight.py | REMOVE | Superseded by CLI pick-best subcommand. |
| compare_crib_integration.py | AUDIT | Assess relevance; may merge into summarize-run. |
| tiny_tuning_sweep.py | KEEP | Deterministic harness (possible test fixture). |
| spy_eval.py | REMOVED | Deleted (replaced by package API + CLI spy-eval). |

## Examples

| File | Decision | Notes |
|------|----------|-------|
| run_autopilot_demo.py | MIGRATE | Promote to kryptos.examples then delete duplicate experimental copy. |

## Experimental Examples

| File | Decision | Notes |
|------|----------|-------|
| run_full_smoke.py | REMOVE | Replaced by chained CLI examples. |
| run_autopilot_demo.py | MIGRATE | Consolidate; see Examples above. |
| condensed_tuning_report.py | REMOVE | Logic merged into `kryptos.k4.report` (write_condensed_report). |
| generate_top_candidates.py | REMOVE (Replaced) | Markdown generation now in `kryptos.k4.report` (write_top_candidates_markdown). |
| (removed) run_ops_tiny_sweep.py | Removed (Migrated) | Use `kryptos.examples.tiny_weight_sweep` or CLI sweep. |
| sections_demo.py | KEEP | Educational; future examples module move. |
| sample_composite_run.py | KEEP | Pipeline illustration; README referenced. |

## Experimental Tools

| File | Decision | Notes |
|------|----------|-------|
| run_hill_search.py | REMOVE | Hill logic lives in package. |
| run_hill_canonical.py | REMOVE | Thin wrapper superseded. |
| run_pipeline_sample.py | REMOVE | Use k4-decrypt CLI instead. |
| holdout_score.py | REMOVE | Replaced by tuning-holdout-score CLI. |
| run_sweep_on_artifact_samples.py | REMOVE | Covered by weight sweep CLI. |
| clean_and_summarize_matches.py | REMOVE | end_to_end_process covers. |
| summarize_crib_hits.py | REMOVE | crib_hit_counts integrated. |
| aggregate_spy_phrases.py | REMOVE (Replaced) | Logic in `kryptos.spy.aggregate_phrases`. |
| extract_spy_cribs.py | AUDIT | Security/determinism review before promotion. |
| collect_sanborn_sources.py | KEEP | External fetch helper; possible relocation. |
| k3_double_rotation.py | HISTORICAL (MOVED) | Relocated to docs/archive/k3_double_rotation.py |
| remove_top_level_wrappers.py | KEEP | Internal cleanup utility. |
| auto_remove_compat_wrappers.py | KEEP | Internal cleanup utility. |

## Dev Scripts

| File | Decision | Notes |
|------|----------|-------|
| ask_triumverate.py | REMOVED | Consolidated into `kryptos.autopilot` + CLI `autopilot`. |
| ask_best_next.py | REMOVED | Redundant helper deleted; use `kryptos autopilot --plan`. |
| autopilot_daemon.py | REMOVED | Loop logic now in `autopilot.run_autopilot_loop`. |
| cracker_daemon.py | REMOVED | Candidate acceptance & decision writing merged into autopilot module. |
| manager_daemon.py | REMOVED | Parameter sweep shim deprecated; tuning handled via existing modules/CLI. |
| (removed) spy_extractor.py | Removed (Replaced) | Logic lives in `kryptos.spy.extractor.extract`. |
| run_plan.py | REMOVED | Plan injection handled by CLI `--plan` flag. |
| create_pr.py | AUDIT | Check for secret leakage; potential automation move. |
| migrate_run_artifacts.py | REMOVED | Obsolete; no legacy run_* dirs outside k4_runs. |
| migrate_misplaced_reports.py | REMOVED | Obsolete; no misplaced src/artifacts/reports tree present. |
| orchestrator.py | KEEP | Multi-stage coordination; candidate for packaging. |
| README.md / README_pr.md | KEEP | Docs; keep updated. |

## Demo

| File | Decision | Notes |
|------|----------|-------|
| run_k4_demo.py | MIGRATE | Promote to kryptos.examples.k4_demo; then remove script. |
| README.md | KEEP | Demo index; update after migrations. |

## Cross-repo / Non-Python

| Path | Decision | Notes |
|------|----------|-------|
| games/scripts/download-sounds.js | KEEP | Unrelated game asset helper. |

## Duplicate / Redundant Files

spy_eval.py removed; package implementation + CLI subcommand in place. generate_top_candidates.py
removed; replaced by `kryptos.k4.report.write_top_candidates_markdown`. condensed_tuning_report.py
removed; replaced by `kryptos.k4.report.write_condensed_report`. aggregate_spy_phrases.py removed;
replaced by `kryptos.spy.aggregate_phrases`.

## Immediate Execution Plan (Refreshed)

1. Finalize removal of legacy demo runner after CLI example addition. 2. Validate
`examples.tiny_weight_sweep` outputs (legacy tiny sweep removed). 3. Audit `extract_spy_cribs.py`
(security/determinism) and decide promote vs remove. 4. Fold or delete `compare_crib_integration.py`
(merge into summarize-run/report). 5. Migrate autopilot & demo examples into `examples/` canonical
package path. 6. Add `tuning-report` CLI subcommand wrapping report utilities. 7. Profile positional
letter deviation weight and document calibration results.

Updated: 2025-10-24T00:45Z (migrated run_k4_demo.py & run_autopilot_demo.py to kryptos.examples.*)

Change Log Addendum:

- Implemented rarity-weighted crib bonus in `kryptos.k4.scoring.rarity_weighted_crib_bonus`.
- Fully removed deprecated `spy_eval.py` legacy script.
- Removed legacy `PipelineExecutor`; tests migrated to pipeline/composite utilities.
