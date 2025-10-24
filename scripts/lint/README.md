# Lint Tools

**Single consolidated tool:** `mdlint.py`

## Usage

**Automatic (pre-commit hooks):**

```bash
git commit  # Hooks run automatically
```

**Manual:**

```bash
# Check markdown style
python scripts/lint/mdlint.py check

# Reflow markdown paragraphs to 120 chars
python scripts/lint/mdlint.py reflow docs/

# Run all linters manually
pre-commit run --all-files

# Run tests with coverage
pytest --cov=src --cov-report=term-missing
```

## What's Automated

All linting runs **automatically on git commit** via pre-commit hooks:

- ✅ Python: flake8, ruff (lint + format), pyupgrade, trailing-comma
- ✅ Markdown: style check, paragraph reflow (120 chars)
- ✅ General: EOF fixer, trailing whitespace, YAML validation

## Configuration

- `.pre-commit-config.yaml` - Hook definitions
- `.markdownlint.json` - Markdown line length (120)
- `pyproject.toml` - Ruff rules
- `.flake8` - Flake8 config

## Why One File?

Previously had 5 separate files:

- `check_md.py` + `reflow_md.py` → **consolidated to mdlint.py** (both markdown tools)
- `pep8_spacing_autofix.py` → **deleted** (incomplete, ruff-format handles it)
- `run_lint.ps1` → **deleted** (just use `pre-commit run --all-files`)
- `run_tests_coverage.ps1` → **deleted** (just use `pytest --cov=src`)

**Result:** 1 tool instead of 5, all auto-triggered, no manual scripts needed.
