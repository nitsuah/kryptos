# K4 Attack Landscape — 3D Fingerprint

Breadcrumb: Home > Docs > Analysis > Attack Landscape

**Generated:** 2026-08-12  
**Framework:** Three-dimensional "pundit squad" model — Past / Present / Frontier  
**Purpose:** Give any session a complete orientational picture of where we stand and where to go next.

> **Quick orientation:** K4 is a 97-character ciphertext carved in copper at CIA HQ, unsolved since 1990. Sculptor Jim Sanborn has confirmed four plaintext anchors and described "five or six techniques." The architecture is confirmed as **substitution → transposition → K4 ciphertext** (not transposition-first). All 14 clean 2-layer composite vectors have returned null results. The frontier is 3-layer composites, pre-cipher masking, and secondary-key derivation.

---

## Dimension 1 — PAST: What We Have Covered and What It Proved

### 1.1 Confirmed Architecture

```
plaintext
    ↓
[Layer A: substitution — polyalphabetic or matrix-based]
    ↓
pre-transposition text
    ↓
[Layer B: transposition — geometric/columnar/route]
    ↓
K4 ciphertext (97 chars)
```

**Evidence:** Non-uniform local IC (segments vary 0.058–0.071). Transposition-first yields uniform IC. The confirmed ciphertext segments at positions 22–34 (EAST+NORTHEAST) have characters that were not adjacent pre-transposition — the transposition scattered them to those positions.

### 1.2 Confirmed Cribs

| Position (0-idx) | Cipher    | Plain     | Source       |
|------------------|-----------|-----------|--------------|
| 22–25            | LRVQ      | EAST      | Sanborn 2023 |
| 26–34            | QPRNGKSSO | NORTHEAST | Sanborn 2020 |
| 63–68            | NYPVTT    | BERLIN    | Sanborn 2010 |
| 69–73            | MZFPK     | CLOCK     | Sanborn 2014 |

> **Index note:** Community docs and some files in this repo use 1-indexed positions. The values above are 0-indexed (Python convention). `CONTRIBUTING.md` has an off-by-one error: `'NORTHEAST': [25]` should be `[26]`; `'BERLIN': [64]` should be `[63]`.

### 1.3 Derived Vigenère-Equivalent Keystreams

```
EAST (pos 22–25):      HRDX   — shifts [7, 17, 3, 23]
NORTHEAST (pos 26–34): DBAUZGSAV — shifts [3, 1, 0, 20, 25, 6, 18, 0, 21]
BERLIN (pos 63–68):    MUYKLG — shifts [12, 20, 24, 10, 11, 6]
CLOCK (pos 69–73):     KORNA  — shifts [10, 14, 17, 13, 0]
```

These are the effective per-position shifts AFTER transposition has rearranged things. Under the composite model these are not the raw substitution key letters — they are the convolution of the transposition permutation and the substitution key.

### 1.4 Ruled-Out Attack Vectors

| Attack | Module | Result | Key Reason |
|--------|--------|--------|------------|
| Single-layer repeating Vigenère | n/a | RULED OUT | HRDXDBAUZGSAV as repeating key produces no English outside crib window |
| Simple Caesar / monoalphabetic | n/a | RULED OUT | IC ≈ 0.062 rules out single-alphabet substitution |
| Direct Berlin Clock Vigenère (all 720 states) | `run_composite_sweep` | RULED OUT | Shifts 17, 20, 25 exceed max clock row value of 11; all 720 states tested |
| Transposition-first composite | n/a | RULED OUT | Non-uniform IC; transposition-first produces uniform IC |
| PALIMPSEST / ABSCISSA as K4 Vigenère keys | community + pipeline | RULED OUT | No match at any crib position |
| Keyed alphabet realignment (KRYPTOS/PALIMPSEST/ABSCISSA) | `check_keyed_alphabet_realignment` | NULL | Keystream at EAST+NORTHEAST does not simplify under any of the three alphabets |
| Full 2-layer sweep: 3 alphabets × 3 grids × 720 clock states × ENE+columnar routes | `run_composite_sweep` | NULL | Best candidates ≤1 keyword hit; no simultaneous 4-crib match |
| ENE diagonal route transposition (67.5°) | `read_ene_diagonal` | NULL | Tested in full sweep; no breakthrough |
| Clock → Hill 2×2 invertibility pre-filter | `run_clock_hill_attack` | NULL | ~100 invertible states; all tested; no crib match |
| 4-char clock key → Vigenère | `run_clock_vigenere_attack` | NULL | 4 encoding schemes × 720 states |
| Non-standard Berlin Clock sub-row encodings | `run_clock_subrow_attack` | NULL | 5-hr only, 1-hr only, minute rows, row sums |
| Berlin Clock lamp counts as transposition column widths | `run_clock_transposition_attack` | NULL | Lamp values [4,3,11,4] as columnar widths |
| Beaufort cipher sweep | `run_beaufort_sweep` | NULL | 10 key candidates × 2 alphabets |
| Quagmire I–IV (all variants) | `run_quagmire_sweep` | NULL | 6,240 combinations; Q3 Berlin Clock minute-state indicator keys |
| Physical-grid tableau walk (108 geometric routes) | `run_physical_grid_attack` | NULL | KRYPTOS Vigenère tableau × Quagmire III; 0 positional crib hits |
| ADFGVX (Polybius + columnar) | `kryptos.k4.adfgvx` | NULL | Ground-truth verified; no K4 crib match |
| Nihilist (Polybius + numeric key) | `kryptos.k4.nihilist` | NULL | Ground-truth verified; no K4 crib match |

