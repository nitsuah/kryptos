# Tasks

Last Updated: 2026-05-24 (validation + coverage refresh)

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


## In Progress

- [ ] Execute conservative docs cleanup plan from `AUDIT.md`.
  - Priority: P2
  - Constraint: no speculative information or theory removals or archival moves without explicit approval or concrete evidence to support action.
  - Acceptance Criteria: docs index and planning links are consistent with active versus historical intent.


## Todo

- [ ] Add scalable campaign orchestration with bounded parallel workers.
  - Priority: P2
  - Problem: larger K4 search batches still run too slowly.
  - Acceptance Criteria: bounded parallel execution is reproducible and emits useful telemetry.

- [ ] Consolidate roadmap references between the root roadmap and docs phase plans.
  - Priority: P2
  - Problem: planning sources can still drift.
  - Acceptance Criteria: one canonical roadmap flow is linked from README and docs.

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
