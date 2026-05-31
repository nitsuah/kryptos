# K4 Active Research State

**Last Updated:** 2026-05-25  
**Status:** Living document — update after each meaningful run or finding

This document tracks what is currently known, what has been tested and ruled out, and the active attack queue for K4 cryptanalysis.

---

## Confirmed Facts (High Confidence)

| Fact | Evidence | Source |
|------|----------|--------|
| K4 is 97 chars: `OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR` | Sculpture transcription | Community |
| Plaintext at 0-indexed 22–25 = EAST | Sanborn confirmed | 2023 |
| Plaintext at 0-indexed 26–34 = NORTHEAST | Sanborn confirmed | 2020 |
| Plaintext contains BERLIN | Sanborn confirmed | 2010 |
| Plaintext contains CLOCK (follows BERLIN) | Sanborn confirmed | 2014 |
| BERLIN ciphertext = NYPVTT at 0-indexed 63–68 | Deduced from community position | Community |
| CLOCK ciphertext = MZFPK at 0-indexed 69–73 | Deduced from community position | Community |
| Sanborn used "five or six techniques" | Direct quote | Wired, 2005 |
| Deliberate misspellings likely in K4 (pattern from K1, K3) | IQLUSION, DESPARATLY | K1/K3 solved |
| K4 IC ≈ 0.062 (near-English, not random) | Computed | Internal |
| Local IC non-uniform across segments | Computed | Internal |

---

## Ruled Out (Confirmed Negative Results)

| Hypothesis | Status | Evidence |
|------------|--------|----------|
| Single-layer repeating Vigenère with any key | RULED OUT | Running any known word or the derived 13-char keystream HRDXDBAUZGSAV as repeating key does not produce English outside crib window |
| Direct Berlin Clock single-layer Vigenère | RULED OUT | Clock values bounded 0–11; required keystream shifts include 17, 20, 25 which no clock row can produce. All 720 states tested. |
| Transposition-first composite | RULED OUT | Non-uniform local IC profile is a signature of transposition-AFTER-substitution; transposition-first would produce uniform IC |
| Simple Caesar or monoalphabetic substitution | RULED OUT | IC ≈ 0.062 rules out single-alphabet substitution (which would preserve IC close to English at 0.0667) |
| K1/K2 keys (PALIMPSEST, ABSCISSA) as direct Vigenère keys for K4 | RULED OUT | Previously tested by community; confirmed by CONTRIBUTING.md pipeline results |

---

## Current Structural Understanding

**Cipher architecture (most likely):**
```
plaintext
    ↓
[Layer A: substitution — likely polyalphabetic or matrix-based]
    ↓
pre-transposition text
    ↓
[Layer B: transposition — geometric/columnar/route]
    ↓
K4 ciphertext (97 chars)
```

**Decryption direction (attack):**
```
K4 ciphertext
    ↓
[Invert Layer B: transposition reversal]
    ↓
substituted-but-not-transposed text
    ↓
[Invert Layer A: substitution reversal with key]
    ↓
plaintext
```

**Key insight:** The 13 characters at K4 positions 22–34 (LRVQQPRNGKSSO) that produce EASTNORTHEAST under some key were NOT contiguous in the pre-transposition text. The transposition pulled them from scattered positions. Reversing the transposition first is the prerequisite for clean substitution key recovery.

### Derived Keystreams (Vigenère-equivalent per-position shifts)

Assuming pure Vigenère at the substitution layer (before transposition):

```
EAST (pos 22–25):      keystream = HRDX  (shifts: 7, 17, 3, 23)
NORTHEAST (pos 26–34): keystream = DBAUZGSAV  (shifts: 3, 1, 0, 20, 25, 6, 18, 0, 21)
BERLIN (pos 63–68):    keystream = MUYKLG  (shifts: 12, 20, 24, 10, 11, 6)
CLOCK (pos 69–73):     keystream = KORNA  (shifts: 10, 14, 17, 13, 0)
```

Under the composite model, these are NOT the actual substitution key letters at those positions — they are the effective shifts after the transposition has already rearranged things. The true key letters live at the transposition source positions, not the ciphertext positions.

---

## Active Attack Queue (Priority Order)

### Priority 1: Inverse Transposition + Keystream Collapse

**Goal:** Find transposition permutation P such that inverting P on K4 yields pre-transposition text where the keystream at EAST+NORTHEAST positions collapses to a recognizable pattern.

**Implementation plan:**
1. Enumerate grid geometries: 10×10 (pad 3), 7×14 (pad 1), 8×13 (pad 7)
2. For each geometry, implement ENE diagonal reading at θ=67.5° (tan≈2.414), extracting character order
3. Apply P⁻¹ (invert the ENE diagonal reading permutation) to K4 ciphertext
4. At the resulting positions for EAST+NORTHEAST, recompute keystream
5. Check if keystream = any Berlin Clock row vector, any keyword (KRYPTOS, PALIMPSEST, etc.), or any recognizable pattern
6. Also check columnar permutations with column widths [4, 11, 23, 24] derived from Berlin Clock lamp counts

**Success criterion:** Keystream resolves to a structured key (clock state, word, or bounded-value vector).

**Estimated search space:** ~few hundred permutations (3 geometries × variants). Sub-second.

### Priority 2: Keyed Alphabet Realignment

**Goal:** Check if using a non-linear alphabet (KRYPTOS or PALIMPSEST keyed) changes the derived keystream into a recognizable pattern.

