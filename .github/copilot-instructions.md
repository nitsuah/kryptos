# Kryptos Copilot Instructions

## Purpose

Kryptos is a research toolkit for analyzing Kryptos ciphertexts, with active emphasis on robust infrastructure,
reproducible workflows, and iterative K4-oriented experimentation.

Use this file as a concise operating guide. For changing status, priorities, and metrics, always defer to
`ROADMAP.md`, `TASKS.md`, and `AUDIT.md`.

## Source Of Truth

- Project status and milestones: `ROADMAP.md`
- Active work queue and completed decisions: `TASKS.md`
- Documentation inventory and cleanup ledger: `AUDIT.md`
- Contributor process, operating standards, and quickstart: `CONTRIBUTING.md`
- Canonical docs navigation: `docs/INDEX.md`

## Architecture Constraints

1. Pipeline-first design
- Compose cryptanalysis through stage factories in `src/kryptos/k4/pipeline.py`.
- Stages return `StageResult` objects; do not mutate candidate objects in place.

2. Provenance is mandatory
- Preserve attack lineage and metadata through the full flow.
- Use provenance utilities in `src/kryptos/provenance/` and deduplicate before writing large attempt logs.

3. Scoring semantics
- Scores are negative log-likelihood style values where less negative is better.
- Validate score behavior with existing scoring helpers instead of introducing ad-hoc scale changes.

4. Agent orchestration boundaries
- Coordination and autonomous loops are centered in `src/kryptos/autonomous_coordinator.py` and related agent modules.
- Keep message contracts explicit and backward compatible.

## Editing Expectations

- Prefer small, targeted changes over broad rewrites.
- Keep imports explicit; avoid wildcard imports.
- Use dataclasses and protocols where they match existing architecture patterns.
- Do not add files that shadow stdlib module names (for example: `logging.py`, `collections.py`, `typing.py`).

## Testing Workflow

- Default fast validation:
    - `pytest tests/ -m "not slow" -v`
- Full validation when requested or before merge-critical changes:
    - `pytest tests/ -v`
- Focused module runs for iteration speed:
    - `pytest tests/test_k4_pipeline.py -v`

Use deterministic commands and include reproducibility notes in PRs when behavior changes.

## CLI And Runtime Notes

- CLI entry point: `src/kryptos/cli/main.py`
- Artifacts and runtime outputs live under `artifacts/`.
- Prefer repository scripts and documented commands over one-off local procedures.

## Docs Hygiene Rules

- Do not hardcode volatile counts, percentages, or dated status snapshots in this file.
- When metrics or priorities change, update canonical docs (`ROADMAP.md`, `TASKS.md`, `AUDIT.md`) instead of embedding
    drift-prone values here.
- Keep speculative K4 theory docs active when they are part of analysis workflows; avoid archiving active research as
    historical pointer-only content.

## Quick Pointers

- Pipeline: `src/kryptos/k4/pipeline.py`
- Composite scoring: `src/kryptos/k4/composite.py`
- Scoring internals: `src/kryptos/k4/scoring.py`
- OPS agent execution: `src/kryptos/agents/ops.py`
- Agent architecture reference: `docs/reference/AGENTS_ARCHITECTURE.md`
- API reference: `docs/reference/API_REFERENCE.md`
- K1/K2/K3 analysis patterns: `docs/analysis/K1_2_3_PATTERN_ANALYSIS.md`

Keep this document short and stable.
