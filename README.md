# KRYPTOS

Inspired by *The Unexplained* with William Shatner, I set out to solve Kryptos using Python! This project focuses on implementing cryptographic techniques, specifically the Vigenère cipher and structural transposition analysis, to decrypt the famous Kryptos sculpture.

## Current Progress

### ✅ K1: "Between subtle shading and the absence of light lies the nuance of iqlusion"

- **Status**: Solved.
- **Details**: Decrypted via Vigenère using keyed alphabet `KRYPTOSABCDEFGHIJLMNQUVWXZ`. Intentional misspelling preserved: `IQLUSION`.

### ✅ K2: "It was totally invisible. How's that possible?"

- **Status**: Solved.
- **Details**: Vigenère (key: `ABSCISSA`). Includes embedded null/structural padding (`S`) for historical alignment. Contains geospatial coordinates and narrative text.

### ✅ K3: "Slowly, desperately slowly, the remains of passage debris..."

- **Status**: Solved (double rotational transposition method).
- **Details**: Implemented the documented 24×14 grid → 90° rotation → reshape to 8-column grid → second 90° rotation. Resulting plaintext matches known solution including deliberate misspelling `DESPARATLY` (analogous to `IQLUSION` in K1).

### ℹ️ K4: The unsolved mystery

- **Status**: Unsolved.
- **Implemented Toolkit**: See new K4 modules below (Hill cipher exploration, scoring, constraint pipeline).
- **Next Focus**: Research masking techniques, positional/overlay hypotheses, layered transposition, and potential null insertion strategies (see CIA hints: `BERLIN`, `CLOCK`).

## Deliberate Misspellings / Anomalies

| Section | Cipher Plaintext Form | Expected Modern Spelling | Note |
|---------|-----------------------|---------------------------|------|
| K1      | IQLUSION              | ILLUSION                  | Intentional artistic alteration |
| K3      | DESPARATLY            | DESPERATELY               | Preserved from sculpture transcription |

### K2 Structural Padding

K2 contains systematic X (and some Y) insertions serving as alignment/null separators rather than mistakes. They should be treated as structural artifacts when analyzing pattern continuity or constructing transposition hypotheses.

## Features

