# Contributing to KRYPTOS

Thank you for your interest in advancing K4 analysis.

## 📚 Essential Reading for Contributors

**Start here:**

1. **[`docs/INDEX.md`](docs/INDEX.md)** — Canonical docs traversal map
  - Use this as the first stop for navigation across docs, references, analysis, and archive material

2. **This file (`CONTRIBUTING.md`)** — Canonical contributor workflow, operating standards, and autonomous quickstart
  - Consolidated manifesto + maintenance expectations
  - Definition-of-done style checks and review expectations
  - Quick operational command set for autonomous runs

3. **[`ROADMAP.md`](ROADMAP.md)** — Canonical roadmap and milestone flow
  - Current quarter priorities and completion status
  - High-level strategic direction

4. **[`TASKS.md`](TASKS.md)** — Canonical execution backlog
   - Prioritized active work items with acceptance criteria
   - Evidence-driven completion tracking
   - Operational queue used by humans and agents

5. **[`README.md`](README.md)** — Project overview and CLI usage examples
  - Primary orientation for runtime usage
  - Baseline K1-K3/K4 context and entry points

**Architecture & Systems:**

- **[`docs/reference/AUTONOMOUS_SYSTEM.md`](docs/reference/AUTONOMOUS_SYSTEM.md)** — Design of the autonomous solving
system
  - Agent triumvirate (SPY, OPS, Q) architecture
  - Coordination loop and decision-making
  - 24/7 autonomous operation capabilities

- **[`docs/reference/AGENTS_ARCHITECTURE.md`](docs/reference/AGENTS_ARCHITECTURE.md)** — Intelligence layer design
  - SPY (pattern recognition), OPS (orchestration), Q (validation) agents
  - NLP integration, linguistic analysis, strategic direction
  - Agent communication protocols

- **[`docs/reference/PROVENANCE_SYSTEM_EXPLAINED.md`](docs/reference/PROVENANCE_SYSTEM_EXPLAINED.md)** — Memory and
tracking system
  - Search space coverage tracking
  - Attack attempt deduplication
  - Provenance logging for academic rigor

**Performance & Validation:**

- **[`docs/analysis/K1_K2_VALIDATION_RESULTS.md`](docs/analysis/K1_K2_VALIDATION_RESULTS.md)** — K1/K2 Monte Carlo
validation
  - 100% success rate on both K1 and K2 (50 runs each, revalidated 2026-05-24)
  - Deterministic recovery algorithms validated
  - Performance benchmarks

- **[`docs/analysis/K3_VALIDATION_RESULTS.md`](docs/analysis/K3_VALIDATION_RESULTS.md)** — K3 autonomous solving
validation
  - 60-95% observed success rates (period/seed-dependent)
  - SA solver performance analysis
  - Probabilistic vs deterministic algorithms

**API & Reference:**

- **[`docs/reference/API_REFERENCE.md`](docs/reference/API_REFERENCE.md)** — Public API documentation
  - Stable Python entry points
  - CLI commands and subcommands
  - Module-level API contracts

**Understanding these docs will help your contributions align with project architecture, standards, and strategic
direction.**

---

## Manifesto Alignment (Required)

Before opening a PR, verify the change aligns with the standards in this file:

1. What measurable signal improved?
2. How can another contributor reproduce the claim?
3. What weak path was removed, rejected, or de-prioritized?

If a change is exploratory and does not improve validated signal yet, mark it explicitly as exploratory.

## Operating Standards (Consolidated)

These standards consolidate prior manifesto + maintenance guidance into one active location.

1. Truth over narrative
- Prefer measured outcomes over optimistic interpretation.
- Treat negative results as valid outputs.

2. Reproducibility over heroics
- Any substantial claim must be reproducible from committed code, pinned data, and deterministic commands.
- Campaign-relevant runs must produce traceable artifacts/provenance.

3. Baseline rigor before frontier claims
- K1-K3 controls are quality gates for K4 strategy promotion.
- Do not scale strategies that fail known-cipher controls.

4. AI as multiplier, not authority
- Treat AI output as proposals requiring engineering and statistical validation.

5. Maintenance discipline
- Tests are preserved unless redundancy is proven.
- Working scripts graduate into tests or `src/` APIs.
- Outdated docs are consolidated or archived; active queues stay in `ROADMAP.md` and `TASKS.md`.

## Autonomous Quickstart (Consolidated)

Use this for operational autonomous runs:

```bash
python -m kryptos.cli.main autonomous --max-hours 24 --cycle-interval 5
```

Useful monitoring commands:

```bash
python -m kryptos.cli.main autonomous --help
python -m kryptos.cli.main sections
```

## Getting Started

1. Install dependencies:

   ```bash
   git clone https://github.com/nitsuah/kryptos.git
   cd kryptos
   pip install -r requirements.txt
   ```

2. Run tests:

   ```bash
   pytest tests/ -v
   ```

3. Run linting:

   ```bash
   pre-commit run --all-files
   ```

## Quick Start: Hill Constraint Stage

