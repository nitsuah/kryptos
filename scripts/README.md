# Scripts Directory

Purpose: lightweight developer utilities that do not belong in the production package.

Status: active and intentionally small.

## Current Structure

- `scripts/lint/`
	- `mdlint.py`: markdown checks/fixes.
	- `autofix_unused_vars.py`: optional unused-variable helper.
- `scripts/testing/`
	- Testing convenience artifacts and notes.
- `run_k4_overnight_sweeps.py`: thin CLI entry point for
	`kryptos.k4.overnight_runner.run_all_pending_sweeps` — runs every
	registered K4 full-scope attack sweep in order, halting on a
	EurekaSignal breakthrough. Reusable logic (the sweep registry, the
	run/halt behavior) lives in `src/kryptos/k4/overnight_runner.py`.

## Principles

- Reusable functionality belongs in `src/kryptos/`, not scripts.
- Verification belongs in `tests/` and should run via `pytest`.
- Keep scripts focused, documented, and low-risk.

## Historical Note

In January 2025, one-off K1/K2 debugging scripts were removed after their behavior was covered by maintained pytest suites.
This policy remains in effect: debugging scripts are temporary; durable validation belongs in `tests/`.

## Common Commands

```bash
# Lint markdown
python scripts/lint/mdlint.py check
python scripts/lint/mdlint.py fix

# Optional helper for unused vars
python scripts/lint/autofix_unused_vars.py src/ --dry-run

# Run primary test suite
pytest tests/ -v

# Fast-only suite used for rapid iteration
pytest tests/ -m "not slow" -v

# Run every registered K4 full-scope attack sweep in order
python scripts/run_k4_overnight_sweeps.py
```

## References

- `CONTRIBUTING.md`
- `docs/INDEX.md`
