# KRYPTOS

Inspired by *The Unexplained* with William Shatner, I set out to solve Kryptos using Python! This project focuses on
implementing cryptographic techniques, specifically the Vigenère cipher and structural transposition analysis, to
decrypt the famous Kryptos sculpture.

## TL;DR

This Kryptos repository is a research toolkit for exploring layered cipher hypotheses (Vigenère, Hill, transposition,
masking, and related hybrids) with an emphasis on reproducible pipelines and scoring heuristics.

Related documents / quick links:

- K4 Master Plan: `docs/K4_MASTER_PLAN.md`
- Agents Architecture: `docs/AGENTS_ARCHITECTURE.md`
- API Reference: `docs/API_REFERENCE.md`
- Technical debt & roadmap: `docs/TECHDEBT.md`
- Changelog: `docs/CHANGELOG.md`

**K4 is the last unsolved piece of a CIA sculpture puzzle.** Imagine a secret message carved in copper that nobody has
cracked in 30+ years. We're using Python to systematically try every reasonable decryption method – techniques that
cryptanalysts may have attempted manually but couldn't exhaustively explore. Our approach combines automated testing
with intelligent scoring to measure how "English-like" each result appears:

1. **Hill Cipher** - Matrix-based substitution where letters become numbers, transform through matrix multiplication,
then convert back 2. **Transposition** - Systematic letter rearrangement (write in columns, read in rows, or more
complex patterns) 3. **Masking** - Identifying and removing dummy letters that serve as padding or obfuscation 4.
**Berlin Clock** - Using the iconic clock's binary time pattern as a cryptographic key 5. **Combo Attacks** - Chaining
multiple methods together (K4 likely uses 2-3 techniques layered in sequence)

We evaluate candidates using linguistic patterns – common letter pairs, trigram frequencies, real word detection – to
identify promising decryptions. Think of it as trying thousands of lock combinations, but guided by cryptanalytic
intuition rather than brute force. After all, humans design puzzles with intention, not randomness!

## Current Progress

### ✅ K1: "Between subtle shading and the absence of light lies the nuance of iqlusion"

- **Status**: Solved.
- **Details**: Decrypted via Vigenère using keyed alphabet `KRYPTOSABCDEFGHIJLMNQUVWXZ`. Intentional
misspelling preserved: `IQLUSION`.

### ✅ K2: "It was totally invisible. How's that possible?"

- **Status**: Solved.
- **Details**: Vigenère (key: `ABSCISSA`). Includes embedded null/structural padding (`S`) for
historical alignment. Contains geospatial coordinates and narrative text.

### ✅ K3: "Slowly, desperately slowly, the remains of passage debris..."

- **Status**: Solved (double rotational transposition method).
- **Details**: Implemented the documented 24×14 grid → 90° rotation → reshape to 8-column grid →
second 90° rotation. Resulting plaintext matches known solution including deliberate misspelling `DESPARATLY` (analogous
to `IQLUSION` in K1).

### ℹ️ K4: The unsolved mystery

- **Status**: Unsolved.
- **Implemented Toolkit**: See K4 modules below (Hill cipher exploration, scoring, constraint
pipeline, multi-stage fusion).
- **Latest Additions**: Multi-crib positional transposition stage, attempt logging & persistence,
advanced linguistic metrics, 3x3 Hill key pruning (partial_len/partial_min tunable in hill constraint stage).

## Deliberate Misspellings / Anomalies

| Section | Cipher Plaintext Form | Expected Modern Spelling | Note |
|---------|-----------------------|---------------------------|------|
| K1      | IQLUSION              | ILLUSION                  | Intentional artistic alteration |
| K3      | DESPARATLY            | DESPERATELY               | Preserved from sculpture transcription |

### K2 Structural Padding

K2 contains systematic X (and some Y) insertions serving as alignment/null separators rather than mistakes. They should
be treated as structural artifacts when analyzing pattern continuity or constructing transposition hypotheses.

## Features

