# K4 Active Research State

Breadcrumb: Home > Docs > Analysis > K4 Active Research


**Last Updated:** 2026-08-12
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

## Completed Attack Queue — All Prior Vectors (as of 2026-08-12)

Rows 1–3 and 6–14 are cipher-attack sweeps that returned null results. Rows 4–5 are infrastructure/confirmed facts, not attack sweeps — they are included for completeness but should not be counted in null-result tallies.

| # | Attack / Capability | Module | Result |
|---|---------------------|--------|--------|
| 1 | Inverse Transposition + Keystream Collapse | `inverse_transposition_sweep.full_sweep` | **Null** |
| 2 | Keyed Alphabet Realignment (KRYPTOS/PALIMPSEST/ABSCISSA) | `check_keyed_alphabet_realignment` | **Null** |
| 3 | Full Composite Sweep (3 alphabets × 3 grids × 720 clock states × ENE+columnar) | `run_composite_sweep` | **Null** |
| 4 | InstructionalScorer (geography/imperative vocab boost + Levenshtein) | `scoring_instructional` | Integrated (infrastructure) |
| 5 | BERLIN+CLOCK Positional Refinement | `validate_k4_cribs` / `keystream_summary` | Confirmed (architecture) |
| 6 | Clock → Hill 2×2 Invertibility Pre-filter | `run_clock_hill_attack` | **Null** |
| 7 | 4-char Clock Key → Vigenère with NORTHEAST Anchor | `run_clock_vigenere_attack` | **Null** |
| 8 | Non-standard Berlin Clock Sub-row Encodings | `run_clock_subrow_attack` | **Null** |
| 9 | Berlin Clock Lamp Counts as Transposition Column Widths | `run_clock_transposition_attack` | **Null** |
| 10 | Beaufort Cipher Sweep (10 key candidates × 2 alphabets) | `run_beaufort_sweep` | **Null** |
| 11 | Quagmire I–IV (6,240 combos including Q3 Berlin Clock minute-state keys) | `run_quagmire_sweep` | **Null** |
| 12 | Physical-Grid Tableau Walk (108 geometric routes × 2 indicator bases) | `run_physical_grid_attack` | **Null** |
| 13 | ADFGVX (Polybius + columnar) | `kryptos.k4.adfgvx` | **Null** |
| 14 | Nihilist (Polybius + numeric key) | `kryptos.k4.nihilist` | **Null** |

---

## Active Attack Queue — FRONTIER (as of 2026-08-12)

Every clean 2-layer composite and every direct clock-keying variant has now returned null. The frontier shifts to: (a) 3-layer composites, (b) pre-cipher masking/null removal, and (c) clock key derivation approaches that treat K2 coordinates or timezone offsets as secondary inputs.

See [`docs/analysis/K4_ATTACK_LANDSCAPE.md`](K4_ATTACK_LANDSCAPE.md) for the full 3D fingerprint (past / present / frontier).

### 🔴 Priority 1 (OPEN): 3-Layer Composite — Keyed-Alphabet → Clock-Vigenère → Columnar Transposition

Sanborn confirmed "five or six techniques." All tested composites are 2-layer. A 3-layer pipeline combining (1) keyed-alphabet substitution, (2) clock-derived Vigenère, and (3) columnar transposition with clock-derived column widths has **never been run**. The InstructionalScorer is already wired in; the implementation needs to chain the three stages with full EAST+NORTHEAST+BERLIN+CLOCK crib gating.

**Estimated search space:** 3 alphabets × 720 clock states × 4 column-width variants × 6 reading routes ≈ 51,840 combinations. Sub-minute.

### 🔴 Priority 2 (OPEN): Shadow/Null Masking as Layer 0

The World Clock source material describes "the secret is the shadow of the word" — a physical position-masking theory where some K4 characters are null inserts (clock-shadow positions), and the real 64–88 character message is the remainder. If a masking layer preceded the cipher layers, every 2-layer attack on the full 97-char sequence is attacking padded input.

