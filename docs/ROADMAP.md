# Kryptos Roadmap

Breadcrumb: [Docs](INDEX.md) > Roadmap

Last Updated: 2026-09-02
Next Review: 2026-09-15

---

## Current Status

**K4 attack phase:** Phases 6 and 7 (Physical/Geometric Pivot, then the shape-changing transpose family + shadow-angle primitives + city-list keywords + cross-vector consensus scoring) are both complete — every code-executable direction identified so far, including the shape-changing transpose family and both readings of the "shadow of the word" hypothesis, has been implemented, executed against real K4, and returned null. Phase 8 (active) is sourcing three primary-source gaps that no further code can close on its own — see below.

**Architecture:** Confirmed substitution → transposition → K4. The substitution key is not derivable from any standard Berlin Clock row value (shifts at EAST/NORTHEAST reach 17, 20, 25 — exceeding the maximum clock row output of 11). The transposition is not a standard rectangular grid in any simple reading order, including both the shape-preserving and shape-changing 24-column geometric families. At minimum one un-parameterized step remains — the most concrete remaining candidates are genuinely physical/archival facts this repo cannot fully source on its own (the complete World Clock city list, still ~4 of 24 segments short; the Kryptos compass rose's exact bearing, still unmeasured by anyone as far as any source checked shows). A precisely-timed historical moment was found 2026-09-02 (see Phase 8).

---

## Phase 1 — All 14 Prior Attack Vectors ✅ (Complete)

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

## Phase 2 — P1–P7 Frontier Attacks ✅ (Complete — 2026-08-14)

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

## Phase 3 — Frontier Phase 2: 10 New Directions ✅ (Complete — all null; see TASKS.md Done)

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

## Phase 4 — Dashboard & Tooling ✅ (Complete)

- [x] React + Vite + TypeScript SPA in single Docker container
- [x] K4 Attack Dashboard: live Berlin Clock hero, K4 cipher with crib highlights, frozen CIA timestamp clocks
- [x] P1–P7 frontier queue with Run Attack buttons, live polling, Eureka banner
- [x] REST API: `/api/k4/attacks/run`, `/api/k4/attacks/jobs/{id}`, `/api/k4/attacks/frontier`
- [x] Ops Center, K1–K3 decoder, Database admin, Vault, SSE log tail

---

## Phase 6 — Physical/Geometric Pivot ✅ (Complete — 2026-09-01)

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

## Phase 7 — Shape-Changing Transposition + Physically-Modeled Shadow Hypothesis ✅ (Complete — 2026-09-01)

> All items below were implemented and executed against real K4 in the same pass they were planned. Full detail, sourcing, and exact candidate counts: `docs/analysis/K4_ACTIVE_RESEARCH.md`'s Phase 7 section — this is a summary.

### Shape-changing transpose family, wired

`composed_flat_indices` (`geometry_combined_sweep.py`) now correctly handles `reflection.SHAPE_CHANGING`'s four transpose-family transforms (4×24 grid → 24×4): the column-rotation step rotates mod the *current* axis size, and the flat-index formula uses the transposed grid's own row-major numbering. Verified as a valid bijection and correct `apply_forward`/`apply_inverse` round-trip before running at scale; shape-preserving reflections are byte-identical to before (regression-tested). Three runs, all null: default scope (155,520 candidates), geography-derived offsets (414,720), and via `run_three_layer_composite_geometric` (69,120).

### Physically-modeled "shadow of the word" hypothesis

Previously flagged out of scope (requires physical/photographic site access) — re-examined and found tractable. New module `kryptos.k4.solar_geometry`:

- **A — World Clock topper rotation.** Confirmed via Wikipedia: the topper rotates once per minute, decoupled from real solar position. Every *whole-minute* sourced historical timestamp is co-phased (0° apart) — verified in code, not assumed — so this honestly tested the full 0–23 rotation-offset range instead (1,244,160 candidates, null). **Resolved 2026-09-02** for two moments: `chronik-der-mauer.de`'s transcript of Hertle's own recording (his book, 2nd ed. 2015, p.194-195) gives sub-minute precision — the press-conference excerpt with the "sofort … unverzüglich" exchange opens 18:52:40 CET, ends 19:00:54 CET, both genuinely non-zero seconds. `precise_topper_shadow_offsets()` derives real offsets {16, 22} from these — 103,680 more candidates, null.
- **B — Real solar position at CIA HQ, Langley.** Implemented a standard NOAA/Meeus solar-position algorithm, verified against known reference points (Greenwich solstice noon, equator equinox noon). Real solar azimuth at CIA HQ, wired into `clock_rotation.geography_derived_bearings()` exactly like the Mengenlehreuhr bearing — flows into `GEO_BEARING_ORDER_NAMES` automatically. 108,864 candidates (4 whole-minute bearing pairs), null; expanded to 139,968 (6 pairs, 2 from the newly-precise timestamps above), still null.

### World Clock city-list keywords

Sourced: 146 cities + 1 International Date Line marker (147 total plate entries; resolved 2026-09-02 via convergent German+English Wikipedia, correcting an earlier 148 figure) across 24 segments. A complete list isn't available from any text source — but the clock is a permanently-photographed public sculpture, so `kryptos.k4.world_clock_cities` grew from 9 text-sourced names to 119 (7-photo pass) to **130** (2026-09-02, 9-photo pass, closing the Japan/Korea/Australia/Pacific gap — see Phase 8 below) by directly reading the engraved plates off Wikimedia Commons photographs taken at different rotations of the clock's cylinder. Tested as keyed alphabets across four passes (9,720 → 112,320 → 128,520 → 140,400 candidates, null) plus 3 sourced structural counts as rotation offsets (155,520 candidates, null).

### Cross-vector consensus scoring, built

`kryptos.k4.cross_vector_consensus` groups every null-artifact's candidates by *source attack vector* (unlike P16's merged-pool count) and flags a fragment only if it appears across ≥3 distinct vectors. Run against 30 accumulated artifacts (11 with extractable candidates): zero consensus anchors — no accidental cross-vector agreement.

