# Experimental Tooling Inventory ================================

Overview of scripts under `scripts/experimental/` with purpose and disposition.

| Path | Purpose | Disposition | Action | Target | Prerequisites |
|------|---------|-------------|--------|--------|---------------|
| examples/run_autopilot_demo.py | Demo autopilot (Q/OPS/SPY) chain | Keep (convert to package example) | Promote to examples module | Nov 2025 | CLI stable + doc snippet added |
| (removed) examples/run_full_smoke.py | Chained smoke run (demo→OPS→SPY→report) | Removed (CLI chain examples to replace) | N/A | 2025-10-23 | README examples pending add |
| (removed) examples/run_ops_tiny_sweep.py | Tiny crib weight sweep helper | Removed (Migrated) | Use examples.tiny_weight_sweep | 2025-10-24 | CLI sweep stable |
| (removed) examples/condensed_tuning_report.py | Summarize sweep CSV | Removed (to migrate into report API) | Implement report module | 2025-10-23 | `kryptos.k4.report` pending |
| (removed) examples/generate_top_candidates.py | Generate markdown candidate report | Removed (Replaced) | Consolidated into kryptos.k4.report | 2025-10-23 | write_top_candidates_markdown available |
| (removed) tools/run_hill_search.py | Random hill key diagnostic | Removed (package hill utilities) | N/A | 2025-10-23 | hill_search API present |
| (removed) tools/run_hill_canonical.py | Thin hill_constraints wrapper | Removed (use kryptos.k4 APIs) | N/A | 2025-10-23 | API consolidated |
| (removed) tools/run_pipeline_sample.py | Minimal pipeline wrapper | Removed (use k4-decrypt CLI) | N/A | 2025-10-23 | CLI decrypt available |
| (removed) tools/holdout_score.py | Holdout scoring helper | Removed (CLI subcommand) | N/A | 2025-10-23 | `tuning-holdout-score` implemented |
| (removed) tools/run_sweep_on_artifact_samples.py | Crib sweep on existing artifacts | Removed (weight sweep CLI supersedes) | N/A | 2025-10-23 | CLI sweep present |
| (removed) tools/clean_and_summarize_matches.py | Clean matches & summarize | Removed (artifacts pipeline) | N/A | 2025-10-23 | end_to_end_process available |
| (removed) tools/summarize_crib_hits.py | Count crib hits per run | Removed (artifacts pipeline) | N/A | 2025-10-23 | crib_hit_counts integrated |
| (removed) tools/aggregate_spy_phrases.py | Aggregate SPY tokens | Removed (Replaced) | Consolidated into kryptos.spy.aggregate_phrases | 2025-10-23 | spy namespace implemented |
| tools/extract_spy_cribs.py | Extract probable crib tokens | Audit | Security/determinism review then promote | Jan 2026 | review + tests |
| tools/collect_sanborn_sources.py | Fetch & summarize Sanborn sources | Keep (external fetch) | Keep | -- | None |
| tools/k3_double_rotation.py | K3 rotation demo | Keep (historical example) | Keep (tag historical) | -- | None |
| tools/remove_top_level_wrappers.py | Script cleanup helper | Keep (internal maintenance) | Keep | -- | None |

Promotion / Migration Notes:

- Reporting-focused tools (`condensed_tuning_report.py`, `generate_top_candidates.py`) consolidated
into `kryptos.k4.report` (see `write_condensed_report`, `write_top_candidates_markdown`).
- `run_ops_tiny_sweep.py` → removed; replaced by examples.tiny_weight_sweep + CLI sweep.
- `run_full_smoke.py` → deprecate; replace with docs snippet chaining CLI + tuning API.
- `run_hill_search.py` → remove (diagnostic logic should live in a dedicated test or debug module if
still needed).
- `holdout_score.py` → evaluate for promotion if integrated into test/CI flows.
- SPY related tools now partially consolidated: `aggregate_spy_phrases.py` replaced by
`kryptos.spy.aggregate_phrases`; extractor logic migrated to `kryptos.spy.extract` (future removal
of `scripts/dev/spy_extractor.py`). `extract_spy_cribs.py` remains under audit before promotion.

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

Metrics Snapshot (post spy namespace + artifact path consolidation 2025-10-23):

- Removed: 14 (includes spy_extractor, generate_top_candidates, condensed_tuning_report, hill
wrappers)
- Keep (stable or evaluation): 9
- Migrate planned: 5 (remaining demo/autopilot example promotions, tiny sweep example,
compare_crib_integration decision, ops tiny sweep)
- Audit: 2 (extract_spy_cribs.py, create_pr.py)
- Historical: 1

Backlog (ordered, refreshed):

1. Finalize demo migration: convert `run_k4_demo.py` into documented CLI example and remove legacy
script. 2. Validate `examples.tiny_weight_sweep` example outputs; ensure tests/CI use new path. 3.
Decide fate of `compare_crib_integration.py`: merge into summarize-run or delete. 4. Audit
`tools/extract_spy_cribs.py` (security/determinism); write focused tests; decide promote vs remove.
5. Audit `scripts/dev/create_pr.py` for secret leakage; relocate or remove. 6. Add CLI `tuning-
report` subcommand wrapping report module utilities (write_condensed_report,
write_top_candidates_markdown). 7. Performance profiling: positional letter deviation weight
calibration; add doc note & potential CLI flag.

## Next Immediate Actions

- Reference report module in core docs (DONE).
- Replace any lingering doc/script references to generate_top_candidates (DONE here; grep verify
optional).
- Plan spy namespace extraction (design sketch, then tests).

Updated: 2025-10-24T00:56Z (tiny weight sweep example added; legacy tiny sweep removed)
