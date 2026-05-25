# Tasks

Last Updated: 2026-05-25 (All K4-ATTACK-1 through K4-ATTACK-7 complete, including K4-ATTACK-4 composite sweep)

## Done

- [x] Wire manifesto alignment checks into PR cadence.
  - Completed: 2026-04-03
  - Evidence: `.github/pull_request_template.md` includes Manifesto Alignment requirements and `.github/workflows/manifesto-pr-check.yml` enforces them.

- [x] Consolidate scripts policy around pytest-owned validation.
  - Completed: 2025-01-27 (documented), reaffirmed 2026-05-24
  - Evidence: `scripts/README.md` and `scripts/testing/README.md` now point to canonical validation in `tests/` and metrics/analysis docs.

- [x] Create repository-wide docs audit tracker.
  - Completed: 2026-05-24
  - Evidence: `AUDIT.md` maps active/reference/archive/speculative docs and cleanup decisions.

- [x] Implement composite-chain execution for layered K4 hypotheses.
  - Completed: 2026-05-24 (verified in code/tests)
  - Evidence: `src/kryptos/k4/composite.py` (`CompositeChainExecutor`) and chain hypothesis coverage in `tests/test_composite_chains.py`, `tests/test_k4_hypotheses.py`.

- [x] Add cross-run key-memory primitives for Vigenere key recovery.
  - Completed: 2026-05-24 (verified in code/tests)
  - Evidence: `src/kryptos/provenance/search_space.py` (`tried_keys.jsonl` tracking) and `recover_key_by_frequency(..., skip_tried=True)` coverage in `tests/test_cross_run_memory.py`.

- [x] Consolidate roadmap references to canonical planning sources.
  - Completed: 2026-05-24
  - Evidence: `ROADMAP.md` and `TASKS.md` are canonical active planning docs, and legacy phase-planning docs were removed from active navigation.

- [x] **K4-ATTACK-7**: Fix position index bugs in CONTRIBUTING.md quick-start code.
  - Completed: 2026-05-25
  - Evidence: `CONTRIBUTING.md` updated — `'NORTHEAST': [26]`, `'BERLIN': [63]`.

- [x] **K4-ATTACK-1**: Implement `kryptos.k4.keystream_validator` utility.
  - Completed: 2026-05-25
  - Evidence: `src/kryptos/k4/keystream_validator.py`; 14 tests in `tests/test_k4_keystream_validator.py` all pass.
  - Exports: `compute_shifts_at_cribs`, `validate_k4_cribs`, `crib_hit_count`, `keystream_summary`.

- [x] **K4-ATTACK-3**: Implement keyed alphabet realignment test.
  - Completed: 2026-05-25
  - Evidence: `build_keyed_alphabet`, `derive_keystream_under_alphabet`, `check_keyed_alphabet_realignment` added to `vigenere_key_recovery.py`; 14 tests in `tests/test_k4_keyed_alphabet_realignment.py` all pass.
  - Result: None of KRYPTOS/PALIMPSEST/ABSCISSA alphabets simplify the keystream vs. standard — confirms transposition-first architecture.

- [x] **K4-ATTACK-2**: Implement inverse transposition sweep + ENE diagonal reader.
  - Completed: 2026-05-25
  - Evidence: `src/kryptos/k4/inverse_transposition_sweep.py` + `read_ene_diagonal`/`to_grid` in `transposition_routes.py`; 19 tests in `tests/test_k4_inverse_transposition_sweep.py` all pass.
  - Exports: `sweep_grid`, `full_sweep`, `invert_permutation`; reads at tan(67.5°)≈2.414.

- [x] **K4-ATTACK-5**: Implement `InstructionalScorer`.
  - Completed: 2026-05-25
  - Evidence: `src/kryptos/k4/scoring_instructional.py`; 23 tests in `tests/test_k4_instructional_scorer.py` all pass.
  - Exports: `instructional_score`, `combined_instructional_score`, `levenshtein`, `entropy_gate`, `INSTRUCTIONAL_VECTORS`.

