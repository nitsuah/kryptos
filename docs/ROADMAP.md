# 🗺️ Kryptos Roadmap

Breadcrumb: [Docs](INDEX.md) > Roadmap

Last Updated: 2026-08-12
Next Review: 2026-09-01
---

## Completed K4 Attack Vectors ✅ (All 14 — as of 2026-08-12)

> All single-layer and two-layer composite vectors from Sanborn's publicly known techniques have been exhausted. Each run produced a documented null result. The attack frontier has shifted to 3-layer composites, pre-cipher masking, and secondary-key derivation approaches.

- [x] Single-layer repeating Vigenère (all key lengths 1–20, all Kryptos-era keys)
- [x] Direct Berlin Clock Vigenère (all 720 clock states as Vigenère keys)
- [x] Keyed alphabet realignment (KRYPTOS, PALIMPSEST, ABSCISSA)
- [x] Full composite sweep: 3 alphabets × 3 grid geometries × 720 clock states × ENE+columnar routes
- [x] Inverse transposition sweep (10×10, 7×14, 8×13 grids, ENE diagonal + columnar routes)
- [x] Hill 2×2 and 3×3 with BERLIN/CLOCK crib constraints
- [x] Clock → Hill 2×2 invertibility pre-filter (~100 invertible states)
- [x] 4-char clock key → Vigenère with NORTHEAST anchor (4 encoding schemes × 720 states)
- [x] Non-standard Berlin Clock sub-row encodings (5-hr only, 1-hr only, minute rows, row sums)
- [x] Berlin Clock lamp counts as transposition column widths
- [x] Beaufort cipher sweep (10 key candidates × 2 alphabets)
- [x] Quagmire I–IV (6,240 combinations including Q3 Berlin Clock minute-state indicator keys)
- [x] Physical-grid tableau walk (108 geometric routes × 2 indicator bases via Quagmire III)
- [x] ADFGVX and Nihilist (fractionating ciphers)

### Definition of Done

- [x] Each attack run with null-result artifact or `K4_BREAKTHROUGH_SNAPSHOT.md` if a match is found
- [x] Results recorded in `docs/analysis/K4_ACTIVE_RESEARCH.md`

---

## Frontier K4 Attack Vectors 🔭 (Q3 2026 → Open)

> All clean 2-layer composites are exhausted. The following vectors are structurally distinct and have not been run. Each is achievable with the existing pipeline. Priority order reflects estimated information gain per compute invested.

- [ ] **3-Layer Composite: Keyed-Alphabet → Clock-Vigenère → Columnar Transposition** — The only 3-layer pipeline with all three mechanisms already implemented. ~51,840 combinations with full 4-crib gating. Estimated sub-minute on current hardware.
- [ ] **Shadow/Null Masking as Layer 0** — Remove characters at clock-shadow positions (angle-based, lamp-off positions, or stride-N) before any cipher operation. Recalculate crib positions in the residue. ~12 masking variants × full composite sweep.
- [ ] **K2 Coordinate Digits as Clock State Selectors** — Use K2 coordinate values (38:57, 06:05, 17:08, 08:44) as specific HH:MM timestamps to isolate candidate clock states for Hill or Vigenère attacks.
- [ ] **6-Hour Berlin→CIA Timezone Offset** — Apply a +6 or −6 shift to the clock state index, Vigenère key start position, or columnar transposition key ordering. Motivated by Berlin UTC+1 vs. CIA Langley UTC−5.
- [ ] **BERLIN+CLOCK Partial Match Isolation** — Relax the 4-crib gate to 2-crib (BERLIN+CLOCK only at positions 63–73) to surface partial-solution candidates that strict gating suppressed.
- [ ] **Running Key from K3 Plaintext** — Use first 97 chars of K3 decrypted plaintext as a Vigenère running key for K4. Tests the theory that Kryptos sections are chained.
- [ ] **Gronsfeld Cipher with K2 Coordinate Key** — Vigenère variant keyed by decimal digits: `385765` (from K2 `38 57 6 5 N`) or `770844` (from `77 8 44 W`). Not yet implemented.

> **Landscape reference:** `docs/analysis/K4_ATTACK_LANDSCAPE.md` — full 3D fingerprint with priority, evidence basis, and implementation plan for each frontier vector.

---

## Q1 2027: Dashboard, API & Final Push 🖥️

