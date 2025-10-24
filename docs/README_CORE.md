# KRYPTOS — Core Documentation

Breadcrumb: Overview > Core > Detailed Reference

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
- CLI: `kryptos --help` (sections, k4-decrypt, k4-attempts, tuning-*, spy-*)
- Tuning APIs: `kryptos.k4.tuning.*` (weight sweeps, tiny param sweeps, artifact summarization)
- Tests: `tests/` (pytest / unittest)

Related documents / breadcrumbs:

- Autopilot & SPY: `docs/AUTOPILOT.md`
- Reorg policy: `docs/REORG.md`
- Top-level README: `README.md`

### Highlights

- Modular pipeline for multi-stage hypothesis testing (pipeline, composite runners)
- Scoring utilities (n-grams, chi-square, crib/positional bonuses, entropy metrics)
- Attempt logging and reproducible artifacts (CSV/JSON output under `artifacts/k4_runs/` for K4
pipeline runs)
- Tuning harness and a minimal daemon runner for automated sweeps

## Current Progress (Snapshot)

- K1–K3: unified decrypt helpers (`kryptos.k1.decrypt`, etc.) + sections mapping.
- K4: multi-stage pipeline (hill, transposition, masking, Berlin Clock) with adaptive gating &
scoring.
- Tuning: pure functions under `kryptos.k4.tuning` (`run_crib_weight_sweep`, `tiny_param_sweep`,
`pick_best_weight_from_rows`, artifact utilities) and tests.
- CLI: subcommands (sections, k4-decrypt, k4-attempts, tuning-crib-weight-sweep, tuning-pick-best,
tuning-summarize-run, tuning-tiny-param-sweep, tuning-holdout-score, tuning-report, spy-eval, spy-
extract).
- Artifact utilities: consolidated under `kryptos.k4.tuning.artifacts` replacing legacy summarizer
scripts.

## Features (summary)

- Hill cipher solving (2x2, 3x3) with pruning and crib support
- Columnar & route transposition search, including multi-crib positional anchoring
- Masking/null removal stage and Berlin Clock shift hypotheses
- Composite pipeline orchestration, attempt logging, and CSV/JSON artifacts
- Scoring utilities: n-grams, chi-square, crib & positional bonuses, entropy and wordlist heuristics
    - Positional letter deviation metric (periodic bucket chi-square -> normalized) rewarding
        balanced per-position distributions (mitigates false positives from structured transpositions)
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

1. Run the test suite:

```bash
pytest -q  # or: python -m unittest discover -s tests
```

1. Decrypt sections via CLI:

```bash
kryptos sections
kryptos k4-decrypt --cipher data/k4_cipher.txt --limit 25 --adaptive --report
```

1. Programmatic K4 sample:

```python
from kryptos.k4 import decrypt_best

result = decrypt_best("OBKRUOXOGHULBSOLIFB", limit=25, adaptive=True, report=True)
print(result.plaintext, result.score)
```

## CLI Subcommands & Usage

Run `kryptos --help` for full details. Core workflows:

### Sections Listing

```bash
kryptos sections
```

### K4 Decrypt

```bash
kryptos k4-decrypt --cipher data/k4_cipher.txt --limit 40 --adaptive --report
```

Writes artifacts (candidates, attempts) when `--report` is used; prints JSON (plaintext, score,
lineage).

### Attempt Log Flush

```bash
kryptos k4-attempts --label k4
```

Persist in-memory attempt logs to `artifacts/attempts_<label>_<timestamp>.json`.

### Crib Weight Sweep

```bash
kryptos tuning-crib-weight-sweep --weights 0.25,0.5,1.0,1.5 --cribs BERLIN,CLOCK --samples data/holdout_samples.txt --json
```

Outputs per-weight delta rows (baseline vs with-crib scoring). Omit `--json` for human-readable
lines.

### Pick Best Weight

```bash
kryptos tuning-pick-best --csv artifacts/tuning_runs/run_20251023T120000/crib_weight_sweep.csv
```

Returns `{ "best_weight": <float> }` based on the maximum mean delta.

### Summarize Run

```bash
kryptos tuning-summarize-run --run-dir artifacts/tuning_runs/run_20251023T120000
```

Generates cleaned summary + crib hit counts; skip writing artifacts with `--no-write`.

### Tiny Param Sweep

```bash
kryptos tuning-tiny-param-sweep
```

Deterministic miniature sweep (debug/demo).

### Holdout Score

```bash
kryptos tuning-holdout-score --weight 1.0 --no-write
```

Computes mean delta for holdout sentences at the chosen crib weight; omit `--no-write` to write CSV.

### SPY Evaluation

