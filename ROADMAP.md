# 🗺️ Kryptos Roadmap

Last Updated: 2026-06-01
Next Review: 2026-07-01
---

## Untested K4 Attack Vectors 🎯

> These are the highest-priority items before broader infrastructure work. All prior Q3/Q4 sweeps produced null results; these are the remaining untested angles. Each is small and targeted.

- [ ] **Clock → Hill 2×2 invertibility pre-filter** — For each of 720 clock states form a 2×2 matrix from the first 4 lamp values, filter to the ~100 invertible mod 26, apply Hill 2×2 decryption to K4, validate EAST+NORTHEAST. Clock and Hill have only been tested independently so far.
- [ ] **4-char clock key → Vigenère with NORTHEAST anchor** — Derive a 4-char Vigenère key from each clock state (not the full shift sequence), test with `positional_crib_bonus` gating on NORTHEAST at position 26. Several clock→4-char encoding schemes to try.
- [ ] **Non-standard Berlin Clock sub-row encodings** — Hour rows only, minute rows only, row sums → letter. Current sweep only uses `full_berlin_clock_shifts` (all 4 rows concatenated).
- [ ] **Berlin Clock lamp counts as transposition column widths** — Use lamp values (e.g. [4,3,11,4]) as column widths for a multi-round columnar transposition, not Vigenère shifts.
- [ ] **Beaufort cipher sweep** — `kryptos.k4.beaufort` is implemented; no systematic K4 sweep has run. Quick pass with KRYPTOS, PALIMPSEST, BERLIN, CLOCK, ABSCISSA keys.

### Definition of Done

- [ ] Each attack run with null-result artifact or `K4_BREAKTHROUGH_SNAPSHOT.md` if a match is found
- [ ] Results recorded in `k4_research_findings` DB table and `docs/analysis/K4_ACTIVE_RESEARCH.md`

---

## Q1 2027: Dashboard, API & Final Push 🖥️

### Phase 1 — K4 Attack completion
- [ ] All five untested attack vectors above completed and documented

### Phase 2 — Dashboard & UI

- [ ] See `docs/analysis/K4-FRONTEND.md` for full spec. Stack: FastAPI + React SPA, single Docker container, Neon DB (not SQLite — the spec's schema is superseded by existing Neon tables).
- [ ] **Ops Center** — live campaign monitoring, agent status row (SPY/OPS/Q), top fused candidates table, letter frequency chart, live log tail via SSE
- [ ] **K1–K3 Animated Decoder** — step-by-step visual explainer of how each solved section was encrypted and cracked
- [ ] **K4 Attack Dashboard** — real-time pipeline progress, scoring breakdowns, evidence artifact viewer
- [ ] **Vault** — demo encrypt/decrypt interface for all supported ciphers with TTL and read-count enforcement

### Phase 3 — API
- [ ] **REST API** (`/api/status`, `/api/candidates`, `/api/runs`, `/api/stream/logs`, `POST /api/decrypt`)
- [ ] **`strategy_kb` write path** — automate writing successful/failed strategies from `OpsStrategicDirector` back to Neon
- [ ] **Candidate & run storage** — `candidates` and `campaign_runs` tables in Neon (currently file-based under `artifacts/`)

### Phase 4 — Validation & hardening
- [ ] **K3 double-transposition Monte Carlo** — full double-rotational K3 algorithm not yet statistically validated (only single-column SA solver has been)
- [ ] **Stress tests for K1/K2** — test with noise, wrong key lengths, partial ciphertext

### Phase 5 — Post-solution
- [ ] **Solution documentation** — once K4 is solved: full attack path, key insights, solution narrative
- [ ] **README and docs update** — reflect the solution and its cryptanalytic implications

---

## Agent Module Review (Post-K4, Pre-GUI)

- [ ] Review, refactor, or remove optional/partial agent modules in `src/kryptos/agents/`:
    - `spy_nlp.py`
    - `spy_web_intel.py`
    - `linguist.py`
    - `ops_director.py`
- [ ] Decide if these modules are needed, should be modernized, or can be dropped entirely.
- [ ] Document outcome and update architecture docs as needed.

---

## Working Notes

- Active task backlog: `TASKS.md`
- K4 attack context and null results: `docs/analysis/K4_ACTIVE_RESEARCH.md`
- Confirmed keystream analysis: `docs/analysis/K4_KEYSTREAM_ANALYSIS.md`
- Frontend spec: `docs/analysis/K4-FRONTEND.md`
- Monthly governance log: `docs/governance.md`
