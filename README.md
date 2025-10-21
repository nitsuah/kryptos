# KRYPTOS

Inspired by *The Unexplained* with William Shatner, I set out to solve Kryptos using Python! This project focuses on implementing cryptographic techniques, specifically the Vigenère cipher and structural transposition analysis, to decrypt the famous Kryptos sculpture.

## TL;DR

**K4 is the last unsolved piece of a CIA sculpture puzzle.** Imagine a secret message carved in copper that nobody has cracked in 30+ years. We're using Python to systematically try every reasonable decryption method – techniques that cryptanalysts may have attempted manually but couldn't exhaustively explore. Our approach combines automated testing with intelligent scoring to measure how "English-like" each result appears:

1. **Hill Cipher** - Matrix-based substitution where letters become numbers, transform through matrix multiplication, then convert back
2. **Transposition** - Systematic letter rearrangement (write in columns, read in rows, or more complex patterns)
3. **Masking** - Identifying and removing dummy letters that serve as padding or obfuscation
4. **Berlin Clock** - Using the iconic clock's binary time pattern as a cryptographic key
5. **Combo Attacks** - Chaining multiple methods together (K4 likely uses 2-3 techniques layered in sequence)

We evaluate candidates using linguistic patterns – common letter pairs, trigram frequencies, real word detection – to identify promising decryptions. Think of it as trying thousands of lock combinations, but guided by cryptanalytic intuition rather than brute force. After all, humans design puzzles with intention, not randomness!

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
- **Implemented Toolkit**: See K4 modules below (Hill cipher exploration, scoring, constraint pipeline, multi-stage fusion).
- **Latest Additions**: Multi-crib positional transposition stage, attempt logging & persistence, advanced linguistic metrics, 3x3 Hill key pruning (partial_len/partial_min tunable in hill constraint stage).

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
- **3x3 Hill assembly variants & pruning** (row/col/diagonal constructions + partial score pruning) ([learn more](https://en.wikipedia.org/wiki/Hill_cipher))
- **Constrained Hill key derivation** from `BERLIN` / `CLOCK` cribs (single & pairwise) with caching ([learn more](https://en.wikipedia.org/wiki/Crib_(cryptanalysis)))
- **Modular pipeline architecture** (stage factories for all hypothesis families) ([learn more](https://en.wikipedia.org/wiki/Pipeline_(computing)))
- **Columnar transposition** search (partial-score pruning) and crib-constrained inversion utilities ([learn more](https://en.wikipedia.org/wiki/Transposition_cipher#Columnar_transposition))
- **Multi-crib positional transposition stage** (anchors multiple cribs simultaneously) ([learn more](https://en.wikipedia.org/wiki/Transposition_cipher))
- **Adaptive transposition search** (`make_transposition_adaptive_stage`) with sampling + prefix caching heuristics ([learn more](https://en.wikipedia.org/wiki/Heuristic))
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
- **Adaptive fusion weighting** (optional `adaptive=True` in composite run) leveraging wordlist hit rate & trigram entropy heuristics.

## K4 Analysis Toolkit (New / Updated Modules)

Located under `src/k4/`:

- `scoring.py` – composite scoring, positional crib bonus, memoized scoring, advanced metrics
- `hill_cipher.py` – Hill math & crib-based key solving
- `hill_constraints.py` – constrained 2x2 & multi-assembly 3x3 key derivation + pruning + attempt logging
- `transposition.py` – columnar search (standard & adaptive) + attempt logging
- `transposition_constraints.py` – crib positional anchoring (`search_with_multiple_cribs_positions`)
- `berlin_clock.py` – clock shift sequence generation (full lamp state)
- `pipeline.py` – stage factories (`make_hill_constraint_stage`, `make_transposition_stage`, `make_transposition_adaptive_stage`, `make_transposition_multi_crib_stage`, `make_masking_stage`, `make_berlin_clock_stage`)
- `masking.py` – null removal / run collapsing variant generation
- `composite.py` – multi-stage aggregation, weighted fusion, artifact + attempt log persistence
- `attempt_logging.py` – persist Hill / Clock / Transposition attempt logs (`persist_attempt_logs`)
- `reporting.py` – enriched candidate JSON/CSV with baseline metrics + trace

## Roadmap

Detailed future plans (candidate reporting, Berlin Clock expansion, pruning heuristics, extended Hill search, masking strategies) have moved to `ROADMAP.md` → see the full document here: [Roadmap Guide](./ROADMAP.md).

See full document in `docs/K4_STRATEGY.md` – includes current completion status and next actions.

## Contributing

Contribution guidelines moved to `CONTRIBUTING.md` → [Contributing Guide](./CONTRIBUTING.md).

## Quick Start: Hill Constraint Stage

```python
from src.k4 import Pipeline, make_hill_constraint_stage
cipher_k4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQ"
pipe = Pipeline([make_hill_constraint_stage()])
result = pipe.run(cipher_k4)[0]
for cand in result.metadata['candidates'][:5]:
    print(cand['source'], cand['score'], cand['text'][:50])
```

## Quick Start: Composite Multi-Stage Run

```python
from src.k4 import (
    make_hill_constraint_stage,
    make_transposition_adaptive_stage,
    make_transposition_multi_crib_stage,
    make_route_transposition_stage,
    make_masking_stage,
    make_berlin_clock_stage,
    run_composite_pipeline
)

cipher_k4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQ"
positional_cribs = {
    'EAST': [22],
    'NORTHEAST': [25],  # corrected index
    'BERLIN': [64],
    'CLOCK': [69],      # corrected index
}
stages = [
    make_hill_constraint_stage(),
    make_transposition_adaptive_stage(min_cols=5, max_cols=6, sample_perms=200, partial_length=50),
    make_transposition_multi_crib_stage(positional_cribs=positional_cribs, min_cols=5, max_cols=6),
    make_route_transposition_stage(min_cols=5, max_cols=6),
    make_masking_stage(limit=15),
    make_berlin_clock_stage(step_seconds=10800, limit=20)
]
weights = {
    'hill-constraint': 2.0,
    'transposition-adaptive': 1.2,
    'transposition-pos-crib': 1.5,
    'masking': 1.0,
    'berlin-clock': 0.8,
}
res = run_composite_pipeline(cipher_k4, stages, report=True, normalize=True, adaptive=True)
print("Adaptive weights:", res['profile'].get('adaptive_diagnostics'))
print("Top fused candidates:")
for c in res.get('fused', [])[:5]:
    print(c['stage'], c['fused_score'], c['text'][:50])
```

## Attempt Logs Persistence

```python
from src.k4.attempt_logging import persist_attempt_logs
path = persist_attempt_logs(out_dir='reports', label='K4', clear=True)
print("Attempt log written:", path)
```

## Scoring Metrics Snapshot

Use `baseline_stats(text)` to inspect metrics including advanced linguistic features.

## How to Run

```bash
git clone https://github.com/nitsuah/kryptos.git
cd kryptos
pip install -r requirements.txt
python -m unittest discover -s tests
```

## Data Sources

Frequency & n-gram data in `data/` (TSV). High-quality quadgrams loaded automatically if `quadgrams_high_quality.tsv` exists. Fallback unigram distribution used if files absent.

## License

See `LICENSE`.

## References & Research

- [UCSD Crypto Project by Karl Wang](https://mathweb.ucsd.edu/~crypto/Projects/KarlWang/index2.html)
- [Kryptos Wiki](https://en.wikipedia.org/wiki/Kryptos)
- [Vigenère Cipher Explanation](https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher)
- [Kryptosfan Blog](https://kryptosfan.wordpress.com/k3/k3-solution-3/)
- [Berlin Clock](https://en.wikipedia.org/wiki/Mengenlehreuhr)
- [Hill Cipher](https://en.wikipedia.org/wiki/Hill_cipher)
- [Index of Coincidence](https://en.wikipedia.org/wiki/Index_of_coincidence)
- [Entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory))
