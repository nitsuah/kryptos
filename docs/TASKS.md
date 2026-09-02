# Tasks

Breadcrumb: [Docs](INDEX.md) > Tasks

Last Updated: 2026-09-01

---

## Active

Nothing *code-derivable* from current sourcing remains queued — Phases 1-7 have all been implemented, executed against real K4, and returned null. What's next is sourcing three specific primary-source gaps (research done 2026-09-01, concrete leads below — see `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "Primary Sources Needed" section for full detail and sourcing rationale on each). None of these are things this repo can generate on its own.

### Primary-source sourcing (NEW — 2026-09-01)

- [ ] **Source the remaining ~7 segments of the World Clock's 146-city list** (2026-09-02 update: count resolved at 146+1 IDL=147 via convergent German+English Wikipedia; 104 of 146 names now confirmed by directly reading 5 Wikimedia Commons photographs of the actual plates — see `kryptos.k4.world_clock_cities.CONFIRMED_CITIES` and `K4_ACTIVE_RESEARCH.md`'s Phase 7 update). Still missing: Japan/Korea/Australia/NZ, the Pacific/Hawaii zones, and one Middle East/North Africa gap. Try, in order: (1) more Wikimedia Commons photos from `Category:Urania-Weltzeituhr` — read directly (this is what closed the other 17 segments, not OCR/secondary-source guessing); (2) the 360cities.net panorama, rotated to the missing angles; (3) patent DE2515102A1 was checked and is unrelated (a different, more general world-clock-globe invention, not Alexanderplatz-specific) — dead end, don't re-check it. Extend `CONFIRMED_CITIES` if the remaining segments are found — do not fabricate entries.
- [ ] **Source a sub-minute-precision Nov 9 1989 timestamp** — every sourced moment (Schabowski's statement, AP flash, ARD broadcast) is whole-minute precision, which made `solar_geometry.topper_shadow_offsets()` fall back to an exhaustive sweep rather than a single derived value. Top lead: `chronik-der-mauer.de`'s dedicated Hertle article "9. November 1989, 18.00 Uhr: Schabowskis Auftritt" (blocked by bot-detection on automated fetch this session — needs a manual visit). Also: Hertle's books *Chronik des Mauerfalls* / *Sofort, unverzüglich*; the original AP wire filing's internal timestamp; ARD/rbb (Deutsches Rundfunkarchiv) broadcast archives.
- [ ] **Source the Kryptos compass rose's actual measured bearing** — per `elonka.com/kryptos/wishlist.html`, this is a still-open community question, not just gapped in this repo. `elonka.com/kryptos/KryptosAerial.html` already has one uncertain secondary estimate (~220°, explicitly flagged "not exact"). Next steps: a FOIA request or CIA public-affairs inquiry for a measured bearing or high-res overhead photo; contacting Elonka Dunin directly (active community liaison to Sanborn/CIA contacts); a follow-up session with image-reading capability inspecting satellite/overhead imagery of the CIA New Headquarters Building courtyard directly.

---

## Done

### Physical/Geometric Pivot — Phase 7 (2026-09-01, all null)

> Full detail: `docs/ROADMAP.md` Phase 7, `docs/analysis/K4_ACTIVE_RESEARCH.md`'s Phase 7 section.

- [x] **Wired `reflection.SHAPE_CHANGING` into a geometric sweep** — extended `composed_flat_indices` to correctly handle the 4×24→24×4 transpose family (verified bijection + round-trip; shape-preserving reflections unchanged). 3 runs: default scope (155,520), geography-derived offsets (414,720), via `run_three_layer_composite_geometric` (69,120). All null.
- [x] **Solar-position primitive for the "shadow of the word" hypothesis** — `kryptos.k4.solar_geometry`. Hypothesis A (World Clock topper, confirmed 1 rev/min via Wikipedia) honestly reduced to a full 0-23 rotation-offset sweep after finding every sourced timestamp pair vacuously co-phased (1,244,160 candidates, null). Hypothesis B (real solar azimuth at CIA HQ via a verified NOAA/Meeus algorithm) wired into `clock_rotation.geography_derived_bearings()` (108,864 candidates, null).
- [x] **World Clock city-list as keyword source** — `kryptos.k4.world_clock_cities`. 9 individually-sourced city names as keyed alphabets (9,720 candidates, null) plus 2 sourced structural counts (148 cities, 24 segments) as rotation offsets (103,680 candidates, null). Complete list unavailable from any source checked — not fabricated.
- [x] **Cross-vector consensus scoring** — `kryptos.k4.cross_vector_consensus`. Groups candidates by source attack vector (unlike P16's merged-pool count); flags fragments in ≥3 distinct vectors. Scanned 30 artifacts, 11 with candidates: zero consensus anchors.
- [x] **Scheduled overnight full-sweep runner** — `kryptos.k4.overnight_runner.run_all_pending_sweeps` + `scripts/run_k4_overnight_sweeps.py`. Runs every registered full-scope sweep in sequence, halts immediately on `EurekaSignal`.

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

> All implemented and tested; several (P13, P14, P19) subsequently superseded or extended by Phase 6's precise geodesy and geography-derived route directions. See `docs/analysis/K4_ACTIVE_RESEARCH.md` for full current-state detail per vector.

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
