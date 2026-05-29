# Governance and Maintenance Notes

_Last updated: 2026-05-25_


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
