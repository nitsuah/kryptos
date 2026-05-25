
# Metrics

**Last Validated:** 2026-05-24 (fast suite + K1/K2/K3 verification)

## Core Metrics

| Metric              | Value   | Notes                                      |
| ------------------- | ------- | ------------------------------------------ |
| Code Coverage       | 95%     | Measured with pytest-cov on fast suite (`pytest tests/ -m "not slow" --cov=src --cov-report=term`) |
| Source Files        | 86      | Python modules in src/ (excl. tests)       |
| Test Files          | 142     | `test_*.py` modules in tests/              |
| Test Functions      | 633     | Total collected items in current fast-suite run context |
| Test Cases (Total)  | 633     | Collected items (incl. deselected/skipped) |
| Test Cases (Fast)   | 631     | Executed tests in current fast-suite run   |
| Test Cases (Slow)   | 10      | Tests skipped (module-level slow marks)    |
| Lines of Code       | ~50K    | Estimated from 86 files (avg ~580/file)    |
| Documentation Files | 40+     | Comprehensive docs in docs/ directory      |
| Subdirectories      | 33      | Well-organized module structure            |
| Total Package Size  | 712 KB  | Source code only (excl. data/artifacts)    |

## Performance Metrics

| Metric                      | Value         | Notes                                |
| --------------------------- | ------------- | ------------------------------------ |
| Fast Test Duration          | 48.51s        | Measured: 631 fast tests on 2026-05-24 |
| Full Test Duration          | N/A (slow suites are opt-in) | Run with `KRYPTOS_RUN_SLOW_MONTE_CARLO=1` when you want the Monte Carlo path |
| K4 Attack Throughput        | 2.5 atk/sec   | Sequential execution baseline        |
| SA Speedup vs Hill-Climbing | 30-45%        | Simulated annealing optimization     |
| Dictionary Discrimination   | 2.73×         | Improvement over baseline scoring    |
| Target Parallel Throughput  | 10-15 atk/sec | Goal with multiprocessing (4× speed) |

## Validation Success Rates

| Cipher                | Success Rate | Method                     | Notes                      |
| --------------------- | ------------ | -------------------------- | -------------------------- |
| K1 Vigenère           | 100%         | Frequency analysis         | 50/50 runs, deterministic  |
| K2 Vigenère           | 100%         | Frequency analysis         | 50/50 runs, deterministic  |
| K3 Transposition (p5) | 62-68%       | Simulated annealing        | 50 runs, probabilistic and seed-sensitive |
| K3 Transposition (p6) | 83%          | Simulated annealing        | 30 runs, probabilistic     |
| K3 Transposition (p7) | 60-95%       | Simulated annealing        | 20 runs, probabilistic and parameter/seed-sensitive |
| K4 (unsolved)         | TBD          | Multi-stage pipeline       | Research in progress       |

## Module Breakdown

| Category              | Files | Lines | Description                          |
| --------------------- | ----- | ----- | ------------------------------------ |
| Agents                | 8     | ~4K   | SPY, OPS, Q, LINGUIST intelligence   |
| Pipeline              | 4     | ~1.6K | Orchestration and validation         |
| Provenance            | 2     | ~836  | Attack logging and search tracking   |
| K4 Toolkit            | 29    | ~15K  | Cipher implementations and scoring   |
| Research              | 4     | ~2K   | Academic paper analysis              |
| Tests                 | 142   | ~25K+ | Comprehensive test coverage          |

## Code Quality

| Metric                 | Value    | Notes                                    |
| ---------------------- | -------- | ---------------------------------------- |
| Linting Status         | Clean    | Pre-commit hooks enforced                |
| Test Pass Rate         | 100%     | 631 passed, 10 skipped, 2 deselected (fast run, 2026-05-24) |
| Deprecated Code        | Minimal  | executor.py marked for removal           |
| TODO/FIXME Count       | Low      | No critical technical debt               |
| Module Independence    | High     | Clear boundaries, no shadow imports      |
| Documentation Coverage | Extensive| 40+ docs, 3,500+ lines academic writing |

## Health

| Metric           | Value      | Notes                                    |
| ---------------- | ---------- | ---------------------------------------- |
| Open Issues      | 0          | GitHub issue tracking                     |
| PR Turnaround    | <1 day     | Typical PR review time                   |
| Skipped Tests    | 10         | Module-level slow tests (marked skip)    |
| Health Score     | 95/100     | Overseer compliance score                 |
| Last Updated     | 2026-05-24 | Coverage + K1/K2/K3 validation refresh   |
| Project Status   | Active     | Phase 6.2 in progress                    |
| K4 Readiness     | 5%         | 7.5/10 core capabilities working         |
