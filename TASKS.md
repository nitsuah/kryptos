# Tasks

## Done

- [x] Built a modular K4 cryptanalysis toolkit covering Hill, transposition, masking, and scoring workflows.
- [x] Added extensive test suite coverage and split fast vs slow execution paths.
- [x] Added provenance logging and candidate artifact generation.
- [x] Added CI workflows for linting and layered test validation.

## In Progress

- [ ] P0 | Bug | Confidence: High | Fix Docker runtime permission failure for artifact/log output.
  - Problem: Container fails on startup with `PermissionError` when creating `/usr/local/lib/python3.11/site-packages/artifacts`.
  - Impact: Containerized execution path is not operational for autonomous runs.
  - Acceptance Criteria: Container starts and writes artifacts/logs to a writable application-owned path.
  - Dependencies: Dockerfile and runtime path config alignment.

- [ ] P1 | Feature | Confidence: Medium | Complete Phase 6.2 composite-chain validation.
  - Problem: Composite attack orchestration exists but still lacks complete validation thresholds and reporting consistency.
  - Impact: Candidate ranking confidence is lower than needed for production campaigning.
  - Acceptance Criteria: V->T and T->V flows run with explicit thresholds and deterministic validation outputs.
  - Dependencies: Stable runtime artifact path.

## Todo

- [ ] P1 | Reliability | Confidence: Medium | Raise effective coverage gate beyond current baseline.
  - Problem: Coverage gate is intentionally low (60%) to keep CI moving.
  - Impact: Critical modules may regress without sufficient guardrails.
  - Acceptance Criteria: Add targeted tests and raise minimum coverage threshold in CI.
  - Dependencies: Composite validation work.

- [ ] P2 | Feature | Confidence: Medium | Add scalable campaign orchestration with bounded parallel workers.
  - Problem: Current throughput is insufficient for larger K4 search batches.
  - Impact: Slower exploration and delayed hypothesis validation.
  - Acceptance Criteria: Parallel execution mode with reproducible seeds, bounded workers, and performance telemetry.
  - Dependencies: Runtime path and artifact stability.

- [ ] P2 | Docs | Confidence: High | Consolidate roadmap references between root roadmap and docs phase plans.
  - Problem: Multiple roadmap sources can drift.
  - Impact: Planning ambiguity during implementation.
  - Acceptance Criteria: One canonical roadmap flow with clear links from README and docs.
  - Dependencies: None.

