# Contributing to KRYPTOS

Thank you for your interest in advancing K4 analysis.

## 📚 Essential Reading for Contributors

**Start here:**

1. **[`docs/MAINTENANCE_GUIDE.md`](docs/MAINTENANCE_GUIDE.md)** — Core maintenance philosophy and practices
   - When to create/delete tests, scripts, and documentation
   - Code quality standards and review checklist
   - Definition of done for contributions
   - Audit procedures for keeping codebase clean

2. **[`docs/PHASE_6_ROADMAP.md`](docs/PHASE_6_ROADMAP.md)** — Current development roadmap and strategic direction
   - Phase 6 objectives and sprint structure
   - Current K1-K3 success rates (measured, validated)
   - K4 attack strategies and priorities
   - System readiness assessment (75% K4-ready)
   - Cross-references: [`docs/TODO_PHASE_6.md`](docs/TODO_PHASE_6.md) for operational checklist

3. **[`docs/TODO_PHASE_6.md`](docs/TODO_PHASE_6.md)** — Operational task breakdown
   - Prioritized work items with clear success metrics
   - Sprint-by-sprint deliverables
   - Technical implementation details
   - Cross-references roadmap for strategic context

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
  - 100% success rate on both K1 and K2 (50 runs each)
  - Deterministic recovery algorithms validated
  - Performance benchmarks

- **[`docs/analysis/K3_VALIDATION_RESULTS.md`](docs/analysis/K3_VALIDATION_RESULTS.md)** — K3 autonomous solving
validation
  - 68-95% success rates (period-dependent)
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
from src.k4 import Pipeline, make_hill_constraint_stage
cipher_k4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQ"
pipe = Pipeline([make_hill_constraint_stage()])
result = pipe.run(cipher_k4)[0]
for cand in result.metadata['candidates'][:5]:
    print(cand['source'], cand['score'], cand['text'][:50])
```

## Quick Start: Composite Multi-Stage Run

```python
from src.k4 import (
    make_hill_constraint_stage,
    make_transposition_adaptive_stage,
    make_transposition_multi_crib_stage,
    make_route_transposition_stage,
    make_masking_stage,
    make_berlin_clock_stage,
    run_composite_pipeline
)

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
from src.k4.attempt_logging import persist_attempt_logs
path = persist_attempt_logs(out_dir='reports', label='K4', clear=True)
print("Attempt log written:", path)
```

## Workflow

1. Fork and branch from `main`. 2. Implement a focused enhancement (small, testable functions). 3. Add or update tests
under `tests/` (avoid large exhaustive brute-force loops; cap iterations). 4. Update exports in `src/k4/__init__.py` if
you introduce new public symbols. 5. Update `roadmap.md` only if you add or refine planned analytical directions. 6. Run
`python -m unittest discover -s tests` and ensure all tests pass. 7. Submit a PR with a concise description of rationale
and methodology.

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

## Performance

- Avoid factorial explosions without pruning heuristics.
- Profile before optimizing; document any performance-sensitive loops.

## Documentation

- README: High-level overview only.
- `ROADMAP.md`: Detailed upcoming modules and hypotheses.
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

Welcome aboard!
