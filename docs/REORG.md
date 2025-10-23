Repository Reorganization & Wrapper Policy ===========================================

Purpose: document decisions for separating reusable package logic from ad-hoc / wrapper scripts and
define a clear deprecation & promotion lifecycle.

## Policy

- Reusable logic (algorithms, scoring, pipeline assembly) MUST live under the `kryptos/` package
	(single canonical namespace).
- Scripts under `scripts/` are wrappers or operational entrypoints (CLI, daemon, tuning harness).
- Experimental scripts live under `scripts/experimental/` and are not considered stable; they may be
promoted or removed.
- No new persistent scripts unless they directly enable an end-to-end hypothesis test or user demo.

## Moved / Ported

- `spy_eval` logic migrated into `kryptos/tuning/spy_eval.py`.
- Example/demo scripts relocated into `scripts/experimental/examples/`. All temporary shims removed;
tests updated to point to canonical paths.

## Deprecated (Pending Removal)

| Script | Reason | Replacement | Removal Target |
|--------|--------|-------------|----------------|
| (removed) scripts/experimental/tools/run_hill_search.py | Ad-hoc key gen & scoring | k4.hill_search.score_decryptions | Removed 2025-10-23 |
| (removed) scripts/experimental/tools/run_hill_canonical.py | Thin wrapper | k4.hill_constraints.decrypt_and_score | Removed (API consolidated) |
| (removed) scripts/experimental/tools/run_pipeline_sample.py | Pipeline sample wrapper | Direct package pipeline usage | Removed (CLI + direct API) |
| scripts/tuning/spy_eval.py | Legacy evaluation harness | kryptos.tuning.spy_eval | Remove after CLI spy eval |
| (removed) scripts/experimental/examples/run_full_smoke.py | Chained demo wrapper | CLI examples & individual commands | Removed 2025-10-23 |

## Promotion Criteria

Promote an experimental script ONLY if:

- It implements novel reusable logic not present in `src/`.
- At least one test or documented workflow depends on it AND refactoring into package improves
reuse.

## Deletion Criteria

Delete a deprecated script once:

- No docs reference it OR docs updated with package example.
- No tests import or execute it.

## Next Cleanup Steps

1. Implement Hill hypothesis adapter using existing package functions. 2. Remove deprecated hill
wrappers once tests reference adapter. 3. Convert smoke/demo scripts to pure package examples in
docs or consolidate into CLI. 4. Re-run full test suite & update this file with completed deletions.
5. Introduce CLI entrypoints to replace remaining example wrappers (`decrypt`, `autopilot`, `tune`).
(In progress: base CLI present; tuning/spy pending)

Status Snapshot (2025-10-23): Unified package complete, tuning & artifacts modules promoted, docs
archival ongoing, CLI base shipped.

Updated: 2025-10-23