### Phase 1 — K4 Attack completion
- [x] All five untested attack vectors above completed and documented

### Phase 2 — Dashboard & UI

> Stack shipped as specified: FastAPI + React SPA in a single multistage Docker container, served from `frontend/dist` by `create_app()`, backed by Neon. See `docs/analysis/K4-FRONTEND.md`.

- [x] **Ops Center** — live campaign monitoring, agent status row, top fused candidates table, run history with drill-down, ad-hoc decrypt panel (#100). Live log tail via SSE shipped (#118 backe[...]
- [x] **K1–K3 Animated Decoder** — step-by-step visual explainer of how each solved section was encrypted and cracked (#102)
- [x] **Database admin page** — Neon connection status + per-table row counts (#104)
- [x] **Vault** — seal/unseal/peek encrypt/decrypt interface (keyed-alphabet Vigenère) with TTL and read-count enforcement (#115 backend, #116 frontend)
- [ ] **K4 Attack Dashboard** — dedicated real-time pipeline-progress + evidence-artifact viewer (most is covered by Ops Center, Database, and RAG search; a standalone attack-vector fingerprint [...]

### Phase 3 — API
- [x] **REST dashboard API** — `/api/status`, `/api/runs`, `/api/runs/{id}/candidates`, `/api/candidates`, `POST /api/decrypt` (#99); turbovec RAG search at `/api/rag/*` (#113); `GET /api/stream[...]
- [x] **`strategy_kb` write path** — `OpsStrategicDirector.record_strategy()` persists BOOST/PIVOT/STOP/START_NEW decisions to Neon `strategy_kb` table with JSONL fallback; `_record_strategy_fro[...]
- [x] **Candidate & run storage** — `candidates` and `campaign_runs` tables in Neon, persisted best-effort from campaigns (#98)

### Phase 4 — Validation & hardening
- [x] **K3 double-transposition Monte Carlo** — `kryptos.k3.double_rotation_solver` generalizes K3's two-stage 90cw rotation to all divisor-width/rotation-type pairs; brute-force solver exactly [...]
- [x] **Stress tests for K1/K2** — `kryptos.k4.vigenere_stress_tests.run_k1_k2_stress_suite` exercises noise injection, wrong key lengths, and partial-ciphertext truncation against `recover_key_[...]

### Phase 5 — Post-solution
- [ ] **Solution documentation** — once K4 is solved: full attack path, key insights, solution narrative
- [ ] **README and docs update** — reflect the solution and its cryptanalytic implications

---

## Agent Module Review (Post-K4, Pre-GUI)

- [x] Review, refactor, or remove optional/partial agent modules in `src/kryptos/agents/`:
    - `spy_nlp.py`
    - `spy_web_intel.py`
    - `linguist.py`
    - `ops_director.py`
- [x] Decide if these modules are needed, should be modernized, or can be dropped entirely.
- [x] Document outcome and update architecture docs as needed.

> **Outcome**: all four modules kept, none removed. The review found and fixed 4
> bugs in `AutonomousCoordinator`'s integration with `spy_nlp`/`spy_web_intel`/
> `ops_director` (API drift masked by tests mocking buggy call-site signatures),
> including a crash-on-startup (`SpyNLP()` requiring `en_core_web_sm`, not present
> in the runtime image) and a crash-on-cycle-1 (`analyze_situation()` returning
> `None` was unhandled). `linguist.py` is confirmed standalone/well-tested and was
> subsequently wired into `pipeline/validator.py` stage 3 as an opt-in enhanced-
> scoring pass (`PlaintextValidator(enable_linguist=True)`, default `False`,
> degrades gracefully without `torch`/`transformers`). A 5th bug —
> `run_autonomous_loop(max_hours=0.0, ...)` looping forever due to a falsy-zero
> check, previously masked by the crash-on-cycle-1 bug — was uncovered by a 6-hour
> CI hang after the cycle-1 crash was fixed, and also fixed. See
> `docs/analysis/AGENT_MODULE_REVIEW.md`.

---

## Working Notes

- Active task backlog: `TASKS.md`
- K4 attack context and null results: `docs/analysis/K4_ACTIVE_RESEARCH.md`
- Confirmed keystream analysis: `docs/analysis/K4_KEYSTREAM_ANALYSIS.md`
- Frontend spec: `docs/analysis/K4-FRONTEND.md`
- Monthly governance log: `docs/governance.md`
