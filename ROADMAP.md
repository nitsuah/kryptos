
# 🗺️ Kryptos Roadmap

Last Updated: 2026-05-25
Next Review: 2026-06-25


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

## Q3 2026: K4 Structural Attack + Infrastructure (Completed) ✅

- [x] Keystream validation utility (EAST+NORTHEAST lock, Vigenère shift computation)
- [x] Inverse transposition sweep (all grid geometries, ENE diagonal, permutation inversion)
- [x] Keyed alphabet realignment (KRYPTOS, PALIMPSEST, ABSCISSA)
- [x] Full composite parameter sweep (alphabets × grids × angles × clock states)
- [x] InstructionalScorer (vocabulary, Levenshtein, entropy)
- [x] Eureka capture protocol (4-crib match, breakthrough snapshot, halt)
- [x] CONTRIBUTING.md quick-start code index bugfixes
- [x] Sections-decrypt CLI command for K1/K2/K3
- [x] Structured JSON output for section verification
- [x] Section API end-to-end regression harness
- [x] Alphabet auto-selection defaulted in CLI and orchestrators
- [x] Transposition plaintext extraction fix in campaign orchestrator
- [x] Robust autonomous NLP dependency handling (spaCy/NLTK/transformers optional)
- [x] Objective-to-evidence scorecard and evidence gate
- [x] Fresh-environment autonomous smoke validation gate
- [x] The composite sweep and all attack modules are validated by tests and CI. No simultaneous 4-crib match has been found as of this release; null results are documented with full provenance.

### Q3 Definition of Done
- [x] All K4-ATTACK-1 through K4-ATTACK-7 and infrastructure/CLI items implemented and passing tests
- [x] The composite sweep has run on at least one full 720-state clock enumeration × 3 grids × 3 alphabets
- [x] No simultaneous 4-crib match found → documented with artifact evidence
- [x] If a match IS found → `K4_BREAKTHROUGH_SNAPSHOT.md` exists with full parameter trace


## Q4 2026: Extended Search & Adaptive Strategy 🧪

### 1. 3-Layer Composite Attacks
- [ ] Expand to 3-layer composite attacks (substitution → transposition → second substitution layer)
    - [ ] Design and implement pipeline support for 3-stage attack chains
    - [ ] Validate on K1/K2/K3 before K4 application

### 2. Fractionating Ciphers
- [ ] Implement fractionating ciphers (ADFGVX, Nihilist) as identified gap from 30-year coverage analysis
    - [ ] Integrate ADFGVX and Nihilist modules into pipeline
    - [ ] Add test vectors and validation harness

### 3. Adaptive/ML-Driven Strategies
- [ ] Evaluate adaptive strategy selection from historical campaign outcomes
- [ ] Introduce adaptive solver configuration layer
    - [ ] Prototype ML-driven prioritization of attack patterns
    - [ ] Use campaign logs to inform next-run parameter selection

### 4. Visualization & Coverage Intelligence
- [ ] Add coverage-guided visualization for oversaturated vs unexplored regions
    - [ ] Build dashboard or CLI tool for campaign/keyspace visualization

### 5. Cross-Run Memory & Reliability Gates
- [ ] Expand cross-run memory heuristics
- [ ] K2/K3 reliability gates under deterministic harnesses

### 6. Ongoing
- [ ] Run quarterly objective-pruning review using measured KPI deltas
- [ ] Phase 6 Remaining Workstreams
    - [ ] Learning and adaptation loop hardening: adaptive solver config, failure-pattern suppression, strategy re-weighting
    - [ ] Search-space intelligence: transposition and Hill dedupe integration plus coverage-guided prioritization
    - [ ] Composite chain strategy quality: chain ordering priorities, early-stop rules, replayable provenance
    - [ ] Validation expansion: autonomous K1/K2/K3 controls, edge/adversarial coverage improvements
    - [ ] Production hardening: remove residual deprecated execution paths


## Q1 2027 and Beyond: Final Push & Post-Solution Analysis 🎯

- [ ] Add a GUI/cli dashboard for real-time campaign monitoring, evidence review, and dynamic reprioritization
    - [ ] K1–K3 Decoder: input ciphertext + key → plaintext with marker annotations and instructions on how it was encoded and how we hack it
    - [ ] K4 Attack Dashboard: real-time view of campaign progress, scoring breakdowns, and evidence artifacts
    - [ ] Vault - a basic encrypt/decrypt interface for demonstrating different stored concepts of encryption and decryption (e.g. transposition, Vigenère shifts, fractionating ciphers). showing how each tool in our toolbox works.
- [ ] Add Database and interaction API for storing data about keys, plaintexts, attempts, and provenances in a structured way for easier querying and analysis.
- [ ] Post-solution analysis and documentation: once the solution is found, conduct a thorough analysis of the attack path, key insights, and lessons learned; document these in a comprehensive report and update the README and other docs to reflect the solution narrative and its implications for cryptanalysis and later publishing.
- [ ] See `docs/analysis/K4-FRONTEND.md`


## Working Notes
- Active planning is tracked in `ROADMAP.md`, `TASKS.md`, and monthly governance notes in `docs/governance.md`.
- K4 attack context and findings: `docs/analysis/K4_ACTIVE_RESEARCH.md`
- Confirmed keystream analysis: `docs/analysis/K4_KEYSTREAM_ANALYSIS.md`
