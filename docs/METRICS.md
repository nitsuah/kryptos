

# Metrics

Breadcrumb: [Docs](INDEX.md) > Metrics

**Note:** Data and artifacts are planned to migrate to a database as part of the 2027 roadmap. Current metrics reflect the file-based structure.

**Last Validated:** 2026-08-22 (docs audit pass); file counts re-derived by static analysis. Test-function count reflects all `def test_*` functions; pytest-collected count (after marks/deselection) may differ.

## Core Metrics

| Metric              | Value   | Notes                                      |
| ------------------- | ------- | ------------------------------------------ |
| Code Coverage       | 89.35%  | Measured with pytest-cov (Docker, 2026-08-22): `pytest tests/ --cov=kryptos --cov-report=term`; 1192 collected passed, 28 skipped |
| Source Files        | 112     | Python modules in src/ excl. `__init__.py` (131 total incl. `__init__.py`) |
| Test Files          | 184     | `test_*.py` modules in tests/              |
| Test Functions      | 1271    | `def test_*` functions across all test files (static count 2026-08-22) |
| Test Cases (Fast)   | 1192    | 0 failures, 28 skipped (Docker run 2026-08-22; slow Monte Carlo tests excluded) |
| Test Cases (Slow)   | ~22     | `@pytest.mark.slow`-marked test locations (opt-in Monte Carlo) |
| Lines of Code       | ~65K    | Estimated from 112 non-init source files   |
| Documentation Files | 40+     | Comprehensive docs in docs/ directory      |
| Subdirectories      | 33      | Well-organized module structure            |
| Total Package Size  | 712 KB  | Source code only (excl. data/artifacts)    |

## Performance Metrics

| Metric                      | Value         | Notes                                |
| --------------------------- | ------------- | ------------------------------------ |
| Fast Test Duration          | 48.51s        | Measured: 631 fast tests on 2026-05-25 |
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
| Tests                 | 184   | ~25K+ | Comprehensive test coverage          |

## Code Quality

| Metric                 | Value    | Notes                                    |
| ---------------------- | -------- | ---------------------------------------- |
| Linting Status         | Clean    | Pre-commit hooks enforced                |
| Test Pass Rate         | 100%     | 829 passed, 0 failures (AUDIT_2026-06-01 baseline; 1271 functions as of 2026-08-22 static count) |
| Deprecated Code        | Minimal  | executor.py marked for removal (legacy, retiring after migration confirmation) |
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
| Last Updated     | 2026-08-22 | Docs audit: file counts updated to current codebase state |
| Project Status   | Active     | All Q1-2027 phases shipped; frontier K4 attack planning in progress |
| K4 Readiness     | 8.5/10     | Full pipeline, dashboard, RAG, and 14 completed attack vectors; 3-layer composites next |
