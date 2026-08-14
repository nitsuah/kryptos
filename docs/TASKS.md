# Tasks

Breadcrumb: [Docs](INDEX.md) > Tasks

Last Updated: 2026-08-14

---

## Active

### Frontier K4 Attacks — Phase 2 (NEW — 2026-08-14)

> P1–P7 are implemented and running. Phase 2 opens new structural directions: alternative alphabet keywords, aggressive coordinate exploitation, and candidate-text analysis.

#### Alphabet keyword expansion

- [ ] **P11 — Alternative keyed-alphabet keywords** — Test SANBORN, LANGLEY, WENDELL, NORTHEAST, BERLIN, CLOCK, SHADOW, BETWEEN, COMPASS, DIGETAL as keyed-alphabet seeds (instead of KRYPTOS/PALIMPSEST/ABSCISSA) in the full 3-layer composite sweep. Each is a 5-letter keyword substitute; requires no new infrastructure, just adding entries to `KNOWN_KEYED_ALPHABETS`.
- [ ] **P12 — Misspelling-derived substitution** — K1 has IQLUSION (I≡L, Q≡L), K3 has DESPARATLY (A→E). Model these intentional misspellings as a partial keyed-alphabet definition: the swapped pairs (I=Q, A=E in some reduced alphabet) may constrain K4's substitution alphabet directly. Implement as a `MisspellingAlphabetGenerator` and test in P1 chain.

#### Coordinate deep-dive

- [ ] **P13 — Magnetic declination clock offset** — At 38°57'N 77°8'W on Nov 3 1990, magnetic declination was ~−9.9° (NOAA IGRF model). Apply this as a fractional clock-hand rotation offset: the Berlin Clock reading at the nominal CIA timestamp shifts by ~10 min. Implement `magnetic_declination_offset(lat, lon, date)` using the IGRF coefficients and test the resulting modified clock states.
- [ ] **P14 — CIA→Berlin great-circle bearing as cipher parameter** — Bearing from CIA HQ (38°57'N, 77°8'W) to Berlin (52°31'N, 13°24'E) is ~44.4°. Test 44 as: Caesar shift (44 mod 26 = 18 = S), clock minute offset (44 min from CIA timestamp), Vigenère key cycle offset by 44 positions. Three lightweight tests against the 4-crib gate.
- [ ] **P15 — K2 coordinate digits as straddling checkerboard** — Digits 3,8,5,7,6,5 (N coordinate) and 7,7,8,4,4 (W coordinate) as row-header indices in a straddling checkerboard. Build the checkerboard, encode K4 through it, check if output length and character distribution match known ciphertext properties. Implement `kryptos.k4.straddling_checkerboard`.

#### Candidate text analysis

- [ ] **P16 — Candidate corpus fragment mining** — All P1–P7 sweeps wrote null artifacts. Load and merge every `*_NULL.json` artifact, extract `best_candidates[].candidate_text`, and run a sliding-window n-gram counter (4–6 chars) over positions 0–21 (before the EAST crib). Any English fragment appearing in >3% of candidates at a consistent position across multiple attack types is a partial-plaintext anchor. Implement `kryptos.k4.corpus_miner.mine_candidate_corpus(artifact_glob)`.
- [ ] **P17 — QQ/SS bigram hard constraints** — K4 positions 12–13 are QQ and 31–32 are SS. Under a keyed-alphabet + Vigenère model, QQ at consecutive positions constrains the key: if the keyed alphabet maps two distinct letters to Q, both positions must use those specific key letters. Implement `kryptos.k4.bigram_constraint.build_bigram_constraints(ciphertext, doubled_positions)` and wire as a pre-filter in the transposition sweep, pruning permutations that place the doubled ciphertext chars at positions inconsistent with the key.
- [ ] **P18 — Repeating-key CSP over all 4 crib windows** — The 4 confirmed cribs give 22 known (position, shift) pairs. For a repeating Vigenère key of length L (7–15), each position ≡ crib_position mod L must produce that shift. This is a constraint satisfaction problem with ~(22 * L) constraints. Implement `kryptos.k4.key_csp.solve_key_csp(crib_shifts, key_lengths)` using AC-3 or backtracking with arc consistency. A solution to the CSP gives the key directly.

#### CIA/historical keyword research

- [ ] **P19 — Sanborn advisory names as alphabet keywords** — William Webster (DCI 1987–1991), Richard Kerr (DDCI), William Studeman (NSA Director), Ed Scheidt (CIA KGB officer who worked with Sanborn directly). Scheidt is the most important: he designed the encryption with Sanborn and has said "there's still something that needs to be worked out." His name, SCHEIDT, is an untested keyed-alphabet keyword.
- [ ] **P20 — Cyrillic Projector crossover** — Sanborn's "Cyrillic Projector" sculpture (UNC Chapel Hill, 1997) encodes a KGB document. The KGB keywords from that document — translated to Roman alphabet — may cross-reference K4's cipher key. Research and extract the Cyrillic Projector plaintext; test any Roman-alphabet words as K4 keyed-alphabet seeds.

