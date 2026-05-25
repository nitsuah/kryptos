# Tasks

Last Updated: 2026-05-24 (validation + coverage refresh)

## Done

- [x] Build the modular K4 cryptanalysis toolkit.
- [x] Add extensive test coverage and fast/slow execution partitioning.
- [x] Add provenance logging and candidate artifact generation.
- [x] Add layered CI validation.
- [x] Fix the Docker runtime permission failure for artifact and log output.
  - Completed: 2026-03-27
  - Evidence: `docker run --rm kryptos-devops-check kryptos k4-attempts --label docker-smoke` now writes under the application working tree instead of `site-packages`.
- [x] Add Docker smoke CI workflow.
  - Completed: 2026-03-27
  - Evidence: `.github/workflows/docker-smoke.yml` now builds the image and validates CLI startup.
- [x] Complete Phase 6.2 composite-chain validation.
  - Completed: 2026-04-03
  - Evidence: `src/kryptos/k4/composite.py` now enforces explicit score thresholds and deterministic ordering for V->T and T->V chains; validated by `tests/test_composite_chain_thresholds.py`.
- [x] Wire manifesto checks into planning and PR review cadence.
  - Completed: 2026-04-03
  - Evidence: `.github/pull_request_template.md` now requires manifesto alignment notes (signal/reproducibility/pruning), and `.github/workflows/manifesto-pr-check.yml` enforces section presence for non-draft PRs.
- [x] Raise the effective coverage gate beyond the prior baseline.
  - Completed: 2026-05-24
  - Evidence: `pytest.ini` now enforces `fail_under = 80`; fast suite currently validates at 95% total coverage.


## In Progress

(No active tasks currently marked as in progress)


## Todo

- [ ] Add scalable campaign orchestration with bounded parallel workers.
  - Priority: P2
  - Problem: larger K4 search batches still run too slowly.
  - Acceptance Criteria: bounded parallel execution is reproducible and emits useful telemetry.

- [ ] Consolidate roadmap references between the root roadmap and docs phase plans.
  - Priority: P2
  - Problem: planning sources can still drift.
  - Acceptance Criteria: one canonical roadmap flow is linked from README and docs.

- [ ] Add a lightweight monthly governance review note in docs.
  - Priority: P3
  - Problem: lessons and retired hypotheses are not yet captured on a regular cadence.
  - Acceptance Criteria: one recurring section tracks what was promoted, what was retired, and why.

### Recurring Governance Review
- [ ] Add/update a section in docs/governance.md each month summarizing:
  - What was promoted to active research
  - What hypotheses were retired (and why)
  - Lessons learned and next steps
