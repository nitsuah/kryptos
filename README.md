# KRYPTOS

Inspired by *The Unexplained* with William Shatner, I set out to solve Kryptos using Python! This project focuses on implementing cryptographic techniques, specifically the Vigenère cipher and structural transposition analysis, to decrypt the famous Kryptos sculpture.

## Current Progress

### K1: "Between subtle shading and the absence of light lies the nuance of iqlusion"

- **Status**: Solved.
- **Details**: Decrypted via Vigenère using keyed alphabet `KRYPTOSABCDEFGHIJLMNQUVWXZ`. Intentional misspelling preserved: `IQLUSION`.

### K2: "It was totally invisible. How's that possible?"

- **Status**: Solved.
- **Details**: Vigenère (key: `ABSCISSA`). Includes embedded null/structural padding (`S`) for historical alignment. Contains geospatial coordinates and narrative text.

### K3: "Slowly, desperately slowly, the remains of passage debris..."

- **Status**: Solved (double rotational transposition method).
- **Details**: Implemented the documented 24×14 grid → 90° rotation → reshape to 8-column grid → second 90° rotation. Resulting plaintext matches known solution including deliberate misspelling `DESPARATLY` (analogous to `IQLUSION` in K1).

### K4: The unsolved mystery

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

- **Vigenère Cipher** with keyed alphabet handling
- **K3 Double Rotational Transposition** implementation
- **Config Driven** (`config/config.json`) for ciphertexts, keys, and parameters
- **Test Suite** validating K1–K3 solutions
- **Frequency, n-gram, and crib-based scoring utilities**
- **Hill cipher (2x2 & 3x3)** encryption/decryption + key solving from crib segments
- **Constrained Hill key derivation** from `BERLIN` / `CLOCK` cribs (single & pairwise) with caching
- **Modular pipeline architecture** (stage factory for Hill constraints)
- **Columnar transposition** search (with optional partial-score pruning) and crib-constrained inversion utilities
- **Extended scoring metrics**: chi-square, bigram/trigram/quadgram totals, index of coincidence, vowel ratio, letter coverage, baseline metrics
- **Positional crib weighting** (distance-window bonus)
- **Berlin Clock shift hypothesis** scaffolding (now with full lamp enumeration utilities + pipeline stage factory `make_berlin_clock_stage`)
- **Candidate reporting artifacts** (JSON + optional CSV summaries)

## K4 Analysis Toolkit (New Modules)

Located under `src/k4/` (see full roadmap in `roadmap.md`):

- `scoring.py` – frequencies, composite scoring, positional crib bonus, quadgram support
- `hill_cipher.py` – Hill math & crib-based key solving
- `hill_constraints.py` – constrained 2x2 key derivation + caching
- `hill_search.py` – candidate batch scoring
- `transposition.py` / `transposition_constraints.py` – permutation & crib-aware inversion (with pruning)
- `cribs.py` – normalization / annotation
- `berlin_clock.py` – preliminary & full clock shift generation (`full_clock_state`, `full_berlin_clock_shifts`, `enumerate_clock_shift_sequences`)
- `pipeline.py` – `Pipeline`, `Stage`, `StageResult`, `make_hill_constraint_stage()`, `make_berlin_clock_stage()`
- `reporting.py` – JSON/CSV artifact generation utilities

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

Frequency & n-gram data in `data/` (TSV). Fallback values used if missing.

## License

See `LICENSE`.

## References & Research

- [UCSD Crypto Project by Karl Wang](https://mathweb.ucsd.edu/~crypto/Projects/KarlWang/index2.html)
- [Kryptos Wiki](https://en.wikipedia.org/wiki/Kryptos)
- [Vigenère Cipher Explanation](https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher)
- [Kryptosfan Blog](https://kryptosfan.wordpress.com/k3/k3-solution-3/)
