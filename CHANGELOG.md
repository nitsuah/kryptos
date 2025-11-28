# Changelog

All notable changes to the KRYPTOS project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Overseer-compliant documentation (ROADMAP.md, TASKS.md, FEATURES.md, METRICS.md, CHANGELOG.md)

### Changed

- Documentation structure reorganized for better compliance tracking

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
- `docs/audits/SCRIPTS_CLEANUP_2025-01-27.md` - Script cleanup documentation
- `docs/audits/DOCS_AUDIT_2025-01-27.md` - Documentation audit report

### Changed

- Test suite optimized: 583 fast tests (1-2 min) + 24 slow tests (Monte Carlo)
- Updated PHASE_6_ROADMAP.md with measured success rates
- Marked 4 deprecated executor.py test files as skipped (7 tests)
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

- [PHASE_6_ROADMAP.md](./docs/PHASE_6_ROADMAP.md) - Current phase status and objectives
- [TODO_PHASE_6.md](./docs/TODO_PHASE_6.md) - Operational task breakdown
- [MAINTENANCE_GUIDE.md](./docs/MAINTENANCE_GUIDE.md) - Development guidelines
