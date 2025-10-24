--- title: Documentation Index version: 2025-10-24 categories:
  - overview
  - strategy
  - operations
  - tuning
  - autopilot
  - performance
  - architecture
  - debt
  - archive
---

# Kryptos Documentation Index

This index consolidates markdown files under `docs/` into thematic categories and defines a breadcrumb convention for
navigation. Each active doc should begin with a compact breadcrumb line:

`Breadcrumb: Overview > Roadmap > (this page)`

Use `>` separators; keep <=3 segments. Link the previous segment siblings where helpful.

## Categories

### Overview
- `README_CORE.md` (in-depth project overview)
- `ROADMAP.md` (milestones)
- `10KFT.md` (high-level aerial view)

### Strategy
- `K4_STRATEGY.md` (deep technical notes for K4)
- `AUTOPILOT.md` (autopilot / SPY / OPS flow)

### Operations & Tuning
- `EXPERIMENTAL_TOOLING.md` (inventory)
- `ARCHIVED_SCRIPTS.md` (script disposition)
- `LOGGING.md` (logging guidelines)
- `PERF.md` (performance & profiling plan)
- `RESIDUAL_WRITE_SCAN.md` (filesystem hygiene report)

### Architecture & Reorg
- `REORG.md` (wrapper & migration policy)
- `TECHDEBT.md` (cleanup plan & phases)
- `MASTER_AGENT_PROMPT.md` (automation / maintenance agent instructions)

### Archive
- `archive/INDEX.md` (daily snapshots index)
- `archive/*` (dated plan/decision files)
- `sources/*` (reference source material)

## Breadcrumb Conventions

Add at top of each active (non-archived) doc beneath any front-matter:

`Breadcrumb: <Category> > <Subcategory/Doc Family> > <Document Title>`

Examples: `Breadcrumb: Overview > Roadmap > Roadmap` `Breadcrumb: Strategy > K4 > K4 Strategy` `Breadcrumb: Architecture
> Reorg > Wrapper Policy`

## Lifecycle & Duplication Policy

1. A single canonical doc per subject (e.g., roadmap, strategy, tech debt). Older versions move to `archive/`. 2.
Planning docs more than 7 days old archived (`archive/YYYY-MM-DD.md`) with index update. 3. Add `Last updated:`
timestamp at end of each active doc. 4. Use `INDEX.md` to surface new docs; update categories when adding or removing.

## Pending Improvements

- Add DEPRECATIONS.md capturing removal timelines (demo wrappers, legacy APIs).
- Add API_REFERENCE.md summarizing public package surface.
- Add CONTRIBUTING.md enhancements linking logging, paths, and provenance hash guidelines.
- Create test ensuring each non-archived doc has a breadcrumb line.

## Maintenance Checklist (Weekly)

- [ ] Archive stale plan/strategy variants.
- [ ] Verify breadcrumbs present & accurate.
- [ ] Update ROADMAP milestones statuses.
- [ ] Sync TECHDEBT high-impact list with current TODOs.
- [ ] Regenerate RESIDUAL_WRITE_SCAN.md.
- [ ] Add new categories if scope expands.

Last updated: 2025-10-24T00:58Z
