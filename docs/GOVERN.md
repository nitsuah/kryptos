# Governance and Maintenance Notes

> 🧭 [kryptos](../README.md) · [Index](./INDEX.md) · [Features](./FEATURES.md) · [Roadmap](./ROADMAP.md) · [Tasks](./TASKS.md) · [Changelog](./CHANGELOG.md) · [Metrics](./METRICS.md) <!-- nav -->

_Last updated: 2026-09-30_


## Monthly Governance Review (September 2026)

_Completed: 2026-09-30_

- **Audit (2026-09-27).** K4's IC in the docs was wrong (≈0.062 claimed, 0.0361 actual), and the "substitution then transposition, confirmed" architecture built on it was downgraded to a working hypothesis. The "THE COMPASS ROSE IS HERE" plaintext was re-attributed to solvekryptos.com's reconstruction. Numbers pinned by `test_k4_documented_facts.py`.
- **Method change (2026-09-28).** Family-level elimination replaced key sampling as the main tool (P21 crib constraints, structural checks, P22 frontier checks). Three new rules below: positive controls for eliminations, ledger tiers, registry/dispatcher sync.
- **Stop doing.** No new sweeps that re-test fixed (permutation, key) pairs under the same structural assumptions; Phase 7's zero cross-vector consensus and the family eliminations make them low-value. Candidate counts are no longer reported as coverage.
- **Scoring fixed.** The main scorer's n-gram tables were placeholders; replaced with real tables and recalibrated thresholds. Rankings stored before 2026-09-28 are suspect (re-score task in TASKS).
- **Docs and UI (2026-09-30).** README rewritten around the current state; the unbuilt "Akira" dashboard spec archived; the dashboard rebuilt as a single page (`docs/reference/DASHBOARD.md`).
- PR #228 merged with CI green and review addressed. No open issues.
- Next review: October 2026.

## Monthly Governance Review (May 2026 — Q4 Completion)

_Completed: 2026-05-30_

- All Q4 2026 deliverables shipped: S→T→S composite chain, ADFGVX, Nihilist, fuzzy dedup heuristics, keyspace-stats CLI, K1/K2/K3 reliability gates.
- 811 tests passing, 0 failures. No deprecated or TODO markers remain in source.
- ROADMAP.md updated: Q4 marked Completed ✅. Next review scheduled 2026-06-30.
- ADFGVX and Nihilist exposed in `kryptos.k4` public API; pipeline can now discover them by name.
- Eureka early-stop wired into S→T→S chain — consistent with composite_sweep.py halt protocol.
- K1/K2/K3 Sanborn misspellings (IQLUSION, DESPARATLY, UNDERGRUUND) now enforced by deterministic gate tests.


## Monthly Governance Review (August 2026)

_Completed: 2026-08-12_

- All five previously-open K4 attack vectors (clock→Hill, 4-char clock→Vigenère, sub-row encodings, lamp-count transposition, Beaufort sweep) confirmed complete with null results. Added to `K4_ACTIVE_RESEARCH.md` completed table.
- `K4_KEYSTREAM_ANALYSIS.md` sections 7.5–7.7 updated from "NOT YET RUN" to confirmed null results; Open Questions section updated — 11 total items (6 resolved, 5 open).
- `K4_ATTACK_LANDSCAPE.md` created — 3D fingerprint covering all past, present, and frontier attack directions.
- `TASKS.md` and `ROADMAP.md` updated with 3-layer composite attacks as next strategic priority.
- Test count updated in `METRICS.md` (829 tests, up from 633 at last metrics update).
- `docs/INDEX.md` updated with new landscape document.
- Deprecated code: `executor.py` remains marked legacy (retiring after migration confirmation); all other deprecated markers clean. No open CI failures, no governance intervention required.
- Next review: September 2026 (add/update this section monthly).

## Monthly Governance Review (July 2026)

_Completed: 2026-07-01_

- All June 2026 deliverables validated and stable.
- Dashboard (Ops Center, Vault, K1–K3 Animated Decoder, Database admin) shipping and serving via single-container FastAPI+React.
- Quagmire I–IV solver and sweep (6,240 combinations) complete; null result. Physical-grid tableau walk complete; null result.
- SA columnar seeding and early-crib locking verified end-to-end with >90% pruning efficiency.
- Benchmark runner and CI job added for throughput tracking.
- No open issues or PRs requiring governance intervention.
- Next review: August 2026 (add/update this section monthly).

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
- **Positive controls for eliminations (2026-09-28).** A cipher family may only be marked `eliminated` in `kryptos.k4.hypothesis_ledger` if its check ships a test that plants a known solution and shows the check finds it. A null result from a check that was never shown to detect a real hit doesn't count. Enforced by `tests/functional/test_k4_ledger.py::test_every_eliminated_entry_has_a_positive_control`.
- **Say how strong a "ruled out" is.** Use the ledger tiers: `eliminated` (exhaustive over a stated range), `statistical` (compared against shuffled-ciphertext controls), `sampled_null` (specific keys tried), `open`. Candidate counts alone are not coverage.
- **Registry and dispatcher stay in sync.** Every runnable entry in `FRONTIER_VECTORS` needs a branch in `k4_attack_dispatch.py`, and vice versa (`test_attack_registry_matches_dispatcher`).

---

For historical governance notes, see docs/archive/ and AUDIT files.
In the future this process should fully expand to include more audit coverage of features and functional changes as well as cleanup and refactoring guidance.
Update this doc accordingly to keep improving this repo via ROADMAP and TASKS.
