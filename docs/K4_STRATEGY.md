# K4 Strategy & Technical Notes
Breadcrumb: Strategy > K4 > Technical Notes

This document collects K4-specific strategy, modules, and operational notes used by the analysis pipeline. It's
intentionally focused on the unsolved K4 piece and the specialized tooling in `kryptos/k4/` (previously `src/k4/`).

Related documents / breadcrumbs:

- Project core: `README_CORE.md`
- Autopilot: `AUTOPILOT.md`
- Roadmap: `../ROADMAP.md`
- Tuning APIs: `kryptos.k4.tuning.*` (weight sweeps, tiny param sweeps, artifact summarization)

## Current Progress (K4-specific)

- Implemented pipeline scaffolding for multi-stage hypotheses (hill, transposition, masking, berlin-
clock).
- Integrated attempt logging, scoring heuristics (n-grams, crib bonuses, positional bonuses), and
CSV/JSON artifact writers.
- Added adaptive gating heuristics, parallel hill-variant scaffolding, and a tuning harness
scaffold.

## K4 Features (detailed)

- Hill cipher solving (2x2 & partial 3x3 exploration) with crib-anchored pruning and assembly
variants.
- Columnar and route transposition search, including multi-crib positional anchoring and adaptive
sampling.
- Masking / null-removal heuristics to explore structural padding variants.
- Berlin Clock enumeration and validator scoring ordering/occurrence of `BERLIN`/`CLOCK` in
plaintexts.
- Composite orchestration, weighted fusion of stage outputs, and per-run diagnostics.

## Key modules (under `kryptos/k4/`)


## Tuning & Daemon Notes

Prefer direct package APIs over legacy scripts:

*Status:* Implemented (`rarity_weighted_crib_bonus` in `kryptos.k4.scoring`); calibration & fusion weight tuning
pending.

- `kryptos.k4.tuning.tiny_param_sweep`  deterministic micro-grid for smoke validation.
- `kryptos.k4.tuning.artifacts`  cleaning & summarization (`end_to_end_process`).

Legacy scripts (`scripts/tuning/`, certain experimental examples) will be replaced by forthcoming CLI subcommands
(`kryptos tuning ...`).

## Artifacts and format

- Per-run artifacts are written to `artifacts/k4_runs/run_<timestamp>/` or
`artifacts/tuning_runs/run_<timestamp>/`.
- Each run contains `summary.csv` and a `*_top.csv` filtered view for quick review.
- Extended scoring now includes positional letter deviation (bucketed chi-square balance) to
penalize structured transposition artifacts.

## Next K4 priorities (short)

1. Close remaining scoring coverage gaps and add transposition edge-case tests. 2. Implement deterministic small sweeps
and iterate weighting heuristics. 3. Deploy the daemon runner and collect longer campaigns for candidate analysis.

For operational details and code-level examples, refer to the module docstrings in `kryptos/k4/` and the quick examples
in `docs/README_CORE.md`.

## Kryptos K4 Research & Strategy

### 1. Scope & Objectives

K4 remains unsolved publicly. Our goal:

- Reconstruct high-confidence ciphertext normalization.
- Implement systematic candidate generation pipelines (cipher families consistent with design
ethos).
- Integrate objective scoring (language fitness, crib placement, clue satisfaction, linguistic
metrics).
- Maintain reproducibility (config-driven, test harness & artifact lineage + attempt logs).

### 2. Canonical Data

Ciphertext (per sculpture transcription; spaces inserted for readability):

