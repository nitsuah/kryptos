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

## Closing tracked work

week-sotu and vigil read `docs/TASKS.md` from `main`, so an item left unmarked keeps showing as open work. A PR that finishes a tracked item closes it in the same PR, in this order:

1. Finish the code and tests.
2. Before the **last** push, update the docs in the same branch: mark the `docs/TASKS.md` item `- [x]` with a one-line `Done <date>: <what>` note (or record partial progress; to cite the PR number, open the PR as a draft first and add it in this commit). If the `docs/TASKS.md` footer says finished items are removed rather than ticked, remove it and condense it into `docs/CHANGELOG.md` / `docs/FEATURES.md` instead. Tick or condense the matching `docs/ROADMAP.md` line, add a `docs/CHANGELOG.md` Unreleased line, and fix `README.md` / `docs/FEATURES.md` if the change alters what they claim.
3. Commit and push, then open the PR. Say in its description which items it closes (the PR template has a slot for it).
4. **Pre-merge check**, next to CI and review threads: `git diff origin/main...HEAD --stat` must include the tracking docs whenever the PR completes a tracked item. If it doesn't, add the docs commit before merging. Never merge first and "follow up with a docs PR"; that's how stash#158/#159 and avatar#35 left finished work open (2026-09-30).

**A docs-only status PR changes status, nothing else.** When you do have to close items after the fact, touch only the lines for the items you cite (tick, `Done` note, PR link). Don't add, reword, reorder or delete other items, and don't regenerate the file from a template.
