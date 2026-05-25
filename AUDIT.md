# Kryptos Repository Audit

Working audit for the documentation tree, planning docs, and the main feature map.

Status: living draft
Last updated: 2026-05-24

## Purpose

This audit records what each document is for, how it relates to the implemented feature set, and whether it should stay active, stay as reference, or be treated as historical/archive material.

It is intentionally conservative about removal. A document stays in place unless there is clear evidence that it is duplicated, obsolete, or superseded.

## Repository Summary

Kryptos is a Python cryptanalysis toolkit focused on the Kryptos sculpture puzzle, with a heavy emphasis on reproducibility, provenance, and layered cipher search.

The implemented system currently covers:

- K1 and K2 Vigenère recovery with deterministic full success on known ciphertexts.
- K3 transposition solving with probabilistic simulated annealing and validated performance bands.
- Hill cipher search and constraint stages.
- Composite multi-stage pipeline orchestration.
- Scoring, provenance logging, search-space tracking, and candidate reporting.
- Autonomous orchestration through SPY / OPS / Q agents.

## Documentation Classification

- Active: current user-facing, operational, or reference documentation.
- Reference: stable factual or policy material.
- Archive: historical snapshots that should not be treated as the current source of truth.
- Speculative: live theory, research, or hypothesis material that may still change.
- Duplicate: content that substantially repeats another doc and should be consolidated only if the owning source agrees.

## Feature Map

The strongest feature-to-doc links are:

- K1/K2 validation: [docs/analysis/K1_K2_VALIDATION_RESULTS.md](docs/analysis/K1_K2_VALIDATION_RESULTS.md)
- K3 validation: [docs/analysis/K3_VALIDATION_RESULTS.md](docs/analysis/K3_VALIDATION_RESULTS.md)
- K1-K3 pattern analysis for K4 search: [docs/analysis/K123_PATTERN_ANALYSIS.md](docs/analysis/K123_PATTERN_ANALYSIS.md)
- Classical cipher coverage: [docs/analysis/30_YEAR_GAP_COVERAGE.md](docs/analysis/30_YEAR_GAP_COVERAGE.md)
- Autonomous system architecture: [docs/reference/AUTONOMOUS_SYSTEM.md](docs/reference/AUTONOMOUS_SYSTEM.md)
- Agent architecture: [docs/reference/AGENTS_ARCHITECTURE.md](docs/reference/AGENTS_ARCHITECTURE.md)
- Provenance and memory: [docs/reference/PROVENANCE_SYSTEM_EXPLAINED.md](docs/reference/PROVENANCE_SYSTEM_EXPLAINED.md)
- Public API and CLI: [docs/reference/API_REFERENCE.md](docs/reference/API_REFERENCE.md)
- Operational launch guide: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- Governance and maintenance policy: [docs/MANIFESTO.md](docs/MANIFESTO.md) and [docs/MAINTENANCE_GUIDE.md](docs/MAINTENANCE_GUIDE.md)

## Doc Inventory

### Root-Level Docs

| File | Purpose | Status | Recommended action |
|---|---|---:|---|
| [README.md](README.md) | Front door for the project, features, quick links, and current workflow. | Active | Keep current. |
| [FEATURES.md](FEATURES.md) | Canonical feature inventory of implemented capabilities. | Active | Keep current and reconcile with code quarterly. |
| [ROADMAP.md](ROADMAP.md) | High-level milestones and next-phase planning. | Active | Keep current. |
| [TASKS.md](TASKS.md) | Operational task list and backlog. | Active | Keep current. |
| [METRICS.md](METRICS.md) | Validation, coverage, and performance snapshot. | Active | Keep current and refresh with new runs. |
| [CHANGELOG.md](CHANGELOG.md) | Root project changelog. | Reference | Keep as canonical changelog. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contributor entry point and reading order. | Active | Keep current. |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community conduct policy. | Reference | Keep. |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting and security policy. | Reference | Keep. |

### docs/ Governance and Navigation

| File | Purpose | Status | Recommended action |
|---|---|---:|---|
| [docs/INDEX.md](docs/INDEX.md) | Canonical docs traversal map. | Active | Keep as the main navigation hub. |
| [docs/MANIFESTO.md](docs/MANIFESTO.md) | Project philosophy and decision rubric. | Active | Keep current. |
| [docs/MAINTENANCE_GUIDE.md](docs/MAINTENANCE_GUIDE.md) | Docs/tests/scripts maintenance policy. | Active | Keep current. |
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | Fast launch and operation guide for autonomous mode. | Active | Keep current. |
| [docs/TODO_PHASE_6.md](docs/TODO_PHASE_6.md) | Detailed Phase 6 operational checklist. | Active / planning | Keep for now; reconcile overlap with [TASKS.md](TASKS.md) over time. |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Pointer to the canonical root changelog and docs-local history. | Historical pointer | Keep only if the pointer is still useful; otherwise fold the note into [docs/INDEX.md](docs/INDEX.md). |

