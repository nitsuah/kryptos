# CHANGELOG

## [Unreleased]

- Added `kryptos.k4.tuning` module (weight sweeps, tiny param sweeps, best-weight selection).
- Added `kryptos.k4.tuning.artifacts` (match file cleaning, run summarization, crib hit counts, end-
to-end process helper).
- CLI foundation: sections listing, k4 decrypt, attempts (tuning subcommands planned).
- Documentation reorganization & archival of dated plan docs.
- Pending: route scoring refinement, multiprocessing, advanced Hill assemblies.

## [2025-10-23] Spy Namespace & Positional Scoring

- Introduced `kryptos.spy` namespace (extractor + phrase aggregation) replacing legacy
	`scripts/dev/spy_extractor.py` and `aggregate_spy_phrases.py`.
- Added positional letter deviation metric integrated into `combined_plaintext_score_extended` to
	penalize over-structured transposition artifacts and reward balanced per-position distributions.
- Consolidated tuning & report logic; removed deprecated markdown and condensed report generator
scripts.
- Reorganized K4 pipeline artifact output under `artifacts/k4_runs/run_<timestamp>/`.
- Updated documentation (10KFT, AUTOPILOT, EXPERIMENTAL_TOOLING) to reflect new paths & namespaces.
- Archived historical `k3_double_rotation.py` to `docs/archive/` with provenance note.
- Fixed flake8/Ruff issues (F811 redefinition, B023 loop variable closure) and markdown lint
warnings.
- Added CLI subcommands references for spy/tuning/reporting; groundwork for `kryptos spy extract` &
`spy eval`.

## [2025-10-20] Adaptive & Route Expansion

- Added adaptive fusion weighting (wordlist_hit_rate + trigram_entropy heuristics).
- Added route transposition stage (spiral, boustrophedon, diagonal traversals).
- Implemented multi-crib positional transposition stage.
- Added 3x3 Hill key pruning (partial score).
- Added attempt logging & persistence for Hill, Clock, Transposition.
- Added advanced linguistic metrics (wordlist hit rate, trigram entropy, bigram gap variance).
- Added normalization safeguards (equal-score midpoint) & adaptive diagnostics.
- Corrected crib indices (EAST 22, NORTHEAST 25, BERLIN 64, CLOCK 69).

## [Earlier] Pre-adaptive foundation

- Core multi-stage pipeline (Hill, transposition, adaptive transposition, masking, Berlin Clock).
- Weighted multi-stage fusion & candidate artifacts.
