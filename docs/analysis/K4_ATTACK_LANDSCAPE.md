# K4 Attack Landscape — 3D Fingerprint

Breadcrumb: Home > Docs > Analysis > Attack Landscape

**Generated:** 2026-08-12
**Last corrected:** 2026-08-30 — see note below
**Framework:** Three-dimensional "pundit squad" model — Past / Present / Frontier
**Purpose:** Give any session a complete orientational picture of where we stand and where to go next.

> **⚠️ Staleness note (2026-08-30):** Section 3 below (P1–P10) was written 2026-08-12 and, until this correction, still described P1–P7 as untested despite all seven having complete implementations, real null results, and permanent artifacts by this date (P1/P3/P4/P7 recorded in an earlier session; P2/P5/P6 were wired into the dashboard API but never actually executed until this pass closed that gap — see `docs/analysis/K4_ACTIVE_RESEARCH.md`'s Phase 2/4 sections for full detail and artifact names). P8–P10 are also complete (a later session, item 14). Every priority section and the summary table below have been corrected in place; the original motivation text for each is preserved.

> **Quick orientation:** K4 is a 97-character ciphertext carved in copper at CIA HQ, unsolved since 1990. Sculptor Jim Sanborn has confirmed four plaintext anchors and described "five or six techniques." The architecture is confirmed as **substitution → transposition → K4 ciphertext** (not transposition-first). All systematically-tested single-layer and 2-layer attack sweeps, and now all ten P1–P10 frontier directions below, have returned null results — see §1.4 and §3 for the complete annotated list. The genuine frontier now is: the parts of the Physical/Geometric Pivot's own search space that are built but not yet wired into the default sweep (the reflection module's transpose family), a fourth cipher layer (Sanborn's "five or six techniques" implies at least one more than the three-layer chains tested so far), and anything requiring physical/photographic access to the sculpture.

---

## Dimension 1 — PAST: What We Have Covered and What It Proved

### 1.1 Confirmed Architecture

```text
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

```text
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

2. **The transposition is not a standard grid geometry read in any simple order.** All three candidate padded grid geometries (10×10, 7×14, and 8×13 — 97 is prime, so each pads with null characters to fill the grid) plus ENE diagonal routing have been exhausted.

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

The CIA dedication ceremony for Kryptos was November 3, 1990 at approximately 13:00 CIA local time (EST = UTC−5), which is 18:00 UTC and 19:00 Berlin local time (CET = UTC+1). The Berlin Clock lamp state encoding 13:00 (CIA local time on the clock):

```text
Seconds:   ON  (even second)
5-hr row:  [R][R][0][0]  → 2 × 5 = 10
1-hr row:  [R][R][R][0]  → 3 × 1 = 3 → hours = 13
5-min row: [0][0][0][0][0][0][0][0][0][0][0] → 0
1-min row: [0][0][0][0]  → 0 min
           → 13:00 exactly
```

These timestamps have **not** been tested as constrained clock states for the 3-layer composite (keyed-alphabet → Vigenère → columnar transposition). Both 13:00 CIA local and 19:00 Berlin local are strong priors because Sanborn encoded the sculpture at the dedication event. They produce distinct Berlin Clock lamp states and should each be run as priority single-state sweeps before exhausting all 720 states.

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

### ✅ P1 — 3-Layer Composite: Keyed-Alphabet → Clock-Vigenère → Columnar Transposition (COMPLETE — NULL RESULT)

**Result:** Implemented as `kryptos.k4.three_layer_composite.run_three_layer_composite`. CIA dedication timestamps tested first as priority states, then the full hourly sweep, 3 alphabets × grid widths `[7,8,10]` × brute-force columnar permutation. Null. Artifact: `K4_3LAYER_NULL.json`. A follow-on, `run_three_layer_composite_geometric`, swaps the columnar layer for the Physical/Geometric Pivot's named 24-column permutations — also null (`K4_3LAYER_GEOMETRIC_NULL.json`, `K4_3LAYER_GEOMETRIC_FULL_NULL.json`).

**Why this was the highest-priority untested vector (original rationale, preserved):**
- All components are already implemented in the codebase
- It is the minimum extension of the K1–K3 pattern that reaches "five or six techniques"
- The search space is ~51,840 combinations — trivial to exhaust in minutes
- No prior sweep tested this 3-layer chain

**Parameter grid:**

```text
Alphabet keys:  KRYPTOS, PALIMPSEST, ABSCISSA (3)
Clock states:   all 720 (12-hr × 60-min)
Column widths:  [4], [11], [4,4], [4,11,4] from clock lamp rows (4 variants)
Reading routes: row-major, column-major, ENE diagonal, reverse row (6 routes)
```

**Validation gate:** Simultaneous EAST+NORTHEAST+BERLIN+CLOCK match at confirmed 0-indexed positions after all three stages are reversed.

**Implementation note:** The 3-layer chain should be implemented as a `CompositeChainExecutor` variant: `keyed_alphabet_then_vigenere_then_transposition()`. The Eureka protocol must be wired at the final stage.

**Targeted variant:** Run the CIA dedication timestamp (13:00 CIA local = 19:00 Berlin local, Nov 3 1990) as priority clock states before the full 720-state sweep.

---

### ✅ P2 — Shadow/Null Masking as Layer 0 (COMPLETE — NULL RESULT)

**Result:** All six masking variants implemented in `kryptos.k4.masking_v2` (crib-position recalculation included) and wired into the dashboard as attack `p2_shadow_masking`, but never actually executed until 2026-08-30 — the API only ever ran it into an ephemeral in-memory job, so no permanent result existed. Run for real: 8 variants × 3 alphabets × 3 grids × 24 hourly states × 500 perms = 2,304,000 candidates. 40 near-misses, all single-keyword coincidences (e.g. "EAST" appearing as a substring by chance), none positional or simultaneous. Null. Artifacts: `K4_MASK_*_NULL.json` (8 files).

**Why this matters (original rationale, preserved):**
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

### ✅ P3 — K2 Coordinate Digits as Clock State Selectors (COMPLETE — NULL RESULT)

**Result:** Isolated exactly these timestamps in `kryptos.k4.k2_clock_states.get_k2_clock_states`, wired into the dashboard as attack `p3_k2_coord_clock` — each state's clock-Vigenère shifts tested against all known keyed alphabets, then brute-force columnar transposition. Null (zero keyword hits across all states).

**Motivation (original rationale, preserved):** The K2 plaintext encodes a specific geographic location:

```text
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

### ✅ P4 — 6-Hour Timezone Offset as Cipher Modifier (COMPLETE — NULL RESULT)

**Result:** `kryptos.k4.k2_clock_states.get_tz_offset_states` applies the ±6h offset to the CIA-dedication states, wired as attack `p4_timezone_offset`. Null. The Physical/Geometric Pivot separately tests the same 6-hour offset as a *positional* grid permutation (`clock_rotation.BERLIN_LANGLEY_OFFSET_HOURS`) rather than a Vigenère-key-index shift — also null.

**Motivation (original rationale, preserved):** Berlin is UTC+1; CIA Langley, Virginia is UTC−5. The offset is 6 hours exactly. If Sanborn set the encryption clock at Berlin local time but the "read time" is CIA local time, then the nominal clock state is shifted by 6 hours from the Berlin reading.

**Specific applications:**
1. For each clock-state-based attack, also test the state shifted by ±6 hours (±360 minutes, ±360 mod 720 in the state index)
2. Apply a Caesar shift of 6 to any derived Vigenère key
3. Offset the starting column in columnar transposition by 6

This is a 2× expansion of any clock-based sweep at negligible cost.

---

### ✅ P5 — BERLIN+CLOCK Partial Match Isolation (COMPLETE — NULL RESULT)

**Result:** Wired as attack `p5_two_crib_filter` (`run_three_layer_composite(keyword_eureka_threshold=2)`) but, like P2, never actually executed until 2026-08-30. Run for real against both the brute-force transposition (34,560 candidates) and, for the first time, the Physical/Geometric Pivot's geometric transposition (`run_three_layer_composite_geometric`, 69,120 candidates, full clock sweep). Zero near-misses either way — null on both.

**Motivation (original rationale, preserved):** The full sweep required simultaneous 4-crib hits (EAST + NORTHEAST + BERLIN + CLOCK). Requiring all four simultaneously may have suppressed candidates where the transposition was right for two of the four cribs but the substitution key was wrong.

**Approach:** Rerun the inverse transposition sweep with a 2-crib gate (BERLIN+CLOCK at positions 63–73 only). Log all candidates that satisfy even 1 of the 4 cribs. Sort by combined score. Manually inspect the top-10 near-misses — they may reveal the correct transposition geometry even without the full key.

---

### ✅ P6 — Running Key from K3 Plaintext (COMPLETE — NULL RESULT)

**Result:** Implemented as `kryptos.k4.running_key.run_k3_running_key_attack` (4 variants: standard/KRYPTOS alphabet × direct/reversed key) with full `EurekaSignal` wiring, but — like P2 and P5 — never actually executed until 2026-08-30. Zero keyword hits on any variant. Null. Artifact: `K4_P6_RUNNING_KEY_NULL.json`.

**Motivation (original rationale, preserved):** Sanborn said the sections build on each other. K3's plaintext is ~336 characters. The first 97 characters of K3's output could serve as a running Vigenère key for K4 — a "book cipher" where the book is the previous section.

**Implementation:** Extract first 97 chars of K3 decrypted plaintext. Apply as Vigenère key to K4 ciphertext (with and without keyed alphabet pre-substitution). Validate EAST+NORTHEAST cribs in the result.

**K3 plaintext first 97 chars (approximate):**
`SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWERPARTOFTHEDOORWAYWASREMOVED`

---

### ✅ P7 — Gronsfeld Cipher (Numeric Key from K2 Coordinates) (COMPLETE — NULL RESULT)

**Result:** Implemented in `kryptos.k4.gronsfeld.run_gronsfeld_sweep` (was "not yet implemented" as of this doc's original writing — it is now). 5 K2-coordinate-derived digit keys tested. Null. Wired as attack `p7_gronsfeld`.

**Motivation (original rationale, preserved):** Gronsfeld is a Vigenère variant where the key is a sequence of decimal digits (0–9), making each key step a shift of 0–9 rather than 0–25. This drastically reduces the key space and is hand-encryptable. The K2 coordinate digits form natural numeric keys.

**Candidate keys:**
- `385765` (38°57'6.5"N, truncated to 6 digits)
- `770844` (77°8'44"W)
- `385706577` (full N coordinate)
- `3857` (hour and minute of one K2 reading)

**Not yet implemented.** Requires a `gronsfeld_decrypt(ciphertext, digit_key)` function and a sweep integrated with the 4-crib gate.

---

### ✅ P8 — Myszkowski Transposition Variant (COMPLETE — NULL RESULT)

**Result:** Implemented as `kryptos.k4.myszkowski.run_myszkowski_attack`. ABSCISSA and PALIMPSEST (the two Kryptos keys with repeated letters) × decrypt/encrypt direction = 4 candidates. Null. Artifact: `K4_MYSZKOWSKI_NULL.json`.

**Motivation (original rationale, preserved):** Myszkowski transposition uses a repeated-letter keyword to determine column reading order. Columns under the same letter are read together, left-to-right. This is an edge case of columnar transposition not yet tested in isolation. Keywords with repeated letters — for example ABSCISSA (A×2, S×2) or PALIMPSEST (P×2, S×2, T×2) — produce non-standard columnar groupings that the general columnar solver does not enumerate. KRYPTOS itself (K, R, Y, P, T, O, S) has no repeated letters and cannot demonstrate Myszkowski behavior; none of the Kryptos-family repeated-letter keywords have been specifically tested with the Myszkowski algorithm.

---

### ✅ P9 — Trifid Cipher (COMPLETE — NULL RESULT)

**Result:** Implemented as `kryptos.k4.trifid.run_trifid_attack`. 6 keyword candidates × 13 period lengths (3–97) = 78 candidates. Null. Caught and fixed a real bug during implementation: naive `isalpha()` cleaning silently stripped the cube's 27th filler symbol, corrupting decrypt block boundaries. Artifact: `K4_TRIFID_NULL.json`.

**Motivation (original rationale, preserved):** Trifid extends Bifid to a 27-letter cube (adding a period or null character). It fractionates and interleaves triples rather than pairs. If K4 contains exactly 97 characters and the plaintext is ~32 "real" characters with interleaved fractionation, the effective message could be much shorter. Not implemented; medium-low probability given K1–K3 progression doesn't use Trifid.

---

### ✅ P10 — Straddle Checkerboard (COMPLETE — NULL RESULT)

**Result:** Implemented as `kryptos.k4.straddling_checkerboard.run_straddling_checkerboard_attack`, wired as attack `p15_straddling_checkerboard`. Null.

**Motivation (original rationale, preserved):** Used by Soviet-era agents (Cold War theme matches Kryptos). The straddle checkerboard assigns variable-length codes to letters (high-frequency letters get 1 digit, others get 2), producing a compressed representation. If K4's 97 ciphertext characters came from a 60-character plaintext via checkerboard expansion, the effective message density would be different from what scoring assumes. Not yet implemented.

---

## Attack Gap Summary Table

> **Scope:** 10 total frontier directions. All ten are now complete with null results (corrected 2026-08-30 — see the staleness note at the top of this document). "Estimated Combos"/"Expected Runtime" columns are left as originally written (pre-implementation estimates); actual figures are in each priority's Result note above and in `docs/analysis/K4_ACTIVE_RESEARCH.md`'s Ruled Out table.

| Vector | Priority | Status | Estimated Combos | Expected Runtime |
|--------|----------|--------|-----------------|-----------------|
| 3-layer: keyed-alphabet → Vigenère → columnar | P1 | ✅ COMPLETE — NULL | ~51,840 | < 1 min |
| Shadow/null masking as Layer 0 | P2 | ✅ COMPLETE — NULL | ~12 variants × full sweep | < 5 min |
| K2 coordinate digits as clock timestamps | P3 | ✅ COMPLETE — NULL | 5–8 specific states | Seconds |
| 6-hour timezone offset modifier | P4 | ✅ COMPLETE — NULL | 2× any clock sweep | Negligible |
| BERLIN+CLOCK 2-crib soft filter | P5 | ✅ COMPLETE — NULL | Full transposition space | < 5 min |
| Running key from K3 plaintext | P6 | ✅ COMPLETE — NULL | 2–4 combinations | Seconds |
| Gronsfeld numeric key cipher | P7 | ✅ COMPLETE — NULL | ~4 keys | After implementation |
| Myszkowski transposition variant | P8 | ✅ COMPLETE — NULL | ~few keywords | After P1–P7 |
| Trifid cipher | P9 | ✅ COMPLETE — NULL | — | After P1–P7 |
| Straddle Checkerboard | P10 | ✅ COMPLETE — NULL | — | After P1–P7 |

---

## Implementation Checklist for Next Session

*(Obsolete as of 2026-08-30 — all seven items below were completed across two sessions; kept for historical reference only. See `docs/analysis/K4_ACTIVE_RESEARCH.md`'s Physical/Geometric Pivot section for what to work on next, and the "K4 Field Notes" plan published 2026-08-29 for the currently-active checklist.)*

```text
[x] 1. Implement `CompositeChainExecutor.keyed_alphabet_then_vigenere_then_transposition()`
        -> kryptos.k4.three_layer_composite.run_three_layer_composite (+ _geometric variant)

[x] 2. Implement `make_masking_stage_v2(mode)` with 6 masking variants
        -> kryptos.k4.masking_v2, run 2026-08-30

[x] 3. Isolate K2 coordinate timestamps (14:57, 06:05, 17:08, 08:44)
        -> kryptos.k4.k2_clock_states.get_k2_clock_states

[x] 4. Add ±6-hour offset variants to all clock-based sweep parameters
        -> kryptos.k4.k2_clock_states.get_tz_offset_states + clock_rotation.BERLIN_LANGLEY_OFFSET_HOURS

[x] 5. Implement `gronsfeld_decrypt(ciphertext, digit_key)` in `kryptos.k4.gronsfeld`
        -> kryptos.k4.gronsfeld.run_gronsfeld_sweep

[x] 6. Rerun inverse transposition sweep with BERLIN+CLOCK-only 2-crib gate
        -> run 2026-08-30, both brute-force and geometric transposition

[x] 7. Test running-key attack: first 97 chars of K3 plaintext as Vigenère key for K4
        -> kryptos.k4.running_key.run_k3_running_key_attack, run 2026-08-30
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
