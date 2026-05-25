# Provenance And Search-Space Tracking

Last Updated: 2026-05-24

## Purpose

Kryptos tracks both:
- attempt provenance (what was tried, with which parameters, and with what result)
- search-space coverage (which regions/keys were explored)

This enables reproducibility, deduplication, and strategic pruning.

## Main Components

### Attack Logging

Implementation:
- `src/kryptos/provenance/attack_log.py`

Key behavior:
- stores normalized attack records
- supports duplicate detection
- supports downstream analysis/reporting workflows

### Search Space Tracker

Implementation:
- `src/kryptos/provenance/search_space.py`

Key behavior:
- region registration + coverage metrics
- recommendation helpers
- heatmap export data
- cross-run tried-key persistence via `tried_keys.jsonl`

## Storage Locations

Default locations are rooted under `artifacts/` in the current codebase runtime paths.

Common directories:
- `artifacts/attack_logs/`
- `artifacts/search_space/`
- `artifacts/intel_cache/`
- `artifacts/ops_strategy/`

## Cross-Run Memory Status

Implemented baseline:
- `recover_key_by_frequency(..., skip_tried=True, tracker=...)` can skip previously tried keys.

Remaining strategic work:
- broader heuristic/adaptive usage across all orchestrators and solver families remains on roadmap.

See:
- `ROADMAP.md`
- `TASKS.md`
- `AUDIT.md`

## Validation Pointers

Relevant tests:
- `tests/test_attack_generator.py`
- `tests/test_attack_provenance.py`
- `tests/test_cross_run_memory.py`

For current command-level validation evidence, see root `AUDIT.md`.
