# Linting & Code Quality

Automated code quality enforcement for the Kryptos project.

## 🔧 Setup (One-Time)

```bash
# Install pre-commit hooks (auto-runs on git commit)
pre-commit install
```

**That's it!** All linting now runs automatically when you commit files.

## 🚀 Quick Commands

```bash
# Run all linters manually
pre-commit run --all-files

# Run specific linter
pre-commit run ruff --all-files
pre-commit run flake8 --all-files

# Run tests with coverage
pwsh scripts/lint/run_tests_coverage.ps1
```

## 📋 What Gets Checked

**Python (automatic):**
- ✅ `ruff` - Fast Python linter + formatter
- ✅ `flake8` - PEP8 style checker
- ✅ `pyupgrade` - Modern Python syntax (3.10+)
- ✅ `add-trailing-comma` - Consistent formatting

**Markdown (automatic):**
- ✅ `check_md.py` - Line length, trailing spaces, list formatting
- ✅ `reflow_md.py` - Auto-reflow paragraphs to 120 chars

**General (automatic):**
- ✅ Trailing whitespace removal
- ✅ End-of-file fixer
- ✅ YAML syntax check
- ✅ Large file prevention

## 📁 Files in This Directory

| File | Purpose | Usage |
|------|---------|-------|
| `check_md.py` | Markdown style checker | Called by pre-commit |
| `reflow_md.py` | Markdown reflower (120 char lines) | Called by pre-commit |
| `pep8_spacing_autofix.py` | Python spacing fixer (legacy) | Manual use only |
| `run_lint.ps1` | Manual lint runner (legacy) | `pwsh run_lint.ps1` |
| `run_tests_coverage.ps1` | Coverage report | `pwsh run_tests_coverage.ps1` |

## 🔒 Pre-Commit Configuration

All configuration lives in `.pre-commit-config.yaml` at repo root.

**Current hooks:** 1. **flake8** - Max line 120, ignore E203 2. **ruff** - Auto-fix + format 3. **pyupgrade** - Python
3.10+ syntax 4. **add-trailing-comma** - Consistent style 5. **Standard hooks** - EOF, whitespace, yaml 6. **Markdown**
- Reflow + style check

## 🛠️ Troubleshooting

**Pre-commit hook failing?**
```bash
# See what failed
git commit  # Will show errors

# Fix automatically where possible
pre-commit run --all-files

# Skip hooks temporarily (NOT RECOMMENDED)
git commit --no-verify
```

**Need to update hooks?**
```bash
pre-commit autoupdate
```

**Coverage report not working?**
```bash
pip install pytest-cov
pwsh scripts/lint/run_tests_coverage.ps1
```

## 📊 Standards

- **Python line length:** 120 chars
- **Markdown line length:** 120 chars
- **Python version:** 3.10+
- **Code style:** Black-compatible (via ruff-format)

---

**Last Updated:** 2025-10-24
