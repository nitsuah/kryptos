# 2026 Completed Roadmap Phases & Done Tasks (Archive)

> 🧭 [kryptos](../../README.md) · [Index](../INDEX.md) · [Features](../FEATURES.md) · [Roadmap](../ROADMAP.md) · [Tasks](../TASKS.md) · [Changelog](../CHANGELOG.md) · [Metrics](../METRICS.md) <!-- nav -->

Archived 2026-09-24 in the 2027 planning reset (`pmo-ff`). This is the **verbatim** text of the completed
sections removed from [ROADMAP](../ROADMAP.md) (Phases 1–4, 6, 7 and the Phase 8 closed leads) and
[TASKS](../TASKS.md) (Done + resolved items), kept for provenance. The living source of truth for K4 status is
[K4_ACTIVE_RESEARCH](../analysis/K4_ACTIVE_RESEARCH.md); every vector is also in
[K4_CAPABILITY_TABLE](../analysis/K4_CAPABILITY_TABLE.md). A condensed summary is in [FEATURES](../FEATURES.md).

---

# Part 1 — Completed ROADMAP phases (as of 2026-09-03)

### Phase 1 — All 14 Prior Attack Vectors ✅ (Complete)

All single-layer and 2-layer composite vectors exhausted. Each produced a documented null result.

- [x] Single-layer repeating Vigenère (all key lengths 1–20)
- [x] Direct Berlin Clock Vigenère (all 720 clock states)
- [x] Keyed alphabet realignment (KRYPTOS, PALIMPSEST, ABSCISSA)
- [x] Full 2-layer composite: 3 alphabets × 3 grids × 720 clock states × ENE+columnar routes
- [x] Inverse transposition sweep (10×10, 7×14, 8×13 grids)
- [x] Hill 2×2 and 3×3 with crib constraints
- [x] Clock → Hill 2×2 invertibility pre-filter
- [x] 4-char clock key → Vigenère with NORTHEAST anchor
- [x] Non-standard Berlin Clock sub-row encodings
- [x] Berlin Clock lamp counts as transposition column widths
- [x] Beaufort cipher sweep
- [x] Quagmire I–IV (6,240 combinations)
- [x] Physical-grid tableau walk (108 routes)
- [x] ADFGVX and Nihilist fractionating ciphers

---

### Phase 2 — P1–P7 Frontier Attacks ✅ (Complete — 2026-08-14)

> All implemented, tested (75 tests passing), and live in the Docker container at `POST /api/k4/attacks/run`.

| Vector | Module | Status | Notes |
|--------|--------|--------|-------|
| P1 — 3-Layer Composite | `three_layer_composite.py` | ✅ done | CIA timestamps priority-tested, then a full 24-state hourly sweep — both executed, both null |
| P2 — Shadow/Null Masking | `masking_v2.py` | ✅ done | 8 variants, crib positions recalculated |
| P3 — K2 Coordinate Clocks | `k2_clock_states.py` | ✅ done | 5 K2-derived HH:MM timestamps |
| P4 — ±6h Timezone Offset | `k2_clock_states.py` | ✅ done | Doubles any clock sweep |
| P5 — 2-Crib Soft Filter | routes, threshold=2 | ✅ done | Surfaces near-misses |
| P6 — K3 Running Key | `running_key.py` | ✅ done | 4 variants, null result |
| P7 — Gronsfeld Cipher | `gronsfeld.py` | ✅ done | K2 digit keys, null result |

**Highest-value pending run:** P1 full 720-state sweep (unchecked "priority only" in the dashboard). ~51,840 combos, sub-minute runtime.

---

### Phase 3 — Frontier Phase 2: 10 New Directions ✅ (Complete — all null; see TASKS.md Done)

> *(Stale since 2026-08-14 — this section originally described P11–P20 as proposed/untested directions and was never updated after they were actually implemented and executed; corrected 2026-09-02.)* P11–P20 are all implemented, executed against real K4, and null — see `docs/TASKS.md`'s Done section for per-vector results, module names, and artifact references. The individual vector descriptions below are preserved as the **original scoping rationale** (hence present-tense "untested"/"never tested" language) — treat them as historical motivation, not current status. P16's corpus mining specifically found no anchor fragment above its 3% threshold when finally run.

### P11–P12 — Alphabet Keyword Expansion

The K1→K2→K3 key chain is KRYPTOS → PALIMPSEST → ABSCISSA. K4's keyed-alphabet seed is unknown. Sanborn's own name, clue words, and confirmed plaintext words are all untested.

| Vector | Keyword candidates | Basis |
|--------|-------------------|-------|
| **P11 — Sculptor/location names** | SANBORN, LANGLEY, SCHEIDT, WENDELL | Ed Scheidt co-designed K4 with Sanborn; never tested |
| **P11 — Plaintext-derived** | NORTHEAST, BERLIN, CLOCK, COMPASS | K4's own confirmed cribs as the alphabet seed |
| **P11 — Sanborn hint words** | SHADOW, BETWEEN, DIGETAL | Direct public clues: "go between the lines," "digital interpretation" |
| **P12 — Misspelling-derived** | I≡Q (IQLUSION), A≡E (DESPARATLY) | Intentional swaps in K1/K3 may define partial K4 substitution alphabet |

### P13–P15 — Coordinate Exploitation

