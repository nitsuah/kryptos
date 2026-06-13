# K4 Active Research State

Breadcrumb: Home > Docs > Analysis > K4 Active Research


**Last Updated:** 2026-05-31
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
| Single-layer repeating Vigenère with any key | RULED OUT | HRDXDBAUZGSAV as repeating key does not produce English outside crib window |
| Direct Berlin Clock single-layer Vigenère | RULED OUT | All 720 clock states tested (`run_composite_sweep`). Shifts include 17, 20, 25 which no clock row can produce alone. |
| Transposition-first composite | RULED OUT | Non-uniform local IC is a signature of substitution-then-transposition order |
| Simple Caesar or monoalphabetic substitution | RULED OUT | IC ≈ 0.062 rules out single-alphabet substitution |
| K1/K2 keys (PALIMPSEST, ABSCISSA) as direct Vigenère keys for K4 | RULED OUT | Confirmed by community + pipeline results |
| Keyed alphabet (KRYPTOS/PALIMPSEST/ABSCISSA) realignment → structured keystream | RULED OUT | `check_keyed_alphabet_realignment` tested all three alphabets; keystream at EAST+NORTHEAST positions does not resolve to a recognizable pattern under any of them |
| Full composite sweep: 3 alphabets × 3 grid sizes × 720 clock states × ENE+columnar routes | NULL RESULT | `run_composite_sweep` completed; no simultaneous 4-crib match. Null artifact: `K4_COMPOSITE_SWEEP_NULL.json`. Best candidates had ≤1 keyword hit. |
| ENE diagonal route transposition (67.5°) with clock-Vigenère | NULL RESULT | `read_ene_diagonal` integrated into full sweep; all route variants tested. No breakthrough. |
| ADFGVX (Polybius + columnar transposition) | NULL RESULT | Implemented (`kryptos.k4.adfgvx`) and tested against K4; no crib match |
| Nihilist (Polybius + numeric key) | NULL RESULT | Implemented (`kryptos.k4.nihilist`) and tested against K4; no crib match |
| Pure (single-layer) Quagmire I–IV | NULL RESULT | `run_quagmire_sweep` — 6,240 combinations: Q1/Q2/Q3 × 4 alphabet keywords × 10 word keys × 2 indicator bases, Q4 ordered keyword pairs, plus Q3 × 1,440 Berlin Clock minute-state indicator keys on the KRYPTOS tableau. Zero positional crib or keyword hits. Artifact: `K4_QUAGMIRE_NULL.json`. Reinforces the substitution+transposition composite model — implementation verified by exactly reproducing K1/K2 (Quagmire III, KRYPTOS tableau). |
| Physical-grid (copper-screen tableau) keystreams | NULL RESULT | `run_physical_grid_attack` — walks the 26×26 KRYPTOS Vigenère tableau along 108 geometric routes (26 rows, 26 columns, 26 main/26 anti diagonals, 4 serpentine reads) × 2 indicator bases = 216 candidates via Quagmire III. Zero positional crib hits. Artifact: `K4_PHYSICAL_GRID_NULL.json`. Tests the "physical keystream read off the sculpture" theory. (Note: on the cyclic tableau the diagonals are degenerate — anti-diagonals are constant letters, main diagonals 13-letter cycles — so rows/columns/serpentine are the substantive routes.) |

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

### ✅ DONE — Priority 1: Inverse Transposition + Keystream Collapse
`kryptos.k4.inverse_transposition_sweep.full_sweep` — all 3 grid geometries, ENE diagonal + columnar routes. **Null result.** No transposition permutation produced a recognizable keystream at EAST+NORTHEAST positions.

### ✅ DONE — Priority 2: Keyed Alphabet Realignment
`check_keyed_alphabet_realignment` — KRYPTOS, PALIMPSEST, ABSCISSA alphabets tested. **Null result.** No keyed alphabet remapping produces a structured keystream.

### ✅ DONE — Priority 3: Full Composite Sweep (Clock × Grid × Alphabet)
`run_composite_sweep` — 3 alphabets × 3 grids × 720 clock states × ENE+columnar routes. **Null result.** Artifact: `K4_COMPOSITE_SWEEP_NULL.json`. No simultaneous 4-crib match found.