- **Vigenère Cipher** with keyed alphabet handling ([learn more](https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher))
- **K3 Double Rotational Transposition** implementation ([learn more](https://en.wikipedia.org/wiki/Transposition_cipher))
- **Config Driven** (`config/config.json`) for ciphertexts, keys, and parameters ([learn more](https://en.wikipedia.org/wiki/Configuration_file))
- **Test Suite** validating K1–K3 solutions ([learn more](https://en.wikipedia.org/wiki/Unit_testing))
- **Frequency, n-gram, and crib-based scoring utilities** ([learn more](https://en.wikipedia.org/wiki/Frequency_analysis), [n-grams](https://en.wikipedia.org/wiki/N-gram), [cribs](https://en.wikipedia.org/wiki/Crib_(cryptanalysis)))
- **Hill cipher (2x2 & 3x3)** encryption/decryption + key solving from crib segments ([learn more](https://en.wikipedia.org/wiki/Hill_cipher))
- **Constrained Hill key derivation** from `BERLIN` / `CLOCK` cribs (single & pairwise) with caching ([learn more](https://en.wikipedia.org/wiki/Crib_(cryptanalysis)))
- **Modular pipeline architecture** (stage factory for Hill constraints) ([learn more](https://en.wikipedia.org/wiki/Pipeline_(computing)))
- **Columnar transposition** search (with optional partial-score pruning) and crib-constrained inversion utilities ([learn more](https://en.wikipedia.org/wiki/Transposition_cipher#Columnar_transposition))
- **Extended scoring metrics**: chi-square, bigram/trigram/quadgram totals, index of coincidence, vowel ratio, letter coverage, baseline metrics ([chi-square](https://en.wikipedia.org/wiki/Chi-square_test), [index of coincidence](https://en.wikipedia.org/wiki/Index_of_coincidence))
- **Positional crib weighting** (distance-window bonus) ([learn more](https://en.wikipedia.org/wiki/Crib_(cryptanalysis)))
- **Berlin Clock shift hypothesis** scaffolding (full lamp enumeration utilities + pipeline stage factory) ([learn more](https://en.wikipedia.org/wiki/Mengenlehreuhr))
- **Columnar transposition stage factory** (`make_transposition_stage`) for permutation search integration ([learn more](https://en.wikipedia.org/wiki/Transposition_cipher))
- **Adaptive transposition stage** (`make_transposition_adaptive_stage`) with sampling + prefix caching heuristics ([learn more](https://en.wikipedia.org/wiki/Heuristic))
- **Masking/null-removal stage** (`make_masking_stage`) exploring structural padding elimination variants ([learn more](https://en.wikipedia.org/wiki/Null_cipher))
- **Weighted multi-stage fusion utilities** (`normalize_scores`, `fuse_scores_weighted`) for score aggregation ([learn more](https://en.wikipedia.org/wiki/Ensemble_learning))
- **High-quality quadgram table** auto-loaded when present (`data/quadgrams_high_quality.tsv`) ([learn more](https://en.wikipedia.org/wiki/N-gram))
- **Candidate reporting artifacts** (JSON + optional CSV summaries) ([learn more](https://en.wikipedia.org/wiki/Reproducibility))

## K4 Analysis Toolkit (New Modules)

Located under `src/k4/` (see full roadmap in `roadmap.md`):

- `scoring.py` – frequencies, composite scoring, positional crib bonus, quadgram support
- `hill_cipher.py` – Hill math & crib-based key solving
- `hill_constraints.py` – constrained 2x2 key derivation + caching
- `hill_search.py` – candidate batch scoring
- `transposition.py` / `transposition_constraints.py` – permutation & crib-aware inversion (with pruning)
- `cribs.py` – normalization / annotation
- `berlin_clock.py` – preliminary & full clock shift generation (`full_clock_state`, `full_berlin_clock_shifts`, `enumerate_clock_shift_sequences`)
- `pipeline.py` – `Pipeline`, `Stage`, `StageResult`, `make_hill_constraint_stage()`, `make_berlin_clock_stage()`, `make_transposition_stage()`, `make_transposition_adaptive_stage()`, `make_masking_stage()`
- `masking.py` – null removal / run-collapsing variant generation and scoring
- `composite.py` – aggregation + optional weighted fusion (see `run_composite_pipeline` with `weights`)

Exports aggregated in `src/k4/__init__.py`.

## Roadmap

Detailed future plans (candidate reporting, Berlin Clock expansion, pruning heuristics, extended Hill search, masking strategies) have moved to `roadmap.md` → see the full document here: [Detailed Roadmap](./roadmap.md).

## Contributing

Contribution guidelines moved to `CONTRIBUTING.md` → read them here: [Contributing Guide](./CONTRIBUTING.md).

## Quick Start: Hill Constraint Stage

```python
from src.k4 import Pipeline, make_hill_constraint_stage

cipher_k4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQ"  # sample beginning
pipe = Pipeline([make_hill_constraint_stage()])
result = pipe.run(cipher_k4)[0]  # StageResult
for cand in result.metadata['candidates'][:5]:
    print(cand['source'], cand['score'], cand['text'][:50])
```

## Quick Start: Composite Multi-Stage Run

```python
from src.k4 import (
    make_hill_constraint_stage,
    make_transposition_adaptive_stage,
    make_masking_stage,
    make_berlin_clock_stage,
    run_composite_pipeline
)

cipher_k4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQ"
stages = [
    make_hill_constraint_stage(),
    make_transposition_adaptive_stage(min_cols=5, max_cols=6, sample_perms=200, partial_length=50),
    make_masking_stage(limit=15),
    make_berlin_clock_stage(step_seconds=10800, limit=20)
]
weights = {
    'hill-constraint': 2.0,
    'transposition-adaptive': 1.2,
    'masking': 1.0,
    'berlin-clock': 0.8,
}
res = run_composite_pipeline(cipher_k4, stages, report=True, weights=weights, normalize=True)
print("Top fused candidates:")
for c in res.get('fused', [])[:5]:
    print(c['stage'], c['fused_score'], c['text'][:50])
```

## Scoring Metrics Snapshot

Use `from src.k4 import baseline_stats` to inspect metrics for any candidate plaintext.

## How to Run

```bash
git clone https://github.com/nitsuah/kryptos.git
cd kryptos
pip install -r requirements.txt
python -m unittest discover -s tests
```

## Data Sources

Frequency & n-gram data in `data/` (TSV). High-quality quadgrams loaded automatically if `quadgrams_high_quality.tsv` exists (fallback to `quadgrams.tsv`). Fallback unigram distribution used if files absent.

## License

See `LICENSE`.

## References & Research

- [UCSD Crypto Project by Karl Wang](https://mathweb.ucsd.edu/~crypto/Projects/KarlWang/index2.html)
- [Kryptos Wiki](https://en.wikipedia.org/wiki/Kryptos)
- [Vigenère Cipher Explanation](https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher)
- [Kryptosfan Blog](https://kryptosfan.wordpress.com/k3/k3-solution-3/)
