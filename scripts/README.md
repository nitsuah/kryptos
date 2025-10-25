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

### Testing & Analysis

- **run_hypothesis.py** - Test individual cipher hypotheses

  ```bash
  python scripts/run_hypothesis.py --hypothesis hill_2x2
  ```

- **run_random_baseline.py** - Establish random gibberish baseline

  ```bash
  python scripts/run_random_baseline.py --iterations 1000
  ```

- **test_composite_hypotheses.py** - Quick composite hypothesis testing

  ```bash
  python scripts/test_composite_hypotheses.py
  ```

- **test_composite_hypotheses_full.py** - Full composite hypothesis testing

  ```bash
  python scripts/test_composite_hypotheses_full.py
  ```

- **test_provenance.py** - Test artifact provenance tracking

  ```bash
  python scripts/test_provenance.py
  ```

- **test_stage_aware_scoring.py** - Test stage-aware scoring system

  ```bash
  python scripts/test_stage_aware_scoring.py
  ```

### Development Tools

- **dev/orchestrator.py** - Development orchestration utilities
- **lint/** - Linting configuration and scripts

## 🔄 Migration to CLI

Many script functionalities are being migrated to the main CLI (`kryptos` command):

| Script Function | CLI Command | Status |
|----------------|-------------|--------|
| run_hypothesis | `kryptos k4-decrypt` | ✅ Migrated |
| run_random_baseline | (future CLI command) | 📋 Planned |
| tuning operations | `kryptos tuning-*` | ✅ Migrated |
| autonomous system | `kryptos autonomous` | ✅ Migrated |

## 📦 Archived Scripts

See `archive/` for old/deprecated scripts:

- No archived scripts yet

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
