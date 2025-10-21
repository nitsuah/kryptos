# Plan for Tomorrow - 2025-10-21

## Core Tomorrow Plan (Checklist)

- [x] 1. Define stage interface spec (inputs/outputs) and verify factory functions.
- [x] 2. Add unit tests for each stage (initial pruning, pattern bonus, parallel variants).
- [x] 3. Implement/verify scoring/fitness (frequency + crib + clock pattern + extended bonus).
- [x] 4. Create initial pipeline config (ordering, thresholds, pruning).
- [x] 5. Validate logging persistence on sample attempt (attempt_log.jsonl, summary.json).
- [x] 6. Run tiny end-to-end sample with trivial cipher slice.
- [x] 7. Add parallel/batch execution stub (hill variants parameter diversification).
- [ ] 8. Prepare tuning script/notebook for hill & transposition parameter sweeps.
- [ ] 9. Add artifact CSV export per stage (top candidates).
- [ ] 10. Implement adaptive gating refinement (dynamic threshold adjustment based on prior stage deltas).
- [ ] 11. Performance counters (candidates/ms, score bucket distribution) integrated into summary.
- [ ] 12. Fallback n-gram loader test (simulate missing files and verify graceful defaults).

## Execution Kickoff (Focus Block)

Stage Interface (1):

- [x] List all stage factory functions (hill, transposition adaptive/multi-crib, masking, berlin clock).
- [x] Define common StageContext (ciphertext, params, prior_results).
- [x] Define output contract (candidates list, scores, metadata dict).
- [x] Draft interface in code (placeholder types) and mark TODOs. -> DONE

Unit Tests Scaffold (2):

- [x] Create test_stage_interface.py with dummy mock stage.
- [x] Add fixture for sample ciphertext and crib set. (Mock via literal for now)
- [x] Add negative test (no candidates -> empty list). -> DONE

Scoring/Fitness (3):

- [x] Enumerate components: n-gram freq, crib positional bonus, berlin clock pattern validation.
- [x] Determine weight defaults.
- [x] Provide pure function score_candidate(text, meta, weights) (implicit via combined score functions).
- [ ] Add fallback path when n-gram data missing (explicit test harness) -> pending test.

## Pipeline Config Draft

Minimal prototype:

- order: ["hill", "transposition_adaptive", "transposition_multi_crib", "masking", "berlin_clock"]
- iteration_budget: 250 (hill), 100 (each transposition), 50 (masking), 30 (clock)
- adaptive_thresholds: hill.score >= 0.15 to feed transposition_adaptive
- candidate_cap_per_stage: 40
- pruning_rule: keep top N by score (N = 15) + any with crib_bonus >= 1.0
- retry_on_empty: hill -> expand key space by +5 keys; transposition -> widen columns by +2

## Logging & Metrics Spec

Artifacts per run:

- attempt_log.jsonl: one line per candidate (stage, rank, score, components, elapsed_ms)
- summary.json: totals (candidates_generated, pruned, final, wall_clock, best_score)
- metrics counters: stage_time_ms, candidates_per_ms, score_distribution (bucketed)

Durability:

- write to ./artifacts/run_timestamp/  (timestamp = UTC ISO string)
- provide flush after each stage to allow mid-run inspection

## Performance Targets

- hill stage: <= 75ms for iteration_budget 250
- transposition stages each: <= 50ms
- masking: <= 30ms
- berlin_clock: <= 25ms
- total trivial end-to-end test: < 300ms
- unit tests aggregate: < 2s

## Micro-Milestones

- [x] Negative candidate pruning logic test.
- [x] Pattern bonus metric test (BERLIN before CLOCK ordering).
- [x] Parallel hill variant metadata test.
- [x] Composite pipeline sample dry-run (scripts/run_pipeline_sample.py).
- [x] Artifact directory creation + summary writer.
- [ ] Positional crib bonus test coverage.
- [ ] N-gram fallback simulation test.
- [ ] Artifact CSV export implementation + test.
- [ ] Tuning notebook/script scaffold (parameter sweep).
- [ ] Adaptive gating dynamic threshold experiment.

Integration Order (Updated Progress)

1. Extend scoring (real n-gram + enhanced crib bonus) – DONE (extended + pattern bonus).
2. Implement Berlin Clock validator stub – DONE.
3. Build pipeline executor with config + pruning – DONE.
4. Add logging + artifacts summary – DONE.
5. Run trivial end-to-end – DONE.
6. Introduce parallel hill variant generation – DONE.
7. Tuning script scaffold – PENDING.
8. Adaptive gating refinement – PENDING.
9. Artifact CSV export – PENDING.

## Detailed Sequence

1. Hill hypothesis generator: low scope, adds missing branches (key generation + score loop). Define deterministic small key search space so test is stable.
2. Transposition constraint hypothesis: exercise multi-crib positional bonus lines; ensure test seeds cribs and column range to guarantee at least one hit.
3. Berlin clock + optional Vigenère trial: add metadata assertions (shift index, maybe key tried). Keep key list tiny to avoid slow tests.
4. Full K4 end‑to‑end pipeline: integrate all stages on a shortened or mock ciphertext segment for speed; assert diagnostics, fused scores, artifact path creation.
5. Scoring loader fallbacks: simulate missing n-gram files or configs to trigger fallback paths; assert default scores loaded correctly.

Considerations:

- Make hypothesis functions pure and injectable (accept ciphertext, params) for easy test control.
- Limit search spaces to keep runtime fast (<0.5s per test).
- Use fixtures for crib sets and sample ciphertext.
- Add coverage for failure/empty-return branches with a second negative test (e.g., no valid Hill keys).
- Ensure artifact writing mocked or directed to a temp directory for deterministic cleanup.

Next step after these: target remaining scoring loader fallbacks with simulated missing files/config.

## Mapping

- Items 1–4 above correspond to Core items 1–4.
- Item 5 aligns with Core item 5.
- End-to-end validations (Sequence 4) plus tiny sample cover Core item 6.
- Parallel stub (Core 7) is pending after sequence tasks.
- Tuning script (Core 8) follows once baseline tests pass.

## CLOSING UP

Update primary MD files across the repo for clarity on new pipeline architecture, stage interfaces, scoring components, and artifact logging.

Ensure all new code is PEP8 compliant; run pre-commit hooks and autofixers as needed.
