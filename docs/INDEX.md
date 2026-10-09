# Kryptos Docs Index

> 🧭 [kryptos](../README.md) · **Index** · [Features](./FEATURES.md) · [Roadmap](./ROADMAP.md) · [Tasks](./TASKS.md) · [Changelog](./CHANGELOG.md) · [Metrics](./METRICS.md) <!-- nav -->

This is the traversal map for humans and AI agents.

## Start Here

- [README.md](../README.md) - Project overview, where K4 stands, quick start
- [analysis/K4_NEGATIVE_SPACE.md](analysis/K4_NEGATIVE_SPACE.md) - The short answer to "what's been ruled out and what's left"; its machine-readable twin is `kryptos ledger` / `GET /api/k4/ledger`
- [ROADMAP.md](ROADMAP.md) - Canonical roadmap and grouped strategic priorities
- [TASKS.md](TASKS.md) - Canonical execution backlog
- [Contributing](https://github.com/nitsuah/.github/blob/main/CONTRIBUTING.md) - Contribution workflow (nitsuah org-wide)

## Reference

- [docs/reference/API_REFERENCE.md](reference/API_REFERENCE.md) - Public Python API, CLI subcommands, HTTP endpoints and Neon tables
- [docs/reference/DASHBOARD.md](reference/DASHBOARD.md) - Dashboard design: the single-page Ghost in the Shell interface, its module ring, and which endpoint each module reads
- [docs/reference/AUTONOMOUS_SYSTEM.md](reference/AUTONOMOUS_SYSTEM.md) - Autonomous agent orchestration
- [docs/reference/AGENTS_ARCHITECTURE.md](reference/AGENTS_ARCHITECTURE.md) - Agent triumvirate design
- [docs/reference/PROVENANCE_SYSTEM_EXPLAINED.md](reference/PROVENANCE_SYSTEM_EXPLAINED.md) - Search-space tracking and provenance
- [CHANGELOG.md](CHANGELOG.md) - Change history and version tracking
- [METRICS.md](METRICS.md) - Project metrics and health snapshot
- [GOVERN.md](GOVERN.md) - Governance and maintenance policy

## Analysis

- [docs/analysis/K4_WORLD_CLOCK_FACE_TRANSCRIPTION.md](analysis/K4_WORLD_CLOCK_FACE_TRANSCRIPTION.md) - Attributed 2017 top/bottom World Clock transcription, provenance, uncertainty, and limitations for per-letter lookup experiments
- [docs/analysis/K4_ACTIVE_RESEARCH.md](analysis/K4_ACTIVE_RESEARCH.md) - **The narrative log for K4: confirmed facts, ruled-out hypotheses, every phase's runs, and open primary-source needs**
- [docs/analysis/K4_NEGATIVE_SPACE.md](analysis/K4_NEGATIVE_SPACE.md) - Eliminated, statistical and sampled-null families with their ranges, the full-reconstruction test, and what is still open, ranked
- [docs/analysis/K4_CAPABILITY_TABLE.md](analysis/K4_CAPABILITY_TABLE.md) - Every K4 attack vector/infrastructure component, status, and real candidate count in one scannable table
- [docs/analysis/K4_KEYSTREAM_ANALYSIS.md](analysis/K4_KEYSTREAM_ANALYSIS.md) - Keystream derivation from the EAST, NORTHEAST, BERLIN and CLOCK cribs, the IC analysis, and what is and isn't established about the layer structure
- [docs/analysis/K4_KEYED_COLUMNAR_FRONTIER.md](analysis/K4_KEYED_COLUMNAR_FRONTIER.md) - Exact crib-gated test of long, clock-derived keyword column orders combined with known K1/K2 keys; bounded nulls and limits
- [docs/analysis/30_YEAR_GAP_COVERAGE.md](analysis/30_YEAR_GAP_COVERAGE.md) - Classical cipher technique coverage assessment (pre-1990 techniques; see doc for current coverage %)
- [docs/analysis/K1_2_3_PATTERN_ANALYSIS.md](analysis/K1_2_3_PATTERN_ANALYSIS.md) - K1-K3 pattern extraction used to guide K4
- [docs/analysis/K1_K2_VALIDATION_RESULTS.md](analysis/K1_K2_VALIDATION_RESULTS.md) - K1/K2 Monte Carlo validation results (100%)
- [docs/analysis/K3_VALIDATION_RESULTS.md](analysis/K3_VALIDATION_RESULTS.md) - K3 SA solver validation results (62–95% seed-dependent)

## Planning

- [ROADMAP.md](ROADMAP.md) - High-level project roadmap
- [TASKS.md](TASKS.md) - Current task backlog

## Historical / Archived

- [docs/archive/2026-completed-roadmap-and-tasks.md](archive/2026-completed-roadmap-and-tasks.md) - Verbatim ROADMAP Phases 1–4/6/7 + TASKS Done, archived in the 2027 planning reset (2026-09-24)
- [docs/archive/AUDIT_2026-06-01.md](archive/AUDIT_2026-06-01.md) - Most recent src/ audit (see doc for test counts)
- [docs/archive/AUDIT_2026-05-24.md](archive/AUDIT_2026-05-24.md)
- [docs/archive/AUDIT_2025-10-26.md](archive/AUDIT_2025-10-26.md)
- [docs/archive/K4_ATTACK_LANDSCAPE.md](archive/K4_ATTACK_LANDSCAPE.md) - Superseded 2026-09-01 by K4_ACTIVE_RESEARCH.md; kept for historical evidence-basis narrative
- [docs/archive/K4-T1.md](archive/K4-T1.md) - Superseded 2026-09-01. Its "2025 Smithsonian Archive"/"K5" premise was flagged unverified/likely-fabricated as of that date — **that flag was wrong**; both are real (see K4_ACTIVE_RESEARCH.md's External Developments section). Its specific mechanism (RIS, ENE routing, Hill 2×2) is still null as originally noted
- [docs/archive/K4-CLOCKS.html](archive/K4-CLOCKS.html) - Superseded 2026-09-01; NORTHEAST position labels are known incorrect (see K4_KEYSTREAM_ANALYSIS.md §1)
- [docs/archive/K4-FRONTEND.md](archive/K4-FRONTEND.md) - Superseded 2026-09-01; describes a SQLite schema that was never built (actual: Neon/Postgres)
- [docs/archive/K4-v2.md](archive/K4-v2.md) - Archived 2026-09-30, never built: the "Akira" CRT dashboard spec, superseded by [reference/DASHBOARD.md](reference/DASHBOARD.md)

## Sources

- [docs/sources/SANBORN.md](sources/SANBORN.md) - Sanborn research checklist and artist-clue strategy
- [docs/sources/SANBORN_QUOTES.md](sources/SANBORN_QUOTES.md) - Sanborn's public statements on K4, with citations and a confidence tier for each
- [docs/sources/CLOCK.md](sources/CLOCK.md) - World Clock / Berlin Clock geographic and cryptographic interpretation

> **DB-backed sources** (query via `source_chunks`, `sanborn_timeline`, `discovered_cribs` tables):
> Smithsonian 2009 oral history transcript, Sanborn public statement timeline, crib candidates with provenance.

## Reading Order

1. README for the high-level picture.
2. This index for navigation.
3. K4_NEGATIVE_SPACE for what's ruled out and what's open.
4. ROADMAP and TASKS for active priorities and the execution queue.
5. GOVERN for the rules (ledger tiers, positive controls) and CONTRIBUTING (nitsuah/.github) for workflow.
6. Reference docs for implementation details.
7. Analysis docs for measured validation and the run-by-run history.

- [K4 Open5 Frontier](./analysis/K4_OPEN5_FRONTIER.md) — bounded diagnostics for the five remaining K4 hypothesis families.
