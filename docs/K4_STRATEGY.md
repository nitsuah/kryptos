# Kryptos K4 Research & Strategy

## 1. Scope & Objectives

K4 remains unsolved publicly. Our goal:

- Reconstruct high-confidence ciphertext normalization.
- Implement systematic candidate generation pipelines (cipher families consistent with design ethos).
- Integrate objective scoring (language fitness, crib placement, clue satisfaction, linguistic metrics).
- Maintain reproducibility (config-driven, test harness & artifact lineage + attempt logs).

## 2. Canonical Data

Ciphertext (per sculpture transcription; spaces inserted for readability):

``` text
OBKR UOXOGHULBSOLIFBBWFLRVQQPRNGKSSO TWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTT MZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

Known plaintext cribs (confirmed by Sanborn) with expected start indices (0-based for analysis convenience):

| Plain | Expected Index | Cipher Segment |
|-------|----------------|----------------|
| EAST | 22 | (under investigation) |
| NORTHEAST | 25 | QQPRNGKSS |
| BERLIN | 64 | NYPVTT |
| CLOCK | 69 | MZFPK |

(Indices validated; the table above shows the corrected values (NORTHEAST=25, CLOCK=69). Prior values (NORTHEAST=26 and CLOCK=70) were off-by-one errors. Harmonized for positional scoring. See validation in [`tests/test_k4_cribs.py`](../tests/test_k4_cribs.py).)

## 3. Constraints & Observations

- K1–K3 show deliberate anomalies → tolerate misspellings/nulls.
- Clues suggest possible method shift (like K3 shift to pure transposition) → evaluate hybrid approaches (matrix + transposition + key-stream).
- CLOCK self-map letter indicates potential polyalphabetic coincidence or matrix edge alignment.
- Spatial/temporal clues (EAST/NORTHEAST/BERLIN CLOCK) reinforce directional/time-based key schedule hypothesis (Berlin Clock encoding route).

## 4. Candidate Cipher Families (Tracked)

1. Polyalphabetic / key-stream (Berlin Clock derived shifts). [IN PROGRESS]
2. Columnar / double transposition with anchored cribs. [IN PROGRESS]
3. Hill cipher (2x2, 3x3 constrained by cribs). [IN PROGRESS]
4. Masking / null removal to expose latent structure. [COMPLETED (stage)]
5. Hybrid matrix + transposition chain. [PLANNED]
6. Progressive key (autokey/Berlin-lamp injection). [PLANNED]

## 5. Prioritization Status

| Priority | Item | Status |
|----------|------|--------|
| A | Hill cipher small block search (2x2 & 3x3 assemblies) | Expanded + pruning added |
| B | Columnar / multi-crib positional transposition | Multi-crib stage added |
| C | Berlin Clock key-stream enumeration | Implemented (full lamp & attempt logging) |
| D | Masking/null heuristic | Completed |
| E | Weighted multi-stage fusion | Completed |
| F | Advanced linguistic metrics (entropy, wordlist hit rate) | Completed |

## 6. Data Normalization Tasks

DONE: normalization utilities; still ensure consistent indexing for positional scoring (verify EAST/NORTHEAST alignment). Pending: automatic index validation test.

## 7. Scoring Components (Implemented)

- Unigram/bigram/trigram/quadgram additive log scores.
- Chi-square penalty (scaled).
- Crib bonus & positional crib bonus.
- Index of coincidence, vowel ratio, letter coverage.
- Letter entropy, repeating bigram fraction.
- Wordlist hit rate, trigram entropy, bigram gap variance.
- Weighted fusion (stage-normalized min-max).
- Memoized combined score (LRU cache).

## 8. Hill Cipher Path (Current State)

- 2x2 key derivation from single & paired cribs.
- 3x3 variant assembly (row/col/diag) + sliding window concatenations.
- Partial score pruning for 3x3 candidates (reduce evaluation expense).
- Attempt logging for each key attempt (pruned & successful) → persisted via composite run.

Next: Evaluate additional assembly heuristics (spiral, snake) and consider plaintext/cipher swapped orientation tests (P = K*C vs C = K*P) with small sample.

## 9. Transposition Constraint Solver (Current State)

- Standard & adaptive permutation search (sampling + prefix caching).
- Multi-crib positional stage enumerating permutations satisfying window constraints.
- Attempt logging at permutation level (search & adaptive).

Next: Integrate simultaneous alignment scoring (weighted by rarity of alignment probability) and add route-transposition patterns.

## 10. Berlin Clock Key Stream (Current State)

- Full lamp state encoding with quarter markers differentiation.
- Dual-direction shift application (forward/backward) enumerated across time range.
- Attempt logging per time-mode combination.

Next: Derive candidate reference times (historical events) and cluster high scoring intervals; refine by dynamic step reduction near promising hours.

## 11. Testing Infrastructure

Completed: Unit tests for scoring, Hill, transposition, Berlin Clock, masking, fusion, entropy metrics, positional constraints.
Pending: Tests for attempt log persistence artifact and multi-crib stage correctness (positions captured). Add failure mode tests (pruned keys/perms recorded).

## 12. Workflow Log (Recent Updates)

- Added advanced linguistic metrics to scoring.
- Introduced memoized scoring & pipeline profiling.
- Implemented attempt logging + persistence (Hill, Clock, Transposition).
- Added 3x3 Hill pruning via partial score threshold.
- Added multi-crib positional transposition stage.
- Updated README with new features and examples.
- Added automated crib index validation test.
- Implemented adaptive fusion weighting (wordlist_hit_rate + trigram_entropy heuristics).
- Implemented route transposition stage (spiral / boustrophedon / diagonal variants).

## 13. Performance & Optimization

Implemented: LRU caching, partial score pruning, prefix caching.
Next: Profile hotspots for 3x3 key generation & multi-crib permutation enumeration; implement parallelization option (multiprocessing) for heavy search stages.

## 14. Artifact & Reproducibility

Implemented: Candidate JSON/CSV with metrics + transformation trace + lineage; attempt logs persisted in timestamped JSON.
Next: Add compression option & integrate provenance hash of ciphertext + parameters.

## 15. Updated Next Actions

1. Refine route transposition scoring (add positional crib bonus integration).
2. Expand 3x3 Hill assemblies (spiral, column zigzag) + orientation flip tests.
3. Probability-weighted multi-crib scoring (rarity weighting vs simple bonus).
4. Multiprocessing / parallel stage execution benchmarking.
5. Failure mode tests for pruning (assert pruned recorded correctly).
6. Refine adaptive fusion weighting thresholds (entropy band & bonuses).
7. Add diagonal-start variants (anti-diagonal snake) & perimeter-in/out variants.

## 16. References

(See README for links; add matrix conjecture, entropy references.)

---
Updated: 2025-10-20
