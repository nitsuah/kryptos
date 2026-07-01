# Tasks

Breadcrumb: [Docs](INDEX.md) > Tasks

Last Updated: 2026-06-27

## In Progress

#### Phase 1: Dashboard & UI

- [x] Develop dedicated K4 Attack Dashboard: visual fingerprint map of attack vectors plausible vs. covered vs. unknown (Ops Center, Database, and RAG search already cover live progress, scoring, and artifact lookup)
- [x] Improve K4 dashboard visual representation and component styling

#### Phase 2: Post-Solution Analysis

- [ ] Analyze and document attack path, key insights, and lessons learned after solution
- [ ] Write comprehensive report on solution narrative and cryptanalytic implications
- [ ] Update README and documentation to reflect solution and research outcomes

#### Phase 3: Misc/Supporting

- [x] Update docs/analysis/K4-FRONTEND.md for frontend/dashboard integration
- [ ] Ensure all new features have test coverage and artifact logging

## Done

### Dashboard, REST API, Web UI & Ops Strategy KB (Q1 2027 Phases 1–3)

- [x] **FastAPI dashboard endpoints** — `/api/status`, `/api/runs`, `/api/runs/{id}/candidates`, `/api/candidates`, `POST /api/decrypt` over the `create_app()` factory (#99).
- [x] **Neon persistence for campaigns** — `campaign_runs` + `candidates` tables (`db_schema.py`) with best-effort write path from live campaigns (#93 schema/`kryptos db-init`, #98 persistence).
- [x] **React + Vite + TypeScript SPA** — terminal-aesthetic dashboard scaffold with Ops Center (#100), K1–K3 animated decoder (#102), Database admin page (#104), and Vault page (#116). Vite b[...]
- [x] **Kryptos Vault** — seal/unseal/peek API + `vault_payloads` table; keyed-alphabet Vigenère with TTL and read-count enforcement, key never stored, wrong-key attempts don't burn a read (#11[...]
- [x] **Single-container delivery** — FastAPI serves the built SPA from `frontend/dist` via `StaticFiles(html=True)`; root `Dockerfile` builds the bundle in a `node:22-alpine` stage and ships it[...]
- [x] **turbovec RAG behind the FastAPI app** — `/api/rag/*` semantic search over `artifacts/` embedded into the dashboard service (#113, #87).
- [x] **SSE live-log tail** — `GET /api/stream/logs` (StreamingResponse, `text/event-stream`) backed by a thread-safe ring buffer fed by a `kryptos`-logger handler (#118); `LogTail` EventSource [...]
- [x] **`strategy_kb` write path** — `OpsStrategicDirector.record_strategy()` + `_record_strategy_from_decision()` persist BOOST/PIVOT/STOP/START_NEW decisions to Neon `strategy_kb` with JSONL f[...]

### SA transposition seeding + early-crib locking verification

- [x] **Seedable SA columnar solver** — added `seed_perm` to `solve_columnar_permutation_simulated_annealing` (and the multi-start variant's first restart) so the search can be seeded from a kno[...]
- [x] **Early-crib locking pruning verified** — `search_with_multiple_cribs_positions` rejects permutations that don't place cribs at their known positions before scoring, pruning >90% of the co[...]

### K4 attack benchmarks + physical-grid keystreams

- [x] **`kryptos.benchmarks` + `kryptos benchmark` CLI + CI job** — timed runner over the fast K4 attack sweeps recording runtime, throughput (tested/sec), and search-space reduction (e.g. clock[...]
- [x] **`kryptos.k4.physical_grid.run_physical_grid_attack`** — builds the 26×26 KRYPTOS Vigenère tableau and walks it along 108 geometric routes (rows/columns/diagonals/serpentine) into the Q[...]

### Quagmire I–IV solver + K4 sweep

- [x] **`kryptos.k4.quagmire`** — canonical encrypt/decrypt for Quagmire I–IV (keyed plaintext/ciphertext alphabets, both Kryptos first-letter and ACA indicator-base conventions). Ground-truth[...]
- [x] **`kryptos.k4.quagmire_sweep.run_quagmire_sweep`** — 6,240 combinations against K4: Q1/Q2/Q3 × 4 alphabet keywords × 10 word keys × 2 indicator bases, Q4 ordered keyword pairs, plus Q3 [...]

### Agent Module Review (Post-K4, Pre-GUI)

- [x] **Audited `spy_nlp.py`, `spy_web_intel.py`, `linguist.py`, `ops_director.py`** — all four kept; none removed. See `docs/analysis/AGENT_MODULE_REVIEW.md`.
- [x] **Bug 1 — dead/crash-prone `SpyNLP()` in `AutonomousCoordinator.__init__`** — direct construction raised `OSError: [E050]` (`en_core_web_sm` not in runtime image), crashing the coordinat[...]
- [x] **Bug 2 — `_check_web_intelligence()` called `SpyWebIntel` with wrong kwargs/return-shape** — fixed to call `gather_intelligence()`/`get_top_cribs()` with their real signatures (no `max_[...]
- [x] **Bug 3 — `update_attack_progress(progress)` arity mismatch** — real signature is `update_attack_progress(attack_type, attempts, best_score)`; fixed call sites.
- [x] **Bug 4 — unhandled `analyze_situation() -> None`** — `OpsStrategicDirector.analyze_situation()` returns `None` when no decision is needed (the common case on early cycles); previously c[...]
- [x] **Bug 5 — `run_autonomous_loop(max_hours=0.0, ...)` infinite loop** — `if max_hours and ...` / `if max_cycles and ...` treated `0`/`0.0` ("exit immediately") the same as `None` ("infinit[...]
- [x] **`linguist.py` status** — confirmed standalone, extensively unit-tested (`tests/functional/test_linguist.py`), not wired into `pipeline/validator.py` (which uses `scoring_enhanced` instea[...]
- [x] **Updated `docs/reference/AGENTS_ARCHITECTURE.md`, `ROADMAP.md`** with corrected integration details and findings summary.

### Linguist Integration (`pipeline/validator.py` stage 3)

- [x] **Wired `LinguistAgent` into `PlaintextValidator`** — new `enable_linguist` constructor flag (default `False`). `_init_linguist()` gates on `torch`/`transformers` availability and `Linguis[...]

### RAG API (turbovec) — semantic search over `artifacts/`

- [x] **`kryptos serve`** — minimal FastAPI app (`src/kryptos/api/`) with `/health`, `/api/rag/status`,
  `POST /api/rag/reindex`, `GET /api/rag/search` endpoints
- [x] **turbovec-backed `ArtifactIndex`** — `src/kryptos/rag/` chunks `artifacts/` (`.json`/`.md`), embeds with
  `sentence-transformers` (`all-MiniLM-L6-v2`), indexes with `turbovec.IdMapIndex` (4-bit quantization), persisted
  under `data/turbovec/`
- This is the "Now" item from motor-pool's `docs/AI_STACK_STRATEGY.md`, scoped separately from the Q1 2027 Phase 2
  Data & API dashboard work above

### K4 Attack — Untested Vectors (PR #83, merged)

- [x] **Clock → Hill 2×2 invertibility pre-filter** — `kryptos.k4.clock_hill_attack.run_clock_hill_attack`. Null result.
- [x] **4-char clock key → Vigenère with NORTHEAST anchor** — `kryptos.k4.clock_hill_attack.run_clock_vigenere_attack`. Null result.
- [x] **Non-standard Berlin Clock sub-row encodings** — `kryptos.k4.clock_subrow_attack.run_clock_subrow_attack`. Null result.
- [x] **Berlin Clock lamp counts as transposition column widths** — `kryptos.k4.clock_subrow_attack.run_clock_transposition_attack`. Null result.
- [x] **Beaufort cipher sweep** — `kryptos.k4.beaufort_sweep.run_beaufort_sweep`. Null result.

### K3 Double-Transposition Monte Carlo (Phase 4 validation)

- [x] **Generalized double-rotation solver** — `kryptos.k3.double_rotation_solver` generalizes K3's two-stage 90cw grid rotation to all 18 divisor-widths of 336 x 6 rotation types, both stages. [...]
- [x] **Brute-force recovery** — `brute_force_double_rotation_solve` ranks K3's true plaintext as the #1 candidate (match_ratio=1.0) out of 11,664 (width, rotation) combinations.
- [x] **Monte Carlo validation** — `run_k3_double_rotation_monte_carlo` over 20 random parameter pairs: 75% best-of-top-10 success. Failures cluster around `'identity'`/extreme-aspect-ratio grid[...]

### K1/K2 Vigenère Stress Tests (Phase 4 validation)

- [x] **Stress-test harness** — `kryptos.k4.vigenere_stress_tests.run_k1_k2_stress_suite` runs `recover_key_by_frequency` against K1 (PALIMPSEST, 63-char ciphertext) and K2 (ABSCISSA, 367-char c[...]
- [x] **Noise**: K2 recovers ABSCISSA at all 8 trials up to 20% noise (plaintext match ratio degrades gracefully 1.0 -> ~0.76); K1 only recovers PALIMPSEST at 0% and 5% noise (4/8 trials), collaps[...]
- [x] **Wrong key length**: for both K1 and K2, only the true key length yields the correct key with a perfect plaintext match; all four off-by-(-2..+2) lengths fail for both.
- [x] **Partial ciphertext**: K2 recovers ABSCISSA exactly down to 25% (91 chars); K1 only recovers PALIMPSEST at 100% (63 chars) -- 75/50/25% truncations all fail. See `tests/e2e/test_k1_k2_stres[...]`
