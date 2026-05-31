# Tasks

Last Updated: 2026-05-31


## Todo

### K4 Attack — Untested Vectors (circle back before wider UI work)

> These attacks were identified during doc review as genuinely not-yet-run. All prior Q3/Q4 work produced null results; these are the remaining untested angles. See `docs/analysis/K4_ACTIVE_RESEARCH.md` attack queue for full detail.

- [ ] **Clock → Hill 2×2 invertibility pre-filter**: For each of 720 clock states, form a 2×2 matrix from the first 4 lamp values, filter to the ~100 that are invertible mod 26, apply Hill 2×2 decryption to K4 with those matrices, validate EAST+NORTHEAST. Never run — clock and Hill have only been tested independently.
- [ ] **4-char clock key → Vigenère with NORTHEAST anchor**: Derive a 4-char Vigenère key from each clock state (not the full shift sequence), test against K4 with `positional_crib_bonus` gating on NORTHEAST at position 26. Several clock→4-char encoding schemes to try.
- [ ] **Non-standard Berlin Clock encodings**: Test sub-row encodings (5-hour row only, top 2 rows only, minute rows only, row values as keyed-alphabet offset) as Vigenère keys. Current sweep only uses `full_berlin_clock_shifts` (all 4 rows concatenated).
- [ ] **Berlin Clock lamp counts as transposition column widths**: Use lamp values (e.g. [4,3,11,4] at 23:59) as column widths for a 4-round columnar transposition, not Vigenère shifts. Mentioned in K4-T1.md but not run.
- [ ] **Beaufort cipher sweep**: `kryptos.k4.beaufort` is implemented but no systematic sweep against K4 has run. Quick pass with key candidates: KRYPTOS, PALIMPSEST, BERLIN, CLOCK, ABSCISSA.

# Q1 2027: Final Push & Post-Solution Analysis

### Phase 1: Dashboard & UI
- Implement real-time campaign monitoring dashboard (CLI/GUI)
- Build K1–K3 Decoder: input ciphertext + key → annotated plaintext, with encoding/hacking instructions
- Develop K4 Attack Dashboard: live campaign progress, scoring breakdowns, evidence artifact viewer
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
