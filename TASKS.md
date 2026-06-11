# Tasks

Last Updated: 2026-06-10


## Todo

- [ ] **Linguist integration** — wire `LinguistAgent.cross_validate_with_spy`/`batch_validate` (`kryptos.agents.linguist`) into `pipeline/validator.py` stage 3 as an optional enhanced-scoring pass alongside `scoring_enhanced`, gated on `torch`/`transformers` availability (see `docs/analysis/AGENT_MODULE_REVIEW.md`).

# Q1 2027: Final Push & Post-Solution Analysis

### Phase 1: Dashboard & UI
- Implement real-time campaign monitoring dashboard (CLI/GUI)
- Build K1–K3 Decoder: input ciphertext + key → annotated plaintext, with encoding/hacking instructions
- Develop K4 Attack Dashboard: live campaign progress, scoring breakdowns, evidence artifact viewer, visual fingerprint map of attack vectors plausible vs. covered vs. unknown

- Create Vault: demo encrypt/decrypt interface for all supported ciphers

### Phase 2: Data & API
- Integrate database (e.g., neon) for storing keys, plaintexts, attempts, provenance
- Develop API endpoints for querying and managing cryptanalysis data

### Phase 3: Post-Solution Analysis
- Analyze and document attack path, key insights, and lessons learned after solution
- Write comprehensive report on solution narrative and cryptanalytic implications
- Update README and documentation to reflect solution and research outcomes

### Phase 4: Misc/Supporting
- Update docs/analysis/K4-FRONTEND.md for frontend/dashboard integration
- Ensure all new features have test coverage and artifact logging


## In Progress

## Done

### Agent Module Review (Post-K4, Pre-GUI)

- [x] **Audited `spy_nlp.py`, `spy_web_intel.py`, `linguist.py`, `ops_director.py`** — all four kept; none removed. See `docs/analysis/AGENT_MODULE_REVIEW.md`.
- [x] **Bug 1 — dead/crash-prone `SpyNLP()` in `AutonomousCoordinator.__init__`** — direct construction raised `OSError: [E050]` (`en_core_web_sm` not in runtime image), crashing the coordinator on startup. Removed; `SpyNLP` remains correctly used via `SpyAgent`'s guarded fallback.
- [x] **Bug 2 — `_check_web_intelligence()` called `SpyWebIntel` with wrong kwargs/return-shape** — fixed to call `gather_intelligence()`/`get_top_cribs()` with their real signatures (no `max_sources`/`max_age_days`/`n` kwargs; `new_cribs` is a dict key, `get_top_cribs()` returns `list[str]`). Verified live: 48 cribs found from real scrape.
- [x] **Bug 3 — `update_attack_progress(progress)` arity mismatch** — real signature is `update_attack_progress(attack_type, attempts, best_score)`; fixed call sites.
- [x] **Bug 4 — unhandled `analyze_situation() -> None`** — `OpsStrategicDirector.analyze_situation()` returns `None` when no decision is needed (the common case on early cycles); previously crashed with `AttributeError` on `decision.timestamp`. Added early-return + log message; verified live (`OPS: no strategic decision needed at this time`).
- [x] **`linguist.py` status** — confirmed standalone, extensively unit-tested (`tests/functional/test_linguist.py`), not wired into `pipeline/validator.py` (which uses `scoring_enhanced` instead). Documented as a future integration candidate (see Todo).
- [x] **Updated `docs/reference/AGENTS_ARCHITECTURE.md`, `ROADMAP.md`** with corrected integration details and findings summary.

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
