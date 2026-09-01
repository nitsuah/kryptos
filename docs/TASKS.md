# Tasks

Breadcrumb: [Docs](INDEX.md) > Tasks

Last Updated: 2026-09-01

---

## Active

### Physical/Geometric Pivot — Phase 7 (NEW — 2026-09-01)

> Phase 6 (24-column geometric permutation front-end, reflections, geodesy-derived bearings, Nov 9 1989 clock state, P2/P5/P6 loop closures) is complete — see `docs/ROADMAP.md` Phase 6 and `docs/analysis/K4_ACTIVE_RESEARCH.md`. These are the next items, in priority order.

- [ ] **Wire `reflection.SHAPE_CHANGING` into a geometric sweep** — `geometry_combined_sweep.DEFAULT_REFLECTIONS` only exercises the 4 shape-preserving transforms (`identity`/`flip_h`/`flip_v`/`rotate_180`); the 4 shape-changing ones (`transpose`/`anti_transpose`/`flip_h_then_transpose`/`flip_v_then_transpose`, in `kryptos.k4.reflection.SHAPE_CHANGING`) turn the 4×24 grid into 24×4 and were never wired into a runnable sweep. Needs a sweep variant (or `composed_flat_indices` extension) that re-derives flat indices for the transposed shape. Highest-value pending item — the single largest untested slice of the pivot's own search space.
- [ ] **Solar-position primitive for the "shadow of the word" hypothesis** — Sanborn: "the secret is the shadow of the word." Two computationally-tractable readings (neither requires physical/photographic site access, correcting the prior "out of scope" assessment in `K4_ATTACK_LANDSCAPE.md`): (A) the Alexanderplatz World Clock's rotating topper turns at a fixed, documented 1 rev/min rate decoupled from real solar position — model as a deterministic function of elapsed time from a reference timestamp; (B) a literal sunlight shadow cast by the Kryptos courtyard sculpture at CIA HQ Langley — needs true solar azimuth/elevation via a standard solar-position algorithm (e.g. NOAA SPA) applied to the already-known CIA HQ coordinates. Build as `kryptos.k4.solar_geometry`; feed derived angles into the existing `geometry_combined_sweep`/`three_layer_composite_geometric` sweeps as a transposition-order or clock-offset parameter — no new attack pipeline needed.
- [ ] **World Clock city-list as keyword source** — the Weltzeituhr's rotating drum lists ~148 world cities, untested as a keyed-alphabet seed (city names, city count mod 26, list position of Berlin, etc.) — same category as P11/P19's keyword-expansion research, a source not yet mined.
- [ ] **Cross-vector consensus scoring** (carried over from 2026-08-28) — a candidate fragment appearing at the same position across *multiple, independently-derived* attack vectors (P1–P20 plus the Phase 6/7 geometric family) is a stronger signal than a repeated fragment within one vector's own sweep. Needs enough corpus volume across vectors before it's worth building.
- [ ] **Scheduled overnight full-sweep runner** (carried over from 2026-08-28) — several full sweeps are sub-minute-to-low-minutes runtime but still require someone to remember to click "run" in the dashboard; a scheduled/batch job would close this out.

---

## Done

### Physical/Geometric Pivot — Phase 6 (2026-08-29 to 2026-09-01, all null)

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

### Alphabet keyword expansion, coordinate deep-dive, candidate-text analysis — Phase 2/3 (P11–P20, 2026-08-14)

> All implemented and tested; several (P13, P14, P19) subsequently superseded or extended by Phase 6's precise geodesy and geography-derived route directions. See `docs/analysis/K4_ATTACK_LANDSCAPE.md` for full parameter detail per vector.

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

### Core P1–P7 Frontier Attacks — Phase 0 (complete)

- [x] **P1 — 3-Layer Composite** (`three_layer_composite.py`) — keyed-alphabet → clock-Vigenère → columnar transposition. Both CIA-timestamp priority states **and** the full 24-state hourly sweep executed. Null. Artifact: `K4_3LAYER_NULL.json`.
- [x] **P2 — Shadow/Null Masking** (`masking_v2.py`) — see Phase 6 above for the actual execution (this entry covers implementation only).
- [x] **P3 — K2 Coordinate Clock Times** (`k2_clock_states.py`) — 5 K2-derived HH:MM timestamps. Null.
- [x] **P4 — ±6h Timezone Offset** (in `k2_clock_states.py`). Null.
- [x] **P5 — 2-Crib Soft Filter** — see Phase 6 above for the actual execution (this entry covers implementation only).
- [x] **P6 — K3 Running Key** (`running_key.py`) — see Phase 6 above for the actual execution (this entry covers implementation only).
- [x] **P7 — Gronsfeld Cipher** (`gronsfeld.py`) — K2 coordinate digit keys. Null.

### K4 Attack Dashboard & UI

- [x] K4 Attack Dashboard with live Berlin Clock hero section
- [x] K4CipherVisualizer with EAST/NORTHEAST/BERLIN/CLOCK crib highlights
- [x] P1–P7 frontier queue with Run Attack buttons and live polling
- [x] Stats strip, progress bars, Eureka banner

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
