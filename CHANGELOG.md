# CHANGELOG

## [Unreleased]

### Added

* Composite pipeline stage timing (`stage_durations_ms`) instrumentation.
* Provenance hash propagation (`provenance_hash`) into run profile and `DecryptResult.metadata`.
* Rarity-weighted crib bonus (`scoring.rarity_weighted_crib_bonus`) and baseline stats integration.
* Consolidated tuning CLI (`scripts/tuning.py`) - single tool replacing 5 separate scripts.
* Consolidated markdown linting (`scripts/lint/mdlint.py`) - check + reflow in one tool.
* Agent triumvirate fully implemented: SPY (pattern recognition), OPS (parallel orchestration), Q (statistical
validation).

### Changed

* Migrated legacy `src/k4/` package into unified `kryptos/k4/` namespace; updated imports, tests,
docs.
* Normalized artifact metadata structure (timings + provenance).
* Consolidated configuration: flake8 rules moved to `pyproject.toml` (single source of truth).
* Updated pre-commit hooks to use consolidated linting tools.

### Removed / Deprecated

* Fully removed deprecated `scripts/tuning/spy_eval.py` (replaced by package API + CLI subcommand).
* Removed deprecated experimental scripts: `run_full_smoke.py`, `run_hill_search.py`,
`clean_and_summarize_matches.py`, `summarize_crib_hits.py`, `run_pipeline_sample.py` (functionality migrated to package
APIs & CLI subcommands).
* Removed legacy executor (`PipelineExecutor`) and migrated tests to `Pipeline` & composite helpers.
* Consolidated scripts: 5 tuning scripts → `tuning.py`, 5 lint scripts → `mdlint.py`, `.flake8` → `pyproject.toml`.
* Massive documentation cleanup: 20→6 core docs (70% reduction), archive cleanup (11→2 files).

### Pending

* Route scoring refinement, multiprocessing enhancements, advanced Hill assemblies.
* Rarity weighting calibration harness & positional deviation weight tuning.

## [2025-10-20] Adaptive & Route Expansion

* Added adaptive fusion weighting (wordlist_hit_rate + trigram_entropy heuristics).
* Added route transposition stage (spiral, boustrophedon, diagonal traversals).
* Implemented multi-crib positional transposition stage.
* Added 3x3 Hill key pruning (partial score).
* Added attempt logging & persistence for Hill, Clock, Transposition.
* Added advanced linguistic metrics (wordlist hit rate, trigram entropy, bigram gap variance).
* Added normalization safeguards (equal-score midpoint) & adaptive diagnostics.
* Corrected crib indices (EAST 22, NORTHEAST 25, BERLIN 64, CLOCK 69).

## [Earlier] Pre-adaptive foundation

* Core multi-stage pipeline (Hill, transposition, adaptive transposition, masking, Berlin Clock).
* Weighted multi-stage fusion & candidate artifacts.