```text
OBKR UOXOGHULBSOLIFBBWFLRVQQPRNGKSSO TWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTT MZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

Known plaintext cribs (confirmed by Sanborn) with expected start indices (0-based for analysis convenience):

| Plain | Expected Index | Cipher Segment |
|-------|----------------|----------------|
| EAST | 22 | (under investigation) |
| NORTHEAST | 25 | QQPRNGKSS |
| BERLIN | 64 | NYPVTT |
| CLOCK | 69 | MZFPK |

#### Index Corrections

Indices have been validated; the table above shows the corrected values (NORTHEAST=25, CLOCK=69). Prior values
(NORTHEAST=26 and CLOCK=70) were off-by-one errors. These have been harmonized for positional scoring. See validation in
[`tests/test_k4_cribs.py`](../tests/test_k4_cribs.py).

### 3. Constraints & Observations

- K1–K3 show deliberate anomalies → tolerate misspellings/nulls.
- Clues suggest possible method shift (like K3 shift to pure transposition) → evaluate hybrid
approaches (matrix + transposition + key-stream).
- CLOCK self-map letter indicates potential polyalphabetic coincidence or matrix edge alignment.
- Spatial/temporal clues (EAST/NORTHEAST/BERLIN CLOCK) reinforce directional/time-based key schedule
hypothesis (Berlin Clock encoding route).

### 4. Candidate Cipher Families (Tracked)

1. Polyalphabetic / key-stream (Berlin Clock derived shifts). [IN PROGRESS] 2. Columnar / double transposition with
anchored cribs. [IN PROGRESS] 3. Hill cipher (2x2, 3x3 constrained by cribs). [IN PROGRESS] 4. Masking / null removal to
expose latent structure. [COMPLETED (stage)] 5. Hybrid matrix
+ transposition chain. [PLANNED] 6. Progressive key (autokey/Berlin-lamp injection). [PLANNED]


### 5. Prioritization Status

| Priority | Item | Status |
|----------|------|--------|
| A | Hill cipher small block search (2x2 & 3x3 assemblies) | Expanded + pruning added |
| B | Columnar / multi-crib positional transposition | Multi-crib stage added |
| C | Berlin Clock key-stream enumeration | Implemented (full lamp & attempt logging) |
| D | Masking/null heuristic | Completed |
| E | Weighted multi-stage fusion | Completed |
| F | Advanced linguistic metrics (entropy, wordlist hit rate) | Completed |

### 6. Data Normalization Tasks

DONE: normalization utilities; still ensure consistent indexing for positional scoring (verify EAST/NORTHEAST
alignment). Pending: automatic index validation test.

### 7. Scoring Components (Implemented)

- Unigram/bigram/trigram/quadgram additive log scores.
- Chi-square penalty (scaled).
- Crib bonus & positional crib bonus.
- Index of coincidence, vowel ratio, letter coverage.
- Letter entropy, repeating bigram fraction.
- Wordlist hit rate, trigram entropy, bigram gap variance.
- Weighted fusion (stage-normalized min-max).
- Memoized combined score (LRU cache).
- Positional letter deviation metric integrated into extended composite score.
Planned enhancement: rarity-weighted crib scoring augments positional crib bonus with a frequency- based multiplier.

Algorithm sketch:

- alignment_frequency = occurrences_of_alignment / total_permutations_sampled_for_window
- rarity_weight = 1 / (1 + alignment_frequency * k) (initial k = 5.0)
- crib_bonus_component *= rarity_weight

Calibration (see PERF.md):

- Collect alignment_frequency distribution; sweep k in {1,2,5,10}.
- Measure Spearman correlation (old vs new ranking) for top-50; target ≥0.9.
- Select k producing uplift of rare alignments into top quartile without destabilizing high-
confidence candidates.

### 8. Hill Cipher Path (Current State)

- 2x2 key derivation from single & paired cribs.
- 3x3 variant assembly (row/col/diag) + sliding window concatenations.
- Partial score pruning for 3x3 candidates (reduce evaluation expense).
- Attempt logging for each key attempt (pruned & successful) → persisted via composite run.

Next: Evaluate additional assembly heuristics (spiral, snake) and consider plaintext/cipher swapped orientation tests (P
= K*C vs C = K*P) with small sample.

### 9. Transposition Constraint Solver (Current State)

- Standard & adaptive permutation search (sampling + prefix caching).
- Multi-crib positional stage enumerating permutations satisfying window constraints.
- Attempt logging at permutation level (search & adaptive).

Next: Integrate simultaneous alignment scoring (weighted by rarity of alignment probability) and add route-transposition
patterns.

#### Adaptive Sampling (Planned Detail)

Adaptive permutation sampling will dynamically tune effort per column count:

- Bootstrap: sample a small fixed batch (e.g. 200 permutations) and compute median and 95th
percentile scores.
- Expansion: if 95th percentile exceeds calibrated threshold (see PERF.md) expand sampling (2–4x)
for that column width.
- Early cutoff: if both median and p95 below low-quality boundary, abort further sampling for that
width.
- Rarity boost: increase exploration depth (expansion factor) for widths generating uncommon crib
alignment patterns.

Instrumentation:

- Persist per-width summary objects: {cols, sampled, expanded, median_score, p95_score} in attempt
logs.
- Track alignment_frequency for crib placements to feed rarity-weighted scoring.

Edge cases:

- Sparse high outlier (single very high score) → cap expansion factor to prevent runaway sampling.
- Uniform low scores → immediate cutoff to conserve runtime.
- Degenerate grids (non-divisible shapes) → skip expansion logic safely.

Success criteria: ≥30% reduction in low-quality permutations versus baseline exhaustive search while preserving top-10
candidate set (no loss of previous top scores in validation diffs).

### 10. Berlin Clock Key Stream (Current State)

- Full lamp state encoding with quarter markers differentiation.
- Dual-direction shift application (forward/backward) enumerated across time range.
- Attempt logging per time-mode combination.

Next: Derive candidate reference times (historical events) and cluster high scoring intervals; refine by dynamic step
reduction near promising hours.

### 11. Testing Infrastructure

Completed: Unit tests for scoring, Hill, transposition, Berlin Clock, masking, fusion, entropy metrics, positional
constraints. Pending: Tests for attempt log persistence artifact and multi-crib stage correctness (positions captured).
Add failure mode tests (pruned keys/perms recorded).

### 12. Workflow Log (Recent Updates)

- Added advanced linguistic metrics to scoring.
- Introduced memoized scoring & pipeline profiling.
- Implemented attempt logging + persistence (Hill, Clock, Transposition).
- Added 3x3 Hill pruning via partial score threshold.
- Added multi-crib positional transposition stage.
- Updated README with new features and examples.
- Added automated crib index validation test.
- Implemented adaptive fusion weighting (wordlist_hit_rate + trigram_entropy heuristics).
- Implemented route transposition stage (spiral / boustrophedon / diagonal variants).
- Added positional letter deviation metric for distribution balance.

### 13. Performance & Optimization

Implemented: LRU caching, partial score pruning, prefix caching. Next: Profile hotspots for 3x3 key generation & multi-
crib permutation enumeration; implement parallelization option (multiprocessing) for heavy search stages.

### 14. Artifact & Reproducibility

Implemented: Candidate JSON/CSV with metrics + transformation trace + lineage; attempt logs persisted in timestamped
JSON. Next: Add compression option & integrate provenance hash of ciphertext + parameters.

### 15. Updated Next Actions

1. Calibrate positional letter deviation weight (evaluate impact across historical candidate sets). 2. Refine route
transposition scoring (add positional crib bonus integration). 3. Expand 3x3 Hill assemblies (spiral, column zigzag) +
orientation flip tests. 4. Probability-weighted multi-crib scoring (rarity weighting vs simple bonus). 5.
Multiprocessing / parallel stage execution benchmarking. 6. Failure mode tests for pruning (assert pruned recorded
correctly). 7. Refine adaptive fusion weighting thresholds (entropy band & bonuses). 8. Add diagonal-start variants
(anti- diagonal snake) & perimeter-in/out variants. 9. Implement adaptive transposition sampling loop with per-width
metrics & validation benchmarks. 10. Integrate rarity-weighted crib scoring and complete calibration sweep (k parameter
selection).

### 16. References

(See README for links; add matrix conjecture, entropy references.)

--- Updated: 2025-10-23T23:50Z (positional deviation metric + next actions weight calibration + adaptive sampling &
rarity-weighted crib scoring plan)
