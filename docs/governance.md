# Governance and Maintenance Notes

Breadcrumb: Home > Docs > Governance


_Last updated: 2026-05-30_


## Monthly Governance Review (May 2026 — Q4 Completion)

_Completed: 2026-05-30_

- All Q4 2026 deliverables shipped: S→T→S composite chain, ADFGVX, Nihilist, fuzzy dedup heuristics, keyspace-stats CLI, K1/K2/K3 reliability gates.
- 811 tests passing, 0 failures. No deprecated or TODO markers remain in source.
- ROADMAP.md updated: Q4 marked Completed ✅. Next review scheduled 2026-06-30.
- ADFGVX and Nihilist exposed in `kryptos.k4` public API; pipeline can now discover them by name.
- Eureka early-stop wired into S→T→S chain — consistent with composite_sweep.py halt protocol.
- K1/K2/K3 Sanborn misspellings (IQLUSION, DESPARATLY, UNDERGRUUND) now enforced by deterministic gate tests.


## Monthly Governance Review (June 2026)

- All objectives from the May 2026 review remain validated and in effect.
- Codebase confirmed clean of legacy executor/wrapper code after migration.
- CLI, campaign, and explainability features stable and fully covered by tests.
- Documentation and artifact hygiene maintained; no drift detected.
- No open issues or PRs requiring governance intervention at this time.
- Next review: July 2026 (add/update this section monthly).

## Monthly Governance Review (May 2026)

- All K4-ATTACK, infrastructure, and CLI objectives for Phase 6.3 are complete and validated.
- Legacy executor/wrapper surfaces have been reviewed; no remaining executor.py or wrapper modules in the codebase.
- Autonomous campaign orchestration and robust NLP fallback are now the default, with all dependencies optional.
- Documentation, test, and artifact hygiene are enforced via pre-commit and CI.
- No open issues or PRs requiring governance intervention at this time.
- Next review: June 2026 (add/update this section monthly).

## Governance Policy

- All major architectural or research changes require evidence-backed validation and must be documented in ROADMAP.md and TASKS.md.
- Monthly review notes are to be added/updated in this file and referenced in ROADMAP.md.
- Deprecated or legacy code must be retired promptly after migration is confirmed.
- Community contributions are reviewed according to CONTRIBUTING.md and must meet reproducibility and documentation standards.

---

For historical governance notes, see docs/archive/ and AUDIT files.
In the future this process should fully expand to include more audit coverage of features and functional changes as well as cleanup and refactoring guidance.
Update this doc accordingly to keep improving this repo via ROADMAP and TASKS.