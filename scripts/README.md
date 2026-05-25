# Scripts Directory

Purpose: lightweight developer utilities that do not belong in the production package.

Status: active and intentionally small.

## Current Structure

- `scripts/lint/`
	- `mdlint.py`: markdown checks/fixes.
	- `autofix_unused_vars.py`: optional unused-variable helper.
- `scripts/testing/`
	- Testing convenience artifacts and notes.

## Principles

- Reusable functionality belongs in `src/kryptos/`, not scripts.
- Verification belongs in `tests/` and should run via `pytest`.
- Keep scripts focused, documented, and low-risk.

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
```

## References

- `docs/MAINTENANCE_GUIDE.md`
- `docs/INDEX.md`
- `CONTRIBUTING.md`