- [x] **K4-ATTACK-6**: Implement Eureka capture protocol.
  - Completed: 2026-05-25
  - Evidence: `src/kryptos/k4/eureka.py`; 16 tests in `tests/test_k4_eureka.py` all pass.
  - Exports: `check_eureka`, `write_breakthrough_snapshot`, `eureka_check_and_capture`, `EurekaSignal`.

- [x] **K4-ATTACK-4**: Implement full composite parameter sweep.
  - Completed: 2026-05-25
  - Evidence: `src/kryptos/k4/composite_sweep.py`; 21 tests in `tests/test_k4_composite_sweep.py` all pass.
  - Exports: `run_composite_sweep`.
  - Covers: KNOWN_KEYED_ALPHABETS × K4_GRID_GEOMETRIES × Berlin Clock states × reading routes.
  - On 4-keyword hit: raises `EurekaSignal` + writes breakthrough snapshot.
  - On null result: writes provenance artifact with full run parameters.


## In Progress

(none — all K4-ATTACK tasks complete)


## Done

- [x] Wire manifesto alignment checks into PR cadence.
  - Completed: 2026-04-03
  - Evidence: `.github/pull_request_template.md` includes Manifesto Alignment requirements and `.github/workflows/manifesto-pr-check.yml` enforces them.

- [x] Consolidate scripts policy around pytest-owned validation.
  - Completed: 2025-01-27 (documented), reaffirmed 2026-05-24
  - Evidence: `scripts/README.md` and `scripts/testing/README.md` now point to canonical validation in `tests/` and metrics/analysis docs.

- [x] Create repository-wide docs audit tracker.
  - Completed: 2026-05-24
  - Evidence: `AUDIT.md` maps active/reference/archive/speculative docs and cleanup decisions.

- [x] Implement composite-chain execution for layered K4 hypotheses.
  - Completed: 2026-05-24 (verified in code/tests)
  - Evidence: `src/kryptos/k4/composite.py` (`CompositeChainExecutor`) and chain hypothesis coverage in `tests/test_composite_chains.py`, `tests/test_k4_hypotheses.py`.

- [x] Add cross-run key-memory primitives for Vigenere key recovery.
  - Completed: 2026-05-24 (verified in code/tests)
  - Evidence: `src/kryptos/provenance/search_space.py` (`tried_keys.jsonl` tracking) and `recover_key_by_frequency(..., skip_tried=True)` coverage in `tests/test_cross_run_memory.py`.

- [x] Consolidate roadmap references to canonical planning sources.
  - Completed: 2026-05-24
  - Evidence: `ROADMAP.md` and `TASKS.md` are canonical active planning docs, and legacy phase-planning docs were removed from active navigation.


## In Progress

- [ ] K4 structural attack implementation (Phase 1 of 2026 K4 push).
  - Priority: P1
  - Context: `docs/analysis/K4_KEYSTREAM_ANALYSIS.md` + `docs/analysis/K4_ACTIVE_RESEARCH.md`
  - Sub-tasks tracked as K4-ATTACK-1 through K4-ATTACK-7 in ROADMAP.md.
  - Acceptance Criteria: all 7 attack tasks implemented with passing tests; composite sweep run with null-result artifact or breakthrough snapshot.


## Todo

- [ ] **K4-ATTACK-4**: Implement full composite parameter sweep (~2,700 combinations).
  - Priority: P1
  - Problem: The combined (alphabet × grid × angle × clock state) search space is tractable but has not been exhaustively enumerated.
  - Details: Wire `check_keyed_alphabet_realignment` + `sweep_grid` + `eureka_check_and_capture` into a single campaign runner. 3 alphabets × 3 grids × ~100 clock states × 2 angles.
  - Acceptance Criteria: sweep completes in <60s on K4; any simultaneous 4-crib match triggers Eureka capture; null-result artifact written with run parameters.

### Infrastructure Tasks (P1)

- [ ] Build objective-to-evidence scorecard.
  - Priority: P1
  - Problem: roadmap goals are clear, but proof of attainment is not yet centralized in one measurable view.
  - Acceptance Criteria: one maintained scorecard maps each strategic goal to KPI target, current value, evidence command, and artifact/doc link.

