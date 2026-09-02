# K4 Active Research State

Breadcrumb: Home > Docs > Analysis > K4 Active Research


**Last Updated:** 2026-09-02
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
| Combined 24-column geometric permutation + physical tableau (Physical/Geometric Pivot) | NULL RESULT | `run_geometry_combined_sweep` — 20 fill-orders/routes (16 `geometry24` orders incl. reversed + 4 ENE/NE route families) × 4 shape-preserving reflections × {0,+6,-6} Berlin/Langley rotation offsets × 3 remainder modes (trailing/leading/drop for the 97th char) × 108 `physical_grid` tableau routes × 2 indicator bases = **155,520 candidates**, ~7s. **Zero candidates matched even one positional crib** (`best_candidates` empty). Artifact: `K4_GEOMETRY_COMBINED_NULL.json`. This is the permutation front-end `physical_grid.py` lacked — see [Physical/Geometric Pivot](#physicalgeometric-pivot-2026-08-29) below. |
| Combined geometric permutation with geography-derived rotation offsets | NULL RESULT | Same sweep as above with `rotation_offsets` replaced by 6 geography-derived values (CIA→Berlin bearing mod 24, K2-coordinate-derived hours, magnetic declination) — **311,040 candidates**, ~14s. Zero positional crib hits (one incidental substring-only "EAST" keyword hit, not positionally correct). Artifact: `K4_GEOMETRY_COMBINED_GEO_NULL.json`. |
| Combined geometric permutation using the exact CIA→Berlin bearing as a route direction (item 12) | NULL RESULT | `order_names=GEO_BEARING_ORDER_NAMES` — the real ~44.4° great-circle bearing (not snapped to a named 16-point compass direction) and its 180°-reversed counterpart, traced via `ene_routes.trace_route`'s float-bearing support, × 4 reflections × {0,+6,-6} × 3 remainder modes × 108 tableau routes × 2 bases = **15,552 candidates**, <1s. Zero positional or keyword hits. Artifact: `K4_GEOMETRY_COMBINED_GEO_BEARING_NULL.json`. |
| Myszkowski transposition (P8) — repeated-letter keyword grouped-column transposition | NULL RESULT | `run_myszkowski_attack` (`kryptos.k4.myszkowski`) — `ABSCISSA` and `PALIMPSEST` (the two Kryptos keys that actually have repeated letters; KRYPTOS doesn't) × decrypt/encrypt direction = **4 candidates**. Zero positional or keyword hits. Artifact: `K4_MYSZKOWSKI_NULL.json`. |
| Trifid cipher (P9) — 27-cell (3×3×3) cube fractionation | NULL RESULT | `run_trifid_attack` (`kryptos.k4.trifid`) — 6 keyword candidates (KRYPTOS, PALIMPSEST, ABSCISSA, and 3 pairwise concatenations) × 13 period lengths (3–97) = **78 candidates**. Zero positional or keyword hits. Artifact: `K4_TRIFID_NULL.json`. |
| Simulated-annealing substitution-key search behind a Phase-1 geometric permutation front-end (item 15, optional) | NULL RESULT | `run_geometry_substitution_sa_sweep` (`kryptos.k4.geometry_substitution_search`) — 8 base `geometry24` fill orders (identity reflection, zero rotation, trailing remainder) × 3 SA restarts (3,000 iterations each, temperature/cooling schedule) = **24 candidates**, ~14s. Zero positional crib hits (one incidental substring-only "BERLIN" keyword hit, not positionally correct). Artifact: `K4_GEOMETRY_SUBSTITUTION_SA_NULL.json`. Fills a genuine gap in the existing heuristic-search infrastructure (`hill_genetic.py` is Hill-3×3-specific, `transposition_analysis.py`'s SA is columnar-permutation-specific): a proper SA search over the general substitution key space, paired with the Phase-1 geometric permutation inversion instead of only the handful of named keyed alphabets every other composite sweep tries. |
| Mengenlehreuhr → Weltzeituhr precise bearing (69.0°/70.8°) as route direction | NULL RESULT | `clock_rotation.mengenlehreuhr_weltzeituhr_bearings()` — real geodesic bearing between the Berlin Clock's current and 1990 (Sanborn-era) locations and the World Clock at Alexanderplatz, both within 1.5–3.3° of exact ENE. Wired into `geometry_combined_sweep.GEO_BEARING_ORDER_NAMES` automatically. **46,656 candidates**, zero positional or keyword hits. Artifact: `K4_GEOMETRY_COMBINED_GEO_BEARING_NULL.json`. |
| November 9 1989 (Berlin Wall fall) as priority clock state | NULL RESULT | `three_layer_composite.BERLIN_WALL_PRIORITY_TIMES` — 3 sourced CET moments (18:53/19:05/20:00) + EST equivalents, via `run_three_layer_composite_geometric`. **17,280 candidates**, zero hits. Artifact: `K4_3LAYER_GEOMETRIC_BERLINWALL_NULL.json`. |
| P2 shadow/null masking, thorough scope (already wired, never previously executed) | NULL RESULT | 8 masking variants × 4 alphabets × 2 grids (7/8 cols) × 2 clock states (00:00/12:00) × 24 perms/grid × 2 routes = **6,144 candidates**. 40 near-misses, all single-keyword coincidences, none positional or simultaneous. Artifacts: `K4_MASK_*_NULL.json` (8 files). |
| P5 BERLIN+CLOCK 2-crib relaxed gate — both brute-force and Phase-1 geometric transposition (already wired, never previously executed) | NULL RESULT | `run_three_layer_composite(keyword_eureka_threshold=2)` (34,560 candidates) and, for the first time, the same relaxed gate against `run_three_layer_composite_geometric` (69,120 candidates, full clock sweep). Zero near-misses either way. Artifacts: `K4_P5_2CRIB_NULL.json`, `K4_P5_GEOMETRIC_2CRIB_NULL.json`. |
| P6 K3 plaintext as running Vigenère key (already wired, never previously executed) | NULL RESULT | 4 variants (standard/KRYPTOS alphabet × direct/reversed key) = **4 candidates**, zero keyword hits. Artifact: `K4_P6_RUNNING_KEY_NULL.json`. |
| `reflection.py` shape-changing transpose family, wired into a sweep (Phase 7) | NULL RESULT | `composed_flat_indices` extended to handle the 4×24→24×4 transpose family correctly (verified bijection + round-trip). 3 runs: default scope (**155,520**), geography-derived offsets (**414,720**), and via `run_three_layer_composite_geometric` (**69,120**). Zero positional or keyword hits any way. Artifacts: `K4_GEOMETRY_COMBINED_SHAPECHANGING_NULL.json`, `K4_GEOMETRY_COMBINED_SHAPECHANGING_GEO_NULL.json`, `K4_3LAYER_GEOMETRIC_SHAPECHANGING_NULL.json`. |
| "Shadow of the word" as a computed shadow angle — World Clock topper rotation (full 0-23 sweep, then a resolved precise-angle sweep) and real solar azimuth at CIA HQ (Phase 7) | NULL RESULT | `kryptos.k4.solar_geometry` — solar-position algorithm verified against known reference points; topper-rotation hypothesis honestly reduced to a full-range sweep after finding every *whole-minute* sourced timestamp pair vacuously co-phased, then resolved for two sub-minute-precision timestamps sourced from Hertle's own press-conference transcript (18:52:40/19:00:54 CET). **1,244,160 + 103,680 candidates** (topper, full-range then precise) + **108,864 → 139,968 candidates** (solar bearing route directions, expanded with the precise timestamps). Zero hits. Artifacts: `K4_GEOMETRY_COMBINED_TOPPER_ROTATION_NULL.json`, `K4_GEOMETRY_COMBINED_TOPPER_PRECISE_NULL.json`, `K4_GEOMETRY_COMBINED_SOLAR_BEARING_NULL.json`. |
| World Clock's 146-city list as keyed-alphabet/numeric-offset source (Phase 7) | NULL RESULT | `kryptos.k4.world_clock_cities` — 119 individually-sourced city names (read directly off the sculpture's plates via 7 Wikimedia Commons photographs, ~20 of 24 segments; complete 146-name list still unavailable) as keyed alphabets (**9,720 → 112,320 → 128,520 candidates** across three passes, text-sourced then photograph-expanded twice) plus 3 sourced structural counts (146/147/24) as rotation offsets (**155,520 candidates**). Zero hits. Artifacts: `K4_WORLD_CLOCK_CITIES_NULL.json`, `K4_GEOMETRY_COMBINED_WORLDCLOCK_NULL.json`. |
| Cross-vector consensus scoring across every null-result artifact (Phase 7) | NULL RESULT | `kryptos.k4.cross_vector_consensus` — groups candidates by source attack vector (unlike P16's merged-pool count) and flags fragments appearing in ≥3 *distinct* vectors. Scanned 30 artifacts, 11 with extractable candidates: **zero cross-vector consensus anchors**. Artifact: `K4_CROSS_VECTOR_CONSENSUS_NULL.json`. |

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

*(This section's own P1–P10 entries below are the current record — the separate 3D-fingerprint document this line used to point to was archived 2026-09-01 as fully superseded; see [`docs/archive/K4_ATTACK_LANDSCAPE.md`](../archive/K4_ATTACK_LANDSCAPE.md) for its historical evidence-basis narrative only.)*

### ✅ Priority 1 (COMPLETE — NULL RESULT): 3-Layer Composite — Keyed-Alphabet → Clock-Vigenère → Columnar Transposition

*(Entry stale since 2026-08-12 — this doc listed it OPEN after it had already been implemented; corrected 2026-08-29 as part of the Physical/Geometric Pivot's doc-hygiene pass.)*

Implemented in `kryptos.k4.three_layer_composite.run_three_layer_composite` — chains (1) keyed-alphabet mono-substitution, (2) clock-derived Vigenère (CIA-dedication-timestamp states prioritized, then a full hourly sweep), and (3) brute-force columnar transposition at grid widths `[7, 8, 10]` (`K4_GRID_GEOMETRIES`), gated on all 4 confirmed cribs. **Null result.** Artifact: `K4_3LAYER_NULL.json`. Also wired into the API as `p1_three_layer` and, with a relaxed 2-crib gate, as `p5_two_crib_filter`. See the Physical/Geometric Pivot's `run_three_layer_composite_geometric` for the follow-on that swaps the brute-force columnar layer for the Pivot's 24-column named geometric permutations — a distinct search space (`K4_GRID_GEOMETRIES` never includes width 24), not a duplicate of this entry.

### ✅ Priority 2 (COMPLETE — NULL RESULT): Shadow/Null Masking as Layer 0

*(Entry stale since 2026-08-12 — listed OPEN after it had already been implemented and, as of Phase 4/v2.1 below, executed; corrected 2026-09-01.)*

The World Clock source material describes "the secret is the shadow of the word" — a physical position-masking theory where some K4 characters are null inserts (clock-shadow positions), and the real 64–88 character message is the remainder. If a masking layer preceded the cipher layers, every 2-layer attack on the full 97-char sequence is attacking padded input.

Implemented in `kryptos.k4.masking_v2` (8 variants: stride-2/3/4, block-8, clock-shadow×2, arc-fraction×2, crib positions recalculated per residue) and wired into the API as `p2_shadow_masking`. Executed for real in Phase 4/v2.1 (below) against `composite_sweep`: **6,144 candidates, null** — 40 near-misses, all single-keyword coincidences. Artifacts: `K4_MASK_*_NULL.json` (8 files).

Note: this closes the *masking-as-a-preprocessing-step* reading of "the secret is the shadow of the word." A separate, physically-literal reading — a real or mechanical shadow determining a transposition order rather than a null-removal mask — is still open; see Phase 7 in `docs/ROADMAP.md`.

### ✅ Priority 3 (COMPLETE — NULL RESULT): K2 Coordinate Digits as Clock State Selectors

*(Entry stale since 2026-08-12; corrected 2026-08-29.)*

`kryptos.k4.k2_clock_states.get_k2_clock_states` isolates exactly these timestamps (`K2_CLOCK_TIMES`: 14:57, 06:05, 17:08, 08:44, 13:57), wired into the API as `p3_k2_coord_clock` — each state's clock-Vigenère shifts tested against all `KNOWN_KEYED_ALPHABETS`, then brute-force columnar transposition at widths `[7, 8, 10]`. **Null result** (zero keyword hits across all states tested).

### ✅ Priority 4 (COMPLETE — NULL RESULT): 6-Hour Berlin→CIA Timezone Offset as Cipher Modifier

*(Entry stale since 2026-08-12; corrected 2026-08-29.)*

`kryptos.k4.k2_clock_states.get_tz_offset_states` applies the ±6-hour offset to the CIA-dedication clock states, wired into the API as `p4_timezone_offset` — same clock-Vigenère + columnar-transposition pipeline as Priority 3. **Null result.** The Physical/Geometric Pivot's `clock_rotation.py` (`BERLIN_LANGLEY_OFFSET_HOURS`, `PRIORITY_OFFSETS`) separately tests this same 6-hour offset as a *positional* permutation of the 24-column grid rather than a Vigenère-key-index shift — also null (see `docs/analysis/K4_ACTIVE_RESEARCH.md`'s Physical/Geometric Pivot section).

### ✅ Priority 5 (COMPLETE — NULL RESULT): BERLIN+CLOCK Partial Match Isolation

*(Entry stale since 2026-08-12 — listed OPEN after it had already been wired and, as of Phase 4/v2.1 below, executed; corrected 2026-09-01.)*

The full sweep validated all 4 cribs simultaneously. Relaxing to 2-crib validation (BERLIN+CLOCK only at positions 63–73) with a wider transposition search may surface partial-solution candidates that the strict 4-crib gate rejected. This is a softer filter that widens the search net.

Wired as `p5_two_crib_filter` (`run_three_layer_composite(keyword_eureka_threshold=2)`). Executed for real in Phase 4/v2.1 (below) against both the brute-force transposition (**34,560 candidates**) and, for the first time, the Physical/Geometric Pivot's own geometric transposition (**69,120 candidates**, full clock sweep). **Null both ways** — zero near-misses. Artifacts: `K4_P5_2CRIB_NULL.json`, `K4_P5_GEOMETRIC_2CRIB_NULL.json`.

### ✅ Priority 6 (COMPLETE — NULL RESULT): Running Key from K3 Plaintext

*(Entry stale since 2026-08-12 — listed OPEN after it had already been implemented and, as of Phase 4/v2.1 below, executed; corrected 2026-09-01.)*

K3's plaintext is approximately 336 characters. Using the first 97 characters of K3's decrypted plaintext as a running Vigenère key for K4 has never been attempted. Sanborn called K4 the "last layer" — if the sections are chained, earlier plaintext may be the key material for the next section.

Implemented in `kryptos.k4.running_key.run_k3_running_key_attack` (4 variants: standard/KRYPTOS alphabet × direct/reversed key). Executed for real in Phase 4/v2.1 (below): **4 candidates, null** — zero keyword hits on any variant. Artifact: `K4_P6_RUNNING_KEY_NULL.json`.

### ✅ Priority 7 (COMPLETE — NULL RESULT): Gronsfeld Cipher (Numeric Key from K2 Coordinates)

*(Entry stale since 2026-08-12 — said "not yet implemented"; corrected 2026-08-29.)*

Implemented in `kryptos.k4.gronsfeld.run_gronsfeld_sweep` — 5 K2-coordinate-derived digit keys (`K2_COORDINATE_KEYS`: `385765`, `770844`, `385706577`, `3857`, `3857065770844`) applied as Gronsfeld shifts. **Null result.** Wired into the API as `p7_gronsfeld`.

### 🔵 Deferred (LOWER PRIORITY): P8–P10

These three directions are structurally distinct but lower-probability given the K1–K3 pattern.

- ✅ **P8 — Myszkowski Transposition (COMPLETE — NULL RESULT, 2026-08-29):** Repeated-letter keywords (ABSCISSA, PALIMPSEST) with Myszkowski column-grouping (tied-rank columns read row-by-row together rather than one at a time). Note: KRYPTOS itself has no repeated letters and does not demonstrate Myszkowski behavior. Implemented as a self-contained `kryptos.k4.myszkowski` module (the grouped-row read pattern isn't reducible to `transposition.py`'s whole-column-read `apply_columnar_permutation`, so "reuse the columnar solver" from the original scoping note didn't hold up once the primitive was actually written). See Ruled Out table above.
- ✅ **P9 — Trifid Cipher (COMPLETE — NULL RESULT, 2026-08-29):** 27-cell (3×3×3) cube fractionation extending Bifid to triples. Implemented in `kryptos.k4.trifid` — keyword-mixed cube (reuses `quagmire.keyword_alphabet`) + a filler 27th symbol, block-wise encrypt/decrypt, swept across 6 keyword candidates × 13 period lengths. See Ruled Out table above.
- **P10 — Straddle Checkerboard:** Implemented in an earlier session (`kryptos.k4.straddling_checkerboard`) — out of scope for this pass, not touched here.

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
| 24-column grid + fill-order engine | ✅ Complete | `kryptos.k4.geometry24` — 4×24(+1) grid, 8 base fill orders (row/col-major, boustrophedon, alternating-column, spiral, outside-in, center-out, circular-wrapped) + reversed variants (16 total), 3 remainder-handling modes for the 97th character (trailing/leading/drop). |
| Physical front/back reflection library | ✅ Complete | `kryptos.k4.reflection` — 8 coordinate transforms (identity/flip_h/flip_v/rotate_180 + transpose family); `back_mirror_col`/`back_mirror_row`/`back_mirror_both` are literal aliases matching the brief's `back(row,23-col)` / `back(3-row,col)` / `back(3-row,23-col)` formulas — which turn out to be exactly the flip/rotate family, not new math. |
| 24-position clock permutation + Berlin/Langley rotation | ✅ Complete | `kryptos.k4.clock_rotation` — column-index permutation (not a Caesar shift); `geography_priority_offsets()` reuses (does not re-derive) `bearing_attack.CIA_BERLIN_BEARING_INT` and `k2_clock_states` values as additional named offset candidates; `geography_derived_bearings()` exposes the exact (unrounded) CIA→Berlin bearing as a route direction for `ene_routes` (item 12). |
| ENE/16-point compass route generator | ✅ Complete | `kryptos.k4.ene_routes` — discrete rational (`fractions.Fraction`) column-per-row slopes for all 16 compass points; the 24-ribbon family per direction is a proven bijection over the 4×24 grid. |
| Canonical hypothesis graph | ✅ Complete | `kryptos.k4.hypothesis_graph` — file-persisted graph mirroring the brief's flow diagram, status per edge (untested/null/partial_null/confirmed/eureka), Mermaid + Markdown rendering. Snapshot: `K4_HYPOTHESIS_GRAPH.json`. |
| Strict validation pipeline + adversarial benchmarks | ✅ Complete | `kryptos.k4.validation` — Prediction Standard levels (crib match, complexity/overfitting guard, independent reproduction check) gating what may be promoted to a breakthrough snapshot; `EXTERNAL_CANDIDATES` registry independently checks outside claims (see Physical/Geometric Pivot section below). |
| Combined geometric-permutation + tableau attack | ✅ Complete | `kryptos.k4.geometry_combined_sweep` — composes fill-order/route → reflection → rotation into a 97-length ciphertext permutation, then reuses `physical_grid`'s tableau keystreams via Quagmire III. **Null result** — see Ruled Out table above. |
| 3-layer geometric composite (Phase 2, item 13) | ✅ Complete | `kryptos.k4.three_layer_composite.run_three_layer_composite_geometric` — mono-subst(keyed) → clock-Vigenère → Phase 1's named 24-column geometric permutation (swaps out `run_three_layer_composite`'s brute-force arbitrary columnar transposition). **Null result** — see Physical/Geometric Pivot §Phase 2 below. |
| Myszkowski transposition (P8, item 14) | ✅ Complete | `kryptos.k4.myszkowski` — repeated-letter-keyword grouped-column transposition primitives (`myszkowski_encrypt`/`myszkowski_decrypt`) + `run_myszkowski_attack` sweep over ABSCISSA/PALIMPSEST × decrypt/encrypt. **Null result.** |
| Trifid cipher (P9, item 14) | ✅ Complete | `kryptos.k4.trifid` — 27-cell (3×3×3) cube fractionation primitives (`trifid_encrypt`/`trifid_decrypt`, keyword-mixed cube via `quagmire.keyword_alphabet` + filler symbol) + `run_trifid_attack` sweep over 6 keyword candidates × 13 period lengths. **Null result.** |
| SA substitution-key search + geometric front-end (P15, item 15, optional) | ✅ Complete | `kryptos.k4.geometry_substitution_search.run_geometry_substitution_sa_sweep` — proper simulated annealing (temperature/cooling, following the same pattern as `transposition_analysis`'s columnar SA) over the 26-letter substitution key space, applied to text produced by inverting a Phase-1 `geometry24` fill order; fills the gap left by `hill_genetic.py` (Hill-3×3-only) and `transposition_analysis.py`'s SA (columnar-permutation-only). **Null result.** |

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
| `docs/archive/K4-CLOCKS.html` (archived) | States NYPVTTMZF at "positions 26–34" | NYPVTTMZF is at 0-indexed 63–71; cipher at 26–34 is QPRNGKSSO |

---

## Physical/Geometric Pivot (2026-08-29)

A research brief ("K4 Next Steps — Physical/Geometric Pivot") redirected the attack surface from "what cipher/key produces K4?" toward "what physical coordinate system, orientation, and traversal does the sculpture itself specify?" — see the seven new modules and combined sweep in the Existing Infrastructure Status table above. Full detail (design rationale, module-by-module notes) lives in the implementation plan; this section records what actually ran and what it found.

**Item 1 (canonicalize crib positions) was already satisfied** before this pivot started: `keystream_validator.K4_CRIBS` is the single canonical source and matches this document's own Position Reference Quick Table exactly. The `CONTRIBUTING.md` file the "Known Documentation Issues" section below flags no longer exists in this repo, so that issue is moot.

**Item 12** ("combine geographic vectors with grid orientation") is covered: `clock_rotation.geography_derived_bearings()` exposes the exact CIA→Berlin great-circle bearing (~44.4°, not snapped to a named compass point) and its 180°-reversed counterpart as route directions, reusing `ene_routes.trace_route`'s existing float-bearing support (no new arithmetic — this is direct reuse of the ENE-route machinery built for item 6). **Item 13** ("explore 3+ layer classical composites") is covered by `run_three_layer_composite_geometric` (Phase 2, below). **Items 10–11** (historical CIA physical-object inventory; physical Berlin World Clock investigation) remain explicitly deferred — they are historical/archival research tasks rather than coding tasks, and need user-supplied sources (as with the Field Guide/kryptosbot URLs) before attempting. **Items 14–16** (remaining obscure cipher families, large unconstrained heuristic searches) are the brief's own explicit lowest-priority tier ("ONLY AFTER THAT") and a substantially different, separate body of work — out of scope for this pivot (items 14 and 15 were picked up in a Phase 3 follow-on; see below).

### Canonical hypothesis graph

Rendered from `K4_HYPOTHESIS_GRAPH.json` after the runs below (`==>` confirmed, `-- null -->` null, `-.->` untested):

```mermaid
flowchart TD
    KRYPTOS_PHYSICAL_STRUCTURE -.-> COMPASS_LODESTONE
    KRYPTOS_PHYSICAL_STRUCTURE -.-> FRONT_BACK_LAYERS
    KRYPTOS_PHYSICAL_STRUCTURE -.-> VIGENERE_TABLEAU_REVERSE
    KRYPTOS_PHYSICAL_STRUCTURE -.-> K4_CIPHERTEXT
    K4_CIPHERTEXT ==> EASTNORTHEAST
    EASTNORTHEAST -.-> DIRECTIONAL_TRAVERSAL
    DIRECTIONAL_TRAVERSAL -.-> BERLIN_WORLD_CLOCK
    BERLIN_WORLD_CLOCK -.-> COORD_SYSTEM_24
    COORD_SYSTEM_24 -.-> GRID_4X24_PLUS_1
    GRID_4X24_PLUS_1 -.-> GEOMETRIC_POSITIONAL_TRANSFORM
    GEOMETRIC_POSITIONAL_TRANSFORM -- null --> SUBSTITUTION_LAYER
    SUBSTITUTION_LAYER -- null --> CLOCK_VIGENERE_LAYER
    CLOCK_VIGENERE_LAYER -- null --> THREE_LAYER_GEOMETRIC_COMPOSITE
```

The `GEOMETRIC_POSITIONAL_TRANSFORM -> SUBSTITUTION_LAYER` edge is what the combined sweep directly tests; the two Phase 2 edges (`SUBSTITUTION_LAYER -> CLOCK_VIGENERE_LAYER -> THREE_LAYER_GEOMETRIC_COMPOSITE`) are `run_three_layer_composite_geometric`'s (see below). The remaining upstream edges (compass/lodestone, front/back layers, tableau-reverse, the clock-as-coordinate-system interpretation) remain untested and are natural next steps — most concretely, wiring `reflection.py`'s shape-changing (transpose) family and a genuine front/back tableau mapping into the sweep, which the current default scope deliberately excludes to bound combinatorics (see `geometry_combined_sweep.py`'s docstring).

### External candidate adversarial benchmarks

Two external sources were checked independently — neither is accepted on the source's own say-so:

- **solvekryptos.com/fieldguide** claims a complete K4 plaintext (`"THE COMPASS ROSE IS HERE X EAST NORTHEAST THIS IS YOUR POSITION X COMMISSION BERLIN CLOCK WHICH IS NORTHEAST OF HERE X"`) via an undisclosed Quagmire-III-variant (f-table/g-table values not published, so the mechanism itself isn't independently reproducible here). Checked against the confirmed crib positions with `X` counted as a literal character — the only way the claim reaches K4's exact 97-character length: **`BERLIN` and `CLOCK` land exactly at the confirmed positions (63, 69), but `EAST` and `NORTHEAST` are off by exactly one position** (found at 21/25, not 22/26). Verdict: **fails strict positional validation at 2 of 4 confirmed anchors** — reproducible via `kryptos.k4.validation.benchmark_external_candidate("solvekryptos_field_guide")`. This is a partial, specific disagreement (not a clean match, not a clean miss) and is recorded as such rather than as either an endorsement or a dismissal.
- **kryptosbot.com/findings** proposes no candidate plaintext (13,302 audited candidates, zero survive verification per the source) — used as a corroborating negative-result cross-reference (its eliminated cipher families overlap heavily with the Ruled Out table above) and as the source of two structural diagnostics now available for future candidates: `check_w_delimiter_pattern` and `check_stehle_anomaly`. Run against real K4: five `W` characters at 0-indexed positions `[20, 36, 48, 58, 74]` (matches the source's "five W characters" description); the letter-to-letter shift sequence in the ciphertext window at positions 55–63 (`DIAWINFB`) is `[5, 18, 22, 12, 5, 18, 22]` — **not constant, but period-4** (indices 0–2 repeat exactly at indices 4–6). Neither diagnostic asserts a theory is true; both are reusable, honest observations pending a precise definition of kryptosbot's own methodology (not available from the page fetched).

### External Developments (2025–2026)

Real-world events since this document's last update materially change the context this project operates in, independent of any of the sweeps above. Recorded here for anyone reading this doc cold; none of it changes an existing null-result status.

- **Sanborn's own 1990 archival papers were found, September 2025.** Researchers Jarett Kobek and Richard Byrne located Jim Sanborn's working materials — sentence strips he'd cut up and taped out of order for CIA verification — in the Smithsonian's Archives of American Art, and pieced together what they believe is K4's complete plaintext by cross-referencing the fragments against Sanborn's public clues. Both are explicit this is **not a cryptographic solve**: "There's no way on earth that this is a cryptographic solve, and we have not claimed that" (Kobek). Sourced: [Scientific American](https://www.scientificamerican.com/article/how-the-cias-kryptos-sculpture-gave-up-its-final-secret/), [RR Auction's own account](https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/).
- **A real, Sanborn-confirmed K5 exists.** Publicized via the November 2025 auction of Sanborn's archive materials: a second 97-character message, thematically cued by K2's own line ("it's buried out there somewhere"), to be released once K4 is *cryptographically* — not archivally — solved. This directly corrects the old K4-T1.md archive banner and the line above; see [Washington Post](https://www.washingtonpost.com/entertainment/art/2025/11/01/kryptos-code-jim-sanborn-k5-auction/).
- **Paradigm (a crypto firm) won the November 2025 auction** and now runs a verification/escrow program: it holds the recovered plaintext privately and lets independent submissions be checked via one-way cryptographic functions without revealing the answer. Sourced: [paradigm.xyz/writing/kryptos](https://www.paradigm.xyz/writing/kryptos).
- **The `solvekryptos_field_guide` benchmark above already found a real, specific discrepancy worth re-stating precisely**, now cross-checked by hand against the site's own claimed mechanism (Quagmire III, KRYPTOS-keyed, physical tableau keystream, one-bit gate — [solvekryptos.com/solution](https://solvekryptos.com/solution)): `EAST` and `NORTHEAST` are both found exactly **one position early** (21/25 vs. the confirmed 22/26), while `BERLIN` and `CLOCK` land exactly on the confirmed positions (63/69) with zero offset. That means the claimed plaintext's opening segment — `"THE COMPASS ROSE IS HERE X"` (21 characters, X counted literally) — is exactly **one character short** of the 22 characters needed to put `EAST` at its confirmed position, and something in the ~29-character middle stretch between `NORTHEAST` and `BERLIN` (`"THIS IS YOUR POSITION X COMMISSION"`) makes up the missing character before `BERLIN`, since that anchor and `CLOCK` land exactly right. This is a specific, well-defined, checkable gap — not a vague mismatch — and is exactly the kind of thing worth putting to Elonka Dunin or the solvekryptos.com maintainers directly rather than guessing at. No fix is proposed here; the discrepancy is recorded, not resolved.
- **Net effect on this project:** the archival plaintext recovery, even if fully correct, does not by itself explain *how* K4 encrypts to that plaintext — the cryptographic mechanism remains the open question this project exists to answer, and Sanborn's own confirmed plaintext opens with "THE COMPASS ROSE IS HERE" and closes with "WHICH IS NORTHEAST OF HERE" — read literally, this is external, independent corroboration that the compass-rose bearing (Phase 8's second open primary-source gap, below) is not a speculative angle but the sculpture's own stated subject.

### Combined sweep results

| Run | Scope | Candidates | Time | Result |
|-----|-------|-----------|------|--------|
| Default (Berlin/Langley ±6 priority) | 20 orders × 4 reflections × {0,+6,-6} × 3 remainder modes × 108 tableau routes × 2 bases | 155,520 | ~7s | Null — zero candidates matched even one positional crib |
| Geography-derived offsets | Same, `rotation_offsets` = 6 values from `clock_rotation.geography_priority_offsets()` (CIA→Berlin bearing, K2-coordinate hours, magnetic declination) | 311,040 | ~14s | Null — one incidental substring-only keyword hit, no positional crib hits |
| Geography-derived bearing as route direction (item 12) | `order_names=GEO_BEARING_ORDER_NAMES` (the exact CIA→Berlin bearing + its reverse) × 4 reflections × {0,+6,-6} × 3 remainder modes × 108 tableau routes × 2 bases | 15,552 | <1s | Null — zero positional or keyword hits |

Each run's full parameters and top candidates are preserved in `K4_GEOMETRY_COMBINED_NULL.json`, `K4_GEOMETRY_COMBINED_GEO_NULL.json`, and `K4_GEOMETRY_COMBINED_GEO_BEARING_NULL.json` respectively, per the regressionless-development protocol (every null result gets a permanent artifact).

### Phase 2 (2026-08-29): 3-layer geometric composite (item 13)

Auditing the brief's items 9–16 against what's actually implemented (not what the brief assumed) found that item 9 is already covered by `bearing_attack.py` and item 12 was completed above; items 10–11 are archival/historical research tasks rather than coding tasks and are deferred pending user-supplied sources (as with the Field Guide/kryptosbot URLs); items 14–16 are the brief's own explicit lowest-priority tier. That leaves **item 13** ("explore 3+ layer classical composites") as the next well-scoped, code-only increment.

`kryptos.k4.three_layer_composite.run_three_layer_composite` (Priority 1, below) already chains mono-substitution → clock-Vigenère → **brute-force arbitrary columnar transposition** at grid widths `[7, 8, 10]` — never the 24-column grid, and never the Phase 1 pivot's *named* geometric fill-orders/reflections/rotations. `run_three_layer_composite_geometric` (new) swaps that transposition layer for Phase 1's `geometry24`/`geometry_combined_sweep` machinery, reusing this module's own `_mono_subst_decrypt`/`_vigenere_decrypt_std`/`_build_clock_sequence` unchanged — a genuinely distinct search space, not a duplicate.

| Run | Scope | Candidates | Time | Result |
|-----|-------|-----------|------|--------|
| Default (priority CIA-timestamp clock states) | 2 clock states × 4 keyed alphabets × 720 geometric-permutation combos | 5,760 | ~1s | Null |
| Full clock sweep | 24 hourly clock states × 4 alphabets × 720 combos | 69,120 | ~12s | Null |

Both null. Artifacts: `K4_3LAYER_GEOMETRIC_NULL.json`, `K4_3LAYER_GEOMETRIC_FULL_NULL.json`. Recorded on two new hypothesis-graph edges (`SUBSTITUTION_LAYER -> CLOCK_VIGENERE_LAYER -> THREE_LAYER_GEOMETRIC_COMPOSITE`, extending the graph additively — see the updated diagram above).

**Grand total across all five real-K4 runs in this pivot (Phase 1 + Phase 2): 556,992 candidates, zero breakthroughs.**

### Phase 2 addendum (2026-08-29): items 10–11 research findings

Items 10–11 (historical physical-object search; physical Berlin World Clock investigation) are archival research tasks, not coding tasks — no attack module came out of this pass. What follows is what was actually verified via web sources, with two corrections to assumptions this doc made earlier.

**Item 11 — Berlin World Clock (Weltzeituhr, Alexanderplatz):**
- A true 24-sided cylinder (regular icositetragon cross-section), ~10m tall, designed by Erich John, unveiled 1969. [Wikipedia (EN)](https://en.wikipedia.org/wiki/World_Clock_(Alexanderplatz)), [Wikipedia (DE)](https://de.wikipedia.org/wiki/Weltzeituhr_(Alexanderplatz))
- Displays **146 city/location names plus one additional, distinct entry specifically for the International Date Line** — the date-line boundary is a dedicated marker, not just an implicit gap between adjacent sectors.
- The base has a **stone mosaic in the shape of a wind rose** (compass rose) marking cardinal directions — a genuine, sourced link between the clock and compass/orientation symbolism, independent of anything at the Kryptos site itself.
- No source gives the exact city-to-side ordering, nor the monument's own compass orientation as installed. Both would require photographic/in-person documentation to pin down — not fabricated here.
- No CIA, Langley, or American reference point is mentioned in connection with the clock in any source checked.

**Item 10 — physical objects at the Kryptos site:**
- Confirmed via CIA's own legacy materials and community sources: a lodestone co-located with an engraved compass rose stone (the engraved needle points at the lodestone), separate Morse-code and classical-cipher granite slabs at the New Headquarters Building entrance (a different location from the main copper-screen sculpture), and the petrified-wood base under the copper screen.
- **No Berlin Wall fragment found in any source** — that specific brief hypothesis appears unfounded; treating it as ruled out pending contrary evidence.
- Community reporting (general web synthesis) describes a carved bearing line on the compass rose stone along the intercardinal axis, consistent with the ENE direction already implied by the "EASTNORTHEAST" plaintext — corroboration for, not new information beyond, the `ENE`/`NE`/`ENE_REVERSED`/`NE_REVERSED` priority directions already implemented in `ene_routes.py` and already tested null in Phase 1.

**Two corrections to prior assumptions in this document:**
1. The lodestone's exact compass-deflection bearing is **explicitly unmeasured** per the community's own authoritative tracking page — [elonka.com's Kryptos measurement wish list](https://www.elonka.com/kryptos/wishlist.html) lists "which way *exactly* is the needle on the compass rose pointing?" as an open, unanswered question as of this research. Earlier informal mentions of "west-southwest" in general web summaries should be read as unverified community characterization, not a measured figure — noted here so it isn't repeated as settled fact.
2. K2's coordinate plaintext reportedly points to a spot **~100 feet from the sculpture** (per [elonka.com's FAQ](https://www.elonka.com/kryptos/faq.html), "about 100' southeast of the sculpture"), not the sculpture's own location. The Phase 2 claim above that "item 9 is already covered by `bearing_attack.py`" assumed K2's coordinate and the CIA-HQ reference point `bearing_attack.py` uses were effectively the same location — that assumption is weaker than stated and should be revisited if a precise offset coordinate is ever sourced.

No new code or attack module follows from this pass — it's a documentation-only update per the above.

### Phase 3 (2026-08-29): Items 14–15 — remaining obscure cipher families + optional heuristic search

Phase 2 explicitly deferred items 14–16 as "the brief's own explicit lowest-priority tier ... a substantially different, separate body of work." This follow-on pass picks up items 14 (P8 Myszkowski, P9 Trifid — P10 Straddle Checkerboard was already done in an earlier session) and 15 (optional large unconstrained heuristic search), each as new self-contained modules following the same `run_X_attack`/`run_X_sweep` dict-return, crib-gated, `validate_candidate`-promoted, always-write-a-null-artifact convention as every other module in this family.

| Run | Scope | Candidates | Time | Result |
|-----|-------|-----------|------|--------|
| P8 — Myszkowski transposition | ABSCISSA + PALIMPSEST × decrypt/encrypt direction | 4 | <1s | Null — zero positional or keyword hits |
| P9 — Trifid cube fractionation | 6 keyword candidates × 13 period lengths (3–97) | 78 | <1s | Null — zero positional or keyword hits |
| P15 — SA substitution search + geometric front-end (optional) | 8 base `geometry24` fill orders × 3 SA restarts (3,000 iterations, temperature/cooling) | 24 | ~14s | Null — zero positional crib hits (one incidental substring-only "BERLIN" keyword hit, not positionally correct) |

Artifacts: `K4_MYSZKOWSKI_NULL.json`, `K4_TRIFID_NULL.json`, `K4_GEOMETRY_SUBSTITUTION_SA_NULL.json`.

Item 15 was scoped after checking for a genuinely non-redundant gap in the existing heuristic-search infrastructure, per the brief's own explicit permission to skip it if none was found: `hill_genetic.py` is a GA over Hill-3×3 matrices specifically, and `transposition_analysis.py`'s SA/GA searches are over columnar-transposition *permutations* specifically — neither searches the general monoalphabetic substitution key space, and every existing composite sweep that pairs a geometric-permutation front-end with a substitution layer (`geometry_combined_sweep`, `run_three_layer_composite_geometric`) only ever tries a handful of *named* keyed alphabets for that layer. `kryptos.k4.geometry_substitution_search` fills exactly that gap: a proper simulated-annealing search over the 26-letter substitution key space (same temperature/cooling structure as the existing columnar SA, applied to a substitution mapping instead of a column permutation), paired with a Phase-1 `geometry24` permutation inversion as the front end. Scope was kept deliberately bounded — the fill-order/reflection/rotation/remainder-mode combinatorics are already exhaustively covered by `geometry_combined_sweep`, so this module only varies the base fill order and lets the stochastic part of the search do the actual heuristic work.

### Phase 4 / v2.1 (2026-08-30): a new bearing, a sourced date, and closing three open loops

A "K4 Field Notes" review (published as an artifact, not committed here) re-read every clue and cross-checked the whole attack surface against actual code rather than doc claims — the same discipline that caught P1/P3/P4/P7's staleness in Phase 2 turned up more of the same, plus one genuinely new lead.

**New lead — the Mengenlehreuhr → Weltzeituhr bearing.** `docs/sources/CLOCK.md` claims a line from the Berlin Clock heading ENE reaches the World Clock at Alexanderplatz, but cites no source and uses the clock's *current* location. The Mengenlehreuhr didn't move to Europa-Center until 1996 — six years after Kryptos was dedicated; from 1975–1995 (Sanborn's entire design window) it stood at Kurfürstendamm/Uhlandstraße. Computed both real geodesic bearings directly (`kryptos.k4.geodesy`, via `clock_rotation.mengenlehreuhr_weltzeituhr_bearings()`):

| Reference point | Bearing to Weltzeituhr | Distance |
|---|---|---|
| Current Mengenlehreuhr (post-1996) | 69.0° | 5.57 km |
| **1990 (Sanborn-era) Mengenlehreuhr** | **70.8°** | 6.31 km |

Exact ENE is 67.5° — both land within 1.5–3.3° of it, corroborating (from real Berlin geography, independent of the plaintext) the same direction already prioritized in `ene_routes.py`. Wired automatically into `geometry_combined_sweep.GEO_BEARING_ORDER_NAMES` (it iterates `clock_rotation.geography_derived_bearings()`, no sweep-side code change needed). **Null result**: 46,656 candidates, zero positional or keyword hits. Artifact: `K4_GEOMETRY_COMBINED_GEO_BEARING_NULL.json`.

**New lead — November 9, 1989 as a clock state.** Every clock-state attack in this project has used the CIA dedication date (Nov 3, 1990); none had used the date `CLOCK.md` itself names as most influential on Sanborn's design. Added `three_layer_composite.BERLIN_WALL_PRIORITY_TIMES` — three sourced Berlin-local (CET) moments from that evening plus their EST equivalents: 18:53 (Schabowski's key statement), 19:05 ("as of now; immediately!"), 20:00 (ARD's lead broadcast) — see [Making the History of 1989](https://1989.rrchnm.org/items/show/704.html) and [berlin.de](https://www.berlin.de/en/history/8482274-8619314-opening-and-fall-of-the-berlin-wall.en.html) for sourcing. Run via `run_three_layer_composite_geometric(priority_clock_times=BERLIN_WALL_PRIORITY_TIMES)`. **Null result**: 17,280 candidates, zero hits. Artifact: `K4_3LAYER_GEOMETRIC_BERLINWALL_NULL.json`.

**Closing three loops that were wired but never executed.** `K4_ATTACK_LANDSCAPE.md` lists Priorities 2, 5, and 6 as *"NOT RUN"* / *"never attempted"* — stale in exactly the way P1/P3/P4/P7 were before Phase 2's correction. All three had complete implementations already wired into the dashboard's attack API; they'd simply never been executed outside the ephemeral in-memory job system, so no permanent artifact or doc record existed for any of them.

| Run | Scope | Candidates | Result |
|-----|-------|-----------|--------|
| P2 — shadow/null masking, thorough scope | 8 masking variants (stride-2/3/4, block-8, clock-shadow×2, arc-fraction×2) × 4 alphabets × 2 grids (7/8 cols) × 2 clock states (00:00/12:00) × 24 perms/grid × 2 routes | 6,144 | Null — 40 near-misses, all single-keyword coincidences (e.g. "EAST" as a substring), none positional or simultaneous |
| P5 — BERLIN+CLOCK 2-crib relaxed gate, brute-force transposition | `run_three_layer_composite(keyword_eureka_threshold=2)` | 34,560 | Null — zero near-misses |
| P5 — same relaxed gate, Phase-1 geometric transposition (new combination) | `run_three_layer_composite_geometric(keyword_eureka_threshold=2, full_clock_sweep=True)` | 69,120 | Null — zero near-misses |
| P6 — K3 plaintext as running Vigenère key | 4 variants (standard/KRYPTOS alphabet × direct/reversed key) | 4 | Null — zero keyword hits on any variant |

Artifacts: `K4_MASK_*_NULL.json` (8 files), `K4_P5_2CRIB_NULL.json`, `K4_P5_GEOMETRIC_2CRIB_NULL.json`, `K4_P6_RUNNING_KEY_NULL.json`. The P5-against-geometric-transposition combination had never been tried in any prior session — P5's original scope only ever relaxed the gate against the brute-force columnar transposition.

**Bug fixed in passing**: the P2 API handler in `k4_attack_routes.py` aggregated near-miss candidates with `best.extend(result.get("best_candidates", []))` *inside* the per-candidate loop instead of `best.append(c)` — an O(n²) duplication that corrupted the dashboard's near-miss reporting for this attack specifically (did not affect the null/non-null verdict itself). Fixed.

**Still open, not attempted this round** (see the "K4 Field Notes" artifact for full detail): `reflection.py`'s shape-changing transpose family was fully built in Phase 1 but `geometry_combined_sweep.DEFAULT_REFLECTIONS` only ever exercises the shape-preserving four — the single largest untested slice of the pivot's own search space. Deferred to keep this round scoped.

### Phase 7 (2026-09-01): shape-changing transpose, shadow-angle primitives, city-list keywords, cross-vector consensus

With the pivot's 13 code-executable items (of 15 — items 10-11 were historical/archival research satisfied via sourced documentation, not code; see the Phase 2 addendum above) plus P2/P5/P6 all executed and null, three concrete new directions were opened and closed in this pass, plus a standing cross-vector scoring capability and a batch-runner to remove "someone has to remember to click it" from future full sweeps.

**Shape-changing transpose family, wired.** `composed_flat_indices` (in `geometry_combined_sweep.py`) now correctly handles `reflection.SHAPE_CHANGING`'s four transpose-family transforms: after a transpose, the grid becomes 24×4 rather than 4×24, so the column-rotation step now rotates mod the *current* axis size (4, not 24) and the flat-index formula uses the transposed grid's own row-major numbering (`rows=COLS, cols=ROWS`) rather than the original 4×24 numbering — verified as a valid bijection and a correct `apply_forward`/`apply_inverse` round-trip before running anything at scale. Shape-preserving reflections are byte-identical to before (regression-tested). Both `geometry_combined_sweep` and `three_layer_composite_geometric` pick this up automatically since both already accept `reflection_names` as a parameter — no new sweep function needed.

**Re-examined "shadow of the word."** Previously flagged in `K4_ATTACK_LANDSCAPE.md` as out of scope, requiring physical/photographic site access. That turns out to be wrong for two independently-computable readings, both implemented in the new `kryptos.k4.solar_geometry`:

- **Hypothesis A — World Clock topper rotation.** Confirmed via Wikipedia (checked 2026-09-01): *"Once per minute, an artistic sculptural rendering of the Solar System made of steel rings and spheres rotates."* — a fixed, documented rate, decoupled from real solar position. However, every historical timestamp this project has sourced (CIA dedication, the three Berlin Wall moments, the World Clock's own 1969 dedication) is reported only to whole-minute precision, and since the topper's period is exactly 60 seconds, any two whole-minute timestamps are *always* co-phased (0° apart) — verified directly in code, not assumed. A single "derived" offset from a sourced pair would therefore be vacuous. Rather than fabricate sub-minute precision that doesn't exist, this operationalizes the hypothesis honestly: exhaustively test the full 0–23 rotation-offset range, a slice no prior sweep (Phase 6 included) ever covered exhaustively (those used only `{0,+6,-6}` or a handful of geography-derived values).
- **Hypothesis B — real solar position at CIA HQ, Langley.** Implemented a standard NOAA/Meeus solar-position algorithm (`solar_geometry.solar_position`; verified against known reference points — Greenwich summer-solstice noon gives elevation ≈61.9°, matching the textbook value; equator/equinox noon gives elevation ≈90°). Computed real solar azimuth at CIA HQ (`bearing_attack.py`'s existing coordinates) at each of the same already-sourced historical moments, wired into `clock_rotation.geography_derived_bearings()` exactly like the Mengenlehreuhr bearing before it — flows into `geometry_combined_sweep.GEO_BEARING_ORDER_NAMES` automatically, no sweep-side change needed.

**Update 2026-09-02 — the vacuity is resolved for two moments.** A follow-up dig (same "Primary Sources Needed" research pass that expanded the World Clock city list) found `chronik-der-mauer.de`'s word-for-word transcript of Hans-Hermann Hertle's own camera/audio recording of the press conference (citing Hertle, *Die Berliner Mauer. Biografie eines Bauwerks*, 2nd ed. 2015, p. 194–195) — a genuinely authoritative source, unlike any timestamp this project had sourced before. It gives **sub-minute precision**: the transcript excerpt containing the "sofort … unverzüglich" exchange opens at **18:52:40 CET**, and the press conference itself ends at **19:00:54 CET** ("Ende der Pressekonferenz: 19:00:54 Uhr"). Both carry genuine non-zero seconds — unlike every other sourced timestamp, these are *not* vacuous inputs to hypothesis A. `solar_geometry.precise_topper_shadow_offsets()` computes the topper's angle within its own minute directly from these two moments (`seconds/60×360`, no reference epoch needed for a fixed-period rotation) — offsets 16 and 22. The same two precise timestamps also feed hypothesis B (`solar_shadow_bearings()`), giving two more real solar-azimuth bearings than the whole-minute versions could.

| Run | Scope | Candidates | Result |
|-----|-------|-----------|--------|
| Shape-changing transpose family, default scope | 20 fill-orders/routes × 4 shape-changing reflections × 3 rotation offsets × 3 remainder modes × 108 tableau routes × 2 bases | 155,520 | Null |
| Shape-changing transpose family, geography-derived offsets | Same, 8 geography-derived rotation offsets | 414,720 | Null |
| Shape-changing transpose family, via `three_layer_composite_geometric` | Full clock sweep | 69,120 | Null |
| Solar-azimuth (hypothesis B) route directions | `order_names=GEO_BEARING_ORDER_NAMES` (4 whole-minute solar-shadow bearing pairs) | 108,864 | Null |
| Topper full-rotation sweep (hypothesis A) | `rotation_offsets=range(24)` (full axis, not just priority values) | 1,244,160 | Null |
| Topper angle from precise timestamps (hypothesis A, resolved) | `rotation_offsets={16, 22}` from `precise_topper_shadow_offsets()` | 103,680 | Null |
| Solar-azimuth from precise timestamps + whole-minute (hypothesis B, expanded) | `order_names=GEO_BEARING_ORDER_NAMES` (now 6 solar-shadow bearing pairs, 2 precise) | 139,968 | Null |

Artifacts: `K4_GEOMETRY_COMBINED_SHAPECHANGING_NULL.json`, `K4_GEOMETRY_COMBINED_SHAPECHANGING_GEO_NULL.json`, `K4_3LAYER_GEOMETRIC_SHAPECHANGING_NULL.json`, `K4_GEOMETRY_COMBINED_SOLAR_BEARING_NULL.json`, `K4_GEOMETRY_COMBINED_TOPPER_ROTATION_NULL.json`, `K4_GEOMETRY_COMBINED_TOPPER_PRECISE_NULL.json`.

**World Clock city-list keywords — expanded 2026-09-02 via direct photograph reading.** Originally sourced only from Wikipedia text (9 individually-named cities out of 148 claimed). Two things changed on a follow-up pass:

- **Count resolved.** German Wikipedia's "Weltzeituhr (Alexanderplatz)" article (checked 2026-09-02) quotes its own primary text: *"Sie enthaelt auf ihrer metallenen Rotunde die Namen von 146 Orten sowie einen zusaetzlichen Eintrag zur Datumsgrenze"* — 146 city names plus one distinct International Date Line marker (147 total plate entries). This matches this document's own earlier item-11 research exactly (independently, on an earlier pass) and disagrees with the English-secondary-source-derived 148 this session had briefly used. Two independent-language primary sources agreeing with each other is stronger evidence than a single-language secondary-source count — `TOTAL_CITY_COUNT` is now 146 (`TOTAL_PLATE_ENTRIES` 147), both tested as rotation offsets.
- **List massively expanded via direct primary-source reading, not a text summary.** The clock is a permanently-photographed public sculpture — rather than accept "no source lists all the names," seven Wikimedia Commons photographs of the actual engraved plates (`Weltzeituhr_Detail_Alexanderplatz.jpg`, `Weltzeituhr.jpg`, `Die_Urania-Weltzeituhr_am_Alexanderplatz.jpg`, `DSC_3226_Urania-Weltzeituhr_Berlin_I.jpg`, `Weltzeituhr,_Berlin_(15910006062).jpg`, `2009-04-07_Berlin_506.jpg`, `2009-04-07_Berlin_508.jpg`) were opened directly in-browser and read visually, transcribing every legible plate rather than relying on any secondary description — including cross-checking one segment across two photos, which caught and corrected a misread from the first, blurrier one (the Middle East/North Africa segment: `BEIRUT` not the initially-misread `KAIRO`/`KAPSTADT`/`KUWAIT`). This covers roughly 20 of the 24 segments — **119 individually confirmed names** in `kryptos.k4.world_clock_cities.CONFIRMED_CITIES`, up from 9. Still not the complete 146 (Japan/Korea, Australia/NZ, and the Pacific/Hawaii zones weren't found legibly photographed), but a large, directly-verified jump rather than a stalled "no source available."

This is the same discipline as everywhere else in this project (verify before recommending, don't fabricate what isn't sourced) applied to actually *finding* a source rather than declaring the search exhausted after one text-only pass.

| Run | Scope | Candidates | Result |
|-----|-------|-----------|--------|
| Confirmed city names as keyed alphabets (initial, text-sourced) | 9 confirmed names × 3 grid widths (7/8/10) × 3 clock states (2 CIA-priority + 1 from the day-loop's `00:00:00`) × 120 perms/grid | 9,720 | Null |
| Confirmed city names as keyed alphabets (expanded, 5-photo pass) | Same scope, 104 confirmed names | 112,320 | Null |
| Confirmed city names as keyed alphabets (expanded further, 7-photo pass) | Same scope, 119 confirmed names | 128,520 | Null |
| Sourced structural counts as rotation offsets | Full `geometry_combined_sweep` default scope (20 fill-orders/routes × 4 shape-preserving reflections × 3 remainder modes × 108 tableau routes × 2 indicator bases = 51,840) × 3 offsets `{146 mod 24, 147 mod 24, 24 mod 24}` = `{2, 3, 0}` | 155,520 | Null |

Artifacts: `K4_WORLD_CLOCK_CITIES_NULL.json`, `K4_GEOMETRY_COMBINED_WORLDCLOCK_NULL.json`.

**Cross-vector consensus scoring, built.** `kryptos.k4.cross_vector_consensus` re-scans every `K4_*_NULL.json` artifact this project has ever produced, groups candidates by *source vector* (not just merged into one pool the way P16's `corpus_miner` does), and flags a positional n-gram fragment only if it appears across `min_distinct_vectors` (default 3) *separate* attack vectors — a repeat within one vector's own large sweep no longer masquerades as cross-model agreement. Run against the 30 artifacts accumulated by this point (11 with extractable candidates): **zero consensus anchors found** — no accidental cross-vector agreement, consistent with everything being null. Artifact: `K4_CROSS_VECTOR_CONSENSUS_NULL.json`.

**Scheduled overnight sweep runner, built.** `kryptos.k4.overnight_runner.run_all_pending_sweeps` (invoked via `scripts/run_k4_overnight_sweeps.py`) runs every registered full-scope sweep — including this phase's five new ones — in sequence; the moment any one raises `EurekaSignal`, it's caught, recorded as the returned summary's breakthrough result, and the remaining queued sweeps are skipped rather than run past an unvalidated breakthrough. `cross_vector_consensus` is registered last since it depends on every other sweep's artifact. Closes the "someone has to remember to click it" gap noted in the 2026-08-28 idea list.

**Grand total across Phase 7's real-K4 sweeps: 2,420,928 candidates (plus the 30-artifact, 11-vector cross-scan), zero breakthroughs, zero cross-vector consensus.**

---

## Primary Sources Needed (researched 2026-09-01)

Phases 1-7 have exhausted what's *inferable* from already-sourced material. What's left needs new primary source material this repo cannot generate on its own — code alone won't move these three forward. This section records concrete leads found by digging (not just "someone should go look"), so the next session doesn't have to re-research from scratch. See `docs/TASKS.md`'s Active section for these as tracked tasks.

### 1. A complete World Clock (Weltzeituhr) city list

`kryptos.k4.world_clock_cities.CONFIRMED_CITIES` holds only 9 of 148 names — every source checked describes the *count* but not the full list. Leads, in order of promise:

- **Wikimedia Commons, `Category:Urania-Weltzeituhr` → `Details of Urania-Weltzeituhr` subcategory (27 files)** — includes close-up shots (e.g. `Weltzeituhr Detail Alexanderplatz.jpg`) that may show individual city-name plates legibly. Worth visual inspection/OCR of each file, segment by segment, to reconstruct the list photographically rather than from a secondary description.
- **German Wikipedia** (`de.wikipedia.org/wiki/Weltzeituhr_(Alexanderplatz)`) — not yet fetched directly in this project; German-language sources on a German landmark are plausibly more detailed than the English article already checked.
- **Patent DE2515102A1** ("World clock with globe display") — found via search, not yet read; patents for this kind of mechanism sometimes include technical drawings that enumerate segments.
- **360cities.net panorama** (`360cities.net/en/image/weltzeituhr-alexanderplatz-berlin-mitte-2`) — a high-resolution 360° panorama might allow reading plate text directly at zoom, unlike a handful of static tourist photos.

### 2. A sub-minute-precision timestamp for a Nov 9 1989 moment

`solar_geometry.topper_shadow_offsets()` had to fall back to an exhaustive 0-23 sweep because every sourced timestamp (Schabowski's statement, the AP flash, ARD's broadcast) is whole-minute precision, and the topper's 60-second rotation period makes any two such timestamps vacuously co-phased. A precise-to-the-second source would make hypothesis A's originally-intended single derived angle actually computable. Leads:

- **`chronik-der-mauer.de`** — published jointly by the Bundeszentrale für politische Bildung (Germany's Federal Agency for Civic Education) and the Robert-Havemann-Gesellschaft, a serious historical archive. Has a dedicated dated article by historian Hans-Hermann Hertle: *"9. November 1989, 18.00 Uhr: Schabowskis Auftritt"* (`chronik-der-mauer.de/material/180368/...`). **Blocked this session by bot-detection (HTTP 403 on automated fetch)** — needs a manual visit, but is the single most promising lead found: an academic archive with a title suggesting minute-level (possibly finer) precision already.
- **Hans-Hermann Hertle's books** — *"Chronik des Mauerfalls"* and *"Sofort, unverzüglich"* (Ch. Links Verlag) are the definitive academic accounts of that evening; a library/archive copy would likely carry more precision than any web summary.
- **Original AP wire filing** — wire services timestamp internally to the minute or second; the Associated Press Corporate Archives (or contemporary newspaper microfilm carrying the wire timestamp) could source the AP-flash moment precisely.
- **ARD/rbb broadcast archives (Deutsches Rundfunkarchiv)** — the actual press-conference video/audio, if timestamped or synchronized against a known broadcast clock, would fix Schabowski's exact statement moment.

### 3. The Kryptos compass rose's actual measured bearing

Per `elonka.com/kryptos/wishlist.html`, "which way exactly is the needle on the compass rose pointing?" remains an **open, unanswered community question** — this is the single most direct physical fact this entire pivot has been reasoning around indirectly (via Berlin-side ENE bearings) rather than measuring at the source. Leads:

- **`elonka.com/kryptos/KryptosAerial.html`** ("Kryptos - The Bird's Eye View") — already gives a partial, explicitly-uncertain secondary estimate: *"one report is that the 'north' direction on the compass rose is pointing roughly south-southwest (around 220 degrees) but this is not exact."* This is a different measurement than the lodestone-deflection bearing this project's `K4_ACTIVE_RESEARCH.md` history already flags as unmeasured — worth distinguishing the two ("which way does the rose's own N mark point" vs. "which way does the needle deflect toward the lodestone") in any future write-up. The page explicitly invites reader submissions/corrections.
- **FOIA request to the CIA** — Kryptos is publicly documented on the CIA's own legacy site; the agency has engaged with Kryptos researchers before (per its own published materials). A FOIA request or public-affairs inquiry asking for a measured bearing or a high-resolution overhead photo of the compass-rose/lodestone slab is a legitimate, concrete next step.
- **Contact Elonka Dunin directly** — the maintainer of the wishlist above is the community's most active liaison to Sanborn and CIA contacts; she may already have unpublished measurements or know who to ask.
- **Satellite/overhead imagery inspection** — Google Earth/Maps imagery of the CIA New Headquarters Building courtyard was not inspected visually in this pass (text search only); a session with image-reading capability pointed at the exact courtyard coordinates could potentially resolve the stone slab's orientation directly, resolution permitting.

---

## Related Documents

- [`docs/analysis/K4_KEYSTREAM_ANALYSIS.md`](K4_KEYSTREAM_ANALYSIS.md) — Detailed keystream derivation and what it rules out
- [`docs/analysis/30_YEAR_GAP_COVERAGE.md`](30_YEAR_GAP_COVERAGE.md) — Classical cipher technique coverage map
- [`docs/TASKS.md`](../TASKS.md) — Implementation backlog
- [`docs/ROADMAP.md`](../ROADMAP.md) — Phase milestones

**Archived (2026-09-01, superseded by this document):**

- [`docs/archive/K4_ATTACK_LANDSCAPE.md`](../archive/K4_ATTACK_LANDSCAPE.md) — 3D attack fingerprint; historical evidence-basis narrative only
- [`docs/archive/K4-T1.md`](../archive/K4-T1.md) — Physical-geometric composite pipeline spec; its own mechanism (RIS, ENE routing, Hill 2×2) is null exactly as noted below. Its "Smithsonian Archive"/"K5" premise was flagged unverified/likely-fabricated as of 2026-09-01 — **that flag was itself wrong**; see "External Developments (2025–2026)" below
- [`docs/archive/K4-CLOCKS.html`](../archive/K4-CLOCKS.html) — Interactive clock theory artifact; NORTHEAST position labels known incorrect (see K4_KEYSTREAM_ANALYSIS.md §1)
- [`docs/archive/K4-FRONTEND.md`](../archive/K4-FRONTEND.md) — Frontend spec describing a SQLite schema that was never built (actual: Neon/Postgres)

## Vault Links
- [[repos/kryptos/docs/archive/K4-FRONTEND|K4-FRONTEND]] — frontend specification (archived, superseded)
- [[repos/kryptos/docs/archive/AUDIT_2026-06-01|AUDIT_2026-06-01]] — most recent src/ audit
- [[repos/kryptos|kryptos runbook]] — repo context