### docs/reference/

| File | Purpose | Status | Recommended action |
|---|---|---:|---|
| [docs/reference/API_REFERENCE.md](docs/reference/API_REFERENCE.md) | Stable public Python API and CLI reference. | Active | Keep current. |
| [docs/reference/AUTONOMOUS_SYSTEM.md](docs/reference/AUTONOMOUS_SYSTEM.md) | Autonomy loop, agent coordination, and runtime behavior. | Active | Keep current. |
| [docs/reference/AGENTS_ARCHITECTURE.md](docs/reference/AGENTS_ARCHITECTURE.md) | SPY / OPS / Q architecture reference. | Active | Keep current. |
| [docs/reference/PROVENANCE_SYSTEM_EXPLAINED.md](docs/reference/PROVENANCE_SYSTEM_EXPLAINED.md) | Search-space tracking, dedupe, and provenance explanation. | Active | Keep current. |

### docs/analysis/

| File | Purpose | Status | Recommended action |
|---|---|---:|---|
| [docs/analysis/30_YEAR_GAP_COVERAGE.md](docs/analysis/30_YEAR_GAP_COVERAGE.md) | Classical cipher coverage audit versus the 1990-era attack surface. | Active | Keep current. |
| [docs/analysis/K123_PATTERN_ANALYSIS.md](docs/analysis/K123_PATTERN_ANALYSIS.md) | Pattern and clue analysis from K1-K3 to guide K4 hypotheses. | Active | Keep current. |
| [docs/analysis/K1_K2_VALIDATION_RESULTS.md](docs/analysis/K1_K2_VALIDATION_RESULTS.md) | Monte Carlo validation of K1/K2 recovery. | Active | Keep current. |
| [docs/analysis/K3_VALIDATION_RESULTS.md](docs/analysis/K3_VALIDATION_RESULTS.md) | Monte Carlo validation of K3 solving. | Active | Keep current. |
| [docs/analysis/K4-theories.md](docs/analysis/K4-theories.md) | Live speculative K4 theory document. | Speculative | Keep in place; do not archive without explicit approval. |
| [docs/analysis/k4_clock_cipher_framework.html](docs/analysis/k4_clock_cipher_framework.html) | Rich HTML theory/mockup for clock-based K4 ideas. | Speculative | Keep if it is still used; archive only if a separate copy is preserved and approved. |

### docs/sources/

| File | Purpose | Status | Recommended action |
|---|---|---:|---|
| [docs/sources/SANBORN.md](docs/sources/SANBORN.md) | Working research checklist for Sanborn-based clues. | Active | Keep current. |
| [docs/sources/CLOCK.md](docs/sources/CLOCK.md) | Clock-based hypothesis notes and clue interpretation. | Active | Keep current. |
| [docs/sources/sanborn_timeline.md](docs/sources/sanborn_timeline.md) | Timeline of public Sanborn statements and sources. | Active | Keep current. |
| [docs/sources/sanborn_crib_candidates.txt](docs/sources/sanborn_crib_candidates.txt) | Candidate crib list derived from sources. | Reference | Keep current. |

### docs/archive/

