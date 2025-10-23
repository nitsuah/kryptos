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

## Summary Counts (Post removals 2025-10-23)

- KEEP: 10
- REMOVE: 11 (legacy experimental scripts physically deleted)
- STUB: 0 (all prior stubs cleared)
- MIGRATE: 8 (reporting, spy aggregation/extraction, tiny sweep, demo & autopilot examples,
pick_best_weight, run_ops_tiny_sweep)
- AUDIT: 3 (extract_spy_cribs.py, create_pr.py, compare_crib_integration.py)
- HISTORICAL: 1 (k3_double_rotation.py)

## Core Tuning Scripts

| File | Decision | Notes |
|------|----------|-------|
| crib_weight_sweep.py | KEEP | Canonical sweep; CLI subcommand mirrors behavior. |
| pick_best_weight.py | MIGRATE | Fold logic into CLI/report module after tests. |
| compare_crib_integration.py | AUDIT | Assess relevance; may merge into summarize-run. |
| tiny_tuning_sweep.py | KEEP | Deterministic harness (possible test fixture). |
| spy_eval.py | REMOVE | Superseded by package + CLI spy-eval. |

## Examples

| File | Decision | Notes |
|------|----------|-------|
| run_autopilot_demo.py | MIGRATE | Promote to kryptos.examples then delete duplicate experimental copy. |

## Experimental Examples

| File | Decision | Notes |
|------|----------|-------|
| run_full_smoke.py | REMOVE | Replaced by chained CLI examples. |
| run_autopilot_demo.py | MIGRATE | Consolidate; see Examples above. |
| condensed_tuning_report.py | REMOVE | Move logic into kryptos.k4.report. |
| generate_top_candidates.py | MIGRATE | Integrate into report module. |
| run_ops_tiny_sweep.py | MIGRATE | Superseded by tuning-crib-weight-sweep CLI. |
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
| aggregate_spy_phrases.py | MIGRATE | Fold into future kryptos.spy aggregation API. |
| extract_spy_cribs.py | AUDIT | Security/determinism review before promotion. |
| collect_sanborn_sources.py | KEEP | External fetch helper; possible relocation. |
| k3_double_rotation.py | HISTORICAL | Preserve; move to docs/archive/. |
| remove_top_level_wrappers.py | KEEP | Internal cleanup utility. |
| auto_remove_compat_wrappers.py | KEEP | Internal cleanup utility. |

## Dev Scripts

| File | Decision | Notes |
|------|----------|-------|
| ask_triumverate.py | KEEP | Autopilot core. |
| ask_best_next.py | KEEP | Autopilot helper. |
| autopilot_daemon.py | KEEP | Long-running orchestrator. |
| cracker_daemon.py | KEEP | Worker daemon. |
| manager_daemon.py | KEEP | Supervisor logic. |
| spy_extractor.py | MIGRATE | Move into kryptos.spy namespace; delete after integration. |
| run_plan.py | KEEP | Plan execution harness. |
| create_pr.py | AUDIT | Check for secret leakage; potential automation move. |
| migrate_run_artifacts.py | KEEP | Temporary migration aid. |
| migrate_misplaced_reports.py | KEEP | Temporary migration aid. |
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

spy_eval.py (script) removed; package implementation + CLI subcommand in place.

## Immediate Execution Plan (Refreshed)

1. Implement kryptos.k4.report (condensed + top candidates) and remove generate_top_candidates
script. 1. Add CLI tests (tuning-*, spy-*); then remove run_ops_tiny_sweep & pick_best_weight. 1.
Create kryptos.spy namespace; migrate spy_extractor & aggregate_spy_phrases. 1. Audit
extract_spy_cribs.py (security/determinism); decide promote vs restrict. 1. Relocate
k3_double_rotation.py to docs/archive/ and update references. 1. Fold compare_crib_integration.py
into summarize-run or remove. 1. Promote demo & autopilot examples into kryptos.examples package
path.

Updated: 2025-10-23
