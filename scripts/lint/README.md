# Lint Tools

**Consolidated tools:** `mdlint.py` + `autofix_unused_vars.py`

## Usage

**Automatic (pre-commit hooks):**

```bash
git commit  # Hooks run automatically
```

**Manual:**

```bash
# Check markdown style
python scripts/lint/mdlint.py check

# Auto-fix markdown issues (trailing whitespace, blank lines around lists, emphasis headings)
python scripts/lint/mdlint.py fix

# Reflow markdown paragraphs to 120 chars
python scripts/lint/mdlint.py reflow docs/

# Auto-fix unused variables (prefix with underscore)
python scripts/lint/autofix_unused_vars.py src/
python scripts/lint/autofix_unused_vars.py src/ --dry-run  # Preview changes

# Run all linters manually
pre-commit run --all-files

# Run tests with coverage
pytest --cov=src --cov-report=term-missing
```

## Auto-Fix Tools

### mdlint.py - Markdown Auto-Fix

**Fixes:**
- Trailing whitespace (all lines, including code blocks)
- MD032: Blank lines around lists
- MD036: Emphasis used instead of heading (`**Text**` → `### Text`)

**Example:**
```bash
python scripts/lint/mdlint.py fix          # Fix all markdown files
python scripts/lint/mdlint.py fix docs/    # Fix specific directory
```

### autofix_unused_vars.py - Unused Variables

**Philosophy:** Preserve code for future use by prefixing with underscore instead of deleting.

**Fixes:**
- F841 flake8 errors (unused variables)
- Prefixes with underscore: `var` → `_var`
- Adds comment explaining future use

**Example:**
```python
# Before
base_len = n // period
extra = n % period

# After
_base_len = n // period  # Future: may use for uneven column handling
_extra = n % period  # Future: may use for uneven column handling
```

**Usage:**
```bash
python scripts/lint/autofix_unused_vars.py src/           # Fix all Python files
python scripts/lint/autofix_unused_vars.py file.py        # Fix specific file
python scripts/lint/autofix_unused_vars.py src/ --dry-run # Preview changes
```

## What's Automated

All linting runs **automatically on git commit** via pre-commit hooks:

- ✅ Python: flake8, ruff (lint + format), pyupgrade, trailing-comma
- ✅ Markdown: style check, auto-fix, paragraph reflow (120 chars)
- ✅ General: EOF fixer, trailing whitespace, YAML validation

## Configuration

- `.pre-commit-config.yaml` - Hook definitions
- `.markdownlint.json` - Markdown line length (120)
- `pyproject.toml` - Ruff rules + flake8 config (consolidated)

## Why Consolidated?

Previously had 6 separate files:

- `check_md.py` + `reflow_md.py` → **consolidated to mdlint.py** (both markdown tools)
- `pep8_spacing_autofix.py` → **deleted** (incomplete, ruff-format handles it)
- `run_lint.ps1` → **deleted** (just use `pre-commit run --all-files`)
- `run_tests_coverage.ps1` → **deleted** (just use `pytest --cov=src`)
- `.flake8` → **merged into pyproject.toml** (single config file)

**Now:** 2 focused tools (markdown + unused vars) instead of 5, all auto-triggered or one-command.
