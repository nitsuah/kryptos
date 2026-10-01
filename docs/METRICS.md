

# Metrics

> 🧭 [kryptos](../README.md) · [Index](./INDEX.md) · [Features](./FEATURES.md) · [Roadmap](./ROADMAP.md) · [Tasks](./TASKS.md) · [Changelog](./CHANGELOG.md) · **Metrics** <!-- nav -->

**Note:** Data and artifacts are planned to migrate to a database as part of the 2027 roadmap. Current metrics reflect the file-based structure.

**Last Validated:** 2026-09-30 (fast suite re-run locally, Python 3.11; file and line counts re-derived). Coverage was last measured 2026-09-28. Test-function count reflects all `def test_*` functions; the pytest-collected count is higher because parametrized tests expand.

## Core Metrics

| Metric              | Value   | Notes                                      |
| ------------------- | ------- | ------------------------------------------ |
| Code Coverage       | 89%     | 2026-09-28 local run, `pytest -m "not slow" --cov=kryptos`. Previous reading 89.27% (Docker, 2026-09-16, 13,216 statements, 1,418 missed). |
| Source Files        | 143     | Python modules in `src/kryptos` excluding `__init__.py` (162 including), 2026-09-30. Up from 136 on 2026-09-27 with `crib_constraints`, `structural_checks`, `frontier_checks`, `english_model`, `hypothesis_ledger`, `run_store` and the API modules. |
| Test Files          | 218     | `test_*.py` modules under `tests/`, 2026-09-30 |
| Test Functions      | 1653    | Static count of `def test_*`, 2026-09-30 (1552 on 2026-09-27) |
| Test Cases (Fast)   | 1773 passed | 2026-09-30: `pytest -m "not slow"`, 33 skipped, 0 failures, 243 s; RAG-index tests deselected locally because they need `turbovec`. |
| Test Cases (Slow)   | 31      | `@pytest.mark.slow` markers in `tests/` (static count, 2026-09-30); includes the reconstruction suite, dictionary Quagmires and the Hill 5×5 planted key |
| Lines of Code       | ~58K    | `wc -l` over all `.py`, 2026-09-30: src 34.7K + tests 23.7K |
| Documentation Files | 40      | Committed Markdown files (`git ls-files '*.md'`), 2026-09-30 |
| Subdirectories      | 21      | `find src -type d` excluding `__pycache__`, 2026-09-30. The earlier figure of 40 counted `__pycache__` directories. |
| Total Package Size  | 712 KB  | Source code only (excl. data/artifacts) — not re-measured this cycle, TBD re-verify |

## Performance Metrics

| Metric                      | Value         | Notes                                |
| --------------------------- | ------------- | ------------------------------------ |
| Fast Test Duration          | 243 s (4:03)  | Full `-m 'not slow'` suite, local, 2026-09-30 (1773 passed + 33 skipped). 261 s in Docker on 2026-09-16. |
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
| K4 Toolkit            | 84    | ~20K  | Cipher implementations, constraint suites, scoring (`src/kryptos/k4/*.py`, 2026-09-30) |
| Research              | 4     | ~2K   | Academic paper analysis              |
| Tests                 | 218   | ~24K  | Smoke / functional / e2e tiers (2026-09-30) |

## Code Quality

| Metric                 | Value    | Notes                                    |
| ---------------------- | -------- | ---------------------------------------- |
| Linting Status         | Clean    | Pre-commit hooks enforced                |
| Test Pass Rate         | 100%     | 1773 passed, 0 failures (local fast suite, 2026-09-30) |
| Deprecated Code        | Minimal  | `executor.py` was listed here for removal; it no longer exists (checked 2026-09-30). `kryptos.deprecation` holds the remaining warning helpers. |
| TODO/FIXME Count       | Low      | No critical technical debt               |
| Module Independence    | High     | Clear boundaries, no shadow imports      |
| Documentation Coverage | Extensive| 40 Markdown docs; every doc outside `archive/` carries the breadcrumb nav (`test_docs_breadcrumbs.py`) |

## Health

| Metric           | Value      | Notes                                    |
| ---------------- | ---------- | ---------------------------------------- |
| Open Issues      | 0          | `gh issue list` — no open issues as of 2026-09-16 |
| PR Turnaround    | <1 day     | Typical PR review time (last measured 2026-08-22, not re-sampled this cycle) |
| Skipped Tests    | 33         | Fast-run skips (local, 2026-09-30): DATABASE_URL-gated, torch/transformers-gated, and a few environment-conditional tests |
| Health Score     | 95/100     | Overseer compliance score (not re-scored this cycle) |
| Last Updated     | 2026-09-30 | Fast suite re-run, counts re-derived |
| Project Status   | Active     | 2027 Q1: Phase 9 (cryptanalysis frontier, code), Phase 8 (primary-source sourcing, needs a person), platform work |
| K4 Readiness     | 8.5/10     | Ledger: 26 eliminated, 7 statistical, 7 sampled null, 5 open. Open code fronts and sourcing needs are in ROADMAP 2027 Q1 |
