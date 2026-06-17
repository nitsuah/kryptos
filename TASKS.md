# Tasks

Last Updated: 2026-06-17


## Todo

# Q1 2027: Final Push & Post-Solution Analysis

### Phase 1: Dashboard & UI
- Develop dedicated K4 Attack Dashboard: visual fingerprint map of attack vectors plausible vs. covered vs. unknown (Ops Center, Database, and RAG search already cover live progress, scoring, and artifact lookup)
- Wire the SSE live-log tail (`/api/stream/logs`) into the Ops Center page (backend in flight on a separate branch)

### Phase 2: Data & API
- `strategy_kb` write path — automate persisting successful/failed strategies from `OpsStrategicDirector` back to Neon

### Phase 3: Post-Solution Analysis
- Analyze and document attack path, key insights, and lessons learned after solution
- Write comprehensive report on solution narrative and cryptanalytic implications
- Update README and documentation to reflect solution and research outcomes

### Phase 4: Misc/Supporting
- Update docs/analysis/K4-FRONTEND.md for frontend/dashboard integration
- Ensure all new features have test coverage and artifact logging


## In Progress

- [ ] **SSE live-log tail** — `GET /api/stream/logs` (StreamingResponse, `text/event-stream`) backed by a thread-safe ring buffer fed by a `kryptos`-logger handler, plus a frontend `LogTail` EventSource component on Ops Center. Backend implemented and unit-tested on the `sse-log-tail` branch.

## Done

### Dashboard, REST API & Web UI (Q1 2027 Phases 1–2)

