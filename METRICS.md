# Metrics

## Core Metrics

| Metric              | Value   | Notes                                      |
| ------------------- | ------- | ------------------------------------------ |
| Code Coverage       | 62.64%  | Measured with pytest-cov (run on 2025-11-28; html report in htmlcov/) |
| Code Coverage est.  | ~60-70% | Extrapolated from test sampling (estimated) |
| Source Files        | 86      | Python modules in src/ (excl. tests)       |
| Test Files          | 126     | Test modules in tests/                     |
| Test Functions      | 534     | Total test items collected this run        |
| Test Cases (Total)  | 534     | All tests (passed + skipped)               |
| Test Cases (Fast)   | 524     | Tests executed (passed) in this run        |
| Test Cases (Slow)   | 10      | Tests skipped (module-level slow marks)    |
| Lines of Code       | ~50K    | Estimated from 86 files (avg ~580/file)    |
| Documentation Files | 40+     | Comprehensive docs in docs/ directory      |
| Subdirectories      | 33      | Well-organized module structure            |
| Total Package Size  | 712 KB  | Source code only (excl. data/artifacts)    |

## Performance Metrics

| Metric                      | Value         | Notes                                |
| --------------------------- | ------------- | ------------------------------------ |
| Fast Test Duration          | 26.35s        | Measured: 524 fast tests (pytest --durations=20) |
| Full Test Duration          | N/A (slow tests skipped) | Full Monte Carlo runs are gated to separate CI job |
| K4 Attack Throughput        | 2.5 atk/sec   | Sequential execution baseline        |
| SA Speedup vs Hill-Climbing | 30-45%        | Simulated annealing optimization     |
| Dictionary Discrimination   | 2.73×         | Improvement over baseline scoring    |
| Target Parallel Throughput  | 10-15 atk/sec | Goal with multiprocessing (4× speed) |

## Validation Success Rates

| Cipher                | Success Rate | Method                     | Notes                      |
| --------------------- | ------------ | -------------------------- | -------------------------- |
| K1 Vigenère           | 100%         | Frequency analysis         | 50/50 runs, deterministic  |
| K2 Vigenère           | 100%         | Frequency analysis         | 50/50 runs, deterministic  |
| K3 Transposition (p5) | 68%          | Simulated annealing        | 50 runs, probabilistic     |
| K3 Transposition (p6) | 83%          | Simulated annealing        | 30 runs, probabilistic     |
| K3 Transposition (p7) | 95%          | Simulated annealing        | 20 runs, probabilistic     |
| K4 (unsolved)         | TBD          | Multi-stage pipeline       | Research in progress       |

## Module Breakdown

| Category              | Files | Lines | Description                          |
| --------------------- | ----- | ----- | ------------------------------------ |
| Agents                | 8     | ~4K   | SPY, OPS, Q, LINGUIST intelligence   |
| Pipeline              | 4     | ~1.6K | Orchestration and validation         |
| Provenance            | 2     | ~836  | Attack logging and search tracking   |
| K4 Toolkit            | 29    | ~15K  | Cipher implementations and scoring   |
| Research              | 4     | ~2K   | Academic paper analysis              |
| Tests                 | 126   | ~25K  | Comprehensive test coverage          |

## Code Quality

| Metric                 | Value    | Notes                                    |
| ---------------------- | -------- | ---------------------------------------- |
| Linting Status         | Clean    | Pre-commit hooks enforced                |
| Test Pass Rate         | 100%     | 524 passed, 10 skipped (fast run, 2025-11-28) |
| Deprecated Code        | Minimal  | executor.py marked for removal           |
| TODO/FIXME Count       | Low      | No critical technical debt               |
| Module Independence    | High     | Clear boundaries, no shadow imports      |
| Documentation Coverage | Extensive| 40+ docs, 3,500+ lines academic writing |

## Health

| Metric           | Value      | Notes                                    |
| ---------------- | ---------- | ---------------------------------------- |
| Open Issues      | TBD        | GitHub issue tracking                    |
| PR Turnaround    | TBD        | Pull request review metrics              |
| Skipped Tests    | 10         | Module-level slow tests (marked skip)    |
| Health Score     | TBD        | Overseer compliance score                |
| Last Updated     | 2025-11-28 | Phase 6.2 validation run                 |
| Project Status   | Active     | Phase 6.2 in progress                    |
| K4 Readiness     | 5%        | 7.5/10 core capabilities working         |