```bash
kryptos spy-eval --labels data/spy_eval_labels.csv --runs artifacts/tuning_runs --thresholds 0.0,0.25,0.5,0.75
```

Prints precision/recall/F1 metrics and best threshold.

### SPY Extraction

```bash
kryptos spy-extract --runs artifacts/tuning_runs --min-conf 0.30
```

Outputs tokens per run meeting confidence threshold.

### End‑to‑End Example Chain

```bash
kryptos k4-decrypt --cipher data/k4_cipher.txt --limit 50 --adaptive --report > decrypt.json
kryptos tuning-crib-weight-sweep --weights 0.5,1.0,1.5 --cribs BERLIN,CLOCK --json > sweep.json
kryptos tuning-pick-best --csv artifacts/tuning_runs/run_*/crib_weight_sweep.csv > best_weight.json
kryptos tuning-holdout-score --weight 1.0 --no-write > holdout.json
kryptos spy-eval --labels data/spy_eval_labels.csv --runs artifacts/tuning_runs --thresholds 0.0,0.25,0.5,0.75 > spy_eval.json
kryptos spy-extract --runs artifacts/tuning_runs --min-conf 0.25 > spy_tokens.json
```

Sequence: decrypt → sweep → select weight → validate holdout → spy evaluate → spy extract.

## Tuning & Artifact Post‑Processing

Prefer direct APIs over scripts:

- Weight sweep: `from kryptos.k4.tuning import run_crib_weight_sweep`
- Pick best weight: `from kryptos.k4.tuning import pick_best_weight_from_rows`
- Tiny param sweep: `from kryptos.k4.tuning import tiny_param_sweep`
- Artifact cleaning & summary: `from kryptos.k4.tuning.artifacts import end_to_end_process`
- Reporting utilities (condensed & top candidates): `from kryptos.k4.report import
write_condensed_report, write_top_candidates_markdown`

### Generating Condensed & Top Candidate Reports

After running a tuning sweep (e.g. `tuning-crib-weight-sweep` followed by `tuning-pick-best` /
`tuning-summarize-run`) you can produce normalized summary artifacts:

```python
from pathlib import Path
from kryptos.k4.report import write_condensed_report, write_top_candidates_markdown

run_dir = Path("artifacts/tuning_runs/run_20251023T071230")  # directory containing per-weight detail CSVs

# 1. Create condensed_report.csv (one row per weight with top delta & snippet)
csv_path = write_condensed_report(run_dir)
print("Condensed CSV written:", csv_path)

# 2. Generate top_candidates.md (ranked markdown list)
md_path = write_top_candidates_markdown(run_dir, limit=7)
print("Top candidates markdown:", md_path)
```

Optional enrichment: if a learned SPY phrases file exists (e.g. `agents/LEARNED.md`) matching
phrases will be annotated inline in the markdown output.

CLI integration candidate (future): a `tuning-report` subcommand could wrap both calls. For now
prefer the direct Python API for batching inside notebooks or scripts.

Example weight sweep:

```python
from pathlib import Path
from kryptos.k4.tuning import run_crib_weight_sweep

rows = run_crib_weight_sweep(weights=[0.5, 1.0, 1.5], run_dir=Path('artifacts/tuning_runs'))
for r in rows:
    print(r.weight, r.score_delta)
```

Legacy wrapper scripts have been removed; all functionality now lives in the CLI subcommands and
direct APIs under `kryptos.k4.tuning.*` and `kryptos.spy` (extraction & phrase aggregation).

### Positional Letter Deviation Metric

Added in October 2025 to improve ranking stability.

Rationale: Plain English tends not to cluster common letters in fixed periodic positions. After
certain transposition or masking operations, artificial patterns emerge (e.g., vowels
disproportionately in one column modulo period). The positional metric partitions text into `period`
buckets by index modulo period (default 5) and computes a chi-square divergence per bucket against
English letter frequencies. Each bucket contributes `1/(1+chi)`; the final score is the mean across
non-empty buckets, yielding a value in [0,1]. A higher score indicates more even positional
distribution. The extended combined score applies a modest weight so n-gram statistics remain
primary.

Usage:

```python
from kryptos.k4.scoring import positional_letter_deviation_score, combined_plaintext_score_extended
val = positional_letter_deviation_score(candidate_plaintext)
rank = combined_plaintext_score_extended(candidate_plaintext)
```

Interpretation guidelines:

- <0.20: likely random/structured artifact
- 0.20–0.45: weak candidate
- 0.45–0.70: plausible English-like distribution
- >0.70: strong positional balance (inspect other metrics)


The thresholds are heuristic and may shift after larger evaluation sets.

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

--- Last updated: 2025-10-23T23:50Z (artifact path consolidation + positional metric)
