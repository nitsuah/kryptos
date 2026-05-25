
# 🗺️ Kryptos Roadmap

Last Updated: 2026-05-25
Next Review: 2026-06-08


## Q1 2026: Foundation (Completed) 🚀
- [x] Deliver the modular K4 analysis toolkit and composite scoring pipeline
- [x] Add broad automated test coverage with fast and slow partitions
- [x] Add provenance, attempt logging, and repeatable scoring utilities
- [x] Add segmented CI validation


## Q2 2026: Coverage & Validation (Completed) ✅
- [x] Fix the container runtime write-permission path
- [x] Complete Phase 6.2 composite validation
- [x] Wire manifesto alignment checks into PR cadence (signal, reproducibility, pruning)
- [x] Improve targeted coverage in low-coverage modules and raise the CI test coverage gate
- [x] Implement composite-chain execution support (`V→T`, `T→V`) plus chain hypothesis classes
- [x] Add cross-run key-memory primitives (`SearchSpaceTracker` tried-key persistence + `skip_tried` path)
- [x] Document confirmed period-13 keystream from EAST+NORTHEAST cribs (see `docs/analysis/K4_KEYSTREAM_ANALYSIS.md`)
- [x] Establish active research state doc and attack queue (see `docs/analysis/K4_ACTIVE_RESEARCH.md`)


## Q3 2026: K4 Structural Attack + Infrastructure (IN PROGRESS) 🏗️

### K4 Structural Attack Track (Primary Focus)

These items are directly informed by the confirmed EASTNORTHEAST keystream analysis.
See `docs/analysis/K4_KEYSTREAM_ANALYSIS.md` and `docs/analysis/K4_ACTIVE_RESEARCH.md` for full context.

- [ ] **[K4-ATTACK-1]** Implement keystream validation utility: lock EAST+NORTHEAST at confirmed positions (0-indexed 22–25, 26–34), compute Vigenère-equivalent shifts, verify against any candidate key/transposition
- [ ] **[K4-ATTACK-2]** Implement inverse transposition sweep: test grid geometries (10×10, 7×14, 8×13) with ENE diagonal reading at θ=67.5°; for each permutation, check whether inverting it causes the keystream at EAST+NORTHEAST positions to collapse to a recognizable pattern
- [ ] **[K4-ATTACK-3]** Implement keyed alphabet realignment: re-derive the keystream at positions 22–34 under KRYPTOS, PALIMPSEST, and ABSCISSA keyed alphabets; flag if any result matches a Berlin Clock reading or structured key
- [ ] **[K4-ATTACK-4]** Implement full composite sweep: ~2,700 combinations (3 alphabets × 3 grids × 3 angle variants × ~100 invertible clock states); validate each against EAST+NORTHEAST + BERLIN+CLOCK simultaneously
- [ ] **[K4-ATTACK-5]** Implement `InstructionalScorer`: vocabulary-boosted scoring for cardinal/spatial/measurement/imperative words; Levenshtein ≤1 fuzzy match; integrate as optional scoring component alongside existing quadgram scoring
- [ ] **[K4-ATTACK-6]** Implement Eureka capture protocol: on simultaneous 4-crib match (EAST+NORTHEAST+BERLIN+CLOCK), emit terminal alert, write `K4_BREAKTHROUGH_SNAPSHOT.md`, halt campaign
- [ ] **[K4-ATTACK-7]** Fix position bugs in CONTRIBUTING.md quick-start code: `NORTHEAST: [25]` → `[26]`, `BERLIN: [64]` → `[63]`

### Infrastructure & CLI Track

- [ ] Add first-class `sections-decrypt` CLI command for K1/K2/K3 with config-backed inputs (`--section`, `--from-config`, `--key`, `--json`)
- [ ] Add structured JSON output mode for section verification (`status`, `plaintext_markers`, `input_source` fields)
- [ ] Add section-level end-to-end regression harness to prevent `kryptos.sections` API drift from cipher core
- [ ] Wire alphabet auto-selection (`try_all_alphabets`) into runtime orchestrators (`ops`, `k4_campaign`) with deterministic tests
- [ ] Fix transposition plaintext extraction in `pipeline/k4_campaign.py` (currently returns ciphertext as plaintext)
- [ ] Make autonomous NLP dependency robust in CI/dev (bootstrap `en_core_web_sm` or provide a tested fallback path)
- [ ] Establish objective-to-evidence scorecard for strategic goals (K1-K3 controls, K4 campaign throughput, reproducibility, autonomous stability)
- [ ] Gate strategic claim promotion with reproducible evidence (tests + runtime command + artifact path required)
- [ ] Add fresh-environment autonomous smoke validation gate

### Q3 Definition of Done
- K4-ATTACK-1 through K4-ATTACK-4 are implemented and passing tests
- The composite sweep has run on at least one full 720-state clock enumeration × 3 grids × 3 alphabets
- No simultaneous 4-crib match found → document the null result with artifact evidence
- If a match IS found → `K4_BREAKTHROUGH_SNAPSHOT.md` exists with full parameter trace


## Q4 2026: Extended Search & Adaptive Strategy 🧪
- [ ] Expand to 3-layer composite attacks (substitution → transposition → second substitution layer)
- [ ] Implement fractionating ciphers (ADFGVX, Nihilist) as identified gap from 30-year coverage analysis
- [ ] Expand cross-run memory heuristics
- [ ] Evaluate adaptive strategy selection from historical campaign outcomes
- [ ] Introduce adaptive solver configuration layer
- [ ] Add coverage-guided visualization for oversaturated vs unexplored regions
- [ ] Run quarterly objective-pruning review using measured KPI deltas
- [ ] Phase 6 Remaining Workstreams
    - [ ] Learning and adaptation loop hardening: adaptive solver config, failure-pattern suppression, strategy re-weighting
    - [ ] Search-space intelligence: transposition and Hill dedupe integration plus coverage-guided prioritization
    - [ ] K2/K3 reliability gates under deterministic harnesses
    - [ ] Composite chain strategy quality: chain ordering priorities, early-stop rules, replayable provenance
    - [ ] Validation expansion: autonomous K1/K2/K3 controls, edge/adversarial coverage improvements
    - [ ] Production hardening: remove residual deprecated execution paths


## Working Notes
- Active planning is tracked in `ROADMAP.md` and `TASKS.md` only.
- K4 attack context and findings: `docs/analysis/K4_ACTIVE_RESEARCH.md`
- Confirmed keystream analysis: `docs/analysis/K4_KEYSTREAM_ANALYSIS.md`
