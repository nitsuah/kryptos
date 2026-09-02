# KRYPTOS

[![CI fast](https://github.com/nitsuah/kryptos/actions/workflows/ci-fast.yml/badge.svg)](https://github.com/nitsuah/kryptos/actions)

[![CI (smoke)](https://github.com/nitsuah/kryptos/actions/workflows/demo-smoke.yml/badge.svg)](https://github.com/nitsuah/kryptos/actions)

[![CI (slow)](https://github.com/nitsuah/kryptos/actions/workflows/ci-slow.yml/badge.svg)](https://github.com/nitsuah/kryptos/actions)

Inspired by *The Unexplained* with William Shatner, I set out to solve Kryptos using Python! This project focuses on
implementing cryptographic techniques, specifically the Vigenère cipher and structural transposition analysis, to
decrypt the famous Kryptos sculpture.

## TL;DR

This Kryptos repository is a research toolkit for exploring layered cipher hypotheses (Vigenère, Hill, transposition,
masking, and related hybrids) with an emphasis on reproducible pipelines and scoring heuristics.

## Autonomous Quickstart

Run a standard autonomous cycle:

```bash
python -m kryptos.cli.main autonomous --max-hours 24 --cycle-interval 5
```

Community standards (contributing, code of conduct, security) are centralized in [nitsuah/.github](https://github.com/nitsuah/.github).


## Repository Structure

The repository is organized for clarity, reproducibility, and future migration to a database-backed architecture. Key folders and files:

- **artifacts/**: Runtime outputs, logs, reports, and temporary artifacts (not git-tracked; will eventually migrate to DB, but required for now)
- **config/**: Configuration files (config.json, subfolders for meta_coordinator, ops_strategy, etc.). Consider moving root-level config/test/lint files here if tool support allows.
- **data/**: Static resources for scoring and analysis (n-gram tables, ciphertext, etc.). Will be replaced by DB in 2027.
- **docs/**: All documentation, analysis, reference, and archive. May migrate to DB for dynamic docs in the future, but static docs remain valuable.
- **scripts/**: Utility scripts for linting, cleanup, and testing. To be audited and centralized for reusability.
- **src/**: Main source code. To be reorganized after other cleanup.
- **tests/**: Test suite. Reorganization planned after repo cleanup.
- **Root files**: Project metadata, requirements, Docker, and key documentation. Some config/test/lint files may move to config/ if supported.

**Planned migrations:**
- Data and artifacts will move to a database as part of 2027 work.
- Documentation may be dynamically served from a DB in the future.


Kryptos is a long-horizon cryptanalysis program, not a promise machine.

### What We Optimize For

1. **Truth over narrative**
  - We prefer uncomfortable results over comforting stories.
  - "Did it improve validated signal?" is the first question.

1. **Reproducibility over heroics**
  - Every claim should be backed by deterministic commands, artifacts, and provenance.
  - If a result cannot be reproduced, it does not count.

1. **Known-cipher reliability before unknown-cipher ambition**
  - K1-K3 performance is the quality gate for K4 campaigns.
  - We do not scale strategies that fail on validated baselines.

1. **AI as amplifier, not oracle**
  - AI accelerates hypothesis generation, coding, and experiment operations.
  - AI output is always treated as a proposal that must survive measurement.

1. **Small, compounding iterations**
  - Prefer narrow changes with clear acceptance criteria.
  - Ship improvements that make the next experiment faster and cleaner.

1. **Kill weak hypotheses quickly**
  - Retire approaches that repeatedly underperform controls.
  - Preserve a decision trail so retired ideas are not re-litigated without new evidence.

### Operating Commitments

- Every significant change includes a validation path (tests, benchmark deltas, or reproducible artifact evidence).
- Every campaign run writes traceable outputs under `artifacts/`.
- Every roadmap claim ties to measurable criteria, not adjectives.
- Every phase includes at least one explicit "stop doing" decision.

For governance and maintenance policy, see `docs/GOVERN.md` (with historical references in `docs/archive/`).

## docs

All Related documents / quick links can generally be found in `docs/`:

- Docs index: `docs/INDEX.md`
- Roadmap: `docs/ROADMAP.md`
- Tasks: `docs/TASKS.md`
- Agents Architecture: `docs/reference/AGENTS_ARCHITECTURE.md`
- API Reference: `docs/reference/API_REFERENCE.md`
- Autonomous System: `docs/reference/AUTONOMOUS_SYSTEM.md`
- Changelog: `docs/CHANGELOG.md`

**K4 is the last unsolved piece of a CIA sculpture puzzle.** Imagine a secret message carved in copper that nobody has
cracked in 30+ years. We're using Python to systematically try every reasonable decryption method – techniques that
crypto analysts may have attempted manually but couldn't exhaustively explore. Our approach combines automated testing
with intelligent scoring to measure how "English-like" each result appears:

1. **Hill Cipher** - Matrix-based substitution where letters become numbers, transform through matrix multiplication,
then convert back.

1. **Transposition** - Systematic letter rearrangement (write in columns, read in rows, or more complex patterns)

1. **Masking** - Identifying and removing dummy letters that serve as padding or obfuscation

1. **Berlin Clock** - Using the iconic clock's binary time pattern as a cryptographic key

1. **Combo Attacks** - Chaining multiple methods together (K4 likely uses 2-3 techniques layered in sequence)

  - We evaluate candidates using linguistic patterns – common letter pairs, trigram frequencies, real word detection – to identify promising decryptions. Think of it as trying thousands of lock combinations, but guided by cryptanalytic intuition rather than brute force. After all, humans design puzzles with intention, not randomness!

## Recent Updates

### K4 Physical/Geometric Pivot + Phase 7 Complete (August–September 2026)

**All 13 code-executable items of the "Physical/Geometric Pivot" research brief (of 15 — items 10-11 were historical/archival research, satisfied via sourced documentation rather than code), plus a follow-on Phase 7, implemented and executed against real K4 — every result null (2.6M+ candidates total across the two phases):**

- 24-column geometric permutation front-end (20 fill-orders/routes) composed with reflections (both shape-preserving *and* shape-changing transpose families), rotations, and remainder modes, combined with the 108-route physical tableau — up to 414,720 candidates per run
- Precise WGS84 geodesy (`geographiclib`) computing the Mengenlehreuhr → Weltzeituhr bearing at both the clock's current and 1990/Sanborn-era locations (both land within 1.5–3.3° of exact ENE)
- November 9 1989 (Berlin Wall fall) added as a sourced priority clock state
- Myszkowski transposition, Trifid cipher, and a simulated-annealing substitution-key search behind the geometric front-end
- P2 shadow/null masking, P5's 2-crib relaxed gate (against both transposition families), and P6's K3-running-key attack — all wired in earlier phases but executed for real for the first time
- A re-examined, computationally-modeled "shadow of the word" hypothesis: the World Clock topper's rotation (verified 1 rev/min, mechanically deterministic) and real solar position at CIA HQ — both tractable without physical site access, correcting an earlier "out of scope" call
- World Clock city-list keyword research, cross-vector consensus scoring across every null-result artifact, and a scheduled overnight full-sweep runner
- New dashboard Pivot Status panel showing the hypothesis graph and geodesy figures

**What's left needs new source material, not new code** — a complete World Clock city list, a sub-minute-precision historical timestamp, or photographic documentation of the Kryptos compass rose's exact bearing. See `docs/ROADMAP.md`'s "Ideas — not yet scheduled" section.

---

### K4 Phase 2 Frontier Open (August 2026)

**P1–P7 attacks implemented, tested, and live in Docker dashboard:**

- P1: 3-layer composite (keyed-alphabet → Berlin Clock Vigenère → columnar transposition), CIA timestamps priority-tested
- P2: 8 shadow/null masking variants (stride-2/3/4, block-8, clock-shadow×2, arc-fraction×2)
- P3/P4: K2 coordinate digits as HH:MM clock times + ±6h timezone offsets (10 states)
- P5: 2-crib soft filter for near-miss surfacing (BERLIN+CLOCK threshold=2)
- P6: K3 plaintext running key (4 variants)
- P7: Gronsfeld cipher with K2 coordinate digit keys

All null results. Keystream analysis confirms Berlin Clock alone is insufficient (shifts reach 17, 20, 25 — exceeding max row output of 11). Phase 2 opens 10 new directions: alternative alphabet keywords (SANBORN, SCHEIDT, SHADOW), coordinate exploitation (magnetic declination, CIA→Berlin bearing), and candidate corpus mining.

**Live dashboard**: `docker compose -f config/docker-compose.yml up -d` → http://localhost:8000 → K4 Dashboard — live Berlin Clock, K4 cipher with crib highlights, Frontier queue with Run Attack buttons.

---

### Phase 6 Comprehensive Cleanup (October 2025)

**Code Optimization**: Removed **3,554 lines** of unnecessary code while preserving all functionality

- Automated cleanup: -2,877 lines (docstrings, comments, verbose logging) across 65 files
- Deprecated code removal: -677 lines (unused configs, obsolete tests)
- Fixed K3 ciphertext correction (336 chars)

**Test Suite Optimization**: 633 collected (**631 fast-selected** / 10 slow tests gated by `KRYPTOS_RUN_SLOW_MONTE_CARLO` / 2 deselected in fast run mode)

- Added `@pytest.mark.slow` to long-running statistical validation tests
- Fast iteration: `pytest -m "not slow"` currently runs 631 tests in ~45-60s on a typical dev machine
- Slow Monte Carlo modules are opt-in via `KRYPTOS_RUN_SLOW_MONTE_CARLO=1` and can be run directly in CI or locally when needed

**Result**: Leaner codebase, faster development cycle, maintained 100% test pass rate

## Current Progress

### ✅ K1: "Between subtle shading and the absence of light lies the nuance of iqlusion"

- **Status**: Solved.
- **Details**: Vigenère cipher with keyed alphabet `KRYPTOSABCDEFGHIJLMNQUVWXZ` (keyword: `KRYPTOS`) and Vigenère key `PALIMPSEST`. Intentional misspelling preserved: `IQLUSION`.

### ✅ K2: "It was totally invisible. How's that possible?"

- **Status**: Solved.
- **Details**: Vigenère cipher with keyed alphabet `KRYPTOSABCDEFGHIJLMNQUVWXZ` (keyword: `KRYPTOS`) and Vigenère key `ABSCISSA`. Includes embedded null/structural padding (`X`, and some `Y`) for historical alignment. Contains geospatial coordinates and narrative text.

### ✅ K3: "Slowly, desperately slowly, the remains of passage debris..."

- **Status**: Solved (double rotational transposition method).
- **Details**: Implemented the documented 24×14 grid → 90° rotation → reshape to 8-column grid → second 90° rotation. Resulting plaintext matches known solution including deliberate misspelling `DESPARATLY` (analogous
to `IQLUSION` in K1).

### ℹ️ K4: The unsolved mystery

- **Status**: Unsolved. Every attack vector attempted so far is null — single-layer, 2-layer, 3-layer composite, all 20 frontier vectors (P1–P20), the full 15-item Physical/Geometric Pivot, and Phase 7's shape-changing transpose family + shadow-angle primitives + city-list keywords. 1400+ tests passing, all attacks instrumented with permanent provenance artifacts.
- **Architecture confirmed**: substitution → transposition → K4 ciphertext (IC evidence; transposition-first definitively ruled out)
- **Confirmed cribs** (0-indexed): EAST@22–25, NORTHEAST@26–34, BERLIN@63–68, CLOCK@69–73
- **What's left**: needs new source material, not new code — a complete World Clock city list, a sub-minute-precision historical timestamp, or photographic documentation of the Kryptos compass rose's exact bearing. See `docs/ROADMAP.md`'s "Ideas — not yet scheduled."
- **Current status**: `docs/analysis/K4_ACTIVE_RESEARCH.md` — the single source of truth for confirmed facts, ruled-out hypotheses, and Phase 1-7 results (older per-vector "3D fingerprint" analysis is archived at `docs/archive/K4_ATTACK_LANDSCAPE.md`).
- **Live dashboard**: `docker compose -f config/docker-compose.yml up -d` → http://localhost:8000 → K4 Dashboard

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
- **Adaptive fusion weighting** (optional `adaptive=True` in composite run) leveraging wordlist hit rate & trigram entropy heuristics

## K4 Analysis Toolkit (New / Updated Modules)

Located under `kryptos/k4/` (migrated from `src/k4/`):

See `docs/reference/API_REFERENCE.md` for code-level API documentation.

## Roadmap

See `ROADMAP.md` for the current roadmap and milestones.

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

Select best performing weight from a prior sweep CSV:

```bash
kryptos tuning-pick-best --csv artifacts/tuning_runs/run_20251023T120000/crib_weight_sweep.csv
```

Clean and summarize a tuning run directory (crib hit counts, aggregates). Writes artifacts unless `--no-write` is
provided:

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

## RAG API (turbovec)

A lightweight FastAPI app provides semantic search over `artifacts/` (decisions, hypotheses, logs, reports), backed by
a [turbovec](https://pypi.org/project/turbovec/) compressed vector index and `sentence-transformers` embeddings.

Start the server:

```bash
kryptos serve --port 8000
```

Build (or rebuild) the index from the current `artifacts/` contents — required before searching, and after any
`artifacts/` changes:

```bash
curl -X POST localhost:8000/api/rag/reindex
```

Check index status:

```bash
curl localhost:8000/api/rag/status
```

Semantic search:

```bash
curl "localhost:8000/api/rag/search?q=Hill+cipher+key+matrix&k=5"
```

Health check:

```bash
curl localhost:8000/health
```

The index is stored under `data/turbovec/` (gitignored, derived from `artifacts/`).

## Recent Changes

- **2026-09-01**: K4 Physical/Geometric Pivot (Phase 6) and its Phase 7 follow-on both complete — shape-changing transpose family wired, "shadow of the word" computationally modeled (World Clock topper rotation + real solar position), World Clock city-list keywords tested, cross-vector consensus scoring built, scheduled overnight sweep runner built. 2.6M+ candidates across both phases, all null. ROADMAP/TASKS refreshed.
- **2026-08-12**: Documentation refresh — created `docs/analysis/K4_ATTACK_LANDSCAPE.md` (3D fingerprint of all completed null-result vectors and 10 frontier directions: P1–P7 active, P8–P10 deferred); updated ROADMAP, TASKS, GOVERN, METRICS, K4_ACTIVE_RESEARCH, K4_KEYSTREAM_ANALYSIS, and INDEX for accuracy
- **2026-06-01**: src/ audit baseline — 829 tests passing (0 failures); Quagmire I–IV, physical-grid tableau walk, SA columnar seeding, early-crib locking verified; all clock-based attack variants complete
- **2026-05-25**: All K4-ATTACK-1 through K4-ATTACK-7 complete; 3-layer composite chain (S→T→S), ADFGVX, Nihilist, Beaufort, Quagmire implementations added
- **2025-10-24**: Fixed CI failures by correcting `.gitignore` pattern - added agents source code (SPY, OPS, Q agents)

## Autopilot (Q / OPS / SPY) Summary

The repository includes an offline autopilot flow (Q / OPS / SPY) to recommend and execute safe tuning and extraction
steps. `ask_triumverate.py` implements a lightweight driver that can run a deterministic OPS tuning sweep and then
invoke the conservative SPY extractor. If `SPY_MIN_CONF` is not set, the autopilot will compute a conservative threshold
using the evaluation harness; it falls back to `0.25` when no labeled runs are available. See
`docs/reference/AGENTS_ARCHITECTURE.md` for full details and CLI examples.

## Contributing

Community contribution guidelines are maintained in [nitsuah/.github](https://github.com/nitsuah/.github/blob/main/CONTRIBUTING.md).

## Docker Fast Coverage

Run the fast test suite with coverage in a lightweight Docker container:

```bash
docker run --rm -v "${PWD}:/app" -w /app python:3.13-slim sh -lc \
  "pip install --no-cache-dir pytest pytest-cov numpy matplotlib requests beautifulsoup4 spacy nltk pyyaml fastapi httpx && \
   python -m spacy download en_core_web_sm && \
   pip install --no-cache-dir -e . --no-deps && \
   pytest tests/ -m 'not slow' --cov=kryptos --cov-report=term"
```

Note: `tests/test_k4_performance.py` contains a micro-benchmark guard that is automatically skipped in container
environments to avoid false regressions from container scheduling variance.

## Scoring Metrics Snapshot

Use `baseline_stats(text)` to inspect metrics including advanced linguistic features.

## Data Sources

Frequency & n-gram data in `data/` (TSV). High-quality quadgrams loaded automatically if `quadgrams_high_quality.tsv`
exists. Fallback unigram distribution used if files absent.

## License

See `LICENSE`.

## Other Documentation

- `docs/ROADMAP.md` — Current roadmap and phase objectives
- `docs/TASKS.md` — Implementation backlog and K4 attack queue
- `docs/CHANGELOG.md` — Change history and version tracking
- `docs/reference/AGENTS_ARCHITECTURE.md` — SPY/OPS/Q agent design and implementation
- `docs/reference/API_REFERENCE.md` — Python API and CLI command reference
- `docs/reference/AUTONOMOUS_SYSTEM.md` — Autonomous coordination system

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
## Community Standards

Shared community policies are centralized in [nitsuah/.github](https://github.com/nitsuah/.github):
- [Contributing](https://github.com/nitsuah/.github/blob/main/CONTRIBUTING.md)
- [Code of Conduct](https://github.com/nitsuah/.github/blob/main/CODE_OF_CONDUCT.md)
- [Security](https://github.com/nitsuah/.github/blob/main/SECURITY.md)