### 1.5 What the Completed Attacks Tell Us

1. **The substitution key is not derivable directly from any standard clock encoding.** Every plausible 1- or 2-value clock reading scheme has been tested as a Vigenère key. The keystream shifts (including 17, 20, 25) cannot come from any Berlin Clock row value alone.

2. **The transposition is not a standard grid geometry read in any simple order.** All three prime-97 grid factorizations (10×10, 7×14, 8×13) plus ENE diagonal routing have been exhausted.

3. **The substitution is not any Quagmire variant with known keywords.** K3 uses Quagmire III with the KRYPTOS tableau — K4 does not use the same family in any of the combinations tested.

4. **The architecture requires at least one step we haven't correctly parameterized.** Either: (a) there is a 3rd cipher layer, (b) there is a pre-cipher masking step, (c) the key is derived from a source we haven't modeled, or (d) the transposition geometry is non-standard (e.g., not a rectangular grid).

---

## Dimension 2 — PRESENT: Current Working Hypotheses

### 2.1 The "Five or Six Techniques" Breakdown

Sanborn confirmed "five or six techniques" (Wired, 2005). Based on K1–K3 progression:

| Technique | K1 | K2 | K3 | K4 (hypothesis) |
|-----------|----|----|----|----|
| Keyed alphabet (KRYPTOS set) | ✅ | ✅ | — | Likely |
| Vigenère polyalphabetic substitution | ✅ (PALIMPSEST) | ✅ (ABSCISSA) | — | Likely variant |
| Columnar/route transposition | — | — | ✅ (double rotation) | Likely |
| Berlin Clock key derivation | — | — | — | Likely (clue) |
| Deliberate misspelling encoding | ✅ IQLUSION | — | ✅ DESPARATLY | Probable |
| Third substitution/fractionation layer | — | — | — | Possible |

**Working hypothesis:** K4 uses 3 layers — (1) keyed alphabet substitution with the KRYPTOS set, (2) a Vigenère pass keyed by a Berlin Clock reading at a specific timestamp, and (3) a columnar transposition whose column order is also derived from the clock. This is the smallest extension of the K1–K3 pattern that reaches "five or six techniques."

### 2.2 The CIA Dedication Timestamp as Clock State

The CIA dedication ceremony for Kryptos was November 3, 1990 at approximately 13:00 local time (18:00 UTC). The Berlin Clock lamp state at 13:00:00:

```
Seconds:   ON  (even second)
5-hr row:  [R][R][0][0]  → 2 × 5 = 10
1-hr row:  [R][R][R][0]  → 3 × 1 = 13 → hours = 13
5-min row: [Y][Y][Y][Y][Y][Y][0][0][0][0][0] → 6×5=30
1-min row: [Y][0][0][0]  → 1 min
           → 13:31 (full lamp encoding including seconds parity)
```

This specific timestamp has **not** been tested as a constrained clock state for the 3-layer composite (keyed-alphabet → Vigenère at 13:31 → columnar transposition). It is a strong prior because Sanborn encoded the sculpture at the dedication event.

### 2.3 InstructionalScorer Integration

`kryptos.k4.scoring_instructional` is fully wired into the composite pipeline and boosts candidates containing:
- Cardinal directions: NORTH, SOUTH, EAST, WEST, NORTHEAST, etc.
- Spatial words: BETWEEN, UNDER, ABOVE, ALONG, SHADOW, LINES
- Measurement words: FEET, METERS, DEGREES, COORDINATES
- Imperative verbs: LOOK, GO, TURN, DIG, FIND, SEEK

