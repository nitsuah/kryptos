--- title: Deprecations & Removal Timeline version: 2025-10-24 Breadcrumb: Architecture >
Deprecations > Timeline ---

# Deprecations & Removal Timeline

This document records pending removals (scripts, wrappers, legacy APIs) with their replacement,
status, and target version/date. Items move to ARCHIVED_SCRIPTS.md after physical deletion.

## Policy

- Deprecate: emit `DeprecationWarning` for one minor release; provide clear replacement.
- Remove: physically delete once no tests/docs reference the item.
- Audit: requires review before deciding promote vs remove.
- Legacy API alias: keep for one minor version with warning; remove after stable release adoption.

## Active Deprecations

| Item | Type | Replacement | Introduced | Target Removal | Notes |
|------|------|-------------|------------|----------------|-------|
| scripts/demo/run_k4_demo.py | Script wrapper | `python -m kryptos.examples.k4_demo` / CLI `kryptos k4-decrypt` | 2025-10-23 | 2025-12-01 | Grace window for downstream users |
| scripts/demo/run_autopilot_demo.py | Script wrapper | `python -m kryptos.examples.autopilot_demo` / CLI `kryptos autopilot` | 2025-10-23 | 2025-12-01 | Remove after CI module invocation added |
| (removed) run_ops_tiny_sweep.py | Script wrapper | `kryptos.examples.tiny_weight_sweep` / CLI sweep | 2025-10-24 | REMOVED | Migrated example added |
| compare_crib_integration.py | Tuning script | Merge into reporting summary or remove | 2025-10-23 | 2026-01-15 | Needs relevance assessment |
| create_pr.py | Dev script | GitHub Actions workflow / CLI helper | 2025-10-23 | 2026-02-01 | Audit secrets usage |
| legacy demo wrappers (k4/autopilot) | Script set | Examples package / CLI | 2025-10-23 | 2025-12-01 | Track via this doc |
| spy_eval legacy alias | CLI subcommand alias | `kryptos spy-eval` (canonical) | 2025-10-23 | 2026-02-01 | Ensure no external direct imports |

## Legacy API Aliases

| Alias | Replacement | Warning Added | Removal Target |
|-------|-------------|---------------|----------------|
| `kryptos.k4.decrypt_best` (tentative alias) | `kryptos.k4.pipeline.decrypt_best` (example) | PENDING | TBD |
| `kryptos.report.write_top_candidates_markdown` (old path) | `kryptos.k4.report.write_top_candidates_markdown` | 2025-10-24 | 2025-11-30 |

## Completed Removals (Recent)

| Item | Removed | Replacement |
|------|---------|------------|
| spy_eval.py (tuning script) | 2025-10-23 | Package + CLI subcommand |
| autopilot_daemon.py | 2025-10-23 | Autopilot loop in module + CLI |
| ask_triumverate.py | 2025-10-23 | Autopilot personas API |
| ask_best_next.py | 2025-10-23 | Autopilot recommend_next_action |
| cracker_daemon.py | 2025-10-23 | Integrated decision logic |
| manager_daemon.py | 2025-10-23 | Unified autopilot + tuning CLI |
| run_plan.py | 2025-10-23 | `kryptos autopilot --plan` |
| spy_extractor.py | 2025-10-23 | `kryptos.spy.extractor` module + CLI |
| run_ops_tiny_sweep.py | 2025-10-24 | examples.tiny_weight_sweep |

## Upcoming Actions

- Add CI invocation for examples.autopilot_demo then remove demo wrapper scripts.
- Decide fate of compare_crib_integration.py (merge or delete) and update this doc.
- Add structured warning in legacy demo wrappers announcing removal date.
- Introduce API reference doc to reduce reliance on legacy entrypoints.

## Checklist Before Removal

- [ ] Replacement documented in README_CORE.md / INDEX.md
- [ ] No test imports referencing deprecated path
- [ ] DeprecationWarning emitted for at least one minor version (if alias)
- [ ] ARCHIVED_SCRIPTS.md updated
- [ ] CI workflows updated (no invocation of deprecated script)

Last updated: 2025-10-24T01:02Z
