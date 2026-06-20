# 🗺️ Kryptos Roadmap

Last Updated: 2026-06-20
Next Review: 2026-07-01
---

## Untested K4 Attack Vectors 🎯

> These are the highest-priority items before broader infrastructure work. All prior Q3/Q4 sweeps produced null results; these are the remaining untested angles. Each is small and targeted.

- [x] **Clock → Hill 2×2 invertibility pre-filter** — For each of 720 clock states form a 2×2 matrix from the first 4 lamp values, filter to the ~100 invertible mod 26, apply Hill 2×2 decryption to K4, validate EAST+NORTHEAST. Clock and Hill have only been tested independently so far.
- [x] **4-char clock key → Vigenère with NORTHEAST anchor** — Derive a 4-char Vigenère key from each clock state (not the full shift sequence), test with `positional_crib_bonus` gating on NORTHEAST at position 26. Several clock→4-char encoding schemes to try.
- [x] **Non-standard Berlin Clock sub-row encodings** — Hour rows only, minute rows only, row sums → letter. Current sweep only uses `full_berlin_clock_shifts` (all 4 rows concatenated).
- [x] **Berlin Clock lamp counts as transposition column widths** — Use lamp values (e.g. [4,3,11,4]) as column widths for a multi-round columnar transposition, not Vigenère shifts.
- [x] **Beaufort cipher sweep** — `kryptos.k4.beaufort` is implemented; no systematic K4 sweep has run. Quick pass with KRYPTOS, PALIMPSEST, BERLIN, CLOCK, ABSCISSA keys.

### Definition of Done

- [x] Each attack run with null-result artifact or `K4_BREAKTHROUGH_SNAPSHOT.md` if a match is found
- [x] Results recorded in `docs/analysis/K4_ACTIVE_RESEARCH.md` (PR #83, all 5 attacks null result)

---

## Q1 2027: Dashboard, API & Final Push 🖥️

### Phase 1 — K4 Attack completion
- [x] All five untested attack vectors above completed and documented

### Phase 2 — Dashboard & UI

> Stack shipped as specified: FastAPI + React SPA in a single multistage Docker container, served from `frontend/dist` by `create_app()`, backed by Neon. See `docs/analysis/K4-FRONTEND.md`.

- [x] **Ops Center** — live campaign monitoring, agent status row, top fused candidates table, run history with drill-down, ad-hoc decrypt panel (#100). Live log tail via SSE shipped (#118 backend, #119 frontend).
- [x] **K1–K3 Animated Decoder** — step-by-step visual explainer of how each solved section was encrypted and cracked (#102)
- [x] **Database admin page** — Neon connection status + per-table row counts (#104)
- [x] **Vault** — seal/unseal/peek encrypt/decrypt interface (keyed-alphabet Vigenère) with TTL and read-count enforcement (#115 backend, #116 frontend)
- [ ] **K4 Attack Dashboard** — dedicated real-time pipeline-progress + evidence-artifact viewer (most is covered by Ops Center, Database, and RAG search; a standalone attack-vector fingerprint view remains)

### Phase 3 — API
- [x] **REST dashboard API** — `/api/status`, `/api/runs`, `/api/runs/{id}/candidates`, `/api/candidates`, `POST /api/decrypt` (#99); turbovec RAG search at `/api/rag/*` (#113); `GET /api/stream/logs` SSE live-log tail (#118).
- [x] **`strategy_kb` write path** — `OpsStrategicDirector.record_strategy()` persists BOOST/PIVOT/STOP/START_NEW decisions to Neon `strategy_kb` table with JSONL fallback; `_record_strategy_from_decision()` auto-invoked on every `analyze()` cycle (#122).
- [x] **Candidate & run storage** — `candidates` and `campaign_runs` tables in Neon, persisted best-effort from campaigns (#98)

### Phase 4 — Validation & hardening
- [x] **K3 double-transposition Monte Carlo** — `kryptos.k3.double_rotation_solver` generalizes K3's two-stage 90cw rotation to all divisor-width/rotation-type pairs; brute-force solver exactly recovers K3's plaintext as the top candidate. Monte Carlo across random parameter pairs: 75% best-of-top-10 success (`tests/e2e/test_k3_double_rotation_monte_carlo.py`)
- [x] **Stress tests for K1/K2** — `kryptos.k4.vigenere_stress_tests.run_k1_k2_stress_suite` exercises noise injection, wrong key lengths, and partial-ciphertext truncation against `recover_key_by_frequency`. K2 (367-char ciphertext) recovers ABSCISSA at noise up to 20% (8/8 trials) and truncation down to 25% (4/4 trials); K1 (63-char ciphertext) only survives noise up to 5% (4/8 trials) and requires the full ciphertext (1/4 partial trials). Wrong key length always fails for both (`tests/e2e/test_k1_k2_stress_suite.py`)

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