- [x] **FastAPI dashboard endpoints** — `/api/status`, `/api/runs`, `/api/runs/{id}/candidates`, `/api/candidates`, `POST /api/decrypt` over the `create_app()` factory (#99).
- [x] **Neon persistence for campaigns** — `campaign_runs` + `candidates` tables (`db_schema.py`) with best-effort write path from live campaigns (#93 schema/`kryptos db-init`, #98 persistence).
- [x] **React + Vite + TypeScript SPA** — terminal-aesthetic dashboard scaffold with Ops Center (#100), K1–K3 animated decoder (#102), Database admin page (#104), and Vault page (#116). Vite bumped 5→8 to clear esbuild/vite CVEs (#103).
- [x] **Kryptos Vault** — seal/unseal/peek API + `vault_payloads` table; keyed-alphabet Vigenère with TTL and read-count enforcement, key never stored, wrong-key attempts don't burn a read (#115 backend, #116 frontend).
- [x] **Single-container delivery** — FastAPI serves the built SPA from `frontend/dist` via `StaticFiles(html=True)`; root `Dockerfile` builds the bundle in a `node:22-alpine` stage and ships it with the API (#114).
- [x] **turbovec RAG behind the FastAPI app** — `/api/rag/*` semantic search over `artifacts/` embedded into the dashboard service (#113, #87).

### SA transposition seeding + early-crib locking verification

- [x] **Seedable SA columnar solver** — added `seed_perm` to `solve_columnar_permutation_simulated_annealing` (and the multi-start variant's first restart) so the search can be seeded from a known pattern (e.g. K3's width/rotation) instead of a random shuffle, validating the seed is a true permutation. Verified end-to-end: random-init SA recovers a planted columnar plaintext on realistic-length text, and seeding at the optimum never scores worse than the seed.
- [x] **Early-crib locking pruning verified** — `search_with_multiple_cribs_positions` rejects permutations that don't place cribs at their known positions before scoring, pruning >90% of the columnar space at depth 1 (5040→2 for one crib, →1 for two) while always retaining the true permutation; the top crib-consistent candidate is the real plaintext. Documented the n-gram scoring-misranking caveat that crib locking sidesteps. See `tests/e2e/test_sa_transposition_crib_lock.py`.

### K4 attack benchmarks + physical-grid keystreams

- [x] **`kryptos.benchmarks` + `kryptos benchmark` CLI + CI job** — timed runner over the fast K4 attack sweeps recording runtime, throughput (tested/sec), and search-space reduction (e.g. clock→Hill invertibility prunes ~79%). Results persist to `benchmarks/results.{json,csv}`; a `benchmarks` job in `ci-fast.yml` publishes a table to the step summary and uploads the artifact.
- [x] **`kryptos.k4.physical_grid.run_physical_grid_attack`** — builds the 26×26 KRYPTOS Vigenère tableau and walks it along 108 geometric routes (rows/columns/diagonals/serpentine) into the Quagmire III solver against K4 with positional crib gating. 216 candidates, **null result**. Tests the physical-keystream theory; documented diagonal degeneracy on the cyclic tableau. Artifact: `K4_PHYSICAL_GRID_NULL.json`; recorded in `docs/analysis/K4_ACTIVE_RESEARCH.md`.

### Quagmire I–IV solver + K4 sweep

- [x] **`kryptos.k4.quagmire`** — canonical encrypt/decrypt for Quagmire I–IV (keyed plaintext/ciphertext alphabets, both Kryptos first-letter and ACA indicator-base conventions). Ground-truth verified: Quagmire III with the KRYPTOS tableau exactly reproduces K1 (PALIMPSEST) and K2 (ABSCISSA) plaintexts.
- [x] **`kryptos.k4.quagmire_sweep.run_quagmire_sweep`** — 6,240 combinations against K4: Q1/Q2/Q3 × 4 alphabet keywords × 10 word keys × 2 indicator bases, Q4 ordered keyword pairs, plus Q3 with 1,440 Berlin Clock minute-state indicator keys. Positional crib gating (EAST@22/NORTHEAST@26/BERLIN@63/CLOCK@69) + EurekaSignal protocol. **Null result** — rules out pure single-layer Quagmire, reinforcing the substitution+transposition composite model. Artifact: `K4_QUAGMIRE_NULL.json`; recorded in `docs/analysis/K4_ACTIVE_RESEARCH.md`.

### Agent Module Review (Post-K4, Pre-GUI)

- [x] **Audited `spy_nlp.py`, `spy_web_intel.py`, `linguist.py`, `ops_director.py`** — all four kept; none removed. See `docs/analysis/AGENT_MODULE_REVIEW.md`.
- [x] **Bug 1 — dead/crash-prone `SpyNLP()` in `AutonomousCoordinator.__init__`** — direct construction raised `OSError: [E050]` (`en_core_web_sm` not in runtime image), crashing the coordinator on startup. Removed; `SpyNLP` remains correctly used via `SpyAgent`'s guarded fallback.
- [x] **Bug 2 — `_check_web_intelligence()` called `SpyWebIntel` with wrong kwargs/return-shape** — fixed to call `gather_intelligence()`/`get_top_cribs()` with their real signatures (no `max_sources`/`max_age_days`/`n` kwargs; `new_cribs` is a dict key, `get_top_cribs()` returns `list[str]`). Verified live: 48 cribs found from real scrape.
- [x] **Bug 3 — `update_attack_progress(progress)` arity mismatch** — real signature is `update_attack_progress(attack_type, attempts, best_score)`; fixed call sites.
- [x] **Bug 4 — unhandled `analyze_situation() -> None`** — `OpsStrategicDirector.analyze_situation()` returns `None` when no decision is needed (the common case on early cycles); previously crashed with `AttributeError` on `decision.timestamp`. Added early-return + log message; verified live (`OPS: no strategic decision needed at this time`).
- [x] **Bug 5 — `run_autonomous_loop(max_hours=0.0, ...)` infinite loop** — `if max_hours and ...` / `if max_cycles and ...` treated `0`/`0.0` ("exit immediately") the same as `None` ("infinite"), since both are falsy. Previously masked by Bug 4's crash-based early exit; exposed once Bug 4 was fixed, causing PR CI to hang for the full 6-hour job timeout (twice). Fixed via `is not None` checks; verified the previously-hanging test now passes in 15.29s.
- [x] **`linguist.py` status** — confirmed standalone, extensively unit-tested (`tests/functional/test_linguist.py`), not wired into `pipeline/validator.py` (which uses `scoring_enhanced` instead). Documented as a future integration candidate (see Todo).
- [x] **Updated `docs/reference/AGENTS_ARCHITECTURE.md`, `ROADMAP.md`** with corrected integration details and findings summary.

### Linguist Integration (`pipeline/validator.py` stage 3)

- [x] **Wired `LinguistAgent` into `PlaintextValidator`** — new `enable_linguist` constructor flag (default `False`). `_init_linguist()` gates on `torch`/`transformers` availability and `LinguistAgent` construction, degrading to `linguist_available=False` on any failure. When enabled, `stage3_linguistic_validation()` adds a `"linguist"` key (confidence/perplexity/coherence/grammar_score/model_used/passed) alongside the existing heuristic fields; `_linguist_score()` and the new `batch_validate_linguist()` re-ranking helper both catch and log scoring exceptions, returning `None` rather than raising. Existing default (`enable_linguist=False`) behavior and `"linguist"`-key absence are unchanged. See `tests/functional/test_validator_linguist.py`.


### RAG API (turbovec) — semantic search over `artifacts/`

- [x] **`kryptos serve`** — minimal FastAPI app (`src/kryptos/api/`) with `/health`, `/api/rag/status`,
  `POST /api/rag/reindex`, `GET /api/rag/search` endpoints
- [x] **turbovec-backed `ArtifactIndex`** — `src/kryptos/rag/` chunks `artifacts/` (`.json`/`.md`), embeds with
  `sentence-transformers` (`all-MiniLM-L6-v2`), indexes with `turbovec.IdMapIndex` (4-bit quantization), persisted
  under `data/turbovec/`
- This is the "Now" item from agent-board's `docs/AI_STACK_STRATEGY.md`, scoped separately from the Q1 2027 Phase 2
  Data & API dashboard work above

### K4 Attack — Untested Vectors (PR #83, merged)

- [x] **Clock → Hill 2×2 invertibility pre-filter** — `kryptos.k4.clock_hill_attack.run_clock_hill_attack`. Null result.
- [x] **4-char clock key → Vigenère with NORTHEAST anchor** — `kryptos.k4.clock_hill_attack.run_clock_vigenere_attack`. Null result.
- [x] **Non-standard Berlin Clock sub-row encodings** — `kryptos.k4.clock_subrow_attack.run_clock_subrow_attack`. Null result.
- [x] **Berlin Clock lamp counts as transposition column widths** — `kryptos.k4.clock_subrow_attack.run_clock_transposition_attack`. Null result.
- [x] **Beaufort cipher sweep** — `kryptos.k4.beaufort_sweep.run_beaufort_sweep`. Null result.

### K3 Double-Transposition Monte Carlo (Phase 4 validation)

- [x] **Generalized double-rotation solver** — `kryptos.k3.double_rotation_solver` generalizes K3's two-stage 90cw grid rotation to all 18 divisor-widths of 336 x 6 rotation types, both stages. `apply_double_rotation(K3_CIPHERTEXT, 24, '90cw', 8, '90cw') == K3_PLAINTEXT` confirmed exactly.
- [x] **Brute-force recovery** — `brute_force_double_rotation_solve` ranks K3's true plaintext as the #1 candidate (match_ratio=1.0) out of 11,664 (width, rotation) combinations.
- [x] **Monte Carlo validation** — `run_k3_double_rotation_monte_carlo` over 20 random parameter pairs: 75% best-of-top-10 success. Failures cluster around `'identity'`/extreme-aspect-ratio grids whose score-tied cyclic rearrangements of the plaintext outrank the exact match under n-gram/word scoring (see `tests/e2e/test_k3_double_rotation_monte_carlo.py`).

### K1/K2 Vigenère Stress Tests (Phase 4 validation)

- [x] **Stress-test harness** — `kryptos.k4.vigenere_stress_tests.run_k1_k2_stress_suite` runs `recover_key_by_frequency` against K1 (PALIMPSEST, 63-char ciphertext) and K2 (ABSCISSA, 367-char ciphertext) across noise injection (0/5/10/20%, 2 trials each), wrong key lengths (+/-2 around the true length), and partial-ciphertext truncation (100/75/50/25%).
- [x] **Noise**: K2 recovers ABSCISSA at all 8 trials up to 20% noise (plaintext match ratio degrades gracefully 1.0 -> ~0.76); K1 only recovers PALIMPSEST at 0% and 5% noise (4/8 trials), collapsing to wrong keys at 10%/20%.
- [x] **Wrong key length**: for both K1 and K2, only the true key length yields the correct key with a perfect plaintext match; all four off-by-(-2..+2) lengths fail for both.
- [x] **Partial ciphertext**: K2 recovers ABSCISSA exactly down to 25% (91 chars); K1 only recovers PALIMPSEST at 100% (63 chars) -- 75/50/25% truncations all fail. See `tests/e2e/test_k1_k2_stress_suite.py` and `docs/analysis/K1_K2_VALIDATION_RESULTS.md`.
