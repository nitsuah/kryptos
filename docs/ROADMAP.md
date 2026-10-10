# Kryptos Roadmap

> 🧭 [kryptos](../README.md) · [Index](./INDEX.md) · [Features](./FEATURES.md) · **Roadmap** · [Tasks](./TASKS.md) · [Changelog](./CHANGELOG.md) · [Metrics](./METRICS.md) <!-- nav -->

Last Updated: 2026-10-09
Next Review: 2026-10-24

> 2027 planning reset (2026-09-24): completed Phases 1–4, 6 and 7 (all null) and Phase 8's two closed leads were moved
> verbatim to [archive/2026-completed-roadmap-and-tasks.md](./archive/2026-completed-roadmap-and-tasks.md) and
> summarized in [FEATURES](./FEATURES.md). What remains open is carried into 2027 Q1 below.

---

## Current Status

**Method.** Until September 2026 the project mostly sampled: pick a key, decrypt, score the result. A null said only
that those exact keys were wrong. Since 2026-09-28 the main tool is family-level elimination: for each cipher family,
check whether *any* key over a stated range can produce the 24 known crib letters, and ship a positive control with
every check. The result is tracked per family in `kryptos.k4.hypothesis_ledger` (26 eliminated, 7 statistical,
7 sampled null, 5 open as of 2026-09-30).

**What's established about K4.**

- A flattening layer exists: K4's IC is 0.0361, near random.
- No periodic key up to period 26 fits the cribs in any of four families (Vigenère, Beaufort, Variant Beaufort, KRYPTOS-keyed Quagmire III), and neither does the sum of two periodic keys
  (p1 + p2 ≤ 24).
- Whether a transposition exists, and which layer comes first, is not established. The older "substitution then
  transposition, confirmed" line rested on IC figures that don't match the ciphertext (corrected 2026-09-27; see
  `docs/analysis/K4_KEYSTREAM_ANALYSIS.md` §4–5).
- Per Sanborn (Nov 2025), BERLIN CLOCK is the Weltzeituhr at Alexanderplatz, not the Mengenlehreuhr.
- The solvekryptos.com reconstruction ("THE COMPASS ROSE IS HERE…") is not Sanborn's text, and used as 97 known letters
  it fits no tested family.

**What's open.** Two kinds of work are left: new cipher structures the ledger doesn't cover yet (code, below), and
physical facts only a person can collect (sourcing, below). Ranked detail: `docs/analysis/K4_NEGATIVE_SPACE.md`.

---

## 2027 Q1 — Phase 9: Cryptanalysis frontier (code)

Each item follows the same rules: exact search where the space allows it, shuffled-ciphertext controls where it
doesn't, a positive-control test either way, and a ledger entry with the right tier.

- [ ] **Irregular transpositions.** Myszkowski, disrupted and incomplete columnar, keyed route ciphers, turning
  grilles, each with a periodic key in both layer orders. The width-10–14 backtracking search in `frontier_checks` is
  the starting point.
- [ ] **Masking that changes length.** Letters inserted or dropped inside words (K1–K3 all carry deliberate
  misspellings). Needs a crib search that allows gaps; letter-for-letter swaps are already covered by the mixed-alphabet
  check.
- [ ] **Two non-periodic layers.** An autokey or running key on top of a wide or irregular transposition. Columnar plus
  autokey is covered only to width 7, and plus an English running key to width 8.
- [ ] **Named key-generation rules.** The K1–K3 ciphertexts, the K0 Morse text or the Cyrillic Projector as running-key
  sources under transposition. The cribs can't pin down a long key on their own, so each rule has to be named first.
- [ ] **Hill 6×6 and up.** Too few whole crib blocks per alignment; testable only with a transposition guess or with
  partial blocks.
- [ ] **Per-letter Weltzeituhr lookups** (city, zone or hour per letter as the key). Blocked on the photographs in
  Phase 8; once recorded, they drop into the existing dial and lookup checks.