| File | Purpose | Status | Recommended action |
|---|---|---:|---|
| [docs/archive/PHASE_6_ROADMAP.md](docs/archive/PHASE_6_ROADMAP.md) | Snapshot of an older Phase 6 plan. | Archive | Keep archived as historical context. |
| [docs/archive/PHASE_7_PLAN.md](docs/archive/PHASE_7_PLAN.md) | Historical planning snapshot for a later phase. | Archive | Keep archived as historical context. |
| [docs/archive/COMPREHENSIVE_STRUCTURE_AUDIT_2025-10-26.md](docs/archive/COMPREHENSIVE_STRUCTURE_AUDIT_2025-10-26.md) | Historical structure audit. | Archive | Keep archived unless you want to consolidate lessons into MAINTENANCE_GUIDE. |
| [docs/archive/DOCS_AUDIT_2025-01-27.md](docs/archive/DOCS_AUDIT_2025-01-27.md) | Prior documentation audit snapshot. | Archive | Keep archived as prior evidence. |
| [docs/archive/DOCS_CHANGELOG_HISTORY.md](docs/archive/DOCS_CHANGELOG_HISTORY.md) | Historical docs-local changelog notes. | Archive | Keep archived if the history itself is useful; otherwise pointer-only status is enough. |
| [docs/archive/HANDOFF-manifesto-pr-cadence-20260403.md](docs/archive/HANDOFF-manifesto-pr-cadence-20260403.md) | Handoff notes for a prior process change. | Archive | Keep archived as a record. |
| [docs/archive/K4_THEORIES_HISTORY.md](docs/archive/K4_THEORIES_HISTORY.md) | Historical note for older K4 theory material. | Archive | Keep archived as a separate historical pointer. |
| [docs/archive/SCRIPTS_CLEANUP_2025-01-27.md](docs/archive/SCRIPTS_CLEANUP_2025-01-27.md) | Historical script cleanup audit. | Archive | Keep archived as a record. |

## Purpose / No-Purpose Review

Documents that clearly have a purpose now:

- [README.md](README.md), [FEATURES.md](FEATURES.md), [ROADMAP.md](ROADMAP.md), [TASKS.md](TASKS.md), and [METRICS.md](METRICS.md) define what the repo does, what is planned, and how it is measured.
- [docs/INDEX.md](docs/INDEX.md) is the traversal map and should remain the first navigation point.
- [docs/reference/*](docs/reference) documents the operational systems and public surface area.
- [docs/analysis/K1_K2_VALIDATION_RESULTS.md](docs/analysis/K1_K2_VALIDATION_RESULTS.md), [docs/analysis/K3_VALIDATION_RESULTS.md](docs/analysis/K3_VALIDATION_RESULTS.md), and [docs/analysis/30_YEAR_GAP_COVERAGE.md](docs/analysis/30_YEAR_GAP_COVERAGE.md) anchor the repo’s claims in evidence.
- [docs/analysis/K123_PATTERN_ANALYSIS.md](docs/analysis/K123_PATTERN_ANALYSIS.md) is useful because it links known K1-K3 patterns to K4 search strategy.
- [docs/sources/*](docs/sources) captures the research material used to justify cribs and hypotheses.

Documents that are useful but should be treated carefully:

- [docs/TODO_PHASE_6.md](docs/TODO_PHASE_6.md) overlaps with [TASKS.md](TASKS.md) but still contains the detailed operational checklist.
- [docs/analysis/K4-theories.md](docs/analysis/K4-theories.md) is speculative, but that is a legitimate purpose because the repo is doing K4 research.
- [docs/analysis/k4_clock_cipher_framework.html](docs/analysis/k4_clock_cipher_framework.html) is a higher-friction theory artifact; keep only if it is genuinely used for analysis or presentations.

Documents that are historical rather than operational:

- Everything in [docs/archive](docs/archive) should be read as historical context unless a specific note says otherwise.
- [docs/CHANGELOG.md](docs/CHANGELOG.md) currently behaves like a pointer note rather than a true living doc.

## Audit Notes on Feature Coverage

The repository’s feature docs line up with the implementation in the following way:

- K1 and K2 are documented as fully validated and the validation docs support that claim.
- K3 is documented as probabilistic and the validation docs reflect the seed- and parameter-sensitive behavior.
- Hill cipher, pipeline orchestration, scoring, provenance, and autonomous agents are all described in the feature docs and referenced by the reference docs.
- K4 remains research-oriented; the docs should make that distinction explicit rather than treating K4 speculation as production fact.

## Working Recommendations

1. Keep the active and reference docs as the first-class source of truth.
2. Treat archive docs as historical evidence, not current guidance.
3. Keep speculative K4 material visible if it is actively used for hypothesis generation.
4. Reconcile overlapping planning docs only when the owning content has a clear canonical home.
5. Update this audit as docs change, especially after roadmap or validation updates.

## Open Questions

- Should [docs/CHANGELOG.md](docs/CHANGELOG.md) remain as a pointer file, or should it be folded fully into [docs/INDEX.md](docs/INDEX.md)?
- Should [docs/TODO_PHASE_6.md](docs/TODO_PHASE_6.md) stay separate from [TASKS.md](TASKS.md), or should one become the canonical operational backlog?
- Should [docs/analysis/k4_clock_cipher_framework.html](docs/analysis/k4_clock_cipher_framework.html) remain active speculative content, or be copied into a dedicated archive entry with a clearer warning label?