```python
from kryptos.k4.pipeline import Pipeline, make_hill_constraint_stage
cipher_k4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQ"
pipe = Pipeline([make_hill_constraint_stage()])
result = pipe.run(cipher_k4)[0]
for cand in result.metadata['candidates'][:5]:
    print(cand['source'], cand['score'], cand['text'][:50])
```

## Quick Start: Composite Multi-Stage Run

```python
from kryptos.k4.pipeline import (
    make_hill_constraint_stage,
    make_transposition_adaptive_stage,
    make_transposition_multi_crib_stage,
    make_route_transposition_stage,
    make_masking_stage,
    make_berlin_clock_stage,
)
from kryptos.k4.composite import run_composite_pipeline

cipher_k4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQ"
positional_cribs = {
    'EAST': [22],
    'NORTHEAST': [25],  # corrected index
    'BERLIN': [64],
    'CLOCK': [69],      # corrected index
}
stages = [
    make_hill_constraint_stage(),
    make_transposition_adaptive_stage(min_cols=5, max_cols=6, sample_perms=200, partial_length=50),
    make_transposition_multi_crib_stage(positional_cribs=positional_cribs, min_cols=5, max_cols=6),
    make_route_transposition_stage(min_cols=5, max_cols=6),
    make_masking_stage(limit=15),
    make_berlin_clock_stage(step_seconds=10800, limit=20)
]
weights = {
    'hill-constraint': 2.0,
    'transposition-adaptive': 1.2,
    'transposition-pos-crib': 1.5,
    'masking': 1.0,
    'berlin-clock': 0.8,
}
res = run_composite_pipeline(cipher_k4, stages, report=True, normalize=True, adaptive=True)
print("Adaptive weights:", res['profile'].get('adaptive_diagnostics'))
print("Top fused candidates:")
for c in res.get('fused', [])[:5]:
    print(c['stage'], c['fused_score'], c['text'][:50])
```

## Attempt Logs Persistence

```python
from kryptos.k4.attempt_logging import persist_attempt_logs
path = persist_attempt_logs(out_dir='reports', label='K4', clear=True)
print("Attempt log written:", path)
```

## Workflow

1. Fork and branch from `main`.
2. Implement a focused enhancement (small, testable functions).
3. Add or update tests under `tests/` (avoid large exhaustive brute-force loops; cap iterations).
4. Update exports in `src/kryptos/k4/__init__.py` if you introduce new public symbols.
5. Update `ROADMAP.md` only if you add or refine planned analytical directions.
6. Run `pytest tests/ -v` and ensure relevant suites pass.
7. Submit a PR with a concise description of rationale and methodology.

## Code Guidelines

- Prefer pure functions over hidden state.
- Use explicit module-level caches (e.g., `_cache_holder`) rather than globals sprinkled across
functions.
- Keep scoring and search logic separate; scoring modules should not mutate state.
- Group related exports logically; avoid re-exporting internal helpers unnecessarily.
- Name stages clearly: `make_<purpose>_stage()`.
- Keep complexity controlled: stepwise search + scoring rather than monolithic brute force.
- **CRITICAL:** Never name files after standard library modules (e.g., `logging.py`, `collections.py`, `typing.py`) as
they will shadow the standard library and cause import errors.

## Testing

- Provide unit tests for each new cipher operation or scoring metric.
- Use deterministic seeds for any randomized sampling.
- Skip placeholder hypothesis tests with `@unittest.skip` until logic is implemented.
- For reproducible fast coverage in Docker, run:

  ```bash
  docker run --rm -v "${PWD}:/app" -w /app python:3.13-slim sh -lc \
    "pip install --no-cache-dir pytest pytest-cov numpy matplotlib requests beautifulsoup4 spacy nltk pyyaml && \
     python -m spacy download en_core_web_sm && \
     pip install --no-cache-dir -e . --no-deps && \
     pytest tests/ -m 'not slow' --cov=src --cov-report=term"
  ```

  The micro-benchmark in `tests/test_k4_performance.py` auto-skips in container runtimes to prevent false
  performance regressions.

## Performance

- Avoid factorial explosions without pruning heuristics.
- Profile before optimizing; document any performance-sensitive loops.

## Documentation

- README: High-level overview only.
- `ROADMAP.md`: Current milestones and priorities.
- Inline comments: Clarify non-obvious math (e.g., matrix inversion steps).

## Data

- Add new frequency / n-gram data as tab-separated `GRAM<TAB>FREQUENCY` in `data/`.
- Include provenance via `#` commented lines at file top.

## Pull Request Checklist

- [ ] Feature isolated and cohesive
- [ ] Tests added / updated
- [ ] All tests pass locally (`pytest tests/`)
- [ ] Linting passes (`pre-commit run --all-files`)
- [ ] README / ROADMAP.md updated if relevant
- [ ] Manifesto alignment explained (signal, reproducibility, and pruning decision)
- [ ] Strategic claims include measurable acceptance criteria

Welcome aboard!