### ✅ DONE — Priority 4: InstructionalScorer
`kryptos.k4.scoring_instructional` — vocabulary boost, Levenshtein fuzzy match, entropy gate. Integrated into sweep scoring pipeline.

### ✅ DONE — Priority 5: BERLIN+CLOCK Positional Refinement
Confirmed via `validate_k4_cribs` and `keystream_summary`. Positions 63–68 (BERLIN) and 69–73 (CLOCK) validated. Keystreams MUYKLG and KORNA computed and stored in `k4_keystream` DB table.

---

### Priority 1 (NEW): Clock → Hill 2×2 Invertibility Pre-filter

**Goal:** Use the Berlin Clock as a Hill 2×2 matrix key directly, not as a Vigenère shift sequence.

**The specific attack not yet run:**
1. For each of the 720 clock states, form a 2×2 matrix from the first 4 lamp values
2. Filter: only ~15% of clock states yield invertible matrices mod 26 (~100 candidates)
3. For each invertible state, apply Hill 2×2 decryption to K4 using that matrix
4. Validate EAST+NORTHEAST cribs in the result
5. If any match, try all column-width permutations on the result

This is distinct from what we've run: we've tested Hill keys exhaustively and clock-Vigenère exhaustively, but **never clock-as-Hill-matrix specifically**.

**Estimated search space:** ~100 clock states × Hill decryption. Trivial runtime.

### Priority 2 (NEW): 4-char Clock Key → Vigenère with NORTHEAST Anchor

**Goal:** Derive a 4-character Vigenère key from each clock state (not the full 4–8 char shift sequence) and test it with the NORTHEAST crib as a positional anchor.

**The gap:** Current sweep cycles through full `berlin_clock_shifts` output (variable length). This attack specifically maps each clock state to a 4-char key (e.g., hour-row sum, minute-row sum, etc. encoded as letters) and tests those as Vigenère keys with `positional_crib_bonus` gating on NORTHEAST at position 26.

**Estimated search space:** 720 states × a few encoding schemes. Sub-second.

### Priority 3 (NEW): Non-standard Berlin Clock encodings

**Goal:** The current sweep uses `full_berlin_clock_shifts` (all 4 lamp rows concatenated). Sanborn may have used a subset or different encoding:
- 5-hour row only (single digit 0–4)
- Top two rows only (5-hour + 1-hour = effective hour 0–23 as 2 values)
- Minute rows only (5-min + 1-min)
- Clock-position-to-alphabet mapping (row values → keyed alphabet offset)

None of these sub-encodings have been tested in isolation.

### Priority 4 (NEW): Berlin Clock × Transposition Column Widths

**Goal:** Use lamp counts from the Berlin Clock as columnar transposition widths, not as Vigenère shifts. At 23:59 the lamp rows show [4,3,11,4] — use these as column widths for a 4-round columnar transposition.

This was mentioned in `K4-T1.md` and `30_YEAR_GAP_COVERAGE.md` but the composite sweep used clock values as Vigenère shifts only, not as transposition column widths.

### Priority 5 (OPEN): Beaufort cipher sweep

`kryptos.k4.beaufort` is implemented but **no systematic sweep against K4 has been run**. Beaufort is the "reciprocal Vigenère" — encryption and decryption use the same operation. Worth a quick pass with the same key candidates used for Vigenère (KRYPTOS, PALIMPSEST, BERLIN, CLOCK, etc.).

---

## Existing Infrastructure Status

