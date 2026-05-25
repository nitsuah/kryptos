
# 🗺️ Kryptos Roadmap

Last Updated: 2026-05-24 (Phase 6/7 implementation audit)
Next Review: 2026-06-01


## Q1 2026: Foundation (Completed) 🚀
- [x] Deliver the modular K4 analysis toolkit and composite scoring pipeline
- [x] Add broad automated test coverage with fast and slow partitions
- [x] Add provenance, attempt logging, and repeatable scoring utilities
- [x] Add segmented CI validation


## Q2 2026: Coverage & Validation (IN PROGRESS) 🏗️
- [x] Fix the container runtime write-permission path
- [x] Complete Phase 6.2 composite validation
- [x] Wire manifesto alignment checks into PR cadence (signal, reproducibility, pruning)
- [x] Improve targeted coverage in low-coverage modules and raise the CI test coverage gate for these modules accordingly
- [x] Implement composite-chain execution support (`V→T`, `T→V`) plus chain hypothesis classes
- [x] Add cross-run key-memory primitives (`SearchSpaceTracker` tried-key persistence + `skip_tried` path)


## Q3 2026: Scaling & Triage (Planned) 🤖
- [ ] Launch the extended K4 campaign with controlled parallelization
- [ ] Improve throughput and reproducibility reporting
- [ ] Add operator-grade result triage support
- [ ] Add first-class section tire-kick CLI flow (`sections-decrypt`) for K1/K2/K3 with config-backed inputs
- [ ] Add structured JSON output mode for section-level verification workflows
- [ ] Add section-level end-to-end regression harness to prevent API wrapper drift
- [ ] Wire alphabet auto-selection (`try_all_alphabets`) into runtime orchestrators (`ops`, `k4_campaign`) with deterministic tests
- [ ] Fix transposition plaintext extraction in `pipeline/k4_campaign.py` (currently score/permutation computed but plaintext passthrough remains)
- [ ] Make autonomous NLP dependency robust in CI/dev (bootstrap `en_core_web_sm` or provide tested fallback path)

## Q4 2026: Exploration (Exploratory) 🧪
- [ ] Expand cross-run memory heuristics
- [ ] Evaluate adaptive strategy selection from historical campaign outcomes
- [ ] Introduce adaptive solver configuration layer (historical Phase 6 objective, not yet implemented)
- [ ] Add coverage-guided visualization/workflow for oversaturated vs unexplored regions
- [ ] Phase 6 Remaining Workstreams (Consolidated)
    - [ ] Learning and adaptation loop hardening: adaptive solver config, failure-pattern suppression, and strategy re-weighting from observed outcomes
    - [ ] Search-space intelligence: transposition and Hill dedupe integration plus coverage-guided unexplored-region prioritization
    - [ ] K2/K3 reliability gates: K2 alphabet auto-selection reliability and K3 transposition reliability targets under deterministic harnesses
    - [ ] Composite chain strategy quality: chain ordering priorities, early-stop rules, and replayable provenance across multi-stage hypotheses
    - [ ] Validation expansion: autonomous K1/K2/K3 controls, edge/adversarial coverage, and critical-module coverage improvements
    - [ ] Production hardening: remove residual placeholder/deprecated execution paths and improve bounded performance under sustained runs

## Working Notes
- Active planning is tracked in `ROADMAP.md` and `TASKS.md` only.
