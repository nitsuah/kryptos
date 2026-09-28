# K4 Negative Space

> 🧭 [kryptos](../../README.md) · [Index](../INDEX.md) · [Features](../FEATURES.md) · [Roadmap](../ROADMAP.md) · [Tasks](../TASKS.md) · [Changelog](../CHANGELOG.md) · [Metrics](../METRICS.md) <!-- nav -->

**Last Updated:** 2026-09-28 (second pass)
**Companion page:** [Kryptos State of Research](https://claude.ai/artifact/PBjhWqNYP5zXCdQb9qfMB3), a readable overview with the coverage map and open to-dos. It replaces the earlier briefing pages (K4 Field Notes, Three Open Leads, Three Moves, K4 Ledger Audit), which are kept for history only.
**Status:** Living document. It records what has *not* been tried, or not tried in a way that settles anything. The machine-readable version is `kryptos.k4.hypothesis_ledger` (`GET /api/k4/ledger`).

---

## Why this doc exists

Phases 1–7 produced millions of null candidates, almost all from one method: fix a transposition and a key, decrypt all 97 letters, score. A null from that method rules out only the exact combinations tried.

The 24 confirmed crib letters support a stronger method. Each crib letter fixes the key value at its position for a given cipher family, so a whole family can be tested at once: does *any* parameter choice reproduce all 24 values? `kryptos.k4.crib_constraints` and `kryptos.k4.structural_checks` do this. Every check has a test that plants a known solution and shows the check finds it (a repo rule since 2026-09-28, see `docs/GOVERN.md`).

| Tier | Meaning |
|------|---------|
| **eliminated** | Exhaustive over the stated range, with a positive control |
| **statistical** | Compared against shuffled-ciphertext controls; K4 behaves like chance |
| **sampled null** | Specific parameters tried and scored; rules out those choices only |
| **open** | Not yet tested in a way that covers the family |

---

## Eliminated (exhaustive over the stated range)

Reproduce with `kryptos crib-constraints` (writes `K4_CRIB_CONSTRAINTS_NULL.json`) or the `p21_crib_constraints` API job.

| Family | Range covered | Result |
|--------|---------------|--------|
| Monoalphabetic, no transposition | any alphabet | 8 of 9 repeated crib letters map to different ciphertext letters |
| Direct periodic key (Vigenère, Beaufort, Variant, Quagmire III KRYPTOS) | periods 1–26 | no period fits |
| Quagmire I / II / III, dictionary keyword alphabets | 231,933 alphabets, periods 1–25 | zero survivors |
| Quagmire IV, Kryptos vocabulary × dictionary | 43 × 231,933, both roles, periods 1–22 | zero survivors |
| Quagmire IV, dictionary × dictionary | 231,933², about 5.4×10¹⁰ pairs, periods 1–22 | zero survivors except 5 chance pairs at period 16 (only 8 constraints), which decrypt to noise |
| Sum of two periodic keys, *any* keywords | every (p1, p2) with p1 + p2 ≤ 24 | linear system unsolvable over GF(2)/GF(13); covers PALIMPSEST + ABSCISSA |
| Ciphertext autokey (+ constant) | lags 1–71, five families | none (lag 72 has two constraints; chance level) |
| Plaintext autokey (+ constant) | lags 1–11 and 31–51 | none; lags 12, 30, 52 have one crib pair, 13–29 and 53–96 none |
| Linear key a·i + b; progressive key K[i mod p] + d·⌊i/p⌋ | all a, b; periods 1–26, all d | none |
| Gronsfeld / Gromark digit keys | 15 Kryptos keyword alphabets | every alphabet needs a shift ≥ 23 |
| Running key from sculpture texts (no transposition) | 22 texts × every alignment × any offset | best 7–8 of 24, equal to a shuffled control |
| Columnar transposition + periodic key, either order | widths 2–9, all column orders, periods 1–22 | zero survivors (width 10 checked to period 20) |
| Phase 6–7 geometric permutations + periodic key, either order | 7,680 mappings, periods 1–22 | zero survivors |
| K3-style double rotation + periodic key, either order | 21,096 layouts (0–11 null pads, all divisor widths, 6 rotations per stage), periods 1–22 | zero survivors |
| Columnar transposition + ciphertext autokey | widths 2–7, every lag with 4+ constraints, every offset | zero survivors |
| Nulls between the crib blocks + periodic key | 1–29 nulls, periods 1–23 | none |
| Hill 2×2 and 3×3, no transposition | every alignment, both directions | no consistent matrix |
| 25-letter and 5–6-letter output ciphers as the last layer | Playfair, Two-Square, Four-Square, 5×5 Bifid, Polybius, ADFGX, ADFGVX; with or without transposition | K4 contains all 26 letters |

Nicodemus (Vigenère by column, then columnar read-out) is the sub-then-transposition case with period = width, so the columnar row covers it.

## Statistical (no signal against controls)

| Family | Range | Result |
|--------|-------|--------|
| Monoalphabetic + transposition | any | IC 0.0361 vs English 0.066 |
| Columnar / geometric + periodic key **allowing 1–2 wrong crib letters** | widths 2–9 and 7,680 geometric, periods 1–22 | near-miss counts inside the control range (columnar 368 vs 249–365; geometric 325 vs 250–430); nothing below period 16 within 2 errors; the lowest-period near miss decrypts to noise |
| Columnar + running key from sculpture texts, either order | widths 2–6 | best 7–10 of 24, same as shuffled controls |

## Sampled null

Mengenlehreuhr lamp keys; geometric/tableau keystream sweeps (~2.4M candidates); fractionating ciphers with Kryptos keywords; Hill with BERLIN/CLOCK-derived matrices; keyword-seeded composites (World Clock cities, K0 Morse, advisory names, Cyrillic Projector); physical readings (shadow, solar, bearings); Chaocipher with 1,936 vocabulary alphabet pairs (best 5/24; implementation reproduces Byrne's published example).

---

## Open, ranked

### Cryptanalysis

| # | Gap | Why it matters | Effort |
|---|-----|----------------|--------|
| 1 | **Longer or structured keys beyond period 22–26** | Most families are only testable up to the point where the 24 cribs stop constraining. A longer key needs an extra assumption (a key-generation rule) to test. | M |
| 2 | **Hill 4×4 and up** | The cribs give too few full blocks per alignment; needs a transposition hypothesis or partial blocks. | M |
| 3 | **Masking other than nulls between cribs** | Nulls inside the plaintext blocks conflict with Sanborn's letter-for-letter crib pairing; other masking forms (phonetic spelling, letter swaps) are not modelled. | L |
| 4 | **Per-position procedural keys** (clock state or bearing per letter) | Depends on the compass-rose bearing and a rule for turning a reading into a key value. | L |

### Evidence and sourcing

| # | Gap | Owner |
|---|-----|-------|
| 1 | Compass-rose bearing (FOIA, Elonka Dunin, CIA Public Affairs drafts in TASKS). Likely matters after decryption rather than for it (see `docs/sources/SANBORN_QUOTES.md` #14). | you |
| 2 | Weltzeituhr: the last 16 city plates, plate order, the wind-rose mosaic's bearing (a Berlin contact with a camera) | you |
| 3 | Upgrade `SANBORN_QUOTES.md` entries from "reported" to "checked" against primary pages | Claude, when page access allows |
| 4 | Submission policy for Paradigm's $1 checker (only fully validated candidates) | you |

### Platform

Done 2026-09-28: `GET /api/k4/ledger` (with the latest suite run, stored in Neon via `k4_constraint_runs` so it survives redeploys), job persistence to Neon plus `GET /api/k4/attacks/jobs`, the registry-matches-dispatcher test, the positive-control rule, and a real scoring word list.

`kryptos ledger` (or `kryptos ledger --json`) prints the ledger from code, so tier tables no longer need hand-editing. No platform gaps from the State of Research list remain open.

---

## Correction (2026-09-28)

An earlier version of this doc said the 18-word scoring list meant "every sweep's language score leaned on it". That overstated it. The main scorer (`combined_plaintext_score`) uses n-grams; the word list only feeds `wordlist_hit_rate` (adaptive fusion weights in `composite.py`) and `transposition_analysis.score_words`. It is now a 261k-word dictionary (4+ letters), which raises English/random separation from 1.55 to 1.91.

## Related

- [K4_ACTIVE_RESEARCH.md](K4_ACTIVE_RESEARCH.md): narrative log and confirmed facts
- [K4_CAPABILITY_TABLE.md](K4_CAPABILITY_TABLE.md): every module and its status
- [K4_KEYSTREAM_ANALYSIS.md](K4_KEYSTREAM_ANALYSIS.md): the crib keystreams and what IC does and doesn't show
- [../sources/SANBORN_QUOTES.md](../sources/SANBORN_QUOTES.md): Sanborn's statements with citations
