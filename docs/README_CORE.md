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

- Core reference (this file): `docs/README_CORE.md`
- K4 strategy: `docs/K4_STRATEGY.md`
- Roadmap: `docs/ROADMAP.md`
- Technical debt tracker: `docs/TECHDEBT.md`
- Sections API: `docs/SECTIONS.md`
- Experimental tooling inventory: `docs/EXPERIMENTAL_TOOLING.md`
- CLI: `kryptos --help` (sections, k4-decrypt, k4-attempts; tuning subcommands forthcoming)
- Tuning APIs: `kryptos.k4.tuning.*` (weight sweeps, tiny param sweeps, artifact summarization)
- Tests: `tests/` (pytest / unittest)

Related documents / breadcrumbs:

- Autopilot & SPY: `docs/AUTOPILOT.md`
- Reorg policy: `docs/REORG.md`
- Top-level README: `README.md`

### Highlights

- Modular pipeline for multi-stage hypothesis testing (pipeline, composite runners)
- Scoring utilities (n-grams, chi-square, crib/positional bonuses, entropy metrics)
- Attempt logging and reproducible artifacts (JSON/CSV output under `artifacts/`)
- Tuning harness and a minimal daemon runner for automated sweeps

## Current Progress (Snapshot)

- K1–K3: unified decrypt helpers (`kryptos.k1.decrypt`, etc.) + sections mapping.
- K4: multi-stage pipeline (hill, transposition, masking, Berlin Clock) with adaptive gating &
scoring.
- Tuning: pure functions under `kryptos.k4.tuning` (`run_crib_weight_sweep`, `tiny_param_sweep`,
`pick_best_weight_from_rows`, artifact utilities) and tests.
- CLI: base subcommands (sections listing, k4 decrypt, attempts). Tuning subcommands in progress.
- Artifact utilities: consolidated under `kryptos.k4.tuning.artifacts` replacing legacy summarizer
scripts.

## Features (summary)

- Hill cipher solving (2x2, 3x3) with pruning and crib support
- Columnar & route transposition search, including multi-crib positional anchoring
- Masking/null removal stage and Berlin Clock shift hypotheses
- Composite pipeline orchestration, attempt logging, and CSV/JSON artifacts
- Scoring utilities: n-grams, chi-square, crib & positional bonuses, entropy and wordlist heuristics
- Tuning harness and a minimal daemon runner for long-running sweeps (`scripts/daemon_runner.py`)

## Modules (under `kryptos/k4/`)

- `scoring.py` — scoring primitives and composite functions
- `hill_cipher.py`, `hill_constraints.py` — hill math and constrained key derivation
- `transposition.py`, `transposition_constraints.py` — columnar/route transposition utilities
- `pipeline.py`, `composite.py` — stage factories and pipeline executor
- `attempt_logging.py`, `reporting.py` — artifact persistence and reporting

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

2. Run the test suite:

```bash
pytest -q  # or: python -m unittest discover -s tests
```

3. Decrypt sections via CLI:

```bash
kryptos sections
kryptos k4-decrypt --limit 25 --adaptive --report
```

4. Programmatic K4 sample:

```python
from kryptos.k4 import decrypt_best

result = decrypt_best("OBKRUOXOGHULBSOLIFB", limit=25, adaptive=True, report=True)
print(result.plaintext, result.score)
```

## Tuning & Artifact Post‑Processing

Prefer direct APIs over scripts:

- Weight sweep: `from kryptos.k4.tuning import run_crib_weight_sweep`
- Pick best weight: `from kryptos.k4.tuning import pick_best_weight_from_rows`
- Tiny param sweep: `from kryptos.k4.tuning import tiny_param_sweep`
- Artifact cleaning & summary: `from kryptos.k4.tuning.artifacts import end_to_end_process`

Example weight sweep:

```python
from pathlib import Path
from kryptos.k4.tuning import run_crib_weight_sweep

rows = run_crib_weight_sweep(weights=[0.5, 1.0, 1.5], run_dir=Path('artifacts/tuning_runs'))
for r in rows:
    print(r.weight, r.score_delta)
```

Legacy wrapper scripts remain temporarily for backwards compatibility and will be replaced by CLI
tuning subcommands (`kryptos tuning ...`).

## Artifacts

- Pipeline runs: `artifacts/k4_runs/run_<timestamp>/`
- Tuning runs: `artifacts/tuning_runs/run_<timestamp>/` (CSV sweeps, per-weight details)
- Reports / summaries: produced via `kryptos.k4.tuning.artifacts` helpers

## Roadmap & Contributing

- Roadmap: `docs/ROADMAP.md`
- Contributing guidelines: `CONTRIBUTING.md`

## Data Sources

- N-gram and frequency data live in `data/` as TSVs; the code falls back to reasonable defaults when
files are missing.

## License & References

- License: `LICENSE`
- References: top-level README + docstrings + strategy docs.

--- Last updated: 2025-10-23 (CLI + tuning API consolidation)
