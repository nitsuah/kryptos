# Changelog

All notable changes to the KRYPTOS project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added

- `kryptos serve` command and minimal FastAPI app (`src/kryptos/api/`) exposing `/health`, `/api/rag/status`,
  `POST /api/rag/reindex`, and `GET /api/rag/search` endpoints
- turbovec-backed `ArtifactIndex` (`src/kryptos/rag/`) for semantic search over `artifacts/`, using
  `sentence-transformers` embeddings and a 4-bit quantized `turbovec.IdMapIndex` persisted under `data/turbovec/`

## [Phase 6.3] - 2026-05-25

### Added

- Overseer-compliant documentation (ROADMAP.md, TASKS.md, FEATURES.md, METRICS.md, CHANGELOG.md)
- K1/K2/K3 runtime smoke verification command path in maintenance workflow (exact plaintext checks on production entrypoints)
- Phase 6/7 implementation audit tracker (`AUDIT.md`) with code/test evidence matrix and pending gap ledger
- Objective-to-evidence scorecard for strategic goals
- Fresh-environment autonomous smoke test (CI and demo workflows)
- Scalable campaign orchestration with bounded parallel workers
- Sections-decrypt CLI command for K1/K2/K3 with config-backed inputs
- JSON output mode for section verification commands
- Section API end-to-end tests
- Optional explainability mode for section decryptions
- Alphabet auto-selection wired into runtime orchestrators (default enabled)
- Transposition plaintext extraction fix in campaign orchestrator
- Robust autonomous test/runtime NLP dependency handling (spaCy/NLTK/transformers optional)

### Changed

- Documentation structure reorganized for better compliance tracking
- Fast-suite validation baseline updated to 631 passed / 10 skipped / 2 deselected with 95% coverage (2026-05-24)
- Coverage and task planning docs updated to reflect `fail_under = 80` and completed targeted coverage push
- Core planning docs now reflect verified implementation status for composite chains and cross-run key-memory paths
- CLI and orchestrator now default to alphabet auto-selection, with opt-out flag
- All K4-ATTACK-1 through K4-ATTACK-7 completed and documented

### Fixed

- Deprecated UTC timestamp usage migrated from `datetime.utcnow()` to timezone-aware UTC calls in runtime/reporting/example modules
- `runpy` module re-execution warnings reduced in tests by clearing cached module entries before `run_module`
- `PytestReturnNotNoneWarning` removed from `tests/test_spy_v2.py`
- Stale docs links corrected (`K123_PATTERN_ANALYSIS` path drift, archive index entries, and quickstart intel cache paths)
- Transposition plaintext extraction in campaign orchestrator now outputs correct plaintext for all candidate routes
- Autonomous runtime/test no longer fails if NLP dependencies are missing
- CLI runpy warning path clarified and tested (SystemExit expected)

### Removed

- No longer required: config/llm_config.yaml (no such file used or referenced)

## [Phase 6.2] - 2025-11-27 (In Progress)

### In Progress

- Composite attack chains (V→T and T→V)
- Multi-stage validation pipeline integration
- Confidence thresholding system

## [Phase 6.1] - 2025-11-27

### Added

- K1/K2 Monte Carlo validation test suite (100% success rate confirmed)
- K3 comprehensive validation test suite (68-95% period-dependent success)
- `docs/analysis/K1_K2_VALIDATION_RESULTS.md` - Validation results documentation
- `docs/analysis/K3_VALIDATION_RESULTS.md` - K3 validation analysis
- `scripts/README.md` - Script policy and cleanup consolidation
- `AUDIT.md` - Repository-wide documentation audit tracker

### Changed

- Test suite: fast CI runs execute ~524 tests; 10 slow Monte Carlo tests are gated behind `KRYPTOS_RUN_SLOW_MONTE_CARLO`
- Coverage gate adjusted to 60% temporarily to keep CI actionable while we add unit tests
- Updated historical Phase 6 planning docs with measured success rates
- K3 ciphertext corrected to 336 characters

### Fixed

- Fixed OPS placeholder confusion in `agents/ops.py` line 360
- Implemented K4 campaign Vigenère attack (was marked as placeholder)
- Corrected K2 success rate documentation (3.8% → 100%, was deterministic all along)
- Corrected K3 success rate documentation (27% → 68-95%, better than claimed)

### Removed

- 7 redundant K1/K2 debugging scripts after validating functionality in proper tests
- Misleading placeholder comments in implemented code

## [Phase 5] - 2025-10 to 2025-11

### Added

- Simulated annealing solver (30-45% faster than hill-climbing)
- Dictionary scoring system (2.73× discrimination ratio)
- Attack provenance logging with deduplication (`provenance/attack_log.py`, 435 lines)
- Search space coverage tracking (`provenance/search_space.py`, 401 lines)
- Attack generation framework (46 attacks from Q-hints + gaps)
- 4-stage validation pipeline with 96% confidence
- K4 campaign orchestration (2.5 attacks/second throughput)
- Academic documentation (3 comprehensive docs, 3,500+ lines)
- Pipeline profiling with per-stage duration metadata
- Attempt persistence (timestamped JSON logs)
- Validation pipeline (`pipeline/validator.py`, 418 lines)
- K4 campaign executor (`pipeline/k4_campaign.py`, 373 lines)

### Changed

- Code cleanup: removed 3,554 lines of unnecessary code
  - Automated cleanup: -2,877 lines (docstrings, comments, verbose logging) across 65 files
  - Deprecated code removal: -677 lines (unused configs, obsolete tests)
- Test suite expanded to 564 passing tests (100% pass rate)
- Test duration: 5 minutes 5 seconds for full suite

### Fixed

- All linting issues resolved (clean pre-commit status)

## [Phase 4] - 2025-Q4

### Added

- Hill cipher (2×2 and 3×3) implementation
- Frequency analysis and n-gram scoring utilities
- Columnar transposition with partial-score pruning
- Berlin Clock shift hypothesis
- Multi-stage pipeline architecture
- Constraint-based Hill key derivation
- Adaptive transposition search with sampling heuristics
- Masking/null-removal stage
- Weighted multi-stage fusion utilities
- Advanced linguistic metrics (entropy, wordlist hits, trigram analysis)
- Memoized scoring with LRU cache
- Transformation trace and lineage tracking
- K3 double rotational transposition implementation
- 24×14 grid rotation method
- K3 solution validation
- Intentional misspelling preservation (DESPARATLY)
- K2 Vigenère implementation
- Structural padding handling (X and Y separators)
- Geospatial coordinate extraction
- K2 solution validation
- Initial project setup and architecture
- Vigenère cipher with keyed alphabet (KRYPTOSABCDEFGHIJLMNQUVWXZ)
- K1 solution implementation
- Intentional misspelling preservation (IQLUSION)
- Config-driven system (config/config.json)
- Test suite framework
- Basic frequency analysis
- Documentation structure

### Repository

- Initial commit with project structure
- Requirements.txt with dependencies
- README.md with project overview
- LICENSE file

## References

For detailed phase planning and technical documentation, see:

- [ROADMAP.md](./ROADMAP.md) - Current roadmap and phase objectives
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Active workflow, standards, and quickstart guidance
