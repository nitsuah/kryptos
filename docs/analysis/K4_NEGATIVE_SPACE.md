# K4 Negative Space

> 🧭 [kryptos](../../README.md) · [Index](../INDEX.md) · [Features](../FEATURES.md) · [Roadmap](../ROADMAP.md) · [Tasks](../TASKS.md) · [Changelog](../CHANGELOG.md) · [Metrics](../METRICS.md) <!-- nav -->

**Last Updated:** 2026-09-28 (frontier pass)
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
| Columnar widths 10–14 + periodic key, either order (exact search over 10!–14! column orders) | key first: periods 1–22 except 17 (widths 12–14) and 18 (width 14); transposition first: periods 1–17 | no column order fits the cribs |
| Phase 6–7 geometric permutations + periodic key, either order | 7,680 mappings, periods 1–22 | zero survivors |
| K3-style double rotation + periodic key, either order | 21,096 layouts (0–11 null pads, all divisor widths, 6 rotations per stage), periods 1–22 | zero survivors |
| Columnar transposition + ciphertext autokey | widths 2–7, every lag with 4+ constraints, every offset | zero survivors |
| Nulls between the crib blocks + periodic key | 1–29 nulls, periods 1–23 | none |
| Hill 2×2 and 3×3, no transposition | every alignment, both directions | no consistent matrix |
| Linear-recurrence key K[i] = c1·K[i-1] + … + cn·K[i-n] + d (Gromark / Fibonacci style) | orders 1–7, any coefficients and primer, five families | no solution over GF(2)/GF(13) |
| Periodic key + an *arbitrary* mixed alphabet (covers letter-for-letter masking such as letter swaps) | plaintext-side alphabet periods 1–12; ciphertext-side alphabet periods 1–15 | inconsistent; random ciphertexts pass 0% at period 12 |
| Long periodic key spelled from Kryptos words (e.g. PALIMPSESTABSCISSAKRYPTOS) | 24,696 ordered 2–3-word phrases, 27–60 letters, every offset, five families | none |
| Key read per letter from a dial advancing a fixed step | dials of 12, 24, 60, 360, 720, 1440 positions; every start, step, offset; two reading rules | none |
| Route along a compass bearing + periodic key, either order | every whole-degree bearing, widths 4–24 (9,111 distinct routes), periods 1–22 | zero survivors |
| Hill 4×4, no transposition | all four alignments | alignments 1–2: no matrix fits; 0 and 3: only non-invertible matrices fit |
| The solvekryptos.com reconstruction as the plaintext | every family on this page, with all 97 letters known (periods to 48, Hill to 9×9, Quagmire I–IV dictionary, all transposition families) | no family produces K4 from it (see below) |
| 25-letter and 5–6-letter output ciphers as the last layer | Playfair, Two-Square, Four-Square, 5×5 Bifid, Polybius, ADFGX, ADFGVX; with or without transposition | K4 contains all 26 letters |

Nicodemus (Vigenère by column, then columnar read-out) is the sub-then-transposition case with period = width, so the columnar row covers it.

## Statistical (no signal against controls)

| Family | Range | Result |
|--------|-------|--------|
| Monoalphabetic + transposition | any | IC 0.0361 vs English 0.066 |
| Columnar / geometric + periodic key **allowing 1–2 wrong crib letters** | widths 2–9 and 7,680 geometric, periods 1–22 | near-miss counts inside the range of 15 shuffled-ciphertext controls (columnar 368 vs 206–563, with 6 of 15 controls at or above it; geometric 325 vs 250–449, 12 of 15 at or above); nothing below period 16 within 2 errors; the lowest-period near miss decrypts to noise |
| Columnar + running key from sculpture texts, either order | widths 2–6 | best 7–10 of 24, same as shuffled controls |
| Running key from *any* English text, no transposition | five families | key letters at the crib runs score as random; fewer than 1 in 2,000 English fragment pairs score that low |
| Columnar + running key from any English text (key first) | widths 2–8 | best score inside the shuffled-control range |
| Columnar widths 12–14: the column orders that do fit the cribs | key first: period 17 (46 orders, widths 12–14) and 18 (196, width 14); transposition first: period 18 (91, width 14) | every one decrypted under every key the cribs allow (up to two free key slots); best English score 0.16, where English scores about 1 |
| Hill 5×5 | all five alignments | alignments 2–3: no matrix fits; alignment 4: all 11.9M fitting matrices scored, best 0.36 on the English scale (planted key 0.93); alignments 0–1: row-by-row beam search, K4 0.67 / 0.48 vs 0.50–0.72 on random ciphertexts (planted key 0.94) |

## Sampled null