This is critical because the K4 plaintext may be a set of instructions (coordinates, navigation steps) rather than narrative prose. Standard n-gram scoring would penalize such a plaintext. The InstructionalScorer counteracts this bias.

### 2.4 The Eureka Protocol

`kryptos.k4.eureka.check_eureka` is wired into `CompositeChainExecutor`. On any simultaneous 4-crib match (EAST + NORTHEAST + BERLIN + CLOCK at confirmed positions), it:
1. Raises `EurekaSignal` to halt all secondary workers
2. Writes `K4_BREAKTHROUGH_SNAPSHOT.md` with full parameter state
3. Triggers terminal alert

Any new pipeline that chains stages must import and call `eureka_check_and_capture` after each candidate is scored.

### 2.5 Physical and Visual Interpretation (Out of Scope for Automated Pipeline)

Sanborn has said "Who says it is even a math solution?" — hinting that the World Clock is a visual cipher. The CLOCK.md source doc describes:
- Physical shadows from the rotating solar system sculpture
- "Go between the lines" as a reading instruction
- The 148-city ring as a substitution alphabet

These interpretations require physical or photographic access to the sculptures and are out of scope for the automated pipeline. They are documented here as a lower-probability path that would require a different methodology entirely.

---

## Dimension 3 — FRONTIER: Untested Directions (Priority-Ordered)

### 🔴 P1 — 3-Layer Composite: Keyed-Alphabet → Clock-Vigenère → Columnar Transposition

**Why this is the highest-priority untested vector:**
- All components are already implemented in the codebase
- It is the minimum extension of the K1–K3 pattern that reaches "five or six techniques"
- The search space is ~51,840 combinations — trivial to exhaust in minutes
- No prior sweep tested this 3-layer chain

**Parameter grid:**
```
Alphabet keys:  KRYPTOS, PALIMPSEST, ABSCISSA (3)
Clock states:   all 720 (12-hr × 60-min)
Column widths:  [4], [11], [4,4], [4,11,4] from clock lamp rows (4 variants)
Reading routes: row-major, column-major, ENE diagonal, reverse row (6 routes)
```

**Validation gate:** Simultaneous EAST+NORTHEAST+BERLIN+CLOCK match at confirmed 0-indexed positions after all three stages are reversed.

**Implementation note:** The 3-layer chain should be implemented as a `CompositeChainExecutor` variant: `keyed_alphabet_then_vigenere_then_transposition()`. The Eureka protocol must be wired at the final stage.

**Targeted variant:** Run the CIA dedication timestamp (13:31, Nov 3 1990) as a priority single clock state before the full 720-state sweep.

---

### 🔴 P2 — Shadow/Null Masking as Layer 0

**Why this matters:**
If any K4 characters are nulls inserted by Sanborn as "physical shadows" (World Clock shadow theory), then the effective message is shorter than 97 characters. Every attack that assumes 97 solid message characters is attacking padded input, which explains why no substitution key fits cleanly.

**Masking variants to test:**

| Variant | Description | Residue length |
|---------|-------------|----------------|
| Stride-2 | Remove every 2nd character (positions 1,3,5,...) | 49 chars |
| Stride-3 | Remove every 3rd character | 65 chars |
| Stride-4 | Remove every 4th character | 73 chars |
| Clock-shadow (lamp-off positions) | Remove chars at positions where the Berlin Clock lamp is unlit at a given timestamp | variable |
| Arc-fraction | Remove char at position ⌊(clock-hand angle / 360°) × 97⌋ and its neighborhood | ~88–96 chars |
| Block-8 skip | Remove every 8th char (KRYPTOS alphabet period) | 85 chars |

**Recalculation required:** After each masking step, crib positions must be recalculated in the residue. EAST at original position 22 may move to 20, 18, or another position depending on which characters were removed.

**Implementation plan:** Add a `make_masking_stage_v2(mode)` that supports all six variants, recalculates positional cribs in the residue, and feeds the output into the existing 2-layer composite sweep.

---

### 🟠 P3 — K2 Coordinate Digits as Clock State Selectors

**Motivation:** The K2 plaintext encodes a specific geographic location:
```
THIRTY EIGHT DEGREES FIFTY SEVEN MINUTES SIX POINT FIVE SECONDS NORTH
SEVENTY SEVEN DEGREES EIGHT MINUTES FORTY FOUR SECONDS WEST
```

As digits: `38 57 6 5` (N) and `77 8 44` (W). These can be read as HH:MM timestamp pairs:

