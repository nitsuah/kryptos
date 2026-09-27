# K4 Negative Space

> 🧭 [kryptos](../../README.md) · [Index](../INDEX.md) · [Features](../FEATURES.md) · [Roadmap](../ROADMAP.md) · [Tasks](../TASKS.md) · [Changelog](../CHANGELOG.md) · [Metrics](../METRICS.md) <!-- nav -->

**Last Updated:** 2026-09-28
**Companion page:** [Kryptos State of Research](https://claude.ai/artifact/PBjhWqNYP5zXCdQb9qfMB3), a readable overview with the coverage map and open to-dos. It replaces the earlier briefing pages (K4 Field Notes, Three Open Leads, Three Moves, K4 Ledger Audit), which are kept for history only.
**Status:** Living document. It records what has *not* been tried, or not tried in a way that settles anything. The machine-readable version is `kryptos.k4.hypothesis_ledger` (`GET /api/k4/ledger`).

---

## Why this doc exists

Phases 1–7 produced millions of null candidates, but almost all of them came from one method: fix a transposition and a key, decrypt all 97 letters, then score. A null from that method only rules out the exact combinations that were tried. It says nothing about the rest of the family, and the candidate counts don't measure coverage.

The 24 confirmed crib letters support a second method. Each crib letter fixes the key value at its position, for a given cipher family. So a whole family can be tested at once: does *any* parameter choice reproduce all 24 values? `kryptos.k4.crib_constraints` (P21) does this, with a positive-control test for every check (a planted solution must be found).

So there are two strengths of "ruled out":

| Tier | Meaning | Where |
|------|---------|-------|
| **eliminated** | Exhaustive over the stated parameter range, checked against the cribs, with a positive control | `hypothesis_ledger`, tier `eliminated` |
| **sampled null** | Specific parameters were decrypted and scored; none matched | Phase 1–7 sweeps, `K4_ACTIVE_RESEARCH.md` |
| **open** | Not yet tested in a way that covers the family | This doc |

---

## Eliminated by constraint (2026-09-28)

`kryptos crib-constraints` or `POST /api/k4/attacks/run {"attack_id": "p21_crib_constraints"}` reproduces all of these. The artifact is `K4_CRIB_CONSTRAINTS_NULL.json`.

| Family | Range covered | Result |
|--------|---------------|--------|
| Monoalphabetic, with or without transposition | any alphabet | IC 0.0361 vs English 0.066, plus 8 of 9 repeated crib letters map inconsistently |
| Direct periodic key: Vigenère, Beaufort, Variant, Quagmire III (KRYPTOS) | periods 1–26 | no period fits |
| Quagmire I / II / III, dictionary keyword alphabets | 231,933 distinct alphabets (web2 + GCIDE), periods 1–25 | zero survivors (period 26 applies one constraint and passes by chance) |
| Ciphertext autokey (+ constant) | lags 1–71, five families | none; lag 72 has two constraints and survives at chance level |
| Plaintext autokey (+ constant) | lags 1–11 and 31–51 (the lags where ≥ 2 crib pairs interact) | none. Lags 12, 30 and 52 have one pair each; the other 61 lags (13–29, 53–96) have none, so the cribs can't test them |
| Linear key a·i + b | all a, b | none |
| Progressive key K[i mod p] + d·⌊i/p⌋ | periods 1–26, all d | none |
| Gronsfeld / Gromark digit keys | 15 Kryptos keyword alphabets, both directions | every alphabet needs a shift ≥ 23 |
| Running key from sculpture texts | K1–K3 plaintext and ciphertext, K1–K4 ciphertext, KRYPTOS tableau rows, K0 Morse words, Weltzeituhr cities; forward and reversed; every alignment; any constant | best alignment 7–8 of 24, the same as a shuffled-text control |
| Columnar transposition + periodic key, both layer orders | widths 2–9 (all column orders), periods 1–22, five families | zero survivors. Width 10 was checked to period 20 in a one-off run. Survivors at periods 23–26 are chance-level (a period-26 slot pattern has one equality) and decrypt to noise |
| Phase 6–7 geometric permutations + periodic key, both orders | 7,680 mappings, periods 1–22 | zero survivors |

Nicodemus (Vigenère by column, then columnar read-out) is the sub-then-transposition case with period = width, so it's covered by the columnar row.

---

## Open: ranked

Rank is value × tractability. "S/M/L" is rough effort.

### Cryptanalysis

| # | Gap | Why it matters | Effort |
|---|-----|----------------|--------|
| 1 | **Scoring word list has 18 words.** `data/wordlist.txt` has never existed, so `scoring.wordlist_hit_rate` has always used an 18-word fallback. | Every sweep's language score leaned on this. Fixing it changes baselines, so it needs its own PR with before/after calibration on K1–K3. `english-words` (MIT) is now a dependency and can supply the list. | S |
| 2 | **Quagmire IV** (different plain and cipher keywords) | Only the single-keyword Quagmires are covered at dictionary scale. Pairs are 10¹⁰, so prune with the per-side constraints from Q1/Q2 first. | M |
| 3 | **Double periodic keys** (sum of two keywords, e.g. PALIMPSEST + ABSCISSA) | Effective period is the LCM, above 26 for most pairs, so the periodic elimination doesn't cover it. Keyword pairs from Kryptos vocabulary are cheap to check. | S |
| 4 | **K3-style double rotation + key** | K3 used this transposition. It has only been sampled for K4. As a constraint check it needs a padding rule, because 97 is prime. | M |
| 5 | **Transposition + non-periodic key** | Combine the columnar/geometric mappings with the autokey and running-key constraints. The engine already has both halves. | M |
| 6 | **Digraphic ciphers under crib constraints** (Playfair, Four-Square, Bifid) | Only sampled with ~30 keywords. Crib digraphs constrain the square directly. | M |
| 7 | **Self-modifying alphabets** (Chaocipher, Alberti disks) | Would fit "a technique not in the literature". Never touched. | L |
| 8 | **Nulls / masking as constraints** | Masking was sampled inside composites only. Deleting k letters shifts crib alignment in a testable way. | M |
| 9 | **Hill n×n as a constraint** | 2×2/3×3 were derived from BERLIN/CLOCK and sampled. The full crib set allows a direct linear solve per alignment. | S |

### Evidence and sourcing

| # | Gap | Owner |
|---|-----|-------|
| 1 | Compass-rose bearing (FOIA, Elonka Dunin, CIA Public Affairs drafts in TASKS) | you |
| 2 | 16 Weltzeituhr names still unconfirmed; plate order within segments | Claude (photos) |
| 3 | Sanborn primary-quote corpus with citations (`docs/sources/SANBORN.md` is a checklist, not a corpus) | Claude |
| 4 | A submission policy for Paradigm's $1 verifier (only fully validated candidates) | you |

### Platform (backend, independent of the new frontend)

| # | Gap | Effort |
|---|-----|--------|
| 1 | Ledger endpoint done (`GET /api/k4/ledger`). Next: have the constraint suite write its latest numbers into the ledger response instead of fixed text | S |
| 2 | Jobs are in memory only; a restart loses them. Persist job state and artifacts to Neon (the 2027 DB migration) | M |
| 3 | `FRONTIER_VECTORS` duplicates the capability table and drifts (P18's description said 22 pairs). Generate one from the other | S |
| 4 | Positive-control harness as a rule: every attack module ships a planted-solution test, like P21 | M |
| 5 | Scoring calibration benchmark (K1–K3 plus synthetic) to support gap #1 above | M |

---

## Related

- [K4_ACTIVE_RESEARCH.md](K4_ACTIVE_RESEARCH.md): narrative log and confirmed facts
- [K4_CAPABILITY_TABLE.md](K4_CAPABILITY_TABLE.md): every module and its status
- [K4_KEYSTREAM_ANALYSIS.md](K4_KEYSTREAM_ANALYSIS.md): the crib keystreams and what IC does and doesn't show
