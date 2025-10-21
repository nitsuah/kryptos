# Contributing to KRYPTOS

Thank you for your interest in advancing K4 analysis.

## Workflow

1. Fork and branch from `k4`.
2. Implement a focused enhancement (small, testable functions).
3. Add or update tests under `tests/` (avoid large exhaustive brute-force loops; cap iterations).
4. Update exports in `src/k4/__init__.py` if you introduce new public symbols.
5. Update `roadmap.md` only if you add or refine planned analytical directions.
6. Run `python -m unittest discover -s tests` and ensure all tests pass.
7. Submit a PR with a concise description of rationale and methodology.

## Code Guidelines

- Prefer pure functions over hidden state.
- Use explicit module-level caches (e.g., `_cache_holder`) rather than globals sprinkled across functions.
- Keep scoring and search logic separate; scoring modules should not mutate state.
- Group related exports logically; avoid re-exporting internal helpers unnecessarily.
- Name stages clearly: `make_<purpose>_stage()`.
- Keep complexity controlled: stepwise search + scoring rather than monolithic brute force.

## Testing

- Provide unit tests for each new cipher operation or scoring metric.
- Use deterministic seeds for any randomized sampling.
- Skip placeholder hypothesis tests with `@unittest.skip` until logic is implemented.

## Performance

- Avoid factorial explosions without pruning heuristics.
- Profile before optimizing; document any performance-sensitive loops.

## Documentation

- README: High-level overview only.
- `roadmap.md`: Detailed upcoming modules and hypotheses.
- Inline comments: Clarify non-obvious math (e.g., matrix inversion steps).

## Data

- Add new frequency / n-gram data as tab-separated `GRAM<TAB>FREQUENCY` in `data/`.
- Include provenance via `#` commented lines at file top.

## Pull Request Checklist

- [ ] Feature isolated and cohesive
- [ ] Tests added / updated
- [ ] All tests pass locally
- [ ] README / roadmap updated if relevant
- [ ] No linter / syntax errors

Welcome aboard!