The K2 plaintext encodes CIA HQ at 38°57'6.5"N, 77°8'44"W. Beyond HH:MM readings (P3), the coordinate encodes three untested cipher parameters:

- **P13 — Magnetic declination offset** — At CIA HQ on Nov 3 1990, IGRF magnetic declination ≈ −9.9°. Applied as clock-hand rotation, this shifts the nominal 13:00 clock state by ~10 minutes. Never tested.
- **P14 — CIA→Berlin great-circle bearing** — ~50.7°. Tests: Caesar shift 50 mod 26 = 24; clock minute offset 50; transposition start column 50 mod N. Four lightweight tests.
- **P15 — Coordinate digits as straddling checkerboard** — Digits 3,8,5,7,6,5 and 7,7,8,4,4 as row-header indices. A Cold War–era hand-encipherable scheme compatible with Sanborn's "no computers" constraint.

### P16–P18 — Candidate Text Analysis

The null-result sweeps produced thousands of candidate texts that were discarded after failing the 4-crib gate. These contain latent signal:

- **P16 — Corpus fragment mining** — Mine `K4_P{1-7}_*_NULL.json` null-result artifacts from the P1–P7 sweeps for consistent English 4–6-char fragments at positions 0–21 (before the EAST crib). Corpus is currently partial (priority-clock-time P1–P7 runs only, not the full 720-state sweep). Any fragment appearing in >3% of candidates at the same position across multiple attack types is a partial-plaintext anchor worth back-solving.
- **P17 — QQ/SS bigram hard constraints** — K4 has QQ at 12–13 and SS at 31–32. Consecutive identical ciphertext letters constrain valid key letters at those positions. Model as a pre-filter that prunes permutations incompatible with the doubled-letter constraint before scoring.
- **P18 — Repeating-key CSP** — 22 known (position, shift) pairs across 4 crib windows. For a repeating key of length L=7–15, positions ≡ mod L must share key letters. Arc-consistency + backtracking over this constraint set yields the key directly if it repeats. O(L × 26) search space per L.

### P19–P20 — Historical / Cryptographic Research

- **P19 — Ed Scheidt's name and NSA/CIA personnel** — Scheidt is the only known person who designed K4's encryption scheme with Sanborn. His name (SCHEIDT), his division (COMINT, TechSec), and CIA DCI names (WEBSTER) are untested keyed-alphabet seeds with strong prior probability.
- **P20 — Cyrillic Projector crossover** — Sanborn's 1997 "Cyrillic Projector" (UNC Chapel Hill) encodes a 1970 KGB document. The Roman-alphabet rendering of the KGB document keywords may cross-reference K4's key. Research and test any Roman-alphabet words from that document as K4 alphabet seeds.

---

### Phase 4 — Dashboard & Tooling ✅ (Complete)

- [x] React + Vite + TypeScript SPA in single Docker container
- [x] K4 Attack Dashboard: live Berlin Clock hero, K4 cipher with crib highlights, frozen CIA timestamp clocks
- [x] P1–P7 frontier queue with Run Attack buttons, live polling, Eureka banner
- [x] REST API: `/api/k4/attacks/run`, `/api/k4/attacks/jobs/{id}`, `/api/k4/attacks/frontier`
- [x] Ops Center, K1–K3 decoder, Database admin, Vault, SSE log tail

---

### Phase 6 — Physical/Geometric Pivot ✅ (Complete — 2026-09-01)

