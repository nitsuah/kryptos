# Tasks

Breadcrumb: [Docs](INDEX.md) > Tasks

Last Updated: 2026-09-03

---

## Active

One of the three primary-source gaps opened 2026-09-01 remains open; the timestamp one closed 2026-09-02, and the World Clock city list closed 2026-09-02 too (see Done below). See `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "Primary Sources Needed" and "External Developments (2025–2026)" sections for full detail and sourcing rationale. Action items below are split by who actually has to do them — Claude's automatable queue vs. the send that genuinely needs a human.

### Primary-source sourcing (opened 2026-09-01)

- [ ] **Source the Kryptos compass rose's actual measured bearing** — per `elonka.com/kryptos/wishlist.html`, this is a still-open community question, not just gapped in this repo. `elonka.com/kryptos/KryptosAerial.html` already has one uncertain secondary estimate (~220°, explicitly flagged "not exact"). 2026-09-02 update: satellite/overhead imagery of the CIA New Headquarters Building courtyard was inspected directly (Google Maps, unblurred) — confirmed insufficient resolution for ground-level engraving detail (building/lot-scale only), ruling out that specific lead; the underlying reason is resolution physics, not a one-off check — resolving a thin engraved line on a ~1m stone to a useful few degrees needs sub-centimeter, near-nadir imagery of that one feature, and no public satellite/aerial/lidar source gets close (best commercial imagery is ~15-30cm/px). A physical on-site GPS/compass measurement isn't a viable alternative either: the courtyard is inside the CIA's secured grounds, not publicly accessible, and a consumer phone compass is only accurate to roughly ±5-10° regardless. External-plaintext note: Sanborn's own recovered opening line reads "THE COMPASS ROSE IS HERE," independent confirmation this lead is worth pursuing, not a stretch. **[You — the only send]** A FOIA request to CIA (foia.cia.gov) or contacting Elonka Dunin directly (active community liaison to Sanborn/CIA contacts) — both drafted in full and ready to send, see [Three Open Leads](https://claude.ai/code/artifact/7e689fa1-c66d-49b1-abdb-3fc17a866c84) §4. The FOIA draft specifically asks for the original 1990 landscape/installation architectural drawing (which may already have the bearing annotated), not just a photo — a drawing is far more likely to exist and to actually answer the question than commissioning new imagery.
- [ ] **Ask CIA Public Affairs whether an authorized research visit exists** — 2026-09-03, checked directly against CIA's own FAQ (`cia.gov/faqs`): public tours are refused ("Security considerations prevent such tours"), but "CIA provides an extremely limited number of visits annually for approved academic and civic groups." Not a gate loophole, not "can I sneak in" — a narrow, honest question to the Office of Public Affairs (CIA's own named public-facing contact point, `cia.gov/about/organization/public-affairs`) about whether an independent researcher studying the publicly documented Kryptos puzzle can be included in an approved visit, or otherwise get authorized escorted access for non-sensitive observation/measurement. **[You — the only send.]** Draft:
  > Subject: Research inquiry — authorized visit access for Kryptos sculpture research
  >
  > Hello,
  >
  > I'm an independent researcher studying the publicly documented Kryptos sculpture at CIA Headquarters — specifically the still-unsolved K4 passage, which is public information CIA itself has written about. I understand Headquarters doesn't offer public tours, but I've read that a limited number of visits happen each year for approved academic and civic groups.
  >
  > Is there an existing mechanism for an independent researcher to be included in one of those visits, or to otherwise request brief, escorted, non-sensitive access to observe and measure the Kryptos sculpture's compass rose for research purposes? Happy to provide more detail on the specific research question if useful.
  >
  > Thank you for your time.
  >
  > [Your name and contact information]

### External developments follow-up (opened 2026-09-02, resolved 2026-09-02)

- [x] ~~Explain the single-character discrepancy in solvekryptos.com's claimed K4 plaintext~~ — **resolved same day, as a real bug, not a discrepancy.** A CodeRabbit review comment on PR #203 questioned whether the "discrepancy" was actually an indexing artifact; investigating it found this repo's own `keystream_validator.K4_CRIBS` had stored `EAST`/`NORTHEAST` one position too high (22/26 instead of the real 21/25) since that constant's introduction — confirmed three independent ways (direct ciphertext search, this project's own `annotate_cribs()`, and an existing-but-previously-unenforced test). Once fixed, `solvekryptos.com`'s claimed plaintext passes all 4 confirmed anchors exactly, zero offset. The same bug was duplicated in `key_csp.py` and `clock_hill_attack.py`, both fixed alongside it; see `K4_ACTIVE_RESEARCH.md`'s "External Developments" section for the full account.

---

## Done

### External review follow-up (2026-09-03, all null)

> Full detail: `docs/analysis/K4_ACTIVE_RESEARCH.md`'s "External developments, follow-up (2026-09-03)" section.

- [x] **Fixed two IC/methodology overclaims** in the Ruled Out table — "IC rules out monoalphabetic substitution" and "non-uniform local IC proves substitution-then-transposition" were both overstated. The monoalphabetic row now rests on a sharper, code-verified argument instead: 8 of 9 repeated plaintext letters in the 24 confirmed crib characters map to different ciphertext letters at each occurrence, which no fixed 1:1 substitution can produce.
- [x] **Built `kryptos.k4.plaintext_evidence`** — a confidence-tiered plaintext data structure distinguishing the 24 Sanborn-CONFIRMED crib characters from solvekryptos.com's 73-character RECONSTRUCTED guess (explicitly not Sanborn's unpublished archival text). `candidate_repeating_periods()` tested the reconstructed text's full implied keystream for a repeating-key period 2-20: none found. Exploratory diagnostic only, never used to gate a candidate.
- [x] **Checked the Kamchatka Cold War hunch geodesically** — the CIA→Berlin bearing does not continue toward Kamchatka (curves southeast past Berlin; a fresh bearing restarted at Berlin points closer to Vladivostok than Kamchatka or Magadan). Reframed around the real anchor instead: KAMTSCHATKA is a specific node on K4's own named "BERLIN CLOCK." Added `world_clock_cities.WORLD_CLOCK_SEGMENT_HOUR` (sourced hour-index per segment, read directly off the photos) and `run_world_clock_sector_sweep` — 207,360 candidates, null.
- [x] **Built the "known-plaintext" attack surface an external review proposed** — `kryptos.k4.known_plaintext_inversion` inverts every already-enumerated transposition (same `geometry_combined_sweep.composed_flat_indices` primitive) against real K4, derives the substitution shift the reconstructed plaintext would require, and checks for a repeating-key period. 11,520 transposition hypotheses tested (full order × reflection × 24 rotations × remainder-mode space): zero showed a consistent period 2–20 — null. Never gates a candidate; raises no `EurekaSignal`, since it rests on the unverified reconstructed plaintext.
- [x] **Built `kryptos.k4.physical_geometry`** — a typed schema for the sculpture's physical facts, every field unmeasured (`None`) until a cited source supplies it. Only the tableau's back-only reading direction is actually confirmed (CIA's own page); compass bearing and lodestone deflection remain open per Phase 8.
- [x] **Built `kryptos.k4.constraint_chain.evaluate_candidate`** — reports how many of 5 independent evidence layers (confirmed cribs, Sanborn-hint keywords, reconstruction alignment, language score vs. raw-ciphertext baseline, physical geometry) a candidate satisfies at once, without creating a new promotion gate. `validation.validate_candidate`'s strict gate is unchanged and remains the only thing that can raise a candidate's status.
- [x] **Verified two claims from an external review before acting on them** — CIA's own Kryptos page confirms the Vigenère tableau was "intentionally flipped so it can only be read from the back" (checked directly, not assumed); CIA's own FAQ confirms limited academic/civic-group visits exist. Corrected one claim from that review before it entered this repo's docs — the November 2025 auction buyer is Paradigm, publicly self-identified, not "anonymous."

### Physical/Geometric Pivot — Phase 7 (2026-09-01, all null)

> Full detail: `docs/ROADMAP.md` Phase 7, `docs/analysis/K4_ACTIVE_RESEARCH.md`'s Phase 7 section.

- [x] **Wired `reflection.SHAPE_CHANGING` into a geometric sweep** — extended `composed_flat_indices` to correctly handle the 4×24→24×4 transpose family (verified bijection + round-trip; shape-preserving reflections unchanged). 3 runs: default scope (155,520), geography-derived offsets (414,720), via `run_three_layer_composite_geometric` (69,120). All null.
- [x] **Solar-position primitive for the "shadow of the word" hypothesis** — `kryptos.k4.solar_geometry`. Hypothesis A (World Clock topper, confirmed 1 rev/min via Wikipedia) honestly reduced to a full 0-23 rotation-offset sweep after finding every *whole-minute* sourced timestamp pair vacuously co-phased (1,244,160 candidates, null). Hypothesis B (real solar azimuth at CIA HQ via a verified NOAA/Meeus algorithm) wired into `clock_rotation.geography_derived_bearings()` (108,864 candidates, null).
- [x] **Sub-minute-precision Nov 9 1989 timestamp, sourced** (2026-09-02) — `chronik-der-mauer.de`'s word-for-word transcript of Hertle's own recording (citing his book, 2nd ed. 2015, p.194-195): the press-conference excerpt opens 18:52:40 CET, ends 19:00:54 CET — both with genuine non-zero seconds, resolving hypothesis A's vacuity for these two moments. `solar_geometry.precise_topper_shadow_offsets()` derives real (non-vacuous) rotation offsets {16, 22}; both timestamps also expand hypothesis B's solar-bearing set. Reran both sweeps: 103,680 candidates (precise topper) + 139,968 (expanded solar bearing, was 108,864). All null.
- [x] **World Clock city-list as keyword source** — `kryptos.k4.world_clock_cities`. Expanded across three follow-up passes (130 individually-sourced city names as of 2026-09-02, up from the original 9) as keyed alphabets (9,720 → 112,320 → 128,520 → 140,400 candidates, null) plus 3 sourced structural counts (146/147/24) as rotation offsets (155,520 candidates, null). Complete 146-name list still unavailable — not fabricated. **2026-09-02: the "~4 missing segments" primary-source gap closed** — found two more Wikimedia Commons photos taken at different cylinder rotations, adding PJOENGJANG/TOKYO/SEOUL (Japan/Korea), DATUMSGRENZE/WELLINGTON/APIA/MARQUESAS (NZ/Pacific), MAGADAN/SACHALIN/KAMTSCHATKA/KAPDESCHNEW/HONOLULU (Russian Far East/Hawaii) — essentially the full 24-segment ring, only 16 names short of the complete 146.
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
