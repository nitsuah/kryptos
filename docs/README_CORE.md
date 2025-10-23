# KRYPTOS — Core Documentation

This file contains the detailed project overview, features, modules, and quick-start examples for
the KRYPTOS project. The top-level `README.md` is intentionally concise — use this document for in-
depth reference.

## TL;DR

K4 is the unsolved section of the Kryptos sculpture. This repository contains a toolkit to explore
layered cipher hypotheses (Hill, transposition, masking, Berlin Clock shift hypotheses) and a
configurable pipeline to score and rank candidate plaintexts.

This repository contains code, tests, data, and documentation to run and extend experiments.
K4-specific strategy and deep technical notes live under `docs/K4_STRATEGY.md`.

### Quick links

- Documentation: `docs/README_CORE.md` (project reference)
- K4 strategy: `docs/K4_STRATEGY.md` (K4-specific notes)
- Roadmap: `ROADMAP.md`
- Daily plan: `PLAN.md`
- Tuning/daemon runner: `scripts/tune_pipeline.py`, `scripts/daemon_runner.py`
- Tests: `tests/` (run with `python -m unittest discover -s tests`)

Related documents / breadcrumbs:

- Autopilot & SPY: `AUTOPILOT.md`
- Plan: `PLAN.md`
- Roadmap: `../ROADMAP.md`
- Top-level README: `../README.md`

### Highlights

- Modular pipeline for multi-stage hypothesis testing (pipeline, composite runners)
- Scoring utilities (n-grams, chi-square, crib/positional bonuses, entropy metrics)
- Attempt logging and reproducible artifacts (JSON/CSV output under `artifacts/`)
- Tuning harness and a minimal daemon runner for automated sweeps

## Current Progress

- Implemented K1–K3 verified tooling and tests.
- K4: implemented multi-stage pipeline scaffolding, scoring utilities, attempt logging, and adaptive
gating.
- Added unit tests and a tuning harness scaffold; artifacts written to `artifacts/` during runs.

## Features (summary)

- Hill cipher solving (2x2, 3x3) with pruning and crib support
- Columnar & route transposition search, including multi-crib positional anchoring
- Masking/null removal stage and Berlin Clock shift hypotheses
- Composite pipeline orchestration, attempt logging, and CSV/JSON artifacts
- Scoring utilities: n-grams, chi-square, crib & positional bonuses, entropy and wordlist heuristics
- Tuning harness and a minimal daemon runner for long-running sweeps (`scripts/daemon_runner.py`)

## Modules (under `src/k4/`)

- `scoring.py` — scoring primitives and composite functions
- `hill_cipher.py`, `hill_constraints.py` — hill math and constrained key derivation
- `transposition.py`, `transposition_constraints.py` — columnar/route transposition utilities
- `pipeline.py`, `composite.py` — stage factories and pipeline executor
- `attempt_logging.py`, `reporting.py` — artifact persistence and reporting

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Run the test suite:

```bash
python -m unittest discover -s tests
```

1. Run a tiny pipeline sample (preferred: direct package usage; legacy script
`run_pipeline_sample.py` is deprecated). This example writes artifacts to `artifacts/k4_runs/`:

```python
from k4.pipeline import make_hill_constraint_stage, make_masking_stage
from k4.executor import PipelineConfig, PipelineExecutor

stages = [
	make_hill_constraint_stage(name="hill", prune_3x3=True, partial_len=40, partial_min=-900.0),
	make_masking_stage(name="masking", null_chars=["X"], limit=15),
]
cfg = PipelineConfig(ordering=stages, candidate_cap_per_stage=25, pruning_top_n=10,
					 crib_bonus_threshold=5.0, adaptive_thresholds={"hill": -500.0},
					 artifact_root="artifacts", artifact_run_subdir="k4_runs", label="sample-run", enable_attempt_log=True,
					 parallel_hill_variants=0)
PipelineExecutor(cfg).run("OBKRUOXOGHULBSOLIFB")
```

## How to Use the Tuning Harness

- `scripts/tuning/tune_pipeline.py` contains a small sweep harness. For safe local experiments, use
the dry-run mode or set small candidate budgets.
- The daemon runner `scripts/daemon_runner.py` provides a minimal long-loop runner that writes CSV
artifacts to `artifacts/tuning_runs/` and retains the last 20 runs.

## Artifacts

- Attempt logs and run summaries are placed under `artifacts/k4_runs/run_<timestamp>/` (pipeline
runs) or `artifacts/tuning_runs/run_<timestamp>/` when using the tuning harness or daemon.

## Roadmap & Contributing

- See `ROADMAP.md` for the detailed roadmap.
- Contribution guidelines are in `CONTRIBUTING.md`.

## Data Sources

- N-gram and frequency data live in `data/` as TSVs; the code falls back to reasonable defaults when
files are missing.

## License & References

- See `LICENSE` for licensing.
- References and further reading are in the original README and in-line documentation within
`docs/`.
