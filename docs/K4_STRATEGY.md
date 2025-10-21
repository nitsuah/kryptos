# Kryptos K4 Research & Strategy

## 1. Scope & Objectives

K4 remains unsolved publicly. Our goal:

- Reconstruct high-confidence ciphertext normalization.
- Implement systematic candidate generation pipelines (cipher families consistent with design ethos).
- Integrate objective scoring (language fitness, crib placement, clue satisfaction).
- Maintain reproducibility (config-driven, test harness for each hypothesis).

## 2. Canonical Data

Ciphertext (per sculpture transcription; spaces inserted for readability):

``` text
OBKR UOXOGHULBSOLIFBBWFLRVQQPRNGKSSO TWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTT MZFPKWGDKZXTJCDIGKUHUAUEKCAR
```

Length accounting (remove spaces) must be validated in code.

Known plaintext cribs (confirmed by Sanborn):

- Positions 22–25: EAST
- Positions 26–34: NORTHEAST (cipher: QQPRNGKSS)
- Positions 64–69: BERLIN (cipher: NYPVTT)
- Positions 70–74: CLOCK (cipher: MZFPK) (Note: K self-maps)

Open question: Are indices 1-based sculpture positions? We must harmonize indexing (decide zero vs one-based) in code.

## 3. Constraints & Observations

- Multiple deliberate irregularities in K1–K3 (misspellings, omitted letter) suggest transcription artifacts are permissible.
- K3 switched methodology (pure transposition vs Vigenère). Clues hint at a "change in methodology" again.
- Presence of self-mapping letter (K -> K) in CLOCK suggests polyalphabetic system where coincidental alignment occurs (e.g., Vigenère variant) or homophonic / matrix cipher.
- Bauer/Link/Molle conjecture: Hill cipher / matrix (presence of extra L in tableau line). Consider small matrix block size (2x2, 3x3, 5x5) over sanitized text.
- Spatial clues (EAST, NORTHEAST, BERLIN CLOCK) imply directional / temporal semantics—potential key schedule derived from Berlin Clock state encoding (base-5/10 representation via lamp rows).

## 4. Candidate Cipher Families

1. Polyalphabetic (variant Vigenère / autokey / progressive key shifts)
2. Fractionation + transposition (e.g., Bifid / Trifid hybrid using keyed square from tableau anomalies)
3. Columnar/double transposition with inserted nulls aligning known cribs at given coordinates after rotation paths.
4. Hill cipher (mod 26) applied to digraphs/trigraphs with a key matrix chosen to yield known crib mappings at target positions.
5. Running-key using Berlin Clock pattern (daily seconds -> lamp states) as dynamic key stream.
6. Mixed scheme: partial matrix substitution then route transposition (spiral, boustrophedon, knight’s tour) to produce clustering of directional words.

## 5. Initial Prioritization

High payoff/feasibility first:

- A: Hill cipher small block search constrained by BERLIN/CLOCK mapping.
- B: Columnar/double transposition with fixed crib anchoring (simulate insertion of cribs and solve for column order via constraint satisfaction).
- C: Progressive Vigenère (shift pattern derived from Berlin Clock lamps) verifying selective plaintext emergence at known indices.

## 6. Data Normalization Tasks

- Remove spaces & question marks; confirm final length.
- Index mapping: produce dictionary of { plain_index_range: known_plain, cipher_range: cipher_segment }.
- Validate segments align; if not, adjust offset hypothesis.

## 7. Scoring Components

Implement in `analysis.py` expansions:

- English frequency log-likelihood (unigram + bigram).
- Crib satisfaction score (proportion of cribs placed correctly).
- Positional penalty (distance if crib misaligned but present).
- Entropy measure post-decryption (expect moderate natural language entropy).

Return composite fitness: weighted sum.

## 8. Hill Cipher Path

Steps:

1. Extract contiguous segments covering cribs; form linear equations for key matrix unknowns.
2. If plaintext P and ciphertext C block relate via `C = K * P` (mod 26) or `P = K * C`, test orientation.
3. Solve for K using invertible matrices; check determinant coprime to 26.
4. Apply candidate K over full ciphertext; score result.

Potential challenge: Non-contiguous cribs may require guessed intervening plaintext.

## 9. Transposition Constraint Solver

Approach:

- Assume plaintext length N; choose column width w.
- Place known crib strings at target row/column positions after transposition inverse.
- Solve column permutation that produces given cipher ordering; use backtracking + pruning.

## 10. Berlin Clock Key Stream

Berlin Clock encodes time via lamps (hours/5, hours, minutes/5, minutes, seconds). Map lamp states at hypothetical reference moment (e.g., dedication time, sunrise at coordinates, auction date) to numeric sequence; convert to shifts.

- Derive shift array S.
- Apply S mod 26 to ciphertext (forward/backward) attempting to reveal cribs at target positions.

## 11. Testing Infrastructure

Add `tests/test_k4_hypotheses.py` skeleton with parametrized tests:

- hill_cipher_candidate (assert cribs appear)
- transposition_candidate (assert placement alignment)
- berlin_clock_vigenere_candidate (assert substring matches)

Each test should skip (`unittest.skip`) until implemented.

## 12. Iterative Workflow (Status Update)

1. Implement normalization & crib mapping utilities. (COMPLETED)
2. Add Hill cipher solver (2x2, 3x3 brute constrained). (COMPLETED: `hill_cipher.py`, constraints in `hill_constraints.py`)
3. Add transposition constraint solver prototype. (PARTIAL: basic columnar search + pruning; full constraint stage pending)
4. Add Berlin Clock key stream generator. (COMPLETED: basic + full lamp enumeration in `berlin_clock.py`)
5. Produce top-N decrypt outputs & persist artifacts. (COMPLETED: JSON/CSV via `reporting.py`)
6. Refine heuristics. (IN PROGRESS: added positional crib bonus & partial-score pruning)

## 13. Risk Management

- Avoid combinatorial explosion: set pragmatic bounds (e.g., 2x2, 3x3 Hill only; column widths <= 20).
- Maintain reproducibility with seed and saved intermediate files.
- Document unsuccessful paths in `docs/K4_ATTEMPTS.md` to prevent repetition.

## 14. Open Questions

- Exact indexing convention for released clues (need authoritative mapping).
- Was extra L in tableau line intended as matrix hint or aesthetic artifact?
- Null characters usage (e.g., X in K2) repetition pattern in K4?

## 15. Next Immediate Actions (Updated)

- Integrate Berlin Clock overlay as pipeline stage (apply full lamp shifts, score, report).
- Add quadgram loader/score (data/quadgrams.tsv) and incorporate into combined score weighting.
- Implement adaptive transposition pruning (prefix caching + permutation sampling bias).
- Composite multi-stage run: transposition → hill constraints → clock shifts; merge & rank unified candidate set.
- Prototype recursive masking/null removal heuristic (detect/remove low-frequency padding clusters; evaluate score delta).

(Previous items: crib mapping, Hill cipher module, test scaffolds now completed.)

## 16. References

(See README plus:)

- Bauer, Link, Molle (2016) Matrix conjecture.
- Bean (2021) Cryptodiagnosis of K4.
- Wired (2010, 2014) clue releases.
- NYT (2020) NORTHEAST clue.
- Twitter (2020) EAST clue.

---
Prepared: 2025-10-20 (updated)