Specific variants to test:
- Remove every N-th character (N=2,3,4) → decrypt the residue
- Remove characters at positions corresponding to the clock-shadow angle at a specific timestamp (clock hand position → arc fraction × 97)
- Remove characters whose index is a clock-lamp-off position

**Estimated search space:** ~12 masking variants × full composite sweep. Each variant produces a shorter text; crib positions must be recalculated.

### 🟠 Priority 3 (OPEN): K2 Coordinate Digits as Clock State Selectors

The K2 plaintext contains explicit coordinates: `38 57 6 5 N` and `77 8 44 W`. As timestamp indices: hour=38%24=14, minute=57 → 14:57; or hour=6, minute=5 → 06:05; or other combinations. These specific clock states have not been isolated and tested against Hill or Vigenère attacks. Similarly, the W-coordinate digits (77, 8, 44) yield additional candidate timestamps (17:08, 08:44, etc.).

### 🟠 Priority 4 (OPEN): 6-Hour Berlin→CIA Timezone Offset as Cipher Modifier

Berlin is UTC+1; CIA Langley is UTC-5. The offset is 6 hours = 6 positions. If Sanborn encrypted at Berlin local time and intended the receiver at CIA HQ time, a shift of 6 applied to the clock-state index, or to the Vigenère key starting position, or to the columnar transposition key ordering, bridges the gap. Untested as a standalone parameter across all combinations.

### 🟡 Priority 5 (OPEN): BERLIN+CLOCK Partial Match Isolation

The full sweep validated all 4 cribs simultaneously. Relaxing to 2-crib validation (BERLIN+CLOCK only at positions 63–73) with a wider transposition search may surface partial-solution candidates that the strict 4-crib gate rejected. This is a softer filter that widens the search net.

### 🟡 Priority 6 (OPEN): Running Key from K3 Plaintext

K3's plaintext is approximately 336 characters. Using the first 97 characters of K3's decrypted plaintext as a running Vigenère key for K4 has never been attempted. Sanborn called K4 the "last layer" — if the sections are chained, earlier plaintext may be the key material for the next section.

### 🟡 Priority 7 (OPEN): Gronsfeld Cipher (Numeric Key from K2 Coordinates)

The Gronsfeld cipher is a Vigenère variant keyed by decimal digits. K2's coordinate string `385765` (38°57'6.5"N) or `770844` (77°8'44"W) produces a 6-digit numeric key. This is a direct reading of the K2 data as a numeric cipher key. Gronsfeld is not yet implemented in the codebase.

### 🔵 Deferred (LOWER PRIORITY): P8–P10

These three directions are structurally distinct but lower-probability given the K1–K3 pattern. Implement after P1–P7 are exhausted:

