Repository Reorganization & Wrapper Policy =========================================== Breadcrumb:
Architecture > Reorg > Wrapper Policy

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

- `spy_eval` logic migrated into `kryptos/k4/tuning/spy_eval.py`.
- SPY extractor & phrase aggregation migrated into `kryptos/spy/` (legacy script removed).
- Example/demo scripts progressively relocating into `examples/` and CLI usage (`kryptos
k4-decrypt`).
- Report generation consolidated in `kryptos.k4.report` (markdown + condensed CSV).
- K4 run artifacts standardized under `artifacts/k4_runs/`.

## Deprecated (Pending Removal)

| Script | Reason | Replacement | Removal Target |
|--------|--------|-------------|----------------|
| (removed) scripts/experimental/examples/run_ops_tiny_sweep.py | Legacy tiny sweep wrapper | `kryptos.examples.tiny_weight_sweep` / CLI sweep | Removed (2025-10-24) |
| scripts/experimental/examples/run_full_smoke.py | Chained demo wrapper | CLI chain example | Removed (2025-10-23) |
| scripts/demo/run_k4_demo.py | Demo runner (legacy path) | `kryptos k4-decrypt --report` | Dec 2025 (migrate to examples) |
| scripts/tuning/compare_crib_integration.py | Ad-hoc comparison | summarize-run/report subcommands | Jan 2026 (decision) |
| scripts/tuning/pick_best_weight.py | Superseded selection logic | tuning-pick-best CLI | Removed (2025-10-23) |
| scripts/tuning/spy_eval.py | Legacy evaluation harness | `kryptos spy-eval` (package API) | Removed (2025-10-23) |

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

1. Remove legacy demo runner (`run_k4_demo.py`) after CLI example snippet published. 2. Decide fate
of `compare_crib_integration.py` (merge or delete) and update docs. 3. Validate
`examples.tiny_weight_sweep` + CLI sweep outputs (legacy tiny sweep script removed). 4. Add `tuning-
report` CLI subcommand wrapping report utilities. 5. Calibrate positional letter deviation weight
(document evaluation results). 6. Centralize logging setup (`kryptos.logging` helper) and remove
stray print statements. 7. Add artifact provenance hash & compression option.

Status Snapshot (2025-10-23T23:52Z): Spy & tuning namespaces consolidated, report module integrated,
artifact paths standardized, CLI subcommands live for core tuning & spy operations.

Updated: 2025-10-24T00:55Z (tiny weight sweep example added; legacy tiny sweep script removed)