### Scheduled overnight sweep runner, built

`kryptos.k4.overnight_runner.run_all_pending_sweeps` (invoked via `scripts/run_k4_overnight_sweeps.py`) runs every registered full-scope sweep in sequence, halting immediately on a `EurekaSignal` breakthrough rather than continuing past it. Closes the "someone has to remember to click it" gap.

**Grand total across Phase 7's real-K4 sweeps: 2,420,928 candidates, zero breakthroughs, zero cross-vector consensus.**

---

## Phase 8 — Primary-Source Sourcing (Active — opened 2026-09-01)

Everything code-derivable from current sourcing has been tried (Phases 1-7, all null). What's left needs new source material, not new code — three specific gaps opened 2026-09-01, each with concrete leads found by direct research (not just "someone should look"); two are now closed, one remains. Tracked as tasks in `docs/TASKS.md`; full sourcing detail and rationale in `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "Primary Sources Needed" section.

- ~~The remaining ~4 of 24 segments of the World Clock city list~~ — **closed 2026-09-02**: 130 of 146 confirmed (up from 119, up from 9 — count also resolved to 146+1 IDL=147, not 148, via convergent German+English Wikipedia). Closed by finding two more Wikimedia Commons photos taken at different rotations of the clock's cylinder (PJOENGJANG, TOKYO, SEOUL, DATUMSGRENZE, WELLINGTON, APIA, MARQUESAS, MAGADAN, SACHALIN, KAMTSCHATKA, KAPDESCHNEW, HONOLULU), essentially the full ring. Two adjacent hour segments showed no legible text in the photo checked — recorded as "not found," not fabricated. Retested as keyed alphabets: 140,400 candidates, still null.
- ~~A sub-minute-precision Nov 9 1989 timestamp~~ — **resolved 2026-09-02**: `chronik-der-mauer.de`'s transcript of Hertle's own recording gives 18:52:40/19:00:54 CET, both non-vacuous. See Phase 7 above.
- **The Kryptos compass rose's actual measured bearing.** Confirmed via `elonka.com`'s own wishlist to be a still-open *community-wide* question, not just a gap in this repo. One uncertain secondary estimate exists (~220°, explicitly flagged inexact). 2026-09-02: satellite imagery of the CIA courtyard was inspected directly (Google Maps, unblurred) and ruled out — resolution is building/lot-scale, not fine enough for a ground-level stone engraving. Remaining leads: a CIA FOIA/public-affairs request, or contacting Elonka Dunin directly. Outreach drafts for both (the questions to ask Elonka, and the FOIA request text) are ready — see `docs/TASKS.md`.

If none of these surface, this is genuinely paused — inventing more sweep variants over the same structural assumptions (grids, reflections, rotations, clock states) is not expected to move this forward; see the cross-vector consensus scan's zero-agreement result in Phase 7.

**External developments, 2026-09-02:** real-world events since this phase opened change its context, not its task list. Sanborn's own 1990 archival papers were found by independent researchers in September 2025 (not a cryptographic solve, by their own explicit statement); a real, Sanborn-confirmed K5 exists and will be released once K4 is cryptographically solved; and a third-party reconstruction (solvekryptos.com) claiming the actual cipher mechanism was checked against this repo's own confirmed crib positions — all four anchors land exactly right, zero offset. (An earlier pass here reported two anchors as off by exactly one position; that turned out to be a real bug in this repo's own `keystream_validator.K4_CRIBS`, found and fixed the same day — see the doc section below for the full account. The candidate's *mechanism* is still unpublished in enough detail to independently reproduce; only its plaintext's positional alignment is confirmed.) Full detail and sourcing: `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "External Developments (2025–2026)" section. This doesn't close or reprioritize the one remaining open lead above — if anything, the recovered plaintext's own opening line ("THE COMPASS ROSE IS HERE") is independent, external confirmation that the compass-rose bearing lead is worth the FOIA/Elonka outreach.

---

## Phase 5 — Post-Solution (Standing)

- [ ] Solution documentation — full attack path, key insights, solution narrative
- [ ] README update — reflect solution and cryptanalytic implications
- [ ] Archive all null-result artifacts with parameter provenance

---

## Key References

| Document | Purpose |
|----------|---------|
| `docs/archive/K4_ATTACK_LANDSCAPE.md` | Archived — full 3D fingerprint with evidence basis, historical reference only |
| `docs/analysis/K4_ACTIVE_RESEARCH.md` | Living null-result log and confirmed facts |
| `docs/analysis/K4_KEYSTREAM_ANALYSIS.md` | Derived shift sequences at all 4 crib windows |
| `docs/TASKS.md` | Implementation backlog with specific next steps |
| `frontend/` + Docker | `docker compose -f config/docker-compose.yml up -d` → http://localhost:8000 |