- **P8 — Myszkowski Transposition:** Repeated-letter keywords (ABSCISSA: A×2, S×2; PALIMPSEST: P×2, S×2, T×2) with Myszkowski column-grouping. Note: KRYPTOS itself has no repeated letters and does not demonstrate Myszkowski behavior. No infrastructure needed — can reuse columnar solver with grouped-column mode.
- **P9 — Trifid Cipher:** 27-letter cube fractionation (letter + period). Extends Bifid to triples. Medium-low probability given K1–K3 don't use Trifid. Requires new `kryptos.k4.trifid` module.
- **P10 — Straddle Checkerboard:** Variable-length encoding used by Cold War Soviet agents (thematically matches Kryptos). High-frequency letters get 1-digit codes, others get 2-digit codes. Tests whether K4's 97 cipher chars came from a ~60-char plaintext via checkerboard expansion. Requires new `kryptos.k4.straddle` module.

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
| Clock → Hill 2×2 invertibility pre-filter | ✅ Complete | `kryptos.k4.clock_hill_attack.run_clock_hill_attack` — filters clock states by Hill invertibility, applies Hill 2×2, validates 4 cribs. **Null result.** |
| 4-char clock key → Vigenère attack | ✅ Complete | `kryptos.k4.clock_hill_attack.run_clock_vigenere_attack` — 4 encoding schemes × 720 states; NORTHEAST positional gating. **Null result.** |
| Non-standard Berlin Clock sub-row encodings | ✅ Complete | `kryptos.k4.clock_subrow_attack.run_clock_subrow_attack` — 4 sub-row schemes as short Vigenère keys. **Null result.** |
| Berlin Clock lamp counts as transposition column widths | ✅ Complete | `kryptos.k4.clock_subrow_attack.run_clock_transposition_attack` — lamp values as columnar transposition widths. **Null result.** |
| Beaufort sweep against K4 | ✅ Complete | `kryptos.k4.beaufort_sweep.run_beaufort_sweep` — 10 key candidates × 2 alphabets. **Null result.** |
| Quagmire I–IV primitives | ✅ Complete | `kryptos.k4.quagmire` — canonical encrypt/decrypt for all four variants; Q3 with KRYPTOS tableau exactly reproduces K1/K2 (ground-truth tested). |
| Quagmire sweep against K4 | ✅ Complete | `kryptos.k4.quagmire_sweep.run_quagmire_sweep` — Q1–Q4 word keys + Q3 Berlin Clock minute-state indicator keys; positional crib gating; null result. |
| Physical-grid tableau-walk keystreams | ✅ Complete | `kryptos.k4.physical_grid.run_physical_grid_attack` — builds the KRYPTOS Vigenère tableau, walks 108 geometric routes into Quagmire III; positional crib gating; null result. |
| SA columnar transposition (seedable) | ✅ Verified | `solve_columnar_permutation_simulated_annealing(..., seed_perm=...)` — gains an optional starting permutation so the search can be seeded from a known pattern (e.g. K3's width/rotation). Verified end-to-end (`tests/e2e/test_sa_transposition_crib_lock.py`): recovers a planted columnar plaintext on realistic-length text; seeding at the optimum never scores worse than the seed. |
| Early-crib locking (search pruning) | ✅ Verified | `search_with_multiple_cribs_positions` rejects permutations that don't place the cribs at their known positions *before* scoring. Verified to prune >90% of the columnar permutation space at depth 1 (5040→2 for one crib, →1 for two) while always retaining the true permutation, and the top crib-consistent candidate is the real plaintext. Sidesteps the n-gram scoring misranking that affects short fragments. |

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

- [`docs/analysis/K4_ATTACK_LANDSCAPE.md`](K4_ATTACK_LANDSCAPE.md) — **3D attack fingerprint: past / present / frontier** (generated 2026-08-12)
- [`docs/analysis/K4_KEYSTREAM_ANALYSIS.md`](K4_KEYSTREAM_ANALYSIS.md) — Detailed keystream derivation and what it rules out
- [`docs/analysis/K4-T1.md`](K4-T1.md) — Physical-geometric composite pipeline specification with toggle matrix
- [`docs/analysis/K4-CLOCKS.html`](K4-CLOCKS.html) — Interactive clock theory framework (note: NORTHEAST position labels in that doc are incorrect; see K4_KEYSTREAM_ANALYSIS.md §1)
- [`docs/analysis/30_YEAR_GAP_COVERAGE.md`](30_YEAR_GAP_COVERAGE.md) — Classical cipher technique coverage map
- [`docs/analysis/K4-FRONTEND.md`](K4-FRONTEND.md) — React/FastAPI frontend for campaign orchestration
- [`docs/TASKS.md`](../../docs/TASKS.md) — Implementation backlog
- [`docs/ROADMAP.md`](../../docs/ROADMAP.md) — Phase milestones

## Vault Links
- [[repos/kryptos/docs/analysis/K4-FRONTEND|K4-FRONTEND]] — frontend specification
- [[repos/kryptos/docs/archive/AUDIT_2026-06-01|AUDIT_2026-06-01]] — most recent src/ audit
- [[repos/kryptos|kryptos runbook]] — repo context