Completed in this phase's lead-up (2026-09-28–2026-10-09): the P21 crib-constraint engine, structural checks, P22 frontier checks, real scoring tables and word list, job persistence, and the bounded long clue-derived keyed-columnar frontier (widths 15–26; see [K4_KEYED_COLUMNAR_FRONTIER](./analysis/K4_KEYED_COLUMNAR_FRONTIER.md)). The frontier narrows one finite hypothesis but does not close the broader irregular-transposition task. See [CHANGELOG](./CHANGELOG.md).

---

## 2027 Q1 — Phase 8: Primary-source sourcing (needs a person)

Of the three source gaps opened 2026-09-01, two closed on 2026-09-02 (the World Clock city list at 130 of 146 names,
and a sub-minute Nov 9 1989 timestamp). What remains:

- [ ] **Weltzeituhr photographs.** Close-ups of every face of the city ring, the date-line plate, and the wind-rose
  mosaic from above with a straight edge in frame. This unblocks the per-letter lookup keys in Phase 9 and the 16
  unread city plates.
- [ ] **The CIA compass rose's measured bearing** and what the lodestone deflects it to. Still an open community
  question (elonka.com wishlist); the only estimate (~220°) is flagged inexact, and satellite imagery can't resolve it.
  Routes and dials are already covered for every whole degree, so this matters most for reading a solution, not finding
  one.
- [ ] **Send the three outreach drafts**: a FOIA request (asking for the 1990 landscape or installation drawing),
  Elonka Dunin, and CIA Public Affairs (authorized research visit). All three are in `docs/TASKS.md`; each needs a human
  send.
- [ ] **Read Sanborn's quotes against the primary pages.** `docs/sources/SANBORN_QUOTES.md` carries a confidence tier
  per quote; several pages couldn't be fetched automatically.

---

## 2027 Q1 — Platform

- [x] **Single-page dashboard (2026-09-30).** The tabbed SPA became one fixed-height screen with five modules on a ring,
  styled after the Ghost in the Shell interfaces, fitting the viewport without page scrolling, with a drawing of the
  Weltzeituhr and UI for the ledger and job history. See
  `docs/reference/DASHBOARD.md`.
- [ ] **"Try a hypothesis" endpoint.** Pick a family and parameters, get the crib verdict plus a decryption, so the
  dashboard can test ideas without a new module per idea.
- [ ] **Candidate submission gate.** Paradigm checks K4 guesses at $1 each. Before any guess, run every crib and ledger
  check and require the candidate to reproduce from its stated method.
- [ ] **Re-score stored candidates.** Rankings stored before 2026-09-28 used the placeholder n-gram tables.

---

## Standing — Phase 5: Post-Solution (conditional on a solve)

- [ ] Solution documentation — full attack path, key insights, solution narrative
- [ ] README update — reflect solution and cryptanalytic implications
- [ ] Archive all null-result artifacts with parameter provenance

---

## External developments (2025–2026)

Sanborn's 1990 archival papers were found by Kobek and Byrne (Sept 2025, not a cryptographic solve); the plaintext is
sealed and has not been released. A Sanborn-confirmed K5 exists. Paradigm identified itself as the auction buyer in June
2026 and runs a $1-per-guess K4 verifier alongside its Kryptos CTF. Full detail: `docs/analysis/K4_ACTIVE_RESEARCH.md`,
"External Developments".

---

## Key References

| Document | Purpose |
|----------|---------|
| `docs/analysis/K4_NEGATIVE_SPACE.md` | What's ruled out (by tier) and what's open, ranked |
| `docs/analysis/K4_ACTIVE_RESEARCH.md` | Narrative log of every phase and run; confirmed facts |
| `docs/analysis/K4_CAPABILITY_TABLE.md` | Every attack vector and component, status, real candidate count |
| `docs/analysis/K4_KEYSTREAM_ANALYSIS.md` | Derived shift sequences at all four crib windows; the IC analysis |
| `docs/TASKS.md` | Execution backlog, including the outreach drafts |
| `docs/reference/DASHBOARD.md` | Dashboard design and data sources |
| `docs/archive/2026-completed-roadmap-and-tasks.md` | Verbatim archive of completed Phases 1–4/6/7 and TASKS Done (2026-09-24 reset) |
| `docs/archive/K4_ATTACK_LANDSCAPE.md` | Archived 3D fingerprint, historical reference only |