Mengenlehreuhr lamp keys; geometric/tableau keystream sweeps (~2.4M candidates); fractionating ciphers with Kryptos keywords; Hill with BERLIN/CLOCK-derived matrices; keyword-seeded composites (World Clock cities, K0 Morse, advisory names, Cyrillic Projector); physical readings (shadow, solar, bearings); Chaocipher with 1,936 vocabulary alphabet pairs (best 5/24; implementation reproduces Byrne's published example).

---

## The full reconstruction as known plaintext

solvekryptos.com's field guide publishes a full 97-letter reading, THECOMPASSROSEISHEREXEASTNORTHEAST…BERLINCLOCKWHICHISNORTHEASTOFHEREX. It matches the 24 confirmed crib letters, and the other 73 letters are its authors' reconstruction, not Sanborn's text (see `plaintext_evidence.py`).

Treating all 97 letters as known makes every check far stronger: periods up to 48 become testable, and Hill up to 9×9. `frontier_checks.reconstruction_suite` runs every family on this page that way. **Nothing fits.** No periodic, progressive or double-periodic key to period 48, no autokey, linear or recurrence key, no mixed alphabet to period 48, no Hill 2×2–9×9, no dial key, no Quagmire I–IV dictionary alphabet, and no columnar (widths 2–9), geometric, double-rotation or bearing-route transposition with a periodic key to period 48. The keystream it implies, read as a running key, scores as random, not English.

So either the reconstruction is wrong past the cribs, or K4's method sits outside every family tested here. Either way the reconstruction can't be used as a crib to back out the method. The earlier `known_plaintext_inversion` scans (11,520 geometric and 3,674,160 rectangular transpositions) had reached the same null for a smaller family set.

---

## Open, ranked

### Cryptanalysis

| # | Gap | Why it matters | Effort |
|---|-----|----------------|--------|
| 1 | **Other long-key rules** | Recurrence, dial, progressive and English running keys are now covered. Any other rule (a keyword-driven procedure, a non-English running text) has to be named before it can be tested. | M |
| 2 | **Hill 6×6 and up** | Too few full crib blocks; needs a transposition hypothesis or partial blocks. | M |
| 3 | **Masking that isn't letter-for-letter** | Letter-for-letter masking is covered by the mixed-alphabet check; inserted or dropped letters inside words, and respellings that change length, are not modelled. | L |
| 4 | **Per-letter lookup keys** | A steady dial is eliminated; a lookup per letter (Weltzeituhr city or time zone) needs the plate order. | L |

### Evidence and sourcing

| # | Gap | Owner |
|---|-----|-------|
| 1 | Compass-rose bearing (FOIA, Elonka Dunin, CIA Public Affairs drafts in TASKS). Likely matters after decryption rather than for it (see `docs/sources/SANBORN_QUOTES.md` #14). Routes and dial keys along *any* whole-degree bearing are already eliminated, so the measurement would only narrow other constructions. | you |
| 2 | Weltzeituhr: the last 16 city plates, plate order, the wind-rose mosaic's bearing (a Berlin contact with a camera) | you |
| 3 | Upgrade `SANBORN_QUOTES.md` entries from "reported" to "checked" against primary pages | Claude, when page access allows |
| 4 | Submission policy for Paradigm's $1 checker (only fully validated candidates) | you |

### Platform

Done 2026-09-28: `GET /api/k4/ledger` (with the latest suite run, stored in Neon via `k4_constraint_runs` so it survives redeploys), job persistence to Neon plus `GET /api/k4/attacks/jobs`, the registry-matches-dispatcher test, the positive-control rule, and a real scoring word list.

`kryptos ledger` (or `kryptos ledger --json`) prints the ledger from code, so tier tables no longer need hand-editing. `kryptos frontier` / `p22_frontier_checks` runs the frontier checks. No platform gaps from the State of Research list remain open.

**Scoring tables (finding and fix, 2026-09-28).** `data/ngrams/quadgrams.tsv`, `trigrams.tsv`, `bigrams.tsv` and `quadgrams_high_quality.tsv` held about ten illustrative entries each, and `scoring.combined_plaintext_score` read them, so its n-gram terms barely distinguished English from noise. It now loads tables built from 8.9M letters of public-domain English (`data/ngrams/english_{2,3,4}grams.tsv`): separation of English from shuffled English on 97 letters goes from d = 4.2 to 9.4, with no overlap. Every language-scored sweep before this date ranked candidates with the old tables. Their nulls mostly stand, because they rested on crib matches rather than language scores, but a candidate that was *discarded* on language score alone was judged with a weak scorer.

---

## Correction (2026-09-28)

An earlier version of this doc said the 18-word scoring list meant "every sweep's language score leaned on it". That overstated it. The main scorer (`combined_plaintext_score`) uses n-grams (whose tables had their own problem, see Platform above); the word list only feeds `wordlist_hit_rate` (adaptive fusion weights in `composite.py`) and `transposition_analysis.score_words`. It is now a 261k-word dictionary (4+ letters), which raises English/random separation from 1.55 to 1.91.

## Related

- [K4_ACTIVE_RESEARCH.md](K4_ACTIVE_RESEARCH.md): narrative log and confirmed facts
- [K4_CAPABILITY_TABLE.md](K4_CAPABILITY_TABLE.md): every module and its status
- [K4_KEYSTREAM_ANALYSIS.md](K4_KEYSTREAM_ANALYSIS.md): the crib keystreams and what IC does and doesn't show
- [../sources/SANBORN_QUOTES.md](../sources/SANBORN_QUOTES.md): Sanborn's statements with citations
