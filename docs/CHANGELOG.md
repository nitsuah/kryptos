# Changelog

> 🧭 [kryptos](../README.md) · [Index](./INDEX.md) · [Features](./FEATURES.md) · [Roadmap](./ROADMAP.md) · [Tasks](./TASKS.md) · **Changelog** · [Metrics](./METRICS.md) <!-- nav -->

All notable changes to the KRYPTOS project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Changed

- Agent instructions (`.github/copilot-instructions.md`) now require closing tracked work in the same PR: update `docs/TASKS.md`, `docs/ROADMAP.md` and this changelog before the last push, and confirm `git diff origin/main...HEAD --stat` includes them before merge; extended `.github/pull_request_template.md` with a "Closes TASKS item(s)" checklist.

### Changed (2026-09-30 — dashboard, second pass)

- Nine modules consolidated to five: **K4** (was Overview), **Ledger**, **Attacks** (now includes Jobs), **Lab** (Decoder, ad-hoc decrypt and Vault), **System** (now includes run history and the live log). Old `#jobs`, `#vault`, `#console` etc. links redirect.
- Every module is laid out to fit the viewport with no page scrolling; long lists (ledger families, attack vectors, jobs, tables) scroll inside their own panel. Phones and very short screens stack the panels instead.
- The Mengenlehreuhr lamp clock is replaced by a drawing of the **Weltzeituhr** (the clock Sanborn says BERLIN CLOCK means): a solar-system topper that turns once a minute, the 24-panel drum with the engraved city names read so far, a live hour ring, and the wind-rose mosaic. Starts on Berlin's panel; turns with the arrows or by clicking a panel.
- The teal screens are gone: content now sits on white panels framed in lavender (near-black in dark mode), with tier and crib colours tuned for each.

### Changed (2026-09-30 — dashboard and docs)

- **Dashboard rebuilt as a single page** in the style of the Ghost in the Shell interfaces. The five tabs became nine modules on a ring (Overview, Ledger, Attacks, Jobs, Runs, Console, Decoder, Vault, System). The active module fills the stage, neighbours show as tilted previews, and navigation is by dock, ring dial, arrow keys, swipe or URL hash. It scales from phone to wide monitor, follows the system light/dark setting, and honours reduced motion. Only the active module mounts; shared data is polled once. Design notes: `docs/reference/DASHBOARD.md`.
- New dashboard views for the hypothesis ledger (`GET /api/k4/ledger`) and attack-job history (`GET /api/k4/attacks/jobs`), which had no UI.
- `FRONTIER_VECTORS` statuses: P1–P7 and P11–P20 were still marked `Active` although all have run against K4 with null results; they are now `Null`. P21/P22 are `Complete`. P8–P10 were `Deferred` with "requires implementation" descriptions although Myszkowski, Trifid and the straddling checkerboard were implemented and run (null); corrected.
- README rewritten around where K4 stands; ROADMAP, TASKS, INDEX, FEATURES, METRICS, GOVERN, API_REFERENCE and the analysis docs brought up to date. The unbuilt "Akira" dashboard spec moved to `docs/archive/K4-v2.md`.

### Fixed (2026-09-30)

- The dashboard's K4 visualizer highlighted EAST and NORTHEAST one position too high (22 and 26 instead of 21 and 25), the off-by-one fixed in the backend on 2026-09-02. Crib positions now live in `frontend/src/k4.ts`.
- README pointed at files that don't exist (`data/k4_cipher.txt`, `ask_triumverate.py`, `scripts/dev/migrate_run_artifacts.py`, `kryptos.examples.sections_demo`) and said the only open lead was the compass rose.
- TASKS said no score threshold changed with the new n-gram tables. Three did: the pipeline pruning floor (-560 over 40 letters), the hypothesis pruning floor (-420 over 30 letters) and the composite Eureka snapshot floor (-1300; the old 80 was unreachable). `EurekaSignal` itself is crib-based and unchanged.
- METRICS listed `executor.py` for removal; it no longer exists.

### Added (2026-09-28 — frontier pass)

