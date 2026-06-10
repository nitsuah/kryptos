# Tasks

Last Updated: 2026-06-09


## Todo

# Q1 2027: Final Push & Post-Solution Analysis

### Phase 1: Dashboard & UI
- Implement real-time campaign monitoring dashboard (CLI/GUI)
- Build K1–K3 Decoder: input ciphertext + key → annotated plaintext, with encoding/hacking instructions
- Develop K4 Attack Dashboard: live campaign progress, scoring breakdowns, evidence artifact viewer, visual fingerprint map of attack vectors plausible vs. covered vs. unknown

- Create Vault: demo encrypt/decrypt interface for all supported ciphers

### Phase 2: Data & API
- Integrate database (e.g., neon) for storing keys, plaintexts, attempts, provenance
- Develop API endpoints for querying and managing cryptanalysis data

### Phase 3: Post-Solution Analysis
- Analyze and document attack path, key insights, and lessons learned after solution
- Write comprehensive report on solution narrative and cryptanalytic implications
- Update README and documentation to reflect solution and research outcomes

### Phase 4: Misc/Supporting
- Update docs/analysis/K4-FRONTEND.md for frontend/dashboard integration
- Ensure all new features have test coverage and artifact logging


## In Progress

## Done

### K4 Attack — Untested Vectors (PR #83, merged)

- [x] **Clock → Hill 2×2 invertibility pre-filter** — `kryptos.k4.clock_hill_attack.run_clock_hill_attack`. Null result.
- [x] **4-char clock key → Vigenère with NORTHEAST anchor** — `kryptos.k4.clock_hill_attack.run_clock_vigenere_attack`. Null result.
- [x] **Non-standard Berlin Clock sub-row encodings** — `kryptos.k4.clock_subrow_attack.run_clock_subrow_attack`. Null result.
- [x] **Berlin Clock lamp counts as transposition column widths** — `kryptos.k4.clock_subrow_attack.run_clock_transposition_attack`. Null result.
- [x] **Beaufort cipher sweep** — `kryptos.k4.beaufort_sweep.run_beaufort_sweep`. Null result.