> Implemented and executed all 13 code-executable items from the "K4 Physical/Geometric Pivot" research brief (of 15 — items 10-11 were historical/archival research satisfied via sourced documentation, not code) across PRs [#192](https://github.com/nitsuah/kryptos/pull/192), [#193](https://github.com/nitsuah/kryptos/pull/193), [#194](https://github.com/nitsuah/kryptos/pull/194), and [#196](https://github.com/nitsuah/kryptos/pull/196), plus closed three loops (P2/P5/P6) that were wired in Phase 2/3 but never actually executed. See `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "Physical/Geometric Pivot" and "Phase 4 / v2.1" sections for full detail — this is a summary.

| Vector | Result |
|--------|--------|
| 24-column geometric permutation front-end (20 fill-orders/routes × 4 shape-preserving reflections × 3 rotation offsets × 3 remainder modes × 108-route physical tableau × 2 indicator bases) | Null — 155,520 candidates |
| Same, with `rotation_offsets` replaced by 6 geography-derived values (CIA→Berlin bearing mod 24, K2-coordinate hours, magnetic declination) | Null — 311,040 candidates |
| Same, using the exact (unsnapped) CIA→Berlin geodesic bearing as a route direction | Null — 15,552 candidates |
| Mengenlehreuhr → Weltzeituhr precise geodesic bearing (both current and 1990/Sanborn-era clock locations, both within 1.5–3.3° of exact ENE) as route direction | Null — 46,656 candidates |
| November 9 1989 (Berlin Wall fall) as a priority clock state, sourced to three specific CET moments that evening | Null — 17,280 candidates |
| Myszkowski transposition (repeated-letter keyword grouping) | Null — 4 candidates |
| Trifid cipher (27-cell cube fractionation) | Null — 78 candidates |
| Simulated-annealing substitution-key search behind the geometric permutation front-end | Null — 24 candidates |
| P2 shadow/null masking, thorough scope (wired in Phase 3, never previously executed) | Null — 6,144 candidates, 40 near-misses (single-keyword coincidences only) |
| P5 BERLIN+CLOCK 2-crib relaxed gate, brute-force **and** Phase-1 geometric transposition (never previously executed) | Null both ways — 34,560 + 69,120 candidates |
| P6 K3 plaintext as running Vigenère key (wired in Phase 0, never previously executed) | Null — 4 candidates |

**Precise geodesy**: added `kryptos.k4.geodesy` (`geographiclib` WGS84 geodesic engine) as a more precise alternative to `bearing_attack.py`'s spherical-trig bearing — used throughout the pivot's bearing-derived directions above. `bearing_attack.py` itself is untouched (its own null result stands).

**Dashboard**: added a Pivot Status panel (`frontend/src/components/PivotStatusPanel.tsx`, `GET /api/k4/attacks/pivot-status`) showing the hypothesis graph, candidate totals, and geodesy figures with measured/unverified labeling.

**Deliberately deferred to keep Phase 6 scoped** (now Phase 7's first item): `reflection.py`'s shape-changing transpose family (`transpose`, `anti_transpose`, `flip_h_then_transpose`, `flip_v_then_transpose`) was fully built and unit-tested but `geometry_combined_sweep.DEFAULT_REFLECTIONS` only ever exercises the four shape-preserving ones — this is the single largest untested slice of the pivot's own search space.

---

### Phase 7 — Shape-Changing Transposition + Physically-Modeled Shadow Hypothesis ✅ (Complete — 2026-09-01)

> All items below were implemented and executed against real K4 in the same pass they were planned. Full detail, sourcing, and exact candidate counts: `docs/analysis/K4_ACTIVE_RESEARCH.md`'s Phase 7 section — this is a summary.

### Shape-changing transpose family, wired

`composed_flat_indices` (`geometry_combined_sweep.py`) now correctly handles `reflection.SHAPE_CHANGING`'s four transpose-family transforms (4×24 grid → 24×4): the column-rotation step rotates mod the *current* axis size, and the flat-index formula uses the transposed grid's own row-major numbering. Verified as a valid bijection and correct `apply_forward`/`apply_inverse` round-trip before running at scale; shape-preserving reflections are byte-identical to before (regression-tested). Three runs, all null: default scope (155,520 candidates), geography-derived offsets (414,720), and via `run_three_layer_composite_geometric` (69,120).

### Physically-modeled "shadow of the word" hypothesis

Previously flagged out of scope (requires physical/photographic site access) — re-examined and found tractable. New module `kryptos.k4.solar_geometry`:

- **A — World Clock topper rotation.** Confirmed via Wikipedia: the topper rotates once per minute, decoupled from real solar position. Every *whole-minute* sourced historical timestamp is co-phased (0° apart) — verified in code, not assumed — so this honestly tested the full 0–23 rotation-offset range instead (1,244,160 candidates, null). **Resolved 2026-09-02** for two moments: `chronik-der-mauer.de`'s transcript of Hertle's own recording (his book, 2nd ed. 2015, p.194-195) gives sub-minute precision — the press-conference excerpt with the "sofort … unverzüglich" exchange opens 18:52:40 CET, ends 19:00:54 CET, both genuinely non-zero seconds. `precise_topper_shadow_offsets()` derives real offsets {16, 22} from these — 103,680 more candidates, null.
- **B — Real solar position at CIA HQ, Langley.** Implemented a standard NOAA/Meeus solar-position algorithm, verified against known reference points (Greenwich solstice noon, equator equinox noon). Real solar azimuth at CIA HQ, wired into `clock_rotation.geography_derived_bearings()` exactly like the Mengenlehreuhr bearing — flows into `GEO_BEARING_ORDER_NAMES` automatically. 108,864 candidates (4 whole-minute bearing pairs), null; expanded to 139,968 (6 pairs, 2 from the newly-precise timestamps above), still null.

### World Clock city-list keywords

Reference total (not yet all directly confirmed): 146 cities + 1 International Date Line marker (147 total plate entries; resolved 2026-09-02 via convergent German+English Wikipedia, correcting an earlier 148 figure) across 24 segments — this is the clock's known structural size, not a claim that all 146 names are sourced. A complete name list isn't available from any text source — but the clock is a permanently-photographed public sculpture, so `kryptos.k4.world_clock_cities` grew from 9 text-sourced names to 119 (7-photo pass) to **130 directly confirmed** (2026-09-02, 9-photo pass, closing the Japan/Korea/Australia/Pacific *segment* gap — see Phase 8 below) by directly reading the engraved plates off Wikimedia Commons photographs taken at different rotations of the clock's cylinder; 16 of 146 names remain unconfirmed. Tested as keyed alphabets across four passes (9,720 → 112,320 → 128,520 → 140,400 candidates, null) plus 3 sourced structural counts as rotation offsets (155,520 candidates, null).

### Cross-vector consensus scoring, built

`kryptos.k4.cross_vector_consensus` groups every null-artifact's candidates by *source attack vector* (unlike P16's merged-pool count) and flags a fragment only if it appears across ≥3 distinct vectors. Run against 30 accumulated artifacts (11 with extractable candidates): zero consensus anchors — no accidental cross-vector agreement.

### Scheduled overnight sweep runner, built

`kryptos.k4.overnight_runner.run_all_pending_sweeps` (invoked via `scripts/run_k4_overnight_sweeps.py`) runs every registered full-scope sweep in sequence, halting immediately on a `EurekaSignal` breakthrough rather than continuing past it. Closes the "someone has to remember to click it" gap.

**Grand total across Phase 7's real-K4 sweeps: 2,420,928 candidates, zero breakthroughs, zero cross-vector consensus.**

### Phase 8 — full text as of 2026-09-03 (two of three leads closed)

Everything code-derivable from current sourcing has been tried (Phases 1-7, all null). What's left needs new source material, not new code — three specific gaps opened 2026-09-01, each with concrete leads found by direct research (not just "someone should look"); two are now closed, one remains. Tracked as tasks in `docs/TASKS.md`; full sourcing detail and rationale in `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "Primary Sources Needed" section.

- ~~The remaining ~4 of 24 segments of the World Clock city list~~ — **closed 2026-09-02**: 130 of 146 confirmed (up from 119, up from 9 — count also resolved to 146+1 IDL=147, not 148, via convergent German+English Wikipedia). Closed by finding two more Wikimedia Commons photos taken at different rotations of the clock's cylinder (PJOENGJANG, TOKYO, SEOUL, DATUMSGRENZE, WELLINGTON, APIA, MARQUESAS, MAGADAN, SACHALIN, KAMTSCHATKA, KAPDESCHNEW, HONOLULU), essentially the full ring. Two adjacent hour segments showed no legible text in the photo checked — recorded as "not found," not fabricated. Retested as keyed alphabets: 140,400 candidates, still null.
- ~~A sub-minute-precision Nov 9 1989 timestamp~~ — **resolved 2026-09-02**: `chronik-der-mauer.de`'s transcript of Hertle's own recording gives 18:52:40/19:00:54 CET, both non-vacuous. See Phase 7 above.
- **The Kryptos compass rose's actual measured bearing.** Confirmed via `elonka.com`'s own wishlist to be a still-open *community-wide* question, not just a gap in this repo. One uncertain secondary estimate exists (~220°, explicitly flagged inexact). 2026-09-02: satellite imagery of the CIA courtyard was inspected directly (Google Maps, unblurred) and ruled out — resolution is building/lot-scale, not fine enough for a ground-level stone engraving. Remaining leads: a CIA FOIA/public-affairs request, or contacting Elonka Dunin directly. Outreach drafts for both (the questions to ask Elonka, and the FOIA request text) are ready — see `docs/TASKS.md`.

If none of these surface, this is genuinely paused — inventing more sweep variants over the same structural assumptions (grids, reflections, rotations, clock states) is not expected to move this forward; see the cross-vector consensus scan's zero-agreement result in Phase 7.

**External developments, 2026-09-02:** real-world events since this phase opened change its context, not its task list. Sanborn's own 1990 archival papers were found by independent researchers in September 2025 (not a cryptographic solve, by their own explicit statement); a real, Sanborn-confirmed K5 exists and will be released once K4 is cryptographically solved; and a third-party reconstruction (solvekryptos.com) claiming the actual cipher mechanism was checked against this repo's own confirmed crib positions — all four anchors land exactly right, zero offset. (An earlier pass here reported two anchors as off by exactly one position; that turned out to be a real bug in this repo's own `keystream_validator.K4_CRIBS`, found and fixed the same day — see the doc section below for the full account. The candidate's *mechanism* is still unpublished in enough detail to independently reproduce; only its plaintext's positional alignment is confirmed.) Full detail and sourcing: `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "External Developments (2025–2026)" section. This doesn't close or reprioritize the one remaining open lead above — if anything, the recovered plaintext's own opening line ("THE COMPASS ROSE IS HERE") is independent, external confirmation that the compass-rose bearing lead is worth the FOIA/Elonka outreach.

**2026-09-03 follow-up:** a confidence-tiered plaintext data structure (`kryptos.k4.plaintext_evidence` — 24 CONFIRMED vs. 73 RECONSTRUCTED-and-unverified), two doc methodology fixes (IC/monoalphabetic overclaims), and a real geodesic/geometric test of a Cold War Kamchatka hunch (not on the CIA→Berlin bearing; is a specific World Clock sector, tested as rotation offsets — 207,360 candidates, null) — plus a third outreach draft (CIA Public Affairs, a verified-real limited-visit mechanism). Full detail: `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "External developments, follow-up (2026-09-03)" section.

**2026-09-03 follow-up, round 2:** a second external review pass (a fresh capability-table audit of every attack vector run to date) surfaced four genuinely new, previously-unbuilt items rather than repeats — all implemented and run against real K4 the same session. The known-plaintext-inversion engine (built in the first 09-03 pass) was extended to the rectangular-grid transposition family (`inverse_transposition_sweep.K4_GRID_GEOMETRIES`'s 7×14/8×13/10×10 grids), fully exhaustive, no sampling: 3,674,160 permutations (7!+8!+10!) tested in 1,280.74s (~21.3 min, single-core) — null, on both the repeating-period and a broader monoalphabetic-consistency check. CIA's own confirmed "read from the back" fact was tested directly, not just documented: `physical_grid.build_tableau(mirrored=True)` models the real algebraic consequence (a genuine Beaufort-style construction), full 108-route × 2-indicator-base sweep — 216 candidates, null. The reconstructed plaintext's own vocabulary (`ROSE`, `POSITION`, `COMMISSION`, `WHICH`) became a new keyed-alphabet source — 4,320 candidates, null. Separately, a repo-hygiene pass consolidated 17 duplicate copies of the K4 ciphertext literal (verified byte-identical first) down to one canonical import. Full detail: `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "External developments, follow-up (2026-09-03)" section (same section as round 1, appended the same day).

**2026-09-03 follow-up, round 3:** checked Elonka's own measurement wishlist (`elonka.com/kryptos/wishlist.html`) for anything code/research could help with, not just outreach. Nearly all 37 items are on-site physical measurements this repo can't do (font/carving texture, exact bearings, on-site photography, interviews). One item — a source for photos/documentation of the "K0" Morse-code entrance slabs, a part of the installation this project had never used at all — led somewhere real: `rumkin.com/reference/kryptos/k0` gives the actual decoded transcriptions, cross-checked against Elonka's page. Seven genuinely new words (VIRTUALLY, INVISIBLE, LUCID, MEMORY, FORCES, INTERPRETATION, DIGITAL — already flagged as K4-relevant in the language scorer's bonus vocabulary from an earlier session, but never tested as keyed-alphabet seeds) became `kryptos.k4.k0_morse_keywords`: 7,560 candidates, null. Separately, when directly asked "is there really nothing left to implement," an honest audit (not deference to "the roadmap says complete") found a real gap: `hypotheses.py`'s `PlayfairHypothesis`/`FourSquareHypothesis`/`BifidHypothesis`(classic 5x5)/`AutokeyHypothesis` were built and unit-tested but never actually run against real K4 with real crib gating, and never logged anywhere. New `kryptos.k4.classical_cipher_sweep` closes that: 1,065 candidates (30-word expanded keyword list), null, zero near-misses. Full detail: `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "External developments, follow-up (2026-09-03)" section.

---

# Part 2 — TASKS Done (as of 2026-09-03)

#### External developments follow-up (opened 2026-09-02, resolved 2026-09-02)

- [x] ~~Explain the single-character discrepancy in solvekryptos.com's claimed K4 plaintext~~ — **resolved same day, as a real bug, not a discrepancy.** A CodeRabbit review comment on PR #203 questioned whether the "discrepancy" was actually an indexing artifact; investigating it found this repo's own `keystream_validator.K4_CRIBS` had stored `EAST`/`NORTHEAST` one position too high (22/26 instead of the real 21/25) since that constant's introduction — confirmed three independent ways (direct ciphertext search, this project's own `annotate_cribs()`, and an existing-but-previously-unenforced test). Once fixed, `solvekryptos.com`'s claimed plaintext passes all 4 confirmed anchors exactly, zero offset. The same bug was duplicated in `key_csp.py` and `clock_hill_attack.py`, both fixed alongside it; see `K4_ACTIVE_RESEARCH.md`'s "External Developments" section for the full account.

