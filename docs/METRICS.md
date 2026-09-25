

# Metrics

> 🧭 [kryptos](../README.md) · [Index](./INDEX.md) · [Features](./FEATURES.md) · [Roadmap](./ROADMAP.md) · [Tasks](./TASKS.md) · [Changelog](./CHANGELOG.md) · **Metrics** <!-- nav -->

**Note:** Data and artifacts are planned to migrate to a database as part of the 2027 roadmap. Current metrics reflect the file-based structure.

**Last Validated:** 2026-09-16 (PMO audit, full re-run — see below); file counts re-derived by static analysis. Test-function count reflects all `def test_*` functions; pytest-collected count (after marks/deselection/parametrization) is higher and may differ.

## Core Metrics

| Metric              | Value   | Notes                                      |
| ------------------- | ------- | ------------------------------------------ |
| Code Coverage       | 89.27%  | Measured with pytest-cov (Docker, 2026-09-16, PMO audit): README's "Docker Fast Coverage" `python:3.13-slim` command — `pytest tests/ -m 'not slow' --cov=kryptos --cov-report=term`; 13,216 statements, 1,418 missed. Essentially flat vs. the 2026-08-22 reading (89.35%) despite substantial test growth in between. |
| Source Files        | 133     | Python modules in src/ excl. `__init__.py` (152 total incl. `__init__.py`) — re-derived 2026-09-16, up from 112/131 on 2026-08-22 (Phase 6/7/8 modules: geodesy, solar_geometry, cross_vector_consensus, classical_cipher_sweep, k0_morse_keywords, plaintext_evidence, known_plaintext_inversion, physical_geometry, constraint_chain, overnight_runner, and others) |
| Test Files          | 208     | `test_*.py` modules in tests/ (re-derived 2026-09-16, up from 184) |
| Test Functions      | 1535    | `def test_*` functions across all test files (static count 2026-09-16, up from 1271 on 2026-08-22) |
| Test Cases (Fast)   | 1658 passed | 0 failures, 34 skipped (Docker run 2026-09-16, PMO audit; slow-marked tests excluded via `-m 'not slow'`). Pytest-collected count exceeds the static function count above because parametrized tests expand into multiple items. |
| Test Cases (Slow)   | 26      | `@pytest.mark.slow`-marked test items, deselected by the fast run above (was estimated "~22" on 2026-08-22; now an exact count from the same run) |
| Lines of Code       | ~65K    | Not re-measured this cycle — carried over from 2026-08-22; TBD re-verify against the 133-file count above |
| Documentation Files | 40+     | Comprehensive docs in docs/ directory      |
| Subdirectories      | 40      | `find src -type d` count, 2026-09-16 (was 33 on 2026-08-22; grew with new K4 modules — methodology not otherwise changed) |
| Total Package Size  | 712 KB  | Source code only (excl. data/artifacts) — not re-measured this cycle, TBD re-verify |

## Performance Metrics

| Metric                      | Value         | Notes                                |
| --------------------------- | ------------- | ------------------------------------ |
| Fast Test Duration          | 261.37s (4:21)| Full `-m 'not slow'` suite, Docker, 2026-09-16 (1658 passed + 34 skipped). Not directly comparable to the 48.51s/631-test 2026-05-25 baseline — the fast suite has grown substantially since (now 1692 collected non-slow items) as Phase 6-8 K4 attack modules and their tests were added. |
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
| Tests                 | 208   | ~25K+ | Comprehensive test coverage (file count re-derived 2026-09-16, was 184) |

## Code Quality

| Metric                 | Value    | Notes                                    |
| ---------------------- | -------- | ---------------------------------------- |
| Linting Status         | Clean    | Pre-commit hooks enforced                |
| Test Pass Rate         | 100%     | 1658 passed, 0 failures (Docker run 2026-09-16, PMO audit; 1535 functions as of 2026-09-16 static count) |
| Deprecated Code        | Minimal  | executor.py marked for removal (legacy, retiring after migration confirmation) |
| TODO/FIXME Count       | Low      | No critical technical debt               |
| Module Independence    | High     | Clear boundaries, no shadow imports      |
| Documentation Coverage | Extensive| 40+ docs, 3,500+ lines academic writing |

## Health

| Metric           | Value      | Notes                                    |
| ---------------- | ---------- | ---------------------------------------- |
| Open Issues      | 0          | `gh issue list` — no open issues as of 2026-09-16 |
| PR Turnaround    | <1 day     | Typical PR review time (last measured 2026-08-22, not re-sampled this cycle) |
| Skipped Tests    | 34         | Fast-run skips (Docker, 2026-09-16) — DATABASE_URL-gated, torch/transformers-gated, and a few environment-conditional tests; was reported as "10" on 2026-08-22, which undercounted vs. the actual fast-run skip list |
| Health Score     | 95/100     | Overseer compliance score (not re-scored this cycle) |
| Last Updated     | 2026-09-16 | PMO audit: full re-run in Docker (README's "Docker Fast Coverage" command, after fixing a missing `geographiclib` dependency in that same command — see README.md) |
| Project Status   | Active     | All Q1-2027 phases shipped; frontier K4 attack planning in progress |
| K4 Readiness     | 8.5/10     | Full pipeline, dashboard, RAG, and 14 completed attack vectors; 3-layer composites next |