| Component | Status | Notes |
|-----------|--------|-------|
| Hill constraint stage | ✅ Working | Tests passing |
| Transposition adaptive stage | ✅ Working | Tests passing |
| Berlin clock (single-layer) | ✅ Complete | All 720 states tested; ruled out as standalone |
| Composite pipeline | ✅ Working | `run_composite_pipeline` + `CompositeChainExecutor` |
| Quadgram scoring | ✅ Working | High-quality TSV loaded from `data/ngrams/` |
| Positional crib bonus | ✅ Working | `make_transposition_multi_crib_stage` |
| InstructionalScorer | ✅ Complete | `kryptos.k4.scoring_instructional` — vocabulary, Levenshtein, entropy gate |
| ENE diagonal transposition | ✅ Complete | `read_ene_diagonal` in `transposition_routes.py`; integrated into `full_sweep` |
| Inverse transposition sweep | ✅ Complete | `kryptos.k4.inverse_transposition_sweep` — all 3 grid geometries, ENE+columnar routes |
| Keyed alphabet realignment test | ✅ Complete | `check_keyed_alphabet_realignment` — KRYPTOS/PALIMPSEST/ABSCISSA all tested; null result |
| Eureka capture protocol | ✅ Complete | `kryptos.k4.eureka` — 4-crib match, snapshot, halt wired into `CompositeChainExecutor` |
| Period-13 keystream validator | ✅ Complete | `kryptos.k4.keystream_validator` — `validate_k4_cribs`, `keystream_summary` |
| Full composite parameter sweep | ✅ Complete | `run_composite_sweep` — alphabets × grids × clock states × routes; null result |
| S→T→S 3-layer chain | ✅ Complete | `CompositeChainExecutor.substitution_then_transposition_then_substitution()` |
| ADFGVX | ✅ Complete | `kryptos.k4.adfgvx`; null result against K4 |
| Nihilist | ✅ Complete | `kryptos.k4.nihilist`; null result against K4 |
| Beaufort | ✅ Complete | `kryptos.k4.beaufort` (primitives); systematic K4 sweep now in `kryptos.k4.beaufort_sweep` |
| Clock → Hill 2×2 invertibility pre-filter | ✅ Implemented | `kryptos.k4.clock_hill_attack.run_clock_hill_attack` — filters clock states by Hill invertibility, applies Hill 2×2, validates 4 cribs. Null result expected on first run. |
| 4-char clock key → Vigenère attack | ✅ Implemented | `kryptos.k4.clock_hill_attack.run_clock_vigenere_attack` — 4 encoding schemes × 720 states; NORTHEAST positional gating at position 26. |
| Non-standard Berlin Clock sub-row encodings | ✅ Implemented | `kryptos.k4.clock_subrow_attack.run_clock_subrow_attack` — 4 sub-row schemes as short Vigenère keys. |
| Berlin Clock lamp counts as transposition column widths | ✅ Implemented | `kryptos.k4.clock_subrow_attack.run_clock_transposition_attack` — lamp values as columnar transposition widths. |
| Beaufort sweep against K4 | ✅ Implemented | `kryptos.k4.beaufort_sweep.run_beaufort_sweep` — 10 key candidates × 2 alphabets. |
| Quagmire I–IV primitives | ✅ Complete | `kryptos.k4.quagmire` — canonical encrypt/decrypt for all four variants; Q3 with KRYPTOS tableau exactly reproduces K1/K2 (ground-truth tested). |
| Quagmire sweep against K4 | ✅ Complete | `kryptos.k4.quagmire_sweep.run_quagmire_sweep` — Q1–Q4 word keys + Q3 Berlin Clock minute-state indicator keys; positional crib gating; null result. |
| Physical-grid tableau-walk keystreams | ✅ Complete | `kryptos.k4.physical_grid.run_physical_grid_attack` — builds the KRYPTOS Vigenère tableau, walks 108 geometric routes into Quagmire III; positional crib gating; null result. |

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
- [`docs/analysis/K4-FRONTEND.md`](K4-FRONTEND.md) — React/FastAPI frontend for campaign orchestration
- [`TASKS.md`](../../TASKS.md) — Implementation backlog
- [`ROADMAP.md`](../../ROADMAP.md) — Phase milestones

## Vault Links
- [[repos/kryptos/docs/analysis/K4-FRONTEND|K4-FRONTEND]] — frontend specification
- [[repos/kryptos/docs/archive/AUDIT_2026-06-01|AUDIT_2026-06-01]] — most recent src/ audit
- [[repos/kryptos|kryptos runbook]] — repo context
