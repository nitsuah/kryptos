# Autonomous Cryptanalysis System

Last Updated: 2026-05-24

## Overview

The autonomous system coordinates long-running K4-oriented experimentation by combining:
- `AutonomousCoordinator` (orchestration loop)
- `OPS` strategic decisioning
- `SPY` linguistic/pattern analysis
- `Q` validation logic
- optional web-intelligence enrichment

Primary implementation entry points:
- `src/kryptos/autonomous_coordinator.py`
- `src/kryptos/agents/ops_director.py`
- `src/kryptos/agents/spy_nlp.py`
- `src/kryptos/agents/spy_web_intel.py`
- `src/kryptos/autopilot.py`

## Runtime Command

```bash
python -m kryptos.cli.main autonomous --max-hours 24 --cycle-interval 5
```

Related CLI options:
- `--max-hours`
- `--max-cycles`
- `--cycle-interval`
- `--ops-cycle`
- `--web-intel-hours`

## State And Artifacts

The coordinator persists state and emits logs under `artifacts/`.

Key paths:
- `artifacts/autonomous_state.json`
- `artifacts/logs/kryptos_*.log`
- `artifacts/logs/progress_*.md`
- `artifacts/intel_cache/` (web-intel cache)

## Dependency Notes

Autonomous NLP paths depend on spaCy model `en_core_web_sm` in this environment.

If missing, install before autonomous runs/tests:

```bash
python -m spacy download en_core_web_sm
```

## Validation Status (Audit Snapshot)

Validated in this audit:
- CLI entrypoint exists and reports `autonomous` command.
- Coordinator module and related agent modules import successfully.
- `tests/test_autonomous_coordinator.py` currently fails in environments missing `en_core_web_sm`.

See root `AUDIT.md` for command output summary and gap tracking.

## Related Docs

- `docs/INDEX.md`
- `docs/reference/API_REFERENCE.md`
- `docs/reference/AGENTS_ARCHITECTURE.md`
- `docs/analysis/K1_2_3_PATTERN_ANALYSIS.md`
- `ROADMAP.md`
- `TASKS.md`