| Reading | HH:MM | Notes |
|---------|-------|-------|
| 38%24 : 57 | 14:57 | Hour wrap-around |
| 06 : 05 | 06:05 | Direct |
| 17 : 08 | 17:08 | 77%24=17, 8 min |
| 08 : 44 | 08:44 | Direct |
| 38 : 57 | 13:57 | 38%24 alt reading |

Each of these timestamps should be used as the clock state for Hill 2×2 (if invertible) and for Vigenère key derivation, rather than sweeping all 720 states. If Sanborn encoded a metadata pointer from K2 into K4's key, this is how it would manifest.

---

### 🟠 P4 — 6-Hour Timezone Offset as Cipher Modifier

**Motivation:** Berlin is UTC+1; CIA Langley, Virginia is UTC−5. The offset is 6 hours exactly. If Sanborn set the encryption clock at Berlin local time but the "read time" is CIA local time, then the nominal clock state is shifted by 6 hours from the Berlin reading.

**Specific applications:**
1. For each clock-state-based attack, also test the state shifted by ±6 hours (±360 minutes, ±360 mod 720 in the state index)
2. Apply a Caesar shift of 6 to any derived Vigenère key
3. Offset the starting column in columnar transposition by 6

This is a 2× expansion of any clock-based sweep at negligible cost.

---

### 🟡 P5 — BERLIN+CLOCK Partial Match Isolation

**Motivation:** The full sweep required simultaneous 4-crib hits (EAST + NORTHEAST + BERLIN + CLOCK). Requiring all four simultaneously may have suppressed candidates where the transposition was right for two of the four cribs but the substitution key was wrong.

**Approach:** Rerun the inverse transposition sweep with a 2-crib gate (BERLIN+CLOCK at positions 63–73 only). Log all candidates that satisfy even 1 of the 4 cribs. Sort by combined score. Manually inspect the top-10 near-misses — they may reveal the correct transposition geometry even without the full key.

---

### 🟡 P6 — Running Key from K3 Plaintext

**Motivation:** Sanborn said the sections build on each other. K3's plaintext is ~336 characters. The first 97 characters of K3's output could serve as a running Vigenère key for K4 — a "book cipher" where the book is the previous section.

**Implementation:** Extract first 97 chars of K3 decrypted plaintext. Apply as Vigenère key to K4 ciphertext (with and without keyed alphabet pre-substitution). Validate EAST+NORTHEAST cribs in the result.

**K3 plaintext first 97 chars (approximate):**
`SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVED`

---

### 🟡 P7 — Gronsfeld Cipher (Numeric Key from K2 Coordinates)

**Motivation:** Gronsfeld is a Vigenère variant where the key is a sequence of decimal digits (0–9), making each key step a shift of 0–9 rather than 0–25. This drastically reduces the key space and is hand-encryptable. The K2 coordinate digits form natural numeric keys.

