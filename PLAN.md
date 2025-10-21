# Plan for Tomorrow - 2025-10-21

## Core Tomorrow Plan (Checklist)

- [ ] 1. Define stage interface spec (inputs/outputs) and verify factory functions.
- [ ] 2. Add unit tests for each stage.
- [ ] 3. Implement/verify scoring/fitness (frequency + crib + clock pattern).
- [ ] 4. Create initial pipeline config (ordering, iteration counts, adaptive thresholds).
- [ ] 5. Validate logging persistence on sample attempt.
- [ ] 6. Run tiny end-to-end sample with trivial cipher.
- [ ] 7. Add parallel/batch execution stub.
- [ ] 8. Prepare tuning script/notebook for hill climb and transposition parameters.

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
- [x] Provide pure function score_candidate(text, meta, weights).
- [ ] Add fallback path when n-gram data missing (use uniform frequencies). -> EXTEND with real file loader + caching

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
- write to ./artifacts/run_<timestamp>/
- provide flush after each stage to allow mid-run inspection

## Performance Targets
- hill stage: <= 75ms for iteration_budget 250
- transposition stages each: <= 50ms
- masking: <= 30ms
- berlin_clock: <= 25ms
- total trivial end-to-end test: < 300ms
- unit tests aggregate: < 2s

## Micro-Milestones

- [x] Complete negative candidate test.
- [ ] Integrate real n-gram loader (file + cache).
- [ ] Add crib positional bonus logic (positional weights).
- [ ] Add berlin clock pattern validator stub (structure parse).
- [ ] Wire first composite pipeline dry-run.
- [ ] Implement artifact directory creation + summary writer.
- [ ] Add parallel stub (thread pool) for hill variants.
- [ ] Tuning notebook/script scaffold (parameter sweep).

## Integration Order

1. Extend scoring (real n-gram + enhanced crib bonus).
2. Implement berlin clock validator stub.
3. Build pipeline executor with config + pruning.
4. Add logging + artifacts summary.
5. Run trivial end-to-end.
6. Introduce parallel hill variant generation.
7. Tuning script scaffold.

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
