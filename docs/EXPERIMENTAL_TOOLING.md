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
| tools/clean_and_summarize_matches.py | Clean matches & summarize | Keep (reporting candidate) |
| tools/summarize_crib_hits.py | Count crib hits per run | Keep (combine with reporting) |
| tools/aggregate_spy_phrases.py | Aggregate SPY tokens | Keep (may merge) |
| tools/extract_spy_cribs.py | Extract probable crib tokens | Keep (security review later) |
| tools/collect_sanborn_sources.py | Fetch & summarize Sanborn sources | Keep (external fetch) |
| tools/k3_double_rotation.py | K3 rotation demo | Keep (historical example) |
| tools/remove_top_level_wrappers.py | Script cleanup helper | Keep (internal maintenance) |
| tools/k3_double_rotation.py | Demonstrates K3 double rotation | Keep |

Promotion Candidate Notes:

- Reporting-focused tools (condensed report, top candidates) could become `kryptos.report` helpers.
- Holdout scoring may move into `kryptos.scoring` if reused by tests or CI.

Updated: 2025-10-23 """