**Implementation plan:**
1. For each keyed alphabet, remap character values before computing shifts
2. Recompute keystream at positions 22–34 under the keyed alphabet encoding
3. Check if resulting shift sequence maps to clock values, word letters, etc.

**Alphabets:**
- `KRYPTOSABCDEFGHIJLMNQUVWXZ` (used in K1/K2)
- `PALIMPSESTABCDFGHJKNOQRUVWXYZ`
- `ABSCISSADEFGHJKLMNOPQRTUVWXYZ`

**Search space:** 3 alphabets × 1 keystream computation each. Trivial.

### Priority 3: Full Composite Sweep (Clock × Grid × Alphabet)

**Goal:** Exhaustively test the 2,700-combination composite parameter space.

| Parameter     | Options               | Count |
|---------------|-----------------------|-------|
| Alphabet      | linear, KRYPTOS, PALIMPSEST | 3 |
| Grid geometry | 10×10, 7×14, 8×13     | 3     |
| ENE angle     | 67.5°, +/-5° variants | 3     |
| Clock states  | invertible Hill 2×2   | ~100  |

**Validation:** Each combination is accepted only if EAST+NORTHEAST AND BERLIN+CLOCK all validate simultaneously. Random false-positive rate is astronomically small with 4 simultaneous cribs (13+11=24 known chars).

### Priority 4: InstructionalScorer Integration

**Goal:** Stop penalizing K4 candidates that read as geographic instructions rather than narrative English.

**Implementation plan:**
- Add vocabulary boost for INSTRUCTIONAL_VECTORS (cardinal, spatial, measurement, imperative)
- Add Levenshtein ≤ 1 fuzzy match for Sanborn-style misspellings  
- Gate out candidates with entropy > 4.5 bits/symbol outside crib window (prevents crib-saturation false positives)
- Integrate into existing `combined_plaintext_score` or as separate `instructional_score` component

### Priority 5: BERLIN+CLOCK Positional Refinement

**Goal:** Verify or refine exact ciphertext positions for BERLIN and CLOCK, and compute their keystream under the same composite model.

The community positions (0-indexed 63–68 for BERLIN, 69–73 for CLOCK) are based on Sanborn's 2010/2014 clues. Verify these by:
1. Running all cipher candidates that satisfy EAST+NORTHEAST through BERLIN+CLOCK validation
2. If they do not independently match, re-examine whether the community position mapping is correct

---

## Existing Infrastructure Status

| Component | Status | Notes |
|-----------|--------|-------|
| Hill constraint stage | Working | Tests passing |
| Transposition adaptive stage | Working | Tests passing |
| Berlin clock (single-layer) | Working | Tested all 720 states; ruled out |
| Composite pipeline | Working | `run_composite_pipeline` + `CompositeChainExecutor` |
| Quadgram scoring | Working | High-quality TSV loaded |
| Positional crib bonus | Working | `make_transposition_multi_crib_stage` |
| InstructionalScorer | **Missing** | Needs implementation |
| ENE diagonal transposition | **Missing** | Needs implementation |
| Inverse transposition sweep | **Missing** | Needs implementation |
| Keyed alphabet realignment test | **Missing** | Needs implementation |
| Eureka capture protocol | **Missing** | Needs implementation |
| Period-13 keystream validator | **Missing** | Needs implementation |

---

## Position Reference Quick Table

All 0-indexed within K4 string starting with `OBKRUOXO...`:

```
Position  22: L   ← start of EAST crib window
Position  23: R
Position  24: V
Position  25: Q   ← end of EAST
Position  26: Q   ← start of NORTHEAST crib window
Position  27: P
Position  28: R
Position  29: N
Position  30: G
Position  31: K
Position  32: S
Position  33: S
Position  34: O   ← end of NORTHEAST
...
Position  63: N   ← start of BERLIN (1-indexed 64)
Position  64: Y
Position  65: P
Position  66: V
Position  67: T
Position  68: T   ← end of BERLIN
Position  69: M   ← start of CLOCK
Position  70: Z
Position  71: F
Position  72: P
Position  73: K   ← end of CLOCK
```

---

## Known Documentation Issues (Not Yet Fixed in Code)

| File | Issue | Correct Value |
|------|-------|---------------|
| `CONTRIBUTING.md` | `'NORTHEAST': [25]` in positional_cribs | Should be `[26]` |
| `CONTRIBUTING.md` | `'BERLIN': [64]` in positional_cribs | Should be `[63]` |
| `docs/analysis/K4-CLOCKS.html` | States NYPVTTMZF at "positions 26–34" | NYPVTTMZF is at 0-indexed 63–71; cipher at 26–34 is QPRNGKSSO |

---

## Related Documents

- [`docs/analysis/K4_KEYSTREAM_ANALYSIS.md`](K4_KEYSTREAM_ANALYSIS.md) — Detailed keystream derivation and what it rules out
- [`docs/analysis/K4-T1.md`](K4-T1.md) — Physical-geometric composite pipeline specification
- [`docs/analysis/K4-CLOCKS.html`](K4-CLOCKS.html) — Interactive clock theory framework
- [`docs/analysis/30_YEAR_GAP_COVERAGE.md`](30_YEAR_GAP_COVERAGE.md) — Cipher technique coverage map
- [`TASKS.md`](../../TASKS.md) — Implementation backlog
- [`ROADMAP.md`](../../ROADMAP.md) — Phase milestones