---

### Phase 0 (complete): Core P1–P7 Frontier Attacks

> All implemented, tested, and running. See `docs/analysis/K4_ATTACK_LANDSCAPE.md` for full parameter details.

- [x] **P1 — 3-Layer Composite** (`three_layer_composite.py`) — keyed-alphabet → clock-Vigenère → columnar transposition. CIA timestamps tested. 22 tests passing.
- [x] **P2 — Shadow/Null Masking** (`masking_v2.py`) — 8 variants (stride-2/3/4, block-8, clock-shadow×2, arc-fraction×2). 14 tests passing.
- [x] **P3 — K2 Coordinate Clock Times** (`k2_clock_states.py`) — 5 K2-derived HH:MM timestamps as Berlin Clock states. 12 tests passing.
- [x] **P4 — ±6h Timezone Offset** (in `k2_clock_states.py`) — doubles any clock sweep. 7 tests passing.
- [x] **P5 — 2-Crib Soft Filter** (routes, threshold=2) — surfaces near-misses with BERLIN+CLOCK only.
- [x] **P6 — K3 Running Key** (`running_key.py`) — K3 plaintext first 97 chars × 4 variants. 10 tests passing.
- [x] **P7 — Gronsfeld Cipher** (`gronsfeld.py`) — K2 coordinate digit keys. 10 tests passing.

**Full-sweep status:** P1 priority-only (CIA timestamps) has been run. The full 720-state × all-permutation sweep has not yet been executed — this is the highest-value pending run.

---

### Phase 1 — Dashboard & UI (complete)

- [x] K4 Attack Dashboard with live Berlin Clock hero section
- [x] K4CipherVisualizer with EAST/NORTHEAST/BERLIN/CLOCK crib highlights
- [x] P1–P7 frontier queue with Run Attack buttons and live polling
- [x] Stats strip, progress bars, Eureka banner

---

## Deferred (P8–P10)

Lower estimated information gain; re-evaluate after Phase 2 results.

- [ ] **Myszkowski transposition** — repeated-letter keywords (ABSCISSA, PALIMPSEST) with Myszkowski column-grouping logic.
- [ ] **Trifid cipher** — 27-letter cube fractionation; implement `kryptos.k4.trifid`.
- [ ] **Straddle Checkerboard** — variable-length encoding expansion (Cold War motif); implement and test.

---

## Done

### Dashboard, REST API, Web UI & Ops Strategy KB

- [x] FastAPI dashboard endpoints — `/api/status`, `/api/runs`, `/api/candidates`, `POST /api/decrypt`
- [x] Neon persistence — `campaign_runs` + `candidates` + `strategy_kb` tables
- [x] React + Vite + TypeScript SPA — terminal-aesthetic; Ops Center, K1–K3 decoder, Database, Vault, K4 Dashboard
- [x] K4 Attack API — `POST /api/k4/attacks/run`, `GET /api/k4/attacks/jobs/{id}`, `GET /api/k4/attacks/frontier`
- [x] Single-container Docker delivery — FastAPI serves built SPA from `frontend/dist`
- [x] turbovec RAG — semantic search over `artifacts/` at `/api/rag/*`
- [x] SSE live-log tail — `GET /api/stream/logs` via `LogTail` EventSource component

### Validation & hardening

- [x] K3 double-transposition Monte Carlo — `kryptos.k3.double_rotation_solver` recovers K3 plaintext #1 out of 11,664 candidates
- [x] K1/K2 Vigenère stress tests — noise injection, wrong key lengths, partial ciphertext
- [x] Agent module review — fixed 5 bugs in `AutonomousCoordinator` integration; `linguist.py` wired into `PlaintextValidator`

### Earlier K4 attacks (all null results)

- [x] Clock → Hill 2×2, 4-char clock key → Vigenère, non-standard sub-row encodings, lamp counts as column widths
- [x] Beaufort cipher sweep
- [x] Quagmire I–IV (6,240 combinations)
- [x] Physical-grid tableau walk (108 routes)
- [x] ADFGVX and Nihilist fractionating ciphers

### Misc

- [x] Fix off-by-one position labels: `NORTHEAST: [25]` → `[26]`, `BERLIN: [64]` → `[63]` in attack landscape doc
- [x] `.gitignore` entries for `K4_*_NULL.json`, `K4_BREAKTHROUGH_SNAPSHOT.md`, `*_EUREKA.md`
