# Performance & Profiling Plan
Breadcrumb: Performance > Profiling > Plan

This document tracks performance enhancement tasks and profiling methodology.

## Goals

- Calibrate positional letter deviation weight (avoid overweighting structured distribution metric).
- Identify hotspots in multi-crib transposition permutation search and Hill 3x3 assembly.
- Normalize artifact metadata with timing + provenance hash.
- Introduce standardized stage timing collection (start/end timestamps, duration ms).

## Metrics To Collect

| Metric | Description | Collection Method |
|--------|-------------|-------------------|
| stage_duration_ms | Elapsed time per pipeline stage | timing wrapper decorator |
| candidates_per_second | Rate of candidate generation per stage | count/elapsed |
| cache_hit_ratio | LRU scoring cache hits vs misses | expose counters |
| rarity_weighted_crib_bonus | Differential bonus favoring rare-letter cribs (per candidate) | scoring.rarity_weighted_crib_bonus |
| positional_weight_impact | Delta in candidate rank shift when toggling positional deviation weight | comparison run pair |
| memory_peak_mb | Peak RSS during composite run | psutil / tracemalloc (optional) |

## Weight Calibration Procedure

1. Collect baseline scoring outputs for a fixed candidate set (N=500) with positional weight W0. 2.
Sweep candidate weights (e.g., 10, 20, 30, 40) and record Spearman rank correlation vs baseline
n-gram only score. 3. Choose smallest weight maintaining correlation >= 0.85 while improving false-
positive filtering (measured by manual artifact review or crib alignment precision). 4. Document
chosen weight and justification here and in CHANGELOG.

## Artifact Provenance

Add fields to run metadata JSON:


## Hotspot Profiling

Use Python `cProfile` or `pyinstrument` (optional dev dependency) on composite runs with small
limit. Focus on:

- transposition route enumeration
- hill key assembly loops
- scoring aggregation function

## Next Steps

1. Implement timing wrapper utility. 2. Add provenance hash computation helper
(`kryptos.paths.provenance_hash`). 3. Run initial positional weight sweep and record results
(`scripts/tuning/run_rarity_calibration.py`). 4. Add CLI flag `--profile` to emit profiling stats
JSON.

Updated: 2025-10-23T23:59Z
