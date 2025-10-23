# Project index (10k ft view)

This file gives a very short, high-level overview of the repository by top-level directories and the
core Python scripts you will likely use. Each entry has an ELI5 sentence describing what it does.

## Top-level directories

- `kryptos/` — Main Python package and core logic.
  - `src/` — Python package source. Contains the core implementation (k4 executor, agents, and
    utilities).
  - `scripts/` — Development and tooling scripts (orchestration, extractors, tuning harnesses).
  - `tests/` — Unit and integration tests covering the core behaviors.
  - `docs/` — Project documentation (this file and other guides).

- `scripts/` — Repo-level helper scripts (linting, demos, tuning runners). These are convenience
scripts to run common tasks outside the package.

- `artifacts/` — Generated outputs from runs and demos (CSV, JSON, run folders). Useful for
experiment traces and reproducible results.

- `examples/` — Small example programs that show how to wire the package for quick experiments.

## Package layout details (src/k4 and src/kryptos)

- `src/k4/` — The canonical K4 implementation and runtime plumbing used by tuning and demo scripts.
  - Key responsibilities: job execution (parallel variants), scoring, hill/crib algorithms, and
    pipeline composition. Files of interest include `executor.py` (runs variants and aggregates
    results), `hill_search.py` and `hill_constraints.py` (hill-cipher specific search and
    constraints), `scoring.py` (scoring functions used by tuners), and `reporting.py` (helpers
    that format experiment outputs into artifacts/). This package is the primary place to look
    when changing runtime behavior or adding new solver variants.

- `src/kryptos/` — Higher-level package utilities and connectors that sit above `src/k4`.
  - Key responsibilities: glue code, analysis utilities, and convenience modules used by
    experiments and CI. This area contains `analysis.py`, higher-level `report.py` helpers,
    and `scripts/` shims that allow repo-level scripts to be exposed as package-importable
    modules for tests and tooling.

### Note on the `spy_eval` shim and packaging

There is an existing shim at `src/kryptos/scripts/tuning/spy_eval.py` which imports the filesystem
script `scripts/tuning/spy_eval.py` and re-exports functions for tests. Importing directly from
`scripts.*` paths can lead to brittle imports when running inside venvs or when the package is
installed.

Recommended fixes:

- Preferred: Move the canonical `spy_eval` implementation into the package (for example,
`src/kryptos/tuning/spy_eval.py`) and update callers to import `kryptos.tuning.spy_eval`.
- Alternative: Replace the shim with a small package-level wrapper that imports the
implementation from the canonical package location (not from `scripts.*`).

If you'd like, I can perform the preferred fix and port `scripts/tuning/spy_eval.py` into the
package and update import sites in a follow-up commit.

## Core python scripts (ELI5)

- `kryptos/src/k4/executor.py` — Runs job variants in parallel and collects results. ELI5: "It tries
different ways to run a job at once and picks the outputs when they finish."

- `kryptos/scripts/dev/orchestrator.py` — Orchestrates OPS (tuning) runs and stores run metadata.
ELI5: "It runs tuning experiments and remembers what happened so we can learn from it."

- `scripts/dev/ask_triumverate.py` — High-level autopilot driver that runs OPS then SPY extraction.
ELI5: "A small orchestrator that asks the 3 helpers (Q/OPS/SPY) to make recommendations and
optionally write learned hints."

- `scripts/dev/spy_extractor.py` — Conservative extractor that scans run artifacts for crib-like
tokens and writes `agents/LEARNED.md`. ELI5: "It looks for useful little hints in a run and notes
them down if they look confident."

- `kryptos/scripts/tuning/spy_eval.py` — Evaluates different SPY thresholds using labeled runs and
chooses a conservative threshold (precision-first). ELI5: "It tests how picky the extractor should
be so we trust what it finds."

- `scripts/tuning/crib_weight_sweep.py` — OPS tuning harness that sweeps crib weight parameters and
logs results. ELI5: "It tries different weights for crib signals to see which makes the system
perform better."

- `scripts/demo/run_k4_demo.py` — A small demo runner that executes the k4 pipeline and saves
artifacts for review. ELI5: "Runs a demo job and stores its outputs so you can inspect how the
system behaved."

- `scripts/lint/run_lint.ps1` — Repo lint runner that invokes ruff/flake8/pylint and simple markdown
checks. ELI5: "One script to check the code and docs for style and common problems."

- `scripts/lint/check_md.py` and `scripts/lint/reflow_md.py` — Lightweight markdown checks and
reflow utility. ELI5: "Helps keep documentation lines tidy and flags basic markdown issues."

## Where to start (practical tips)

- To run tests: run the project's test command (pytest) from the repo root.
- To run the autopilot demo: run `scripts/dev/ask_triumverate.py` (it will call OPS and optionally
SPY extractor).
- To tune SPY thresholds: use `kryptos/scripts/tuning/spy_eval.py` against labeled runs in
`artifacts/`.
- For quick code/style checks: run `./scripts/lint/run_lint.ps1` from the repo root (PowerShell).

## Notes

- This index is intentionally brief. See individual files and `docs/AUTOPILOT.md` for more detail
when needed.
- If something seems missing, search for `_run_`, `tuning`, `spy`, or `orchestrator` in the repo to
find related scripts.

## Flow and design (high level)

This section briefly explains how the main pieces coordinate during a typical autopilot/tuning run.
It's intentionally compact — think sequence steps rather than full design docs.

1. Orchestrator kicks off an OPS tuning run

- `kryptos/scripts/dev/orchestrator.py` prepares a run, records metadata (e.g., `max_delta`) and
calls OPS tuning routines.
- OPS tuning scripts (e.g., `scripts/tuning/crib_weight_sweep.py`) sweep parameters and write
artifacts under `artifacts/`.

1. Executor runs job variants

- `kryptos/src/k4/executor.py` executes multiple job variants in parallel and collects results;
tuning uses these results to score parameter combinations.

1. SPY extraction and evaluation

- `scripts/dev/spy_extractor.py` scans run artifacts for crib-like tokens and appends confident
findings to `agents/LEARNED.md`.
- `kryptos/scripts/tuning/spy_eval.py` evaluates extractor thresholds against labeled runs and
recommends a conservative `min_conf` (precision-first).

1. Autopilot driver ties them together

- `scripts/dev/ask_triumverate.py` is the high-level driver: it runs OPS tuning, obtains
`max_delta`/run metadata, computes or asks the SPY evaluator for a `min_conf`, then runs the SPY
extractor to record learned hints.

1. Demos and experiments

- `scripts/demo/run_k4_demo.py` or examples under `examples/` run the pipeline end-to-end to produce
reproducible `artifacts/` for inspection and evaluation.

Design notes (TL;DR)

- Separation of concerns: `src/` contains the runtime logic (executor, core algorithms),
`kryptos/scripts/` contains evaluation/tuning helpers, and `scripts/` contains repo-level tooling
(lint, demos, extractors).
- Conservative defaults: SPY extraction favors precision over recall; the eval harness picks
thresholds to avoid noisy learned hints.
- Reproducibility: tuning scripts write structured artifacts so the evaluator and extractor operate
on recorded runs.