- **Vigenère Cipher** with keyed alphabet handling ([learn more](https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher))
- **K3 Double Rotational Transposition** implementation ([learn more](https://en.wikipedia.org/wiki/Transposition_cipher))
- **Config-driven** (`config/config.json`) for ciphertexts, keys, and parameters ([learn more](https://en.wikipedia.org/wiki/Configuration_file))
- **Test Suite** validating K1–K3 solutions ([learn more](https://en.wikipedia.org/wiki/Unit_testing))
- **Frequency, n-gram, and crib-based scoring utilities** ([learn more](https://en.wikipedia.org/wiki/Frequency_analysis) | [n-grams](https://en.wikipedia.org/wiki/N-gram) | [cribs](https://en.wikipedia.org/wiki/Crib_(cryptanalysis)))
- **Hill cipher (2x2 & 3x3)** encryption/decryption + key solving from crib segments ([learn more](https://en.wikipedia.org/wiki/Hill_cipher))
- **3x3 Hill assembly variants & pruning** (row/col/diagonal constructions + partial score pruning) ([learn more](https://en.wikipedia.org/wiki/Hill_cipher))
- **Constrained Hill key derivation** from `BERLIN` / `CLOCK` cribs (single & pairwise) with caching ([learn more](https://en.wikipedia.org/wiki/Crib_(cryptanalysis)))
- **Modular pipeline architecture** (stage factories for all hypothesis families) ([learn more](https://en.wikipedia.org/wiki/Pipeline_(computing)))
- **Columnar transposition** search (partial-score pruning) and crib-constrained inversion utilities ([learn more](https://en.wikipedia.org/wiki/Transposition_cipher#Columnar_transposition))
- **Multi-crib positional transposition stage** (anchors multiple cribs simultaneously) ([learn more](https://en.wikipedia.org/wiki/Transposition_cipher))
- **Adaptive transposition search** (`make_transposition_adaptive_stage`) with sampling prefix caching heuristics ([learn more](https://en.wikipedia.org/wiki/Heuristic))
- **Masking/null-removal stage** exploring structural padding elimination variants ([learn more](https://en.wikipedia.org/wiki/Null_cipher))
- **Berlin Clock shift hypothesis** (full lamp state enumeration + dual-direction application) ([learn more](https://en.wikipedia.org/wiki/Mengenlehreuhr))
- **Weighted multi-stage fusion utilities** (`normalize_scores`, `fuse_scores_weighted`) for score aggregation ([learn more](https://en.wikipedia.org/wiki/Ensemble_learning))
- **High-quality quadgram table** auto-loaded when present (`data/quadgrams_high_quality.tsv`) ([learn more](https://en.wikipedia.org/wiki/N-gram))
- **Advanced linguistic metrics** (wordlist hit rate, trigram entropy, bigram gap variance, entropy, repeating bigram fraction) ([learn more](https://en.wikipedia.org/wiki/Entropy_(information_theory)))
- **Memoized scoring** (LRU cache for repeated candidate evaluation) ([learn more](https://en.wikipedia.org/wiki/Cache_(computing)))
- **Pipeline profiling** (per-stage duration metadata) ([learn more](https://en.wikipedia.org/wiki/Profiling_(computer_programming)))
- **Transformation trace & lineage** (each candidate records stage + transformation chain) ([learn more](https://en.wikipedia.org/wiki/Reproducibility))
- **Attempt logging & persistence** (Hill, Clock, Transposition permutations → timestamped JSON) ([learn more](https://en.wikipedia.org/wiki/Logging))
- **Candidate reporting artifacts** (JSON + optional CSV summaries) ([learn more](https://en.wikipedia.org/wiki/Reproducibility))
- **Adaptive fusion weighting** (optional `adaptive=True` in composite run) leveraging wordlist hit rate & trigram
entropy heuristics

## K4 Analysis Toolkit (New / Updated Modules)

Located under `kryptos/k4/` (migrated from `src/k4/`):

Details and module-level examples for K4 have been moved to `docs/K4_MASTER_PLAN.md` for strategic planning and
`docs/API_REFERENCE.md` for code-level API documentation.

## Roadmap & Technical Debt

See `docs/TECHDEBT.md` for current prioritized work and `docs/K4_MASTER_PLAN.md` for comprehensive strategy and solver-
specific exploration notes.

## CLI Usage Examples

The `kryptos` CLI aggregates decryption, tuning, and SPY analysis workflows. Use `kryptos --help` to view all
subcommands. Below are common end‑to‑end examples.

### List Sections

```bash
kryptos sections
```

### Composite K4 Decrypt

Decrypt K4 ciphertext from a file, limit candidates, enable adaptive fusion, and write artifacts:

```bash
kryptos k4-decrypt --cipher data/k4_cipher.txt --limit 40 --adaptive --report
```

Outputs JSON containing top plaintext, score, lineage, and artifact paths. Artifacts (candidates, attempts) are written
under `artifacts/` when `--report` is used.

### Persist Attempt Logs

Flush in-memory attempt logs to a timestamped JSON file:

```bash
kryptos k4-attempts --label k4
```

### Tuning: Crib Weight Sweep

Run a sweep across candidate weights for optional cribs and samples:

```bash
kryptos tuning-crib-weight-sweep --weights 0.25,0.5,1.0,1.5 \
  --cribs BERLIN,CLOCK \
  --samples data/holdout_samples.txt --json
```

Emits JSON rows: each weight with baseline vs with‑crib deltas.

### Tuning: Pick Best Weight

Select best performing weight from a prior sweep CSV:

```bash
kryptos tuning-pick-best --csv artifacts/tuning_runs/run_20251023T120000/crib_weight_sweep.csv
```

Returns `{ "best_weight": <float> }`.

### Tuning: Summarize Run

Clean and summarize a tuning run directory (crib hit counts, aggregates). Writes artifacts unless `--no-write` is
provided:

```bash
kryptos tuning-summarize-run --run-dir artifacts/tuning_runs/run_20251023T120000
```

### Tuning: Tiny Param Sweep

Deterministic miniature parameter sweep (debug/demo):

```bash
kryptos tuning-tiny-param-sweep
```

### Tuning: Holdout Score

Compute mean scoring deltas for a chosen crib weight over representative holdout samples:

```bash
kryptos tuning-holdout-score --weight 1.25 --out artifacts/reports/holdout.csv
```

Use `--no-write` to skip CSV output and only print JSON.

### SPY Evaluation

Evaluate extraction confidence thresholds against labeled runs:

```bash
kryptos spy-eval --labels data/spy_eval_labels.csv --runs artifacts/tuning_runs --thresholds 0.10,0.25,0.40,0.55
```

Outputs precision/recall/F1 per threshold plus `best_threshold`.

### SPY Extraction

Extract SPY tokens at minimum confidence from all run_* directories:

```bash
kryptos spy-extract --runs artifacts/tuning_runs --min-conf 0.30
```

Returns mapping of run directory → extracted tokens.

### End‑to‑End Flow (Example)

```bash
cp data/k4_cipher.txt work_cipher.txt
kryptos k4-decrypt --cipher work_cipher.txt --limit 50 --adaptive --report > decrypt.json
kryptos k4-attempts --label k4
kryptos tuning-crib-weight-sweep --weights 0.5,1.0,1.5 --cribs BERLIN,CLOCK --json > sweep.json
# Assume sweep CSV written separately; pick best
kryptos tuning-pick-best --csv artifacts/tuning_runs/run_*/crib_weight_sweep.csv
kryptos tuning-holdout-score --weight 1.0 --no-write > holdout.json
kryptos spy-eval --labels data/spy_eval_labels.csv --runs artifacts/tuning_runs --thresholds 0.0,0.25,0.5,0.75 > spy_eval.json
kryptos spy-extract --runs artifacts/tuning_runs --min-conf 0.25 > spy_tokens.json
```

You now have: decrypt.json, sweep.json, holdout.json, spy_eval.json, spy_tokens.json summarizing the pipeline, tuning,
and extraction outputs.

## Recent Changes

- **2025-10-24**: Fixed CI failures by correcting `.gitignore` pattern - added agents source code (SPY, OPS, Q agents)
that was previously blocked
- **2025-10-22**: Added offline autopilot flow (Q/OPS/SPY), conservative SPY extractor with evaluation harness, demo
smoke CI and packaging improvements. See `docs/AUTOPILOT.md` for details

## Autopilot (Q / OPS / SPY) Summary

The repository includes an offline autopilot flow (Q / OPS / SPY) to recommend and execute safe tuning and extraction
steps. `ask_triumverate.py` implements a lightweight driver that can run a deterministic OPS tuning sweep and then
invoke the conservative SPY extractor. If `SPY_MIN_CONF` is not set, the autopilot will compute a conservative threshold
using the evaluation harness; it falls back to `0.25` when no labeled runs are available. See
`docs/AGENTS_ARCHITECTURE.md` for full details and CLI examples.

## Contributing

Contribution guidelines moved to `CONTRIBUTING.md` → [Contributing Guide](./CONTRIBUTING.md).

## Scoring Metrics Snapshot

Use `baseline_stats(text)` to inspect metrics including advanced linguistic features.

## Data Sources

Frequency & n-gram data in `data/` (TSV). High-quality quadgrams loaded automatically if `quadgrams_high_quality.tsv`
exists. Fallback unigram distribution used if files absent.

## License

See `LICENSE`.

## Other Documentation

- `docs/K4_MASTER_PLAN.md` — Complete K4 strategy, hypothesis pipeline, and roadmap
- `docs/AGENTS_ARCHITECTURE.md` — SPY/OPS/Q agent design and implementation
- `docs/API_REFERENCE.md` — Python API and CLI command reference
- `docs/TECHDEBT.md` — Technical debt tracking and cleanup status

## Code Examples

If you prefer to run an example pipeline, use the example script:

```bash
python -m kryptos.examples.sections_demo
```

Or invoke the composite K4 search directly:

```python
from kryptos.k4 import decrypt_best
result = decrypt_best(K4_CIPHERTEXT, limit=40, adaptive=True)
print(result.plaintext, result.score)
```

Minimal lower-level pipeline construction (for experimentation):

```python
from kryptos.k4.pipeline import (
  make_hill_constraint_stage,
  make_masking_stage,
  make_transposition_adaptive_stage,
  make_transposition_stage,
  Pipeline,
)
from kryptos.k4.composite import run_composite_pipeline

stages = [
  make_masking_stage(limit=20),
  make_transposition_adaptive_stage(),
  make_transposition_stage(),
  make_hill_constraint_stage(partial_len=50, partial_min=-850.0),
]
out = run_composite_pipeline(K4_CIPHERTEXT, stages, report=False, limit=30, adaptive=True)
print(out['aggregated'][0]['text'])
```

### Artifact Layout

Pipeline-generated run directories may be grouped under an optional subdirectory for clarity:

```text
artifacts/
  k4_runs/          # pipeline executor runs (run_YYYYMMDDTHHMMSS when artifact_run_subdir is set)
  tuning_runs/      # tuning/daemon sweep runs (run_*)
  reports/          # reporting outputs (top candidates, aggregated attempts) (now under artifacts/)
  decisions/        # autopilot / plan artifacts (JSON summaries)
  logs/             # runtime / diagnostic logs
  output/           # miscellaneous generated outputs / crib extracts
```

Enable grouping by passing `artifact_run_subdir="k4_runs"` to `PipelineConfig`. If you have legacy `artifacts/run_*`
directories from older versions, migrate them safely with:

```bash
python scripts/dev/migrate_run_artifacts.py --dry-run
python scripts/dev/migrate_run_artifacts.py
```

If no legacy directories are present, the script reports that there is nothing to move.

## References & Research

- [UCSD Crypto Project by Karl Wang](https://mathweb.ucsd.edu/~crypto/Projects/KarlWang/index2.html)
- [Kryptos Wiki](https://en.wikipedia.org/wiki/Kryptos)
- [Vigenère Cipher Explanation](https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher)
- [Kryptosfan Blog](https://kryptosfan.wordpress.com/k3/k3-solution-3/)
- [Berlin Clock](https://en.wikipedia.org/wiki/Mengenlehreuhr)
- [Hill Cipher](https://en.wikipedia.org/wiki/Hill_cipher)
- [Index of Coincidence](https://en.wikipedia.org/wiki/Index_of_coincidence)
- [Entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory))
