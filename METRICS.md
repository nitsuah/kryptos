# Metrics

## Core Metrics

| Metric              | Value   | Notes                                      |
| ------------------- | ------- | ------------------------------------------ |
| Code Coverage       | TBD     | Not yet measured - run not-slow            |
| Source Files        | 86      | Python modules in src/ (excl. tests)       |
| Test Files          | 126     | Test modules in tests/                     |
| Test Functions      | 688     | Total test functions defined               |
| Test Cases          | 607     | Tests passing (583 fast / 24 slow)         |
| Lines of Code       | ~50K    | Estimated from 86 files (avg ~580/file)    |
| Documentation Files | 40+     | Comprehensive docs in docs/ directory      |
| Subdirectories      | 33      | Well-organized module structure            |
| Total Package Size  | 712 KB  | Source code only (excl. data/artifacts)    |

## Performance Metrics

| Metric                      | Value         | Notes                                |
| --------------------------- | ------------- | ------------------------------------ |
| Fast Test Duration          | ~1-2 min      | 583 tests (pytest -m "not slow")     |
| Full Test Duration          | ~5 min        | 607 tests including Monte Carlo      |
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
| Test Pass Rate         | 100%     | 607/607 tests passing                    |
| Deprecated Code        | Minimal  | executor.py marked for removal           |
| TODO/FIXME Count       | Low      | No critical technical debt               |
| Module Independence    | High     | Clear boundaries, no shadow imports      |
| Documentation Coverage | Extensive| 40+ docs, 3,500+ lines academic writing |

## Health

| Metric           | Value      | Notes                                    |
| ---------------- | ---------- | ---------------------------------------- |
| Open Issues      | TBD        | GitHub issue tracking                    |
| PR Turnaround    | TBD        | Pull request review metrics              |
| Skipped Tests    | 7          | Deprecated executor.py tests             |
| Health Score     | TBD        | Overseer compliance score                |
| Last Updated     | 2025-01-27 | Phase 6.1 validation completion          |
| Project Status   | Active     | Phase 6.2 in progress                    |
| K4 Readiness     | 75%        | 7.5/10 core capabilities working         |
