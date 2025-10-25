# Scripts Directory

This directory contains utility scripts for development, testing, and analysis.

## 🎯 Active Scripts

### Performance & Optimization

- **benchmark_scoring.py** - Quick scoring benchmarks with readable output

  ```bash
  python scripts/benchmark_scoring.py
  ```

- **profile_scoring.py** - cProfile analysis for scoring hotspots

  ```bash
  python scripts/profile_scoring.py
  ```

### Tuning & Calibration

- **tuning.py** - Main tuning orchestration script

  ```bash
  python scripts/tuning.py --help
  ```

- **calibrate_scoring_weights.py** - Grid search for optimal scoring weights

  ```bash
  python scripts/calibrate_scoring_weights.py
  ```

## 🔄 Migration to CLI

Many script functionalities have been migrated to the main CLI (`kryptos` command):

| Script Function | CLI Command | Status |
|----------------|-------------|--------|
| run_hypothesis | `kryptos k4-decrypt` | ✅ Migrated |
| run_random_baseline | `kryptos k4-decrypt --random-baseline` | ✅ Migrated |
| tuning operations | `kryptos tuning-*` | ✅ Migrated |
| autonomous system | `kryptos autonomous` | ✅ Migrated |

## 📦 Archived Scripts

**All archived scripts have been deleted** - they were fully replaced by:
- CLI commands (`kryptos k4-decrypt`, `kryptos autonomous`)
- Proper pytest tests in `tests/` directory

Previously archived (now deleted):
- `test_*.py` scripts → Migrated to proper pytest tests
- `run_hypothesis.py` → Replaced by `kryptos k4-decrypt`
- `run_random_baseline.py` → Replaced by CLI

## 🎯 Script Guidelines

### When to Use Scripts

- **Performance analysis** (benchmark, profile)
- **One-time calibration** (weight optimization)
- **Development testing** (manual hypothesis testing)
- **Quick experiments** (not worth CLI integration)

### When to Use CLI

- **Production operations** (k4-decrypt, tuning, autonomous)
- **Repeated workflows** (daily operations)
- **User-facing features** (public API)
- **Cross-platform compatibility** (Windows/Linux/Mac)

## 🔧 Development

### Adding New Scripts

1. Create script with clear docstring 2. Add `if __name__ == "__main__": main()` pattern 3. Update this README 4.
Consider CLI migration for repeated use

### Archiving Scripts

When a script becomes obsolete:

1. Move to `archive/` subdirectory 2. Update this README 3. Document reason for archival 4. Keep for historical
reference

### Script to CLI Migration

Checklist:

1. Add CLI subcommand in `src/kryptos/cli/main.py` 2. Move core logic to appropriate module in `src/` 3. Add tests for
CLI command 4. Update documentation 5. Archive original script with migration note

## 📚 Related Documentation

- **CLI Reference:** Run `python -m kryptos.cli.main --help`
- **API Documentation:** `docs/API_REFERENCE.md`
- **Performance:** `docs/PERFORMANCE_OPTIMIZATION.md`

## 🚨 Important Notes

- Scripts are **development tools**, not production code
- Most scripts expect to run from project root
- Check script docstrings for dependencies
- Use `python scripts/script_name.py` (not direct execution)
