# Contributing to KRYPTOS

Thank you for your interest in advancing K4 analysis.

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
