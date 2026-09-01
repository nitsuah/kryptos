# Kryptos Roadmap

Breadcrumb: [Docs](INDEX.md) > Roadmap

Last Updated: 2026-09-01
Next Review: 2026-09-15

---

## Current Status

**K4 attack phase:** Phase 6 (Physical/Geometric Pivot) complete — all 15 items from the pivot research brief plus P2/P5/P6 loop closures are implemented, executed, and null. Phase 7 (next) is open: the one deliberately-deferred slice of the pivot's own search space (`reflection.py`'s shape-changing transpose family), a computationally-modelable take on the "shadow of the word" hypothesis, and World Clock city-list keyword research.

**Architecture:** Confirmed substitution → transposition → K4. The substitution key is not derivable from any standard Berlin Clock row value (shifts at EAST/NORTHEAST reach 17, 20, 25 — exceeding the maximum clock row output of 11). The transposition is not a standard rectangular grid in any simple reading order, including the 24-column/reflection/rotation geometric family added in Phase 6. At minimum one un-parameterized step remains — most likely either the shape-changing transpose (untested), or a genuinely physical parameter (shadow angle, city-list ordering) this repo has not yet modeled.

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
| P1 — 3-Layer Composite | `three_layer_composite.py` | ✅ done | CIA timestamps priority-tested; full 720-state sweep pending |
| P2 — Shadow/Null Masking | `masking_v2.py` | ✅ done | 8 variants, crib positions recalculated |
| P3 — K2 Coordinate Clocks | `k2_clock_states.py` | ✅ done | 5 K2-derived HH:MM timestamps |
| P4 — ±6h Timezone Offset | `k2_clock_states.py` | ✅ done | Doubles any clock sweep |
| P5 — 2-Crib Soft Filter | routes, threshold=2 | ✅ done | Surfaces near-misses |
| P6 — K3 Running Key | `running_key.py` | ✅ done | 4 variants, null result |
| P7 — Gronsfeld Cipher | `gronsfeld.py` | ✅ done | K2 digit keys, null result |

**Highest-value pending run:** P1 full 720-state sweep (unchecked "priority only" in the dashboard). ~51,840 combos, sub-minute runtime.

---

## Phase 3 — Frontier Phase 2: 10 New Directions ✅ (Implemented — see TASKS.md)

> P11–P20 are all implemented (see `docs/TASKS.md` Active section for per-vector detail and module names). "Implemented" here means the attack code exists and is unit-tested, not that every vector has been exhaustively run to a null/positive result — P16's corpus mining, in particular, is scanning a still-partial corpus (only priority-clock-time P1–P7 runs, not the full 720-state sweep).

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

