# Project index (10k ft view)

This file gives a very short, high-level overview of the repository by top-level directories and the core Python scripts
you will likely use. Each entry has an ELI5 sentence describing what it does.

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

## Package layout details (sections & utilities)

- `kryptos/k1/`, `kryptos/k2/`, `kryptos/k3/` — Uniform wrappers exposing `decrypt(ciphertext: str,
**opts)` for solved sections (Vigenère for K1/K2, double rotational transposition for K3). (Implemented)
- `kryptos/k4/` — Canonical K4 pipeline (executor, scoring, hill/crib logic, transposition, masking,
clock enumeration). Change runtime behavior or add solver variants here.
- `kryptos/ciphers.py` — Shared primitive cipher functions (Vigenère, rotational transposition,
Polybius). Will remain as primitives after section wrappers exist.
- `kryptos/analysis.py` — Generic frequency and crib checking utilities used by examples and
reporting.
- `kryptos/reporting.py` — Canonical reporting (frequency chart + crib summary) replacing legacy
`report.py`.
- `kryptos/k4/scoring.py` — Extended scoring metrics (ngrams, positional cribs, linguistic
features).

### SPY & Tuning Consolidation

SPY extraction and aggregation now live under the `kryptos.spy` namespace (e.g. `kryptos.spy.extractor.extract`,
`kryptos.spy.aggregate_phrases`). Legacy script wrappers are deprecated and slated for removal after a short grace
period. Tuning harnesses are consolidated under `kryptos.k4.tuning.*` (weight sweeps, tiny deterministic sweeps,
artifact summarization). Use package APIs or CLI subcommands instead of calling scripts directly.

## Core python modules & scripts (ELI5)

- `kryptos/k4/executor.py` — Runs K4 pipeline variants in parallel and collects results. ELI5: "It
tries different ways at once and gathers the outputs."

- `kryptos/scripts/dev/orchestrator.py` — Orchestrates OPS (tuning) runs and stores run metadata.
ELI5: "It runs tuning experiments and remembers what happened so we can learn from it."

- `scripts/dev/ask_triumverate.py` — Autopilot driver (OPS + SPY). ELI5: "Asks the three helpers to
make recommendations and logs useful hints."

- `kryptos/spy/extractor.py` — Conservative SPY extractor scanning run artifacts for crib-like
tokens and writing learned hints. ELI5: "It finds small quoted bits that look like real words and keeps only the
trustworthy ones."

- `kryptos/k4/tuning/spy_eval.py` — Evaluates SPY thresholds against labeled runs and selects a
precision-first threshold. ELI5: "It decides how strict the extractor should be so we only keep good hints."

- `kryptos.k4.tuning.run_crib_weight_sweep` — Programmatic OPS tuning harness that sweeps crib
weight parameters and returns structured rows (wrapper script still exists). ELI5: "It tries different weights for crib
signals to see which makes the system perform better."

- (Demo) `scripts/demo/run_k4_demo.py` — Small demo runner executing the K4 pipeline and saving
artifacts (migrating to a CLI example). ELI5: "Runs a short pipeline trial and saves what happened."

- `scripts/lint/run_lint.ps1` — Repo lint runner that invokes ruff/flake8/pylint and simple markdown
checks. ELI5: "One script to check the code and docs for style and common problems."

- `scripts/lint/check_md.py` and `scripts/lint/reflow_md.py` — Lightweight markdown checks and
reflow utility. ELI5: "Helps keep documentation lines tidy and flags basic markdown issues."

## Where to start (practical tips)

- To run tests: run the project's test command (pytest) from the repo root.
- To run the autopilot demo: run `scripts/dev/ask_triumverate.py` (OPS + SPY), or forthcoming CLI
`kryptos autopilot`.
- To tune SPY thresholds: use `kryptos/k4/tuning/spy_eval.py` programmatically or CLI `kryptos spy-
eval`.
- For quick code/style checks: run `./scripts/lint/run_lint.ps1` from the repo root (PowerShell).

## Notes

- This index is intentionally brief. See individual files and `docs/AUTOPILOT.md` for more detail
when needed.
- If something seems missing, search for `_run_`, `tuning`, `spy`, or `orchestrator` in the repo to
find related scripts.

## Flow and design (high level)

This section briefly explains how the main pieces coordinate during a typical autopilot/tuning run. It's intentionally
compact — think sequence steps rather than full design docs.

1. Orchestrator kicks off an OPS tuning run

- `kryptos/scripts/dev/orchestrator.py` prepares a run, records metadata (e.g., `max_delta`) and
calls OPS tuning routines.
- OPS tuning now uses package APIs (e.g., `kryptos.k4.tuning.run_crib_weight_sweep`) to sweep
parameters and then persists artifacts under `artifacts/` (script wrappers will migrate to CLI subcommands).

1. Executor runs job variants

- `kryptos/k4/executor.py` executes multiple job variants in parallel and collects results;
tuning uses these results to score parameter combinations.

1. SPY extraction and evaluation

- `kryptos/spy/extractor.py` scans run artifacts (CSV attempts) for crib-like tokens and appends
confident findings to learned hints.
- `kryptos/k4/tuning/spy_eval.py` evaluates thresholds against labeled runs and recommends a
precision-first `min_conf`.

1. Autopilot driver ties them together

- `scripts/dev/ask_triumverate.py` is the high-level driver: it runs OPS tuning, obtains
`max_delta`/run metadata, computes or asks the SPY evaluator for a `min_conf`, then runs the SPY extractor to record
learned hints.

1. Demos and experiments

- Demo examples under `scripts/demo/` or `examples/` run the pipeline end-to-end producing
reproducible artifacts under `artifacts/k4_runs/`.

Design notes (TL;DR)

- Separation of concerns: `kryptos/` holds all reusable logic; `scripts/` are wrappers / tooling;
`examples/` show minimal usage.
- Conservative defaults: SPY extraction favors precision over recall; evaluation picks thresholds to
avoid noisy hints.
- Reproducibility: structured artifacts (CSV/JSON) record configuration & scores for post-run
analysis.

### Sections & Docs Status

- Section packages (`kryptos/k1`, `kryptos/k2`, `kryptos/k3`) implemented; `kryptos/sections.py`
mapping available (K4 included via `decrypt_best`).
- Example orchestration now via the CLI (`kryptos sections`, `kryptos k4-decrypt ...`); several
obsolete demo scripts have been removed or migrated.
- `docs/SECTIONS.md` documents the unified API surface.
- Legacy `src/__init__.py` shim removed; explicit imports only.

--- Last updated: 2025-10-23T23:40Z (spy namespace + artifact path consolidation + tuning docs refresh)