- `kryptos.k4.frontier_checks` (P22, `kryptos frontier`, API `p22_frontier_checks`): recurrence keys, periodic key + arbitrary mixed alphabet, dial keys, routes along every compass bearing, Hill 4×4 (exhaustive) and 5×5 (11.9M matrices scored), running keys from any English text (direct and after columnar transposition), and `reconstruction_suite`, which tests the published full-plaintext reconstruction against every family. Each check has a positive control.
- `frontier_checks.wide_columnar_scan` (exact search over column orders past brute force; widths 10–14 null), `hill_beam_search` (Hill 5×5 at the alignments exhaustive search can't reach), `vocabulary_phrase_keys`.
- `kryptos.k4.english_model` with English 3- and 4-gram tables built from 8.9M letters of public-domain text (`scripts/data/build_english_ngrams.py`).
- Ledger: 6 new eliminated entries, 3 new statistical entries; the open entries narrowed to what is actually left.

### Found (2026-09-28)

- The n-gram tables the main scorer read (`data/ngrams/{bi,tri,quad}grams.tsv`) were placeholders of about ten entries each. Fixed: `scoring` now loads `english_{2,3,4}grams.tsv`; English vs shuffled-English separation on 97 letters rises from d = 4.2 to 9.4 with no overlap. Rankings from earlier sweeps used the old tables.

### Added (2026-09-28 — second negative-space pass)

- `crib_constraints`: error tolerance (`_min_violations`, `tolerance=` on the columnar/geometry scans) and `tolerance_study()` against shuffled-ciphertext controls; `double_periodic_consistency()` (any two periodic keys, solved over GF(2)/GF(13)); `quagmire4_scan()`; `monoalphabetic_conflicts()`; structural checks in the suite output.
- `kryptos.k4.structural_checks`: output-alphabet eliminations, nulls between the crib blocks, Hill 2×2/3×3, K3-style double rotation, columnar + autokey, columnar + running key, Chaocipher (validated against Byrne's published example).
- Job persistence: `k4_attack_jobs` table, finished jobs saved when `DATABASE_URL` is set, `GET /api/k4/attacks/jobs`.
- `hypothesis_ledger.latest_run()` in `GET /api/k4/ledger`; new ledger entries and tiers.
- `docs/sources/SANBORN_QUOTES.md`: Sanborn's statements with citations.
- `quagmire4_dictionary_scan()`: exact dictionary × dictionary Quagmire IV via a difference-vector index (about 5.4×10¹⁰ pairs in 13 s).
- `kryptos.k4.run_store` + `k4_constraint_runs` table: suite runs stored in Neon; `latest_run` falls back to it.
- `kryptos ledger [--json]`: prints the hypothesis ledger from code.
- P21 is single-flight: a second `POST /api/k4/attacks/run` for `p21_crib_constraints` while one is queued or running returns 409 with the active job id. The suite artifact is written to a temp file and renamed into place.
- Rules in `docs/GOVERN.md`, enforced by tests: every `eliminated` ledger entry needs a positive control; the attack registry must match the dispatcher.

### Fixed (2026-09-28 — second pass)

- `scoring.WORDLIST` was an 18-word fallback because `data/wordlist.txt` never existed; it now loads a 261k-word dictionary (4+ letters). English/random separation 1.55 → 1.91.
- `key_csp.periodic_family_consistency` had no positive control (caught by the new rule); it now takes `ciphertext`/`cribs` and has one.
- Docs overstated the word list's reach ("every sweep leaned on it"); the main scorer uses n-grams.

### Added (2026-09-28 — negative-space pass)

- **P21 crib-constraint engine** (`kryptos.k4.crib_constraints`): tests whole cipher families against the 24 crib key values instead of sampling keys. Every check has a positive-control test. Eliminated over stated ranges: ciphertext/plaintext autokey, linear, progressive and Gronsfeld digit keys; running keys over a sculpture corpus (best 7–8/24, equal to a shuffled control); Quagmire I–III for 231,933 dictionary keyword alphabets (periods ≤ 25); columnar transpositions of width 2–9 and 7,680 geometric mappings composed with a periodic key (periods ≤ 22, both layer orders).
- `kryptos crib-constraints` CLI command and `p21_crib_constraints` API attack.
- `kryptos.k4.hypothesis_ledger` and `GET /api/k4/ledger[?tier=]`: every hypothesis family tagged `eliminated` / `statistical` / `sampled_null` / `open`.
- `docs/analysis/K4_NEGATIVE_SPACE.md`: ranked list of untried or under-tested directions.
- `english-words` (MIT) dependency for the dictionary keyword scan.

### Fixed (2026-09-28)

- `running_key.K3_PLAINTEXT_FULL` contained invented text after character 97; now the real K3 plaintext. P6 used only the first 97 characters, so its result stands.
- `cli/main.py`: removed 136 lines of unreachable duplicate parser code after `return parser`.
- P18 frontier description said 22 crib pairs; there are 24.
- Elonka Dunin and FOIA outreach drafts moved into `docs/TASKS.md` from a retired briefing page.

### Fixed (2026-09-27 — K4 deep-dive audit)

- **K4 IC figures in the docs were wrong.** The overall IC is 0.0361, not ≈0.062. Segment ICs are 0.046/0.046/0.034, not 0.058/0.071/0.062. The "substitution → transposition confirmed" architecture built on them is downgraded to a working hypothesis in `K4_ACTIVE_RESEARCH.md`, `K4_KEYSTREAM_ANALYSIS.md`, ROADMAP and README.
- EAST crib release date: Aug 2020, not 2023.
- "THE COMPASS ROSE IS HERE" was credited to Sanborn's own recovered plaintext in ROADMAP, TASKS and `K4_ACTIVE_RESEARCH.md`. It is solvekryptos.com's reconstruction.
- ROADMAP attributed the 17/20 crib shifts to EAST/NORTHEAST; they come from BERLIN/CLOCK.
- `docs/sources/CLOCK.md`: 148 → 146 city names plus a date-line plate; unsourced claims flagged.
- `key_csp.CRIB_SHIFTS` is derived from `keystream_validator.K4_CRIBS` instead of hand-typed; docstrings said 22 shifts, there are 24.
- Lint: unused imports, duplicate set items in `bigram_constraint.COMMON_ENGLISH_DOUBLETS`.

### Added (2026-09-27)

- `kryptos.k4.ic_profile`: overall/segment IC and a reshuffle significance test for segment spread.
- `key_csp.periodic_family_consistency()`: periods 1–26 are inconsistent with the cribs under Vigenère, Beaufort, Variant Beaufort and KRYPTOS-keyed Quagmire III.
- `keystream_validator.K4_CRIB_RELEASES`: crib ciphertext, release month, venue.
- `tests/functional/test_k4_documented_facts.py`: pins every number above.

### Added (2026-08-29 → 2026-09-03 — K4 Phases 6–8, all null)

- **Phase 6 — Physical/Geometric Pivot** (#192, #193, #194, #196): 24-column geometric permutation front-end, precise WGS84 geodesy (`kryptos.k4.geodesy`), Mengenlehreuhr→Weltzeituhr bearing, Nov 9 1989 clock state, Myszkowski/Trifid, SA substitution search; first real executions of P2/P5/P6; dashboard Pivot Status panel.
- **Phase 7** — shape-changing transpose family, `solar_geometry` (shadow hypothesis), `world_clock_cities` (130/146 names sourced), `cross_vector_consensus`, `overnight_runner`: 2,420,928 candidates, null.
- **Phase 8 follow-ups** — `plaintext_evidence`, `known_plaintext_inversion` (incl. 3,674,160 rectangular-grid permutations), mirrored tableau, `k0_morse_keywords`, `classical_cipher_sweep`, `physical_geometry`, `constraint_chain`: all null.

### Fixed (2026-09)

- `keystream_validator.K4_CRIBS` stored `EAST`/`NORTHEAST` one position too high (22/26 → 21/25); same bug fixed in `key_csp.py` and `clock_hill_attack.py` (found via PR #203 review).
- Broken Docker fast-coverage command in docs (#215).

### Changed (2026-09)

- `k4_attack_routes.py` split into a thin route module plus `k4_jobs.py` (job status store) and `k4_attack_dispatch.py` (attack dispatch table) — no behavior change; covered by new characterization tests in `test_k4_attack_routes.py`.
- Netlify + Render deployment documented; Netlify deploy badge in README (#219, #220); orphaned `.playwright-mcp` artifacts untracked (#221).
- Dependency floors raised: openai ≥3.15, anthropic ≥1.6, uvicorn ≥0.53, transformers ≥5.17, psycopg2-binary (#212–#218).
- Planning docs reset for 2027 (`pmo-ff`): completed ROADMAP phases (1–4, 6, 7) and TASKS Done moved verbatim to `docs/archive/2026-completed-roadmap-and-tasks.md` and summarized in FEATURES; Phase 8 carried into 2027 Q1; plain-text `Breadcrumb:` lines replaced with linked breadcrumb navigation; README docs index added.

### Added

- `docs/analysis/K4_ATTACK_LANDSCAPE.md` — 3D attack fingerprint document: past (all systematically-tested single-layer and 2-layer vectors with evidence), present (working hypotheses, InstructionalScorer, Eureka protocol), and frontier (10 untested directions — P1–P7 active, P8–P10 deferred — with implementation checklists)
- `kryptos serve` command and minimal FastAPI app (`src/kryptos/api/`) exposing `/health`, `/api/rag/status`,
  `POST /api/rag/reindex`, and `GET /api/rag/search` endpoints
- turbovec-backed `ArtifactIndex` (`src/kryptos/rag/`) for semantic search over `artifacts/`, using
  `sentence-transformers` embeddings and a 4-bit quantized `turbovec.IdMapIndex` persisted under `data/turbovec/`

### Changed (2026-08-12 doc refresh)

- `docs/analysis/K4_KEYSTREAM_ANALYSIS.md` — Sections 7.5–7.7 updated from "NOT YET RUN" to confirmed null results; Open Questions section expanded from 7 to 11 items reflecting current frontier
- `docs/analysis/K4_ACTIVE_RESEARCH.md` — Active attack queue rebuilt: completed-attacks table (14 null-result attack sweeps), frontier queue (7 active + 3 deferred vectors), infrastructure status corrected from "Implemented" to "Complete/null result" for all 5 PR-83 attacks
- `docs/ROADMAP.md` — Replaced "Untested K4 Attack Vectors" section with completed-vectors table and new "Frontier K4 Attack Vectors" section (10 total: P1–P7 active, P8–P10 deferred)
- `docs/TASKS.md` — Added Phase 0 (Frontier K4 Attack Planning) with 7 active + 3 deferred implementation tasks (10 total); added CONTRIBUTING.md position-label fix to Phase 3
- `docs/analysis/30_YEAR_GAP_COVERAGE.md` — Beaufort status corrected from ❌ Missing to ✅ Swept (null); Gronsfeld gap impact upgraded to MEDIUM; 3-layer composite gap upgraded to HIGH priority
- `docs/METRICS.md` — Test count corrected from 633 to 829 (AUDIT_2026-06-01 baseline); K4 readiness updated from 7.5/10 to 8.5/10
- `docs/GOVERN.md` — Added July and August 2026 governance review entries
- `docs/INDEX.md` — K4_ATTACK_LANDSCAPE.md added; AUDIT_2026-06-01 added; analysis section reordered most-important-first

## [Phase 6.3] - 2026-05-25

### Added

- Overseer-compliant documentation (ROADMAP.md, TASKS.md, FEATURES.md, METRICS.md, CHANGELOG.md)
- K1/K2/K3 runtime smoke verification command path in maintenance workflow (exact plaintext checks on production entrypoints)
- Phase 6/7 implementation audit tracker (`AUDIT.md`) with code/test evidence matrix and pending gap ledger
- Objective-to-evidence scorecard for strategic goals
- Fresh-environment autonomous smoke test (CI and demo workflows)
- Scalable campaign orchestration with bounded parallel workers
- Sections-decrypt CLI command for K1/K2/K3 with config-backed inputs
- JSON output mode for section verification commands
- Section API end-to-end tests
- Optional explainability mode for section decryptions
- Alphabet auto-selection wired into runtime orchestrators (default enabled)
- Transposition plaintext extraction fix in campaign orchestrator
- Robust autonomous test/runtime NLP dependency handling (spaCy/NLTK/transformers optional)

### Changed

- Documentation structure reorganized for better compliance tracking
- Fast-suite validation baseline updated to 631 passed / 10 skipped / 2 deselected with 95% coverage (2026-05-24)
- Coverage and task planning docs updated to reflect `fail_under = 80` and completed targeted coverage push
- Core planning docs now reflect verified implementation status for composite chains and cross-run key-memory paths
- CLI and orchestrator now default to alphabet auto-selection, with opt-out flag
- All K4-ATTACK-1 through K4-ATTACK-7 completed and documented

### Fixed

- Deprecated UTC timestamp usage migrated from `datetime.utcnow()` to timezone-aware UTC calls in runtime/reporting/example modules
- `runpy` module re-execution warnings reduced in tests by clearing cached module entries before `run_module`
- `PytestReturnNotNoneWarning` removed from `tests/test_spy_v2.py`
- Stale docs links corrected (`K123_PATTERN_ANALYSIS` path drift, archive index entries, and quickstart intel cache paths)
- Transposition plaintext extraction in campaign orchestrator now outputs correct plaintext for all candidate routes
- Autonomous runtime/test no longer fails if NLP dependencies are missing
- CLI runpy warning path clarified and tested (SystemExit expected)

### Removed

- No longer required: config/llm_config.yaml (no such file used or referenced)

## [Phase 6.2] - 2025-11-27 (In Progress)

### In Progress

- Composite attack chains (V→T and T→V)
- Multi-stage validation pipeline integration
- Confidence thresholding system

## [Phase 6.1] - 2025-11-27

### Added

- K1/K2 Monte Carlo validation test suite (100% success rate confirmed)
- K3 comprehensive validation test suite (68-95% period-dependent success)
- `docs/analysis/K1_K2_VALIDATION_RESULTS.md` - Validation results documentation
- `docs/analysis/K3_VALIDATION_RESULTS.md` - K3 validation analysis
- `scripts/README.md` - Script policy and cleanup consolidation
- `AUDIT.md` - Repository-wide documentation audit tracker

### Changed

- Test suite: fast CI runs execute ~524 tests; 10 slow Monte Carlo tests are gated behind `KRYPTOS_RUN_SLOW_MONTE_CARLO`
- Coverage gate adjusted to 60% temporarily to keep CI actionable while we add unit tests
- Updated historical Phase 6 planning docs with measured success rates
- K3 ciphertext corrected to 336 characters

### Fixed

- Fixed OPS placeholder confusion in `agents/ops.py` line 360
- Implemented K4 campaign Vigenère attack (was marked as placeholder)
- Corrected K2 success rate documentation (3.8% → 100%, was deterministic all along)
- Corrected K3 success rate documentation (27% → 68-95%, better than claimed)

### Removed

- 7 redundant K1/K2 debugging scripts after validating functionality in proper tests
- Misleading placeholder comments in implemented code

## [Phase 5] - 2025-10 to 2025-11

### Added

- Simulated annealing solver (30-45% faster than hill-climbing)
- Dictionary scoring system (2.73× discrimination ratio)
- Attack provenance logging with deduplication (`provenance/attack_log.py`, 435 lines)
- Search space coverage tracking (`provenance/search_space.py`, 401 lines)
- Attack generation framework (46 attacks from Q-hints + gaps)
- 4-stage validation pipeline with 96% confidence
- K4 campaign orchestration (2.5 attacks/second throughput)
- Academic documentation (3 comprehensive docs, 3,500+ lines)
- Pipeline profiling with per-stage duration metadata
- Attempt persistence (timestamped JSON logs)
- Validation pipeline (`pipeline/validator.py`, 418 lines)
- K4 campaign executor (`pipeline/k4_campaign.py`, 373 lines)

### Changed

- Code cleanup: removed 3,554 lines of unnecessary code
  - Automated cleanup: -2,877 lines (docstrings, comments, verbose logging) across 65 files
  - Deprecated code removal: -677 lines (unused configs, obsolete tests)
- Test suite expanded to 564 passing tests (100% pass rate)
- Test duration: 5 minutes 5 seconds for full suite

### Fixed

- All linting issues resolved (clean pre-commit status)

## [Phase 4] - 2025-Q4

### Added

- Hill cipher (2×2 and 3×3) implementation
- Frequency analysis and n-gram scoring utilities
- Columnar transposition with partial-score pruning
- Berlin Clock shift hypothesis
- Multi-stage pipeline architecture
- Constraint-based Hill key derivation
- Adaptive transposition search with sampling heuristics
- Masking/null-removal stage
- Weighted multi-stage fusion utilities
- Advanced linguistic metrics (entropy, wordlist hits, trigram analysis)
- Memoized scoring with LRU cache
- Transformation trace and lineage tracking
- K3 double rotational transposition implementation
- 24×14 grid rotation method
- K3 solution validation
- Intentional misspelling preservation (DESPARATLY)
- K2 Vigenère implementation
- Structural padding handling (X and Y separators)
- Geospatial coordinate extraction
- K2 solution validation
- Initial project setup and architecture
- Vigenère cipher with keyed alphabet (KRYPTOSABCDEFGHIJLMNQUVWXZ)
- K1 solution implementation
- Intentional misspelling preservation (IQLUSION)
- Config-driven system (config/config.json)
- Test suite framework
- Basic frequency analysis
- Documentation structure

### Repository

- Initial commit with project structure
- Requirements.txt with dependencies
- README.md with project overview
- LICENSE file

## References

For detailed phase planning and technical documentation, see:

- [ROADMAP.md](./ROADMAP.md) - Current roadmap and phase objectives
- [CONTRIBUTING.md](https://github.com/nitsuah/.github/blob/main/CONTRIBUTING.md) (nitsuah org default) - Active workflow, standards, and quickstart guidance
