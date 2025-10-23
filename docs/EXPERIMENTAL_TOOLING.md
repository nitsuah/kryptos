# Experimental Tooling Inventory ================================

Overview of scripts under `scripts/experimental/` with purpose and disposition.

| Path | Purpose | Disposition |
|------|---------|-------------|
| examples/run_autopilot_demo.py | Demo autopilot (Q/OPS/SPY) chain | Keep (convert to package example) |
| examples/run_full_smoke.py | Chained smoke run (demo→OPS→SPY→report) | Deprecate (replace with package doc snippet) |
| examples/run_ops_tiny_sweep.py | Tiny crib weight sweep helper | Keep (doc optional) |
| examples/condensed_tuning_report.py | Summarize sweep CSV | Keep (may refactor into report util) |
| examples/generate_top_candidates.py | Generate markdown candidate report | Keep (consider package reporter) |
| tools/run_hill_search.py | Random hill key diagnostic | Deprecate (remove) |
| (removed) tools/run_hill_canonical.py | Thin hill_constraints wrapper | Removed (use kryptos.k4 APIs) |
| (removed) tools/run_pipeline_sample.py | Minimal pipeline wrapper | Removed (use CLI) |
| tools/holdout_score.py | Holdout scoring helper | Keep (could promote if widely used) |
| tools/run_sweep_on_artifact_samples.py | Crib sweep on existing artifacts | Keep (niche) |
| (migrated) tools/clean_and_summarize_matches.py | Clean matches & summarize | Replaced by `kryptos.k4.tuning.artifacts.clean_all_match_files` + `summarize_run` |
| (migrated) tools/summarize_crib_hits.py | Count crib hits per run | Replaced by `kryptos.k4.tuning.artifacts.crib_hit_counts` / `end_to_end_process` |
| tools/aggregate_spy_phrases.py | Aggregate SPY tokens | Keep (may merge) |
| tools/extract_spy_cribs.py | Extract probable crib tokens | Keep (security review later) |
| tools/collect_sanborn_sources.py | Fetch & summarize Sanborn sources | Keep (external fetch) |
| tools/k3_double_rotation.py | K3 rotation demo | Keep (historical example) |
| tools/remove_top_level_wrappers.py | Script cleanup helper | Keep (internal maintenance) |

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

Updated: 2025-10-23 (duplicate entries removed; dispositions refreshed)