- [ ] Enforce strategic-claim evidence gate in workflow.
  - Priority: P1
  - Problem: features can be marked complete without a uniform proof bundle.
  - Acceptance Criteria: PR/process checks require tests, reproducible runtime command(s), and artifact/document evidence before strategic-completion claims are accepted.

- [ ] Add fresh-environment autonomous smoke test.
  - Priority: P1
  - Problem: autonomous behavior can fail in clean environments due to dependency/bootstrap drift.
  - Acceptance Criteria: deterministic smoke path runs in a fresh environment in CI and validates core autonomous startup behavior.

- [ ] Add scalable campaign orchestration with bounded parallel workers.
  - Priority: P2
  - Problem: larger K4 search batches still run too slowly.
  - Acceptance Criteria: bounded parallel execution is reproducible and emits useful telemetry.

- [ ] Add `sections-decrypt` CLI command for K1/K2/K3 tire-kicks.
  - Priority: P1
  - Problem: proving K1/K2/K3 currently requires custom Python snippets instead of a first-class command.
  - Acceptance Criteria: supports `--section`, `--from-config`/`--cipher`, optional `--key`, and prints deterministic output.

- [ ] Add JSON output mode for section verification commands.
  - Priority: P1
  - Problem: current section-oriented validation is hard to automate in CI and scripted checks.
  - Acceptance Criteria: machine-readable output includes section, input source, plaintext markers, and status fields.

- [ ] Add section API end-to-end tests.
  - Priority: P1
  - Problem: wrappers in `kryptos.sections` can drift from cipher core behavior.
  - Acceptance Criteria: new tests verify K1/K2/K3 outputs via `SECTIONS` using config fixtures.

- [ ] Add optional explainability mode for section decryptions.
  - Priority: P2
  - Problem: debugging decryption behavior currently requires code inspection.
  - Acceptance Criteria: `--explain` can emit bounded transformation diagnostics for Vigenere and K3 pipeline steps.

- [ ] Wire alphabet auto-selection into runtime orchestrators.
  - Priority: P2
  - Problem: `try_all_alphabets` support exists in `vigenere_key_recovery.py` but is not the default path in `ops.py`/`k4_campaign.py`.
  - Acceptance Criteria: orchestrators exercise keyed + standard alphabets where appropriate, with deterministic tests.

- [ ] Fix transposition plaintext extraction in campaign orchestrator.
  - Priority: P2
  - Problem: `execute_transposition_attack` currently computes permutation/score but returns ciphertext as plaintext.
  - Acceptance Criteria: plaintext output reflects the recovered permutation, with regression tests.

- [ ] Stabilize autonomous test/runtime NLP dependency.
  - Priority: P2
  - Problem: autonomous coordinator tests fail in environments missing spaCy model `en_core_web_sm`.
  - Acceptance Criteria: CI/dev path is deterministic (model bootstrap or fallback strategy) and autonomous tests pass consistently.

- [ ] Resolve `python -m kryptos.cli.main` runpy warning path.
  - Priority: P2
  - Problem: module execution emits `runpy` cache warning in current environment.
  - Acceptance Criteria: warning is removed or documented with a tested invocation path that avoids it.

- [ ] Resolve `config/llm_config.yaml` ownership.
  - Priority: P3
  - Problem: config file exists without a clearly documented/runtime-owned integration path.
  - Acceptance Criteria: either wire it to runtime behavior or remove it with a documented rationale.

- [ ] Retire legacy executor/wrapper surfaces after migration confirmation.
  - Priority: P3
  - Problem: historical notes track deprecated execution paths and wrappers that may no longer be needed.
  - Acceptance Criteria: verify usage and remove deprecated surfaces or formally document retention reason.

- [ ] Add a lightweight monthly governance review note in docs.
  - Priority: P3
  - Problem: lessons and retired hypotheses are not yet captured on a regular cadence.
  - Acceptance Criteria: one recurring section tracks what was promoted, what was retired, and why.

### Recurring Governance Review
- [ ] Add/update a section in docs/governance.md each month summarizing:
  - What was promoted to active research
  - What hypotheses were retired (and why)
  - Lessons learned and next steps