> Implemented and executed all 15 items from the "K4 Physical/Geometric Pivot" research brief across PRs [#192](https://github.com/nitsuah/kryptos/pull/192), [#193](https://github.com/nitsuah/kryptos/pull/193), [#194](https://github.com/nitsuah/kryptos/pull/194), and [#196](https://github.com/nitsuah/kryptos/pull/196), plus closed three loops (P2/P5/P6) that were wired in Phase 2/3 but never actually executed. See `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "Physical/Geometric Pivot" and "Phase 4 / v2.1" sections for full detail — this is a summary.

| Vector | Result |
|--------|--------|
| 24-column geometric permutation front-end (16 fill orders × 4 shape-preserving reflections × 3 rotation offsets × 3 remainder modes) combined with the 108-route physical tableau | Null — 155,520 candidates |
| Same, with geography-derived rotation offsets (CIA→Berlin bearing mod 24, K2-coordinate hours, magnetic declination) | Null — 311,040 candidates |
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

## Phase 7 — Shape-Changing Transposition + Physically-Modeled Shadow Hypothesis (Active — opened 2026-09-01)

### Quick win: wire the shape-changing transpose family into a sweep

`reflection.SHAPE_CHANGING` (4 transforms) turns a 4×24 grid into a 24×4 grid — `geometry_combined_sweep` was built only for shape-preserving transforms, so this needs a small variant (or extension) that re-derives `composed_flat_indices` for the transposed shape rather than assuming the fill order and reflection share one grid. Bounded scope: 16 fill orders × 4 shape-changing reflections × 3 rotation offsets × 3 remainder modes × 108 tableau routes × 2 indicator bases — same order of magnitude as Phase 6's shape-preserving runs (~155K candidates).

### Physically-modeled "shadow of the word" hypothesis

Sanborn: *"the secret is the shadow of the word"* and *"who says it is even a math solution?"* — previously flagged in `K4_ATTACK_LANDSCAPE.md` as out of scope because it seemed to require physical/photographic site access. Re-examined 2026-08-31: both plausible readings are actually computable without site access.

- **A — World Clock (Weltzeituhr) topper rotation.** The rotating solar-system sculpture atop the Alexanderplatz World Clock turns at a fixed, documented rate (1 revolution/minute) *decoupled from real solar position* — so its orientation at any moment is a deterministic function of elapsed time from a reference timestamp, not an ephemeris lookup. Model as `angle(t) = (seconds_since_reference / 60 * 360) mod 360`; sweep the one genuinely free parameter (the reference timestamp) anchored to the already-computed ENE compass-rose bearing (Phase 6: 67.5–70.8°) rather than treating it as unconstrained.
- **B — Real sunlight shadow at CIA HQ, Langley.** A literal shadow cast by the Kryptos courtyard sculpture's own copper panel needs true solar azimuth/elevation at a given lat/lon/date/time (standard solar-position algorithm, e.g. NOAA SPA) — tractable with the CIA HQ coordinates and `geodesy.py` infrastructure already in the repo.
- Both hypotheses reduce to: compute a candidate shadow angle, map it to a transposition order or clock-offset parameter, and run it through the existing `geometry_combined_sweep` / `three_layer_composite_geometric` infrastructure. No new attack pipeline needed — only a new parameter-derivation module (proposed: `kryptos.k4.solar_geometry`).

### Research: World Clock city-list as a keyword source

The Weltzeituhr's rotating drum lists ~148 world cities. Untested as a keyed-alphabet seed source (city names, city count mod 26, alphabetical-position-of-Berlin-in-the-list, etc.) — same category of research as P11/P19's keyword expansion, just a source not yet mined.

### Carried over — not yet scheduled

- **Cross-vector consensus scoring** — idea from 2026-08-28, still open: a fragment that surfaces at the same position across *multiple, independently-derived* attack vectors (P1–P20 plus the Phase 6 geometric family) is a far stronger signal than a repeated fragment within one vector's own sweep. Worth building once there's enough corpus volume across vectors to compare.
- **Scheduled overnight full sweeps** — idea from 2026-08-28, still open: several full sweeps (P1's 720-state sweep, Phase 6's geometric variants) are sub-minute-to-low-minutes runtime but still require someone to remember to click "run." A scheduled/batch runner would close this out.

---

## Phase 5 — Post-Solution (Standing)

- [ ] Solution documentation — full attack path, key insights, solution narrative
- [ ] README update — reflect solution and cryptanalytic implications
- [ ] Archive all null-result artifacts with parameter provenance

---

## Key References

| Document | Purpose |
|----------|---------|
| `docs/analysis/K4_ATTACK_LANDSCAPE.md` | Full 3D fingerprint: past/present/frontier with evidence basis |
| `docs/analysis/K4_ACTIVE_RESEARCH.md` | Living null-result log and confirmed facts |
| `docs/analysis/K4_KEYSTREAM_ANALYSIS.md` | Derived shift sequences at all 4 crib windows |
| `docs/TASKS.md` | Implementation backlog with specific next steps |
| `frontend/` + Docker | `docker compose -f config/docker-compose.yml up -d` → http://localhost:8000 |
