# Experimental Tooling Inventory ================================

Overview of scripts under `scripts/experimental/` with purpose and disposition.

| Path | Purpose | Disposition | Action | Target | Prerequisites |
|------|---------|-------------|--------|--------|---------------|
| examples/run_autopilot_demo.py | Demo autopilot (Q/OPS/SPY) chain | Keep (convert to package example) | Promote to examples module | Nov 2025 | CLI stable + doc snippet added |
| (removed) examples/run_full_smoke.py | Chained smoke run (demo→OPS→SPY→report) | Removed (CLI chain examples to replace) | N/A | 2025-10-23 | README examples pending add |
| examples/run_ops_tiny_sweep.py | Tiny crib weight sweep helper | Keep (doc optional) | Merge into tuning docs | Dec 2025 | CLI tuning subcommands tested |
| (removed) examples/condensed_tuning_report.py | Summarize sweep CSV | Removed (to migrate into report API) | Implement report module | 2025-10-23 | `kryptos.k4.report` pending |
| examples/generate_top_candidates.py | Generate markdown candidate report | Keep (consider package reporter) | Promote | Dec 2025 | Reporter module skeleton + tests |
| (removed) tools/run_hill_search.py | Random hill key diagnostic | Removed (package hill utilities) | N/A | 2025-10-23 | hill_search API present |
| (removed) tools/run_hill_canonical.py | Thin hill_constraints wrapper | Removed (use kryptos.k4 APIs) | N/A | 2025-10-23 | API consolidated |
| (removed) tools/run_pipeline_sample.py | Minimal pipeline wrapper | Removed (use k4-decrypt CLI) | N/A | 2025-10-23 | CLI decrypt available |
| (removed) tools/holdout_score.py | Holdout scoring helper | Removed (CLI subcommand) | N/A | 2025-10-23 | `tuning-holdout-score` implemented |
| (removed) tools/run_sweep_on_artifact_samples.py | Crib sweep on existing artifacts | Removed (weight sweep CLI supersedes) | N/A | 2025-10-23 | CLI sweep present |
| (removed) tools/clean_and_summarize_matches.py | Clean matches & summarize | Removed (artifacts pipeline) | N/A | 2025-10-23 | end_to_end_process available |
| (removed) tools/summarize_crib_hits.py | Count crib hits per run | Removed (artifacts pipeline) | N/A | 2025-10-23 | crib_hit_counts integrated |
| tools/aggregate_spy_phrases.py | Aggregate SPY tokens | Keep (may merge) | Merge into kryptos.spy | Dec 2025 | Spy namespace extraction refactor |
| tools/extract_spy_cribs.py | Extract probable crib tokens | Keep (security review later) | Audit & Promote | Jan 2026 | Security review + tests |
| tools/collect_sanborn_sources.py | Fetch & summarize Sanborn sources | Keep (external fetch) | Keep | -- | None |
| tools/k3_double_rotation.py | K3 rotation demo | Keep (historical example) | Keep (tag historical) | -- | None |
| tools/remove_top_level_wrappers.py | Script cleanup helper | Keep (internal maintenance) | Keep | -- | None |

Promotion / Migration Notes:

- Reporting-focused tools (`condensed_tuning_report.py`, `generate_top_candidates.py`) → potential
`kryptos.k4.report` or extension of `kryptos.k4.tuning.artifacts`.
- `run_ops_tiny_sweep.py` → superseded by `kryptos.k4.tuning.tiny_param_sweep` (script may be
dropped once CLI tuning subcommands land).
- `run_full_smoke.py` → deprecate; replace with docs snippet chaining CLI + tuning API.
- `run_hill_search.py` → remove (diagnostic logic should live in a dedicated test or debug module if
still needed).
- `holdout_score.py` → evaluate for promotion if integrated into test/CI flows.
- SPY related tools (`aggregate_spy_phrases.py`, `extract_spy_cribs.py`) may consolidate into future
`kryptos.spy` namespace.

Deprecation Path Legend:

- Keep: no change planned this cycle.
- Deprecate: will be removed once CLI / API replacement is merged.
- Removed / Migrated: logic lives in package; script kept only if still referenced transitively.

## Cleanup Plan

Goal: Eliminate deprecated scripts after equivalent package APIs and CLI examples exist, promote
reusable logic, and ensure all migrations are test-covered.

Removal Criteria: 1. Equivalent function(s) in package namespace (`kryptos.*`). 2. CLI subcommand or
documented usage snippet replaces invocation pattern. 3. Tests cover former script behavior (happy
path + at least one edge case). 4. No active references in docs or other scripts (`grep` clean).

Promotion Criteria: 1. Script encapsulates reusable logic beneficial to users. 2. Can be expressed
as a pure function/module without side-effecting global paths. 3. Minimal test harness added
(pytest) with deterministic behavior.

Metrics Snapshot (post physical removal 2025-10-23):

- Removed: 11
- Keep (stable or evaluation): 11
- Migrate/Promote planned: 6
- Audit/Historical: 3

Backlog (ordered):

1. Add chained CLI example (decrypt + tuning + spy) to README_CORE & AUTOPILOT. 2. Implement
`kryptos.k4.report` and migrate reporting logic (condensed & top candidates). 3. Introduce
`kryptos.spy` namespace consolidating extraction & aggregation. 4. Promote autopilot demo into
`kryptos.examples` module path; remove duplicate experimental copy. 5. Add tests for `tuning-
holdout-score`, artifacts end_to_end_process & crib_hit_counts. 6. Migrate or retire remaining
experimental KEEP scripts after coverage.

Next Immediate Actions:
- Add CLI examples to README_CORE for weight sweep + spy eval/extract.
- Implement tests for new CLI subcommands (tuning & spy) to unblock removals.

Updated: 2025-10-23 (inventory augmented with cleanup plan & metrics)