### Done

#### External review follow-up (2026-09-03, all null)

> Full detail: `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "External developments, follow-up (2026-09-03)" section.

- [x] **Fixed two IC/methodology overclaims** in the Ruled Out table — "IC rules out monoalphabetic substitution" and "non-uniform local IC proves substitution-then-transposition" were both overstated. The monoalphabetic row now rests on a sharper, code-verified argument instead: 8 of 9 repeated plaintext letters in the 24 confirmed crib characters map to different ciphertext letters at each occurrence, which no fixed 1:1 substitution can produce.
- [x] **Built `kryptos.k4.plaintext_evidence`** — a confidence-tiered plaintext data structure distinguishing the 24 Sanborn-CONFIRMED crib characters from solvekryptos.com's 73-character RECONSTRUCTED guess (explicitly not Sanborn's unpublished archival text). `candidate_repeating_periods()` tested the reconstructed text's full implied keystream for a repeating-key period 2-20: none found. Exploratory diagnostic only, never used to gate a candidate.
- [x] **Checked the Kamchatka Cold War hunch geodesically** — the CIA→Berlin bearing does not continue toward Kamchatka (curves southeast past Berlin; a fresh bearing restarted at Berlin points closer to Vladivostok than Kamchatka or Magadan). Reframed around the real anchor instead: KAMTSCHATKA is a specific node on K4's own named "BERLIN CLOCK." Added `world_clock_cities.WORLD_CLOCK_SEGMENT_HOUR` (sourced hour-index per segment, read directly off the photos) and `run_world_clock_sector_sweep` — 207,360 candidates, null.
- [x] **Built the "known-plaintext" attack surface an external review proposed** — `kryptos.k4.known_plaintext_inversion` inverts every already-enumerated transposition (same `geometry_combined_sweep.composed_flat_indices` primitive) against real K4, derives the substitution shift the reconstructed plaintext would require, and checks for a repeating-key period. 11,520 transposition hypotheses tested (full order × reflection × 24 rotations × remainder-mode space): zero showed a consistent period 2–20 — null. Never gates a candidate; raises no `EurekaSignal`, since it rests on the unverified reconstructed plaintext.
- [x] **Built `kryptos.k4.physical_geometry`** — a typed schema for the sculpture's physical facts, every field unmeasured (`None`) until a cited source supplies it. Only the tableau's back-only reading direction is actually confirmed (CIA's own page); compass bearing and lodestone deflection remain open per Phase 8.
- [x] **Built `kryptos.k4.constraint_chain.evaluate_candidate`** — reports how many of 5 independent evidence layers (confirmed cribs, Sanborn-hint keywords, reconstruction alignment, language score vs. raw-ciphertext baseline, physical geometry) a candidate satisfies at once, without creating a new promotion gate. `validation.validate_candidate`'s strict gate is unchanged and remains the only thing that can raise a candidate's status.
- [x] **Verified two claims from an external review before acting on them** — CIA's own Kryptos page confirms the Vigenère tableau was "intentionally flipped so it can only be read from the back" (checked directly, not assumed); CIA's own FAQ confirms limited academic/civic-group visits exist. Corrected one claim from that review before it entered this repo's docs — the November 2025 auction buyer is Paradigm, publicly self-identified, not "anonymous."

#### External review follow-up, round 2 (2026-09-03, all null)

> Full detail: `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "External developments, follow-up (2026-09-03)" section (same section as round 1, appended the same day).

