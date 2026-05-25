# Testing Notes

This folder contains lightweight testing artifacts and helper files.

For canonical test status, coverage, and success rates, use:

- `METRICS.md`
- `docs/analysis/K1_K2_VALIDATION_RESULTS.md`
- `docs/analysis/K3_VALIDATION_RESULTS.md`

## Standard Test Commands

```bash
# Full suite
pytest tests/ -v

# Fast suite (recommended for iteration)
pytest tests/ -m "not slow" -v

# Coverage check
pytest tests/ -m "not slow" --cov=src --cov-report=term
```

## Notes

- Slow Monte Carlo tests are opt-in for regular development runs.
- Keep test logic in `tests/` rather than creating one-off script test harnesses.
