# Kryptos Roadmap

Breadcrumb: [Docs](INDEX.md) > Roadmap

Last Updated: 2026-08-28
Next Review: 2026-09-15

---

## Current Status

**K4 attack phase:** Phase 2 frontier open. All single-layer, 2-layer, and initial 3-layer composite sweeps exhausted with null results. The attack surface has widened into three new structural directions: alternative alphabet keywords, aggressive coordinate exploitation, and candidate-text pattern analysis.

**Architecture:** Confirmed substitution → transposition → K4. The substitution key is not derivable from any standard Berlin Clock row value (shifts at EAST/NORTHEAST reach 17, 20, 25 — exceeding the maximum clock row output of 11). The transposition is not a standard rectangular grid in any simple reading order. At minimum one un-parameterized step remains.

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

## Ideas — not yet scheduled

- **Cross-vector consensus scoring** — new idea (2026-08-28): P16 mines candidate fragments *within* one attack vector's null-result corpus. Twenty structurally independent vectors (P1–P20) each produce scored candidate texts under different key/cipher assumptions; a fragment that surfaces at the same position across *multiple, independently-derived* vectors is a far stronger signal than a repeated fragment within one vector's own sweep, since it would take coincidence across unrelated cryptographic models rather than just within one. Worth building once P1's full sweep and the P11–P20 corpus both have enough volume to compare.
- **Scheduled overnight full sweeps** — new idea (2026-08-28): P1's full 720-state sweep is noted as sub-minute runtime but still "pending" as a manual action; a scheduled job (or a "run everything overnight" dashboard button) that queues every not-yet-run full sweep would close out the "highest-value pending run" backlog without requiring someone to remember to click it.

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