- [x] **Extended `known_plaintext_inversion` to the rectangular-grid family** — `implied_shifts_rectangular()` / `scan_rectangular_transpositions()` apply the same known-plaintext-inversion idea to `inverse_transposition_sweep.K4_GRID_GEOMETRIES`'s 7×14/8×13/10×10 grids (never previously tested this way — that module's own sweeps only ever scored candidates by crib/language match). Added a second, broader diagnostic alongside the repeating-period check: does the implied mapping form a consistent monoalphabetic substitution at all (any bijection, not just a repeating shift). Fully exhaustive, no sampling: 3,674,160 permutations (7!+8!+10!) tested in 1,280.74s — null on both checks.
- [x] **Tested the CIA-confirmed "read from the back" fact directly** — `physical_grid.build_tableau(mirrored=True)` models the actual algebraic consequence of reading the same cyclic tableau from its back (`keyed[(i-j)%26]`, a genuine Beaufort-style construction, not a cosmetic relabeling) rather than just documenting the fact. Full 108-route × 2-indicator-base sweep: 216 candidates, null.
- [x] **New keyword source: the reconstructed plaintext's own vocabulary** — `plaintext_evidence.RECONSTRUCTED_PLAINTEXT_KEYWORDS` (`ROSE`, `POSITION`, `COMMISSION`, `WHICH` — words in the reconstruction not already covered by P11's EAST/NORTHEAST/BERLIN/CLOCK/COMPASS). `run_reconstructed_plaintext_keyword_sweep()`: 4,320 candidates, null.
- [x] **Repo hygiene: consolidated 17 duplicate copies of the K4 ciphertext literal** — verified byte-identical across all 17 before touching anything; 15 now import `physical_grid.K4` (the module 5 others already treated as canonical). `quagmire_sweep.py` keeps its own copy deliberately (importing back would be circular, since `physical_grid.py` imports from it) — documented in place.
- [x] **Closed a real gap in "everything's implemented": `hypotheses.py`'s orphaned classical-cipher classes** — found while auditing the roadmap for the user's "is there really nothing left?" question, not from an external review. `PlayfairHypothesis`, `FourSquareHypothesis`, `BifidHypothesis` (classic 5x5), and `AutokeyHypothesis` were fully implemented and unit-tested, but only ever run on a truncated fixture as a smoke test — never against real K4, never crib-gated, never logged. New `kryptos.k4.classical_cipher_sweep` runs all four for real, scored by this project's own `positional_crib_hits`, with a 30-word expanded keyword list (union of every keyword tested elsewhere in this project). 1,065 candidates, null, zero near-misses.
- [x] **New keyword source from a part of the sculpture never used before: the "K0" Morse-code entrance slabs** (prompted by checking Elonka's wishlist page for anything actionable in code, not just outreach) — `kryptos.k4.k0_morse_keywords`, sourced and cross-checked against `elonka.com/kryptos/wishlist.html` and `rumkin.com/reference/kryptos/k0`. Seven genuinely new keywords (`VIRTUALLY`, `INVISIBLE`, `LUCID`, `MEMORY`, `FORCES`, `INTERPRETATION`, `DIGITAL`) not previously tested as keyed-alphabet seeds, though already flagged as K4-relevant vocabulary in `scoring_instructional.py`'s language-scoring bonus list. `run_k0_morse_keyword_sweep()`: 7,560 candidates, null.

#### Physical/Geometric Pivot — Phase 7 (2026-09-01, all null)

> Full detail: `docs/ROADMAP.md` Phase 7, `docs/analysis/K4_ACTIVE_RESEARCH.md`'s Phase 7 section.

- [x] **Wired `reflection.SHAPE_CHANGING` into a geometric sweep** — extended `composed_flat_indices` to correctly handle the 4×24→24×4 transpose family (verified bijection + round-trip; shape-preserving reflections unchanged). 3 runs: default scope (155,520), geography-derived offsets (414,720), via `run_three_layer_composite_geometric` (69,120). All null.
- [x] **Solar-position primitive for the "shadow of the word" hypothesis** — `kryptos.k4.solar_geometry`. Hypothesis A (World Clock topper, confirmed 1 rev/min via Wikipedia) honestly reduced to a full 0-23 rotation-offset sweep after finding every *whole-minute* sourced timestamp pair vacuously co-phased (1,244,160 candidates, null). Hypothesis B (real solar azimuth at CIA HQ via a verified NOAA/Meeus algorithm) wired into `clock_rotation.geography_derived_bearings()` (108,864 candidates, null).
- [x] **Sub-minute-precision Nov 9 1989 timestamp, sourced** (2026-09-02) — `chronik-der-mauer.de`'s word-for-word transcript of Hertle's own recording (citing his book, 2nd ed. 2015, p.194-195): the press-conference excerpt opens 18:52:40 CET, ends 19:00:54 CET — both with genuine non-zero seconds, resolving hypothesis A's vacuity for these two moments. `solar_geometry.precise_topper_shadow_offsets()` derives real (non-vacuous) rotation offsets {16, 22}; both timestamps also expand hypothesis B's solar-bearing set. Reran both sweeps: 103,680 candidates (precise topper) + 139,968 (expanded solar bearing, was 108,864). All null.
- [x] **World Clock city-list as keyword source** — `kryptos.k4.world_clock_cities`. Expanded across three follow-up passes (130 individually-sourced city names as of 2026-09-02, up from the original 9) as keyed alphabets (9,720 → 112,320 → 128,520 → 140,400 candidates, null) plus 3 sourced structural counts (146/147/24) as rotation offsets (155,520 candidates, null). Complete 146-name list still unavailable — not fabricated. **2026-09-02: the "~4 missing segments" primary-source gap closed** — found two more Wikimedia Commons photos taken at different cylinder rotations, adding PJOENGJANG/TOKYO/SEOUL (Japan/Korea), DATUMSGRENZE/WELLINGTON/APIA/MARQUESAS (NZ/Pacific), MAGADAN/SACHALIN/KAMTSCHATKA/KAPDESCHNEW/HONOLULU (Russian Far East/Hawaii) — essentially the full 24-segment ring, only 16 names short of the complete 146.
- [x] **Cross-vector consensus scoring** — `kryptos.k4.cross_vector_consensus`. Groups candidates by source attack vector (unlike P16's merged-pool count); flags fragments in ≥3 distinct vectors. Scanned 30 artifacts, 11 with candidates: zero consensus anchors.
- [x] **Scheduled overnight full-sweep runner** — `kryptos.k4.overnight_runner.run_all_pending_sweeps` + `scripts/run_k4_overnight_sweeps.py`. Runs every registered full-scope sweep in sequence, halts immediately on `EurekaSignal`.

#### Physical/Geometric Pivot — Phase 6 (2026-08-29 to 2026-09-01, all null)

> Full detail: `docs/ROADMAP.md` Phase 6, `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "Physical/Geometric Pivot" and "Phase 4 / v2.1" sections. PRs [#192](https://github.com/nitsuah/kryptos/pull/192), [#193](https://github.com/nitsuah/kryptos/pull/193), [#194](https://github.com/nitsuah/kryptos/pull/194), [#196](https://github.com/nitsuah/kryptos/pull/196).

- [x] 24-column geometric permutation front-end (`geometry24.py`, 16 fill orders) composed with reflections/rotations/remainder modes and the 108-route physical tableau (`geometry_combined_sweep.py`) — 155,520 + 311,040 + 15,552 candidates, null
- [x] Precise WGS84 geodesy (`kryptos.k4.geodesy`, `geographiclib`) as a more precise alternative to `bearing_attack.py`'s spherical trig
- [x] Mengenlehreuhr → Weltzeituhr precise bearing (current + 1990/Sanborn-era locations, both within 1.5–3.3° of exact ENE) as route direction — 46,656 candidates, null
- [x] November 9 1989 (Berlin Wall fall) as a sourced priority clock state — 17,280 candidates, null
- [x] Myszkowski transposition, Trifid cipher (previously "Deferred P8–P10") — 4 + 78 candidates, null
- [x] Simulated-annealing substitution-key search behind the geometric permutation front-end — 24 candidates, null
- [x] P2 shadow/null masking, thorough scope (wired in Phase 2, executed for the first time) — 6,144 candidates, null
- [x] P5 BERLIN+CLOCK 2-crib relaxed gate, brute-force **and** geometric transposition (wired in Phase 0, executed for the first time) — 34,560 + 69,120 candidates, null
- [x] P6 K3-plaintext running Vigenère key (wired in Phase 0, executed for the first time) — 4 candidates, null
- [x] Dashboard Pivot Status panel (`PivotStatusPanel.tsx`, `GET /api/k4/attacks/pivot-status`)
- [x] Fixed pre-existing O(n²) near-miss duplication bug in the P2 API handler (`k4_attack_routes.py`)

#### Alphabet keyword expansion, coordinate deep-dive, candidate-text analysis — Phase 2/3 (P11–P20, 2026-08-14)

> All implemented and tested; two (P13, P14 — the geodesy-related vectors) subsequently superseded or extended by Phase 6's precise geodesy and geography-derived route directions. See `docs/analysis/K4_ACTIVE_RESEARCH.md` for full current-state detail per vector.

- [x] **P11 — Alternative keyed-alphabet keywords** — SANBORN, LANGLEY, WENDELL, NORTHEAST, BERLIN, CLOCK, SHADOW, BETWEEN, COMPASS, DIGETAL tested in the full 3-layer composite sweep. Null.
- [x] **P12 — Misspelling-derived substitution** — K1's IQLUSION / K3's DESPARATLY swapped-letter pairs modeled as a partial keyed-alphabet definition. Null.
- [x] **P13 — Magnetic declination clock offset** — `k2_clock_states.get_magnetic_declination_states()`. Null.
- [x] **P14 — CIA→Berlin great-circle bearing as cipher parameter** — `bearing_attack.CIA_BERLIN_BEARING_INT`. Null (Phase 6 later added the *unrounded, precise-geodesy* version of this same bearing as a route direction — also null).
- [x] **P15 — K2 coordinate digits as straddling checkerboard** — `kryptos.k4.straddling_checkerboard`, 36 combinations. Null.
- [x] **P16 — Candidate corpus fragment mining** — `kryptos.k4.corpus_miner.mine_candidate_corpus`. No anchor fragment found above the 3% threshold.
- [x] **P17 — QQ/SS bigram hard constraints** — `kryptos.k4.bigram_constraint`. Null.
- [x] **P18 — Repeating-key CSP over all 4 crib windows** — `kryptos.k4.key_csp.solve_key_csp`. No solution for key lengths 7–15.
- [x] **P19 — Sanborn advisory names as alphabet keywords** — `kryptos.k4.advisory_keywords.run_advisory_keyword_sweep`. Null.
- [x] **P20 — Cyrillic Projector crossover** — `kryptos.k4.cyrillic_projector.run_cyrillic_projector_sweep`. Null.

#### Core P1–P7 Frontier Attacks — Phase 0 (complete)

- [x] **P1 — 3-Layer Composite** (`three_layer_composite.py`) — keyed-alphabet → clock-Vigenère → columnar transposition. Both CIA-timestamp priority states **and** the full 24-state hourly sweep executed. Null. Artifact: `K4_3LAYER_NULL.json`.
- [x] **P2 — Shadow/Null Masking** (`masking_v2.py`) — see Phase 6 above for the actual execution (this entry covers implementation only).
- [x] **P3 — K2 Coordinate Clock Times** (`k2_clock_states.py`) — 5 K2-derived HH:MM timestamps. Null.
- [x] **P4 — ±6h Timezone Offset** (in `k2_clock_states.py`). Null.
- [x] **P5 — 2-Crib Soft Filter** — see Phase 6 above for the actual execution (this entry covers implementation only).
- [x] **P6 — K3 Running Key** (`running_key.py`) — see Phase 6 above for the actual execution (this entry covers implementation only).
- [x] **P7 — Gronsfeld Cipher** (`gronsfeld.py`) — K2 coordinate digit keys. Null.

#### K4 Attack Dashboard & UI

- [x] K4 Attack Dashboard with live Berlin Clock hero section
- [x] K4CipherVisualizer with EAST/NORTHEAST/BERLIN/CLOCK crib highlights
- [x] P1–P7 frontier queue with Run Attack buttons and live polling
- [x] Stats strip, progress bars, Eureka banner

#### Dashboard, REST API, Web UI & Ops Strategy KB

- [x] FastAPI dashboard endpoints — `/api/status`, `/api/runs`, `/api/candidates`, `POST /api/decrypt`
- [x] Neon persistence — `campaign_runs` + `candidates` + `strategy_kb` tables
- [x] React + Vite + TypeScript SPA — terminal-aesthetic; Ops Center, K1–K3 decoder, Database, Vault, K4 Dashboard
- [x] K4 Attack API — `POST /api/k4/attacks/run`, `GET /api/k4/attacks/jobs/{id}`, `GET /api/k4/attacks/frontier`
- [x] Single-container Docker delivery — FastAPI serves built SPA from `frontend/dist`
- [x] turbovec RAG — semantic search over `artifacts/` at `/api/rag/*`
- [x] SSE live-log tail — `GET /api/stream/logs` via `LogTail` EventSource component

#### Validation & hardening

- [x] K3 double-transposition Monte Carlo — `kryptos.k3.double_rotation_solver` recovers K3 plaintext #1 out of 11,664 candidates
- [x] K1/K2 Vigenère stress tests — noise injection, wrong key lengths, partial ciphertext
- [x] Agent module review — fixed 5 bugs in `AutonomousCoordinator` integration; `linguist.py` wired into `PlaintextValidator`

#### Earlier K4 attacks (all null results)

- [x] Clock → Hill 2×2, 4-char clock key → Vigenère, non-standard sub-row encodings, lamp counts as column widths
- [x] Beaufort cipher sweep
- [x] Quagmire I–IV (6,240 combinations)
- [x] Physical-grid tableau walk (108 routes)
- [x] ADFGVX and Nihilist fractionating ciphers

#### Misc

- [x] Fix off-by-one position labels in attack landscape doc: `BERLIN: [64]` → `[63]` (a real fix, confirmed correct). `NORTHEAST: [25]` → `[26]` was **also applied at the time but was itself wrong** — `[25]` was the correct 0-indexed position all along; this repo's own `keystream_validator.K4_CRIBS` carried the same wrong `[26]` value until it was found and fixed 2026-09-02 (see `K4_ACTIVE_RESEARCH.md`'s External Developments section). Left here as the historical record rather than silently rewritten.
- [x] `.gitignore` entries for `K4_*_NULL.json`, `K4_BREAKTHROUGH_SNAPSHOT.md`, `*_EUREKA.md`