**Candidate keys:**
- `385765` (38°57'6.5"N, truncated to 6 digits)
- `770844` (77°8'44"W)
- `385706577` (full N coordinate)
- `3857` (hour and minute of one K2 reading)

**Not yet implemented.** Requires a `gronsfeld_decrypt(ciphertext, digit_key)` function and a sweep integrated with the 4-crib gate.

---

### 🔵 P8 — Myszkowski Transposition Variant

**Motivation:** Myszkowski transposition uses a repeated-letter keyword to determine column reading order. Columns under the same letter are read together, left-to-right. This is an edge case of columnar transposition not yet tested in isolation. With the KRYPTOS keyword (repeating T), it produces a non-standard columnar ordering that the general columnar solver would not enumerate.

---

### 🔵 P9 — Trifid Cipher

**Motivation:** Trifid extends Bifid to a 27-letter cube (adding a period or null character). It fractionates and interleaves triples rather than pairs. If K4 contains exactly 97 characters and the plaintext is ~32 "real" characters with interleaved fractionation, the effective message could be much shorter. Not implemented; medium-low probability given K1–K3 progression doesn't use Trifid.

---

### ⬜ P10 — Straddle Checkerboard

**Motivation:** Used by Soviet-era agents (Cold War theme matches Kryptos). The straddle checkerboard assigns variable-length codes to letters (high-frequency letters get 1 digit, others get 2), producing a compressed representation. If K4's 97 ciphertext characters came from a 60-character plaintext via checkerboard expansion, the effective message density would be different from what scoring assumes. Not yet implemented.

---

## Attack Gap Summary Table

| Vector | Priority | Status | Estimated Combos | Expected Runtime |
|--------|----------|--------|-----------------|-----------------|
| 3-layer: keyed-alphabet → Vigenère → columnar | 🔴 P1 | NOT RUN | ~51,840 | < 1 min |
| Shadow/null masking as Layer 0 | 🔴 P2 | NOT RUN | ~12 variants × full sweep | < 5 min |
| K2 coordinate digits as clock timestamps | 🟠 P3 | NOT RUN | 5–8 specific states | Seconds |
| 6-hour timezone offset modifier | 🟠 P4 | NOT RUN | 2× any clock sweep | Negligible |
| BERLIN+CLOCK 2-crib soft filter | 🟡 P5 | NOT RUN | Full transposition space | < 5 min |
| Running key from K3 plaintext | 🟡 P6 | NOT RUN | 2–4 combinations | Seconds |
| Gronsfeld numeric key cipher | 🟡 P7 | NOT IMPLEMENTED | ~4 keys | After implementation |
| Myszkowski transposition variant | 🔵 P8 | NOT RUN | ~720 × few | < 1 min |
| Trifid cipher | 🔵 P9 | NOT IMPLEMENTED | — | After implementation |
| Straddle Checkerboard | ⬜ P10 | NOT IMPLEMENTED | — | After implementation |

---

## Implementation Checklist for Next Session

```
[ ] 1. Implement `CompositeChainExecutor.keyed_alphabet_then_vigenere_then_transposition()`
        - Wire Eureka gate at final stage
        - Test at CIA dedication timestamp (13:31) first as priority single state
        - Then run all 720 × 3 alphabets × 4 column variants × 6 routes

[ ] 2. Implement `make_masking_stage_v2(mode)` with 6 masking variants
        - Add positional crib recalculation for the masked residue
        - Feed each residue into the existing 2-layer composite sweep

[ ] 3. Isolate K2 coordinate timestamps (14:57, 06:05, 17:08, 08:44)
        - Test each as clock state for Hill 2×2 (if invertible) + Vigenère
        - Log results with timestamp metadata

[ ] 4. Add ±6-hour offset variants to all clock-based sweep parameters

[ ] 5. Implement `gronsfeld_decrypt(ciphertext, digit_key)` in `kryptos.k4.gronsfeld`
        - Test with K2 coordinate digit keys
        - Add to public API

[ ] 6. Rerun inverse transposition sweep with BERLIN+CLOCK-only 2-crib gate
        - Log all 1-crib and 2-crib near-misses
        - Generate near-miss artifact for manual review

[ ] 7. Test running-key attack: first 97 chars of K3 plaintext as Vigenère key for K4
```

---

## Structural Constraints That Any Solution Must Satisfy

1. **EAST decrypts at 0-indexed positions 22–25** (cipher LRVQ → plain EAST)
2. **NORTHEAST decrypts at 0-indexed positions 26–34** (cipher QPRNGKSSO → plain NORTHEAST)
3. **BERLIN decrypts at 0-indexed positions 63–68** (cipher NYPVTT → plain BERLIN)
4. **CLOCK decrypts at 0-indexed positions 69–73** (cipher MZFPK → plain CLOCK)
5. **Substitution occurs before transposition** (IC evidence)
6. **The solution must be hand-encryptable** — Sanborn encrypted without computers, using a lookup table or physical device (consistent with clock-based keying)
7. **Deliberate misspelling likely** — K1 (IQLUSION) and K3 (DESPARATLY) both have intentional errors; K4 probable plaintext should be scored with Levenshtein tolerance of 1–2
8. **The plaintext is likely instructional** — EAST, NORTHEAST, BERLIN, CLOCK are all directional/referential words; the full plaintext may be geographic instructions rather than narrative prose

---

## Related Documents

- [`docs/analysis/K4_ACTIVE_RESEARCH.md`](K4_ACTIVE_RESEARCH.md) — Living document: confirmed facts, ruled-out hypotheses, active queue
- [`docs/analysis/K4_KEYSTREAM_ANALYSIS.md`](K4_KEYSTREAM_ANALYSIS.md) — Detailed keystream derivation from the 4 Sanborn cribs
- [`docs/analysis/K4-T1.md`](K4-T1.md) — Physical-geometric resolver specification with toggle matrix
- [`docs/sources/CLOCK.md`](../sources/CLOCK.md) — World Clock geographic and cryptographic interpretation
- [`docs/sources/SANBORN.md`](../sources/SANBORN.md) — Artist-clue research checklist
- [`docs/analysis/30_YEAR_GAP_COVERAGE.md`](30_YEAR_GAP_COVERAGE.md) — Classical cipher technique coverage assessment
- [`docs/ROADMAP.md`](../ROADMAP.md) — Frontier attack vectors and milestones
- [`docs/TASKS.md`](../TASKS.md) — Implementation backlog with specific next steps
