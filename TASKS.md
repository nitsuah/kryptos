# Tasks

Last Updated: 2026-03-27

## Done

- [x] Build the modular K4 cryptanalysis toolkit.
- [x] Add extensive test coverage and fast/slow execution partitioning.
- [x] Add provenance logging and candidate artifact generation.
- [x] Add layered CI validation.

## In Progress

- [ ] Fix the Docker runtime permission failure for artifact and log output.
  - Priority: P0
  - Problem: the container still hits a `PermissionError` on the current artifact path.
  - Acceptance Criteria: the container starts and writes to a writable application-owned location.

- [ ] Complete Phase 6.2 composite-chain validation.
  - Priority: P1
  - Problem: composite validation thresholds and reporting consistency are still incomplete.
  - Acceptance Criteria: V->T and T->V flows run with explicit thresholds and deterministic outputs.

## Todo

- [ ] Raise the effective coverage gate beyond the current baseline.
  - Priority: P1
  - Problem: the current 60 percent gate leaves too much room for regression.
  - Acceptance Criteria: targeted tests land and the CI minimum rises.

- [ ] Add scalable campaign orchestration with bounded parallel workers.
  - Priority: P2
  - Problem: larger K4 search batches still run too slowly.
  - Acceptance Criteria: bounded parallel execution is reproducible and emits useful telemetry.

- [ ] Consolidate roadmap references between the root roadmap and docs phase plans.
  - Priority: P2
  - Problem: planning sources can still drift.
  - Acceptance Criteria: one canonical roadmap flow is linked from README and docs.

