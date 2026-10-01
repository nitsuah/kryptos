# K4 Keystream Analysis — Confirmed Period-13 Window

> 🧭 [kryptos](../../README.md) · [Index](../INDEX.md) · [Features](../FEATURES.md) · [Roadmap](../ROADMAP.md) · [Tasks](../TASKS.md) · [Changelog](../CHANGELOG.md) · [Metrics](../METRICS.md) <!-- nav -->

**Status:** Active research finding
**Last Updated:** 2026-09-30
**Evidence Level:** High — derived directly from Sanborn's confirmed cribs against the K4 ciphertext

**2026-09-27 correction:** §4 (IC) and §5 (architecture ruling) were wrong. The IC figures were never computed from the ciphertext, and the "substitution then transposition" ruling was built on them. Both sections are rewritten below. The EAST release date was also wrong (Aug 2020, not 2023). The numbers are now pinned by `tests/functional/test_k4_documented_facts.py`.

**2026-09-02 correction:** this document's EAST/NORTHEAST positions and every keystream derived from them were wrong by one position throughout — the same bug fixed in `keystream_validator.K4_CRIBS` and traced to independent duplicates in `key_csp.py` and `clock_hill_attack.py` (see `K4_ACTIVE_RESEARCH.md`'s "External Developments (2025–2026)" section for the full story of how this was found). BERLIN/CLOCK were already correct throughout. All values below are corrected and re-verified directly against the real K4 ciphertext.

---

## 1. Confirmed Crib Positions

K4 ciphertext (97 chars, 0-indexed):

```
OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR
0         1         2         3         4         5         6         7         8         9
0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456
```

Sanborn's publicly confirmed plaintext anchors (0-indexed within K4):

| Position (0-idx) | Cipher | Plain     | Source / Date        |
|------------------|--------|-----------|----------------------|
| 21–24            | FLRV   | EAST      | Sanborn clue, Aug 2020 |
| 25–33            | QQPRNGKSS | NORTHEAST | Sanborn clue, Jan 2020 |
| 63–68            | NYPVTT | BERLIN    | Sanborn clue, Nov 2010 |
| 69–73            | MZFPK  | CLOCK     | Sanborn clue, Nov 2014 |

> **Index note:** Community sources and some docs in this repo label these positions as 1-indexed (25–33 → 1-indexed 26–34, etc.). The values above use Python 0-indexed convention consistently. The K4-CLOCKS.html document incorrectly labels NYPVTTMZF as being at "positions 26–34"; NYPVTTMZF is BERLIN+CLOCK's ciphertext, actually at 0-indexed 63–73. The old CONTRIBUTING.md quick-start code (no longer in this repo) listed `'NORTHEAST': [25]` and `'BERLIN': [64]`; **`[25]` for NORTHEAST was correct all along** (this document's own table above previously said otherwise — see the 2026-09-02 correction note up top), and `[64]` for BERLIN was genuinely wrong, correct 0-indexed start is **63**.

---

## 2. Vigenère-Equivalent Keystream

If any substitution layer in K4 operates like Vigenère (cipher = plain + key mod 26), the per-position key letter is:

```
key[i] = (cipher_ord[i] - plain_ord[i]) mod 26
```

### EAST window (positions 21–24)

| Pos | Cipher | Plain | key = (C−P) mod 26 | Key letter |
|-----|--------|-------|--------------------|------------|
| 21  | F (5)  | E (4) | 1                  | B          |
| 22  | L (11) | A (0) | 11                 | L          |
| 23  | R (17) | S (18)| 25                 | Z          |
| 24  | V (21) | T (19)| 2                  | C          |

**EAST keystream: `BLZC` → shifts [1, 11, 25, 2]**

### NORTHEAST window (positions 25–33)

| Pos | Cipher | Plain | key = (C−P) mod 26 | Key letter |
|-----|--------|-------|--------------------|------------|
| 25  | Q (16) | N (13)| 3                  | D          |
| 26  | Q (16) | O (14)| 2                  | C          |
| 27  | P (15) | R (17)| 24                 | Y          |
| 28  | R (17) | T (19)| 24                 | Y          |
| 29  | N (13) | H (7) | 6                  | G          |
| 30  | G (6)  | E (4) | 2                  | C          |
| 31  | K (10) | A (0) | 10                 | K          |
| 32  | S (18) | S (18)| 0                  | A          |
| 33  | S (18) | T (19)| 25                 | Z          |

**NORTHEAST keystream: `DCYYGCKAZ` → shifts [3, 2, 24, 24, 6, 2, 10, 0, 25]**

### Combined 13-character window (positions 21–33)

Reading EAST first, then NORTHEAST:
```
Keystream: B L Z C D C Y Y G C K A Z
Shifts:   [1,11,25,2,3,2,24,24,6,2,10,0,25]
```

Reading in the order the other agent analysis presented (NORTHEAST then EAST):
```
Keystream: D C Y Y G C K A Z B L Z C
Shifts:   [3,2,24,24,6,2,10,0,25,1,11,25,2]
```

---

## 3. What This Rules Out

### 3.1 Single-layer repeating Vigenère

Running `DCYYGCKAZBLZC` (or any rotation of the corrected 13-char window) as a repeating Vigenère key against the full 97-char K4 ciphertext does **not** produce English plaintext outside the crib window. A real Vigenère key that repeats would produce consistently English-like output everywhere. Negative result is confirmed — and was already guaranteed by the Phase 1 exhaustive sweep of every repeating-key length 1–20 (see `docs/ROADMAP.md`'s Phase 1), which covers length-13 keys generally, not just this specific derived string.

### 3.2 Direct Berlin Clock keying

The Berlin Clock rows produce values bounded by:
- 5-hour row: 0–4
- 1-hour row: 0–4
- 5-minute row: 0–11
- 1-minute row: 0–4

The observed keystream shifts [1, 11, 25, 2, 3, 2, 24, 24, 6, 2, 10, 0, 25] include values of 25, 24, 24, 25 that **exceed the maximum Berlin Clock row value of 11**. No direct mapping of a single clock reading to these shifts is possible. Enumeration of all 720 clock states (12 hr × 60 min) as Vigenère keys against K4 was run; no state produces EAST or NORTHEAST at the confirmed positions.

### 3.3 Clock-shifted or scaled values

Linear scaling or shift of clock values doesn't cleanly map to the observed distribution. The values are not a permutation of any recognizable clock encoding.

---

## 4. What the IC Analysis Tells Us

Computed by `kryptos.k4.ic_profile` (pinned in `tests/functional/test_k4_documented_facts.py`):

| Text | IC |
|------|----|
| K4, all 97 letters | **0.0361** |
| Uniform random (1/26) | 0.0385 |
| English prose | ≈0.066 |

| Segment (0-indexed) | IC |
|---------------------|----|
| 0–31  | 0.046 |
| 32–63 | 0.046 |
| 64–96 | 0.034 |

> The previous version of this table read 0.058 / 0.071 / 0.062, and the overall IC was quoted elsewhere as ≈0.062. Neither matches the ciphertext.

**What this does show:** transposition and monoalphabetic substitution both leave IC unchanged, so any cipher built only from those would keep English's ≈0.066. K4's 0.036 means at least one polyalphabetic or otherwise flattening layer is present.

**What this does not show:** layer order. IC is invariant under transposition, so it can't tell "transposition first" from "transposition last". On 32-letter slices it is also very noisy: shuffling K4's own letters at random gives a segment spread at least as large as the real one about 46% of the time (`segment_spread_p_value`). The old conclusion that "non-uniform IC is a signature of transposition applied after substitution" doesn't hold.

---

## 5. Composite Architecture — What Is and Isn't Established

**Established:**

1. A flattening (polyalphabetic-like) layer exists (§4).
2. It is not a direct periodic key of length ≤ 26 under Vigenère, Beaufort, Variant Beaufort, or KRYPTOS-keyed Quagmire III: for every period 1–26, two crib letters that share a key slot imply different key values. The first consistent period is 27, where the 24 cribs barely constrain anything. (`key_csp.periodic_family_consistency`)

**Not established (previously stated as a ruling):** that a transposition layer exists, or which layer comes first. Two families fit the evidence equally well:

- **Non-periodic key, no transposition.** Running key, autokey, or a key produced by a procedure (a clock state per position, a physical reading). Here BLZCDCYYGCKAZ really is the (Vigenère-equivalent) key at positions 21–33.
- **Periodic or structured key plus transposition.** Under this model the cribs' ciphertext letters were scattered before substitution, and the observed keystream is a permuted view of a simpler key.

Every sweep in phases 1–7 assumed the second family. §6 below describes the attack for that family; read it as conditional on that assumption.

**Update 2026-09-28.** Both families have since been tested as families rather than by sampled keys (`crib_constraints`, `structural_checks`, `frontier_checks`). For the first family, autokey, linear, progressive, digit, recurrence (orders 1–7), dial and sculpture-corpus running keys are eliminated, and running keys from any English text show no signal against controls. For the second, columnar transposition of widths 2–9, the geometric mappings, K3's double rotation and compass-bearing routes, each combined with a periodic key of period 1–22 in either order, are eliminated. Columnar widths 10–14 are eliminated for key-first periods 1–22 except 17 (widths 12–14) and 18 (width 14), and for transposition-first periods 1–17; the orders that fit at those exceptions decrypt to noise. What remains of each family is listed in [K4_NEGATIVE_SPACE.md](K4_NEGATIVE_SPACE.md#open-ranked).

---

## 6. Key Derivation After Transposition Reversal

The core attack strategy: if we can identify the correct transposition permutation P, then applying P⁻¹ to the ciphertext yields the substituted-but-not-transposed text. At that point:

- The substituted text at the correct positions will produce EASTNORTHEAST
- The keystream at those positions in the pre-transposition text reveals the **actual substitution key pattern**
- If the key is a recognizable word/phrase or a Berlin Clock reading, we solve K4

**Target:** Find the transposition permutation P such that after inverting it, the keystream at EAST+NORTHEAST positions collapses from high-entropy BLZCDCYYGCKAZ into a recognizable key structure (a word, a clock state, a keyed-alphabet output).

---

## 7. Attack Vectors — Status

### ✅ 7.1 Inverse Transposition Sweep — COMPLETE, NULL RESULT

`kryptos.k4.inverse_transposition_sweep.full_sweep` tested all 3 grid geometries (10×10, 7×14, 8×13) with ENE diagonal (67.5°) and columnar routes. No transposition permutation produced a recognizable keystream at EAST+NORTHEAST positions.

### ✅ 7.2 Keyed Alphabet Realignment — COMPLETE, NULL RESULT

`check_keyed_alphabet_realignment` tested KRYPTOS, PALIMPSEST, and ABSCISSA alphabets. The effective keystream at positions 21–33 does not resolve to a recognizable pattern (clock state, keyword, or bounded-value vector) under any of them.

### ✅ 7.3 InstructionalScorer — COMPLETE

`kryptos.k4.scoring_instructional` — `instructional_score`, `combined_instructional_score`, `entropy_gate`. Integrated into the composite sweep scoring pipeline.

### ✅ 7.4 Full Composite Sweep (Clock × Grid × Alphabet) — COMPLETE, NULL RESULT

`run_composite_sweep` — 3 alphabets × 3 grids × 720 clock states × ENE+columnar routes. No simultaneous 4-crib match found. Null artifact: `K4_COMPOSITE_SWEEP_NULL.json`. Best candidates had ≤ 1 keyword hit.

### ✅ 7.5 Clock → Hill 2×2 Invertibility Pre-filter — COMPLETE, NULL RESULT

`kryptos.k4.clock_hill_attack.run_clock_hill_attack` — filters all 720 clock states by Hill 2×2 invertibility mod 26 (~100 pass), applies Hill decryption to K4, validates 4 cribs. **Null result.** See `K4_ACTIVE_RESEARCH.md`.

### ✅ 7.6 Non-standard Clock Encodings — COMPLETE, NULL RESULT

`kryptos.k4.clock_subrow_attack.run_clock_subrow_attack` — tested 4 sub-row schemes (5-hr only, 1-hr only, minute rows only, row sums → letter) as short Vigenère keys. **Null result.** See `K4_ACTIVE_RESEARCH.md`.

### ✅ 7.7 Beaufort Cipher Sweep — COMPLETE, NULL RESULT

`kryptos.k4.beaufort_sweep.run_beaufort_sweep` — systematic pass with 10 key candidates (KRYPTOS, PALIMPSEST, BERLIN, CLOCK, ABSCISSA, and variants) × 2 alphabets. **Null result.** See `K4_ACTIVE_RESEARCH.md`.

---

## 8. BERLIN/CLOCK Keystream Reference

For completeness, the Vigenère-equivalent keystream at the BERLIN+CLOCK window (pure-Vigenère assumption, 0-indexed 63–73):

| Pos | Cipher | Assumes plain | Shift | Key letter |
|-----|--------|---------------|-------|------------|
| 63  | N (13) | B (1)         | 12    | M          |
| 64  | Y (24) | E (4)         | 20    | U          |
| 65  | P (15) | R (17)        | 24    | Y          |
| 66  | V (21) | L (11)        | 10    | K          |
| 67  | T (19) | I (8)         | 11    | L          |
| 68  | T (19) | N (13)        | 6     | G          |
| 69  | M (12) | C (2)         | 10    | K          |
| 70  | Z (25) | L (11)        | 14    | O          |
| 71  | F (5)  | O (14)        | 17    | R          |
| 72  | P (15) | C (2)         | 13    | N          |
| 73  | K (10) | K (10)        | 0     | A          |

BERLIN keystream: `MUYKLG` | CLOCK keystream: `KORNA`

These also look high-entropy under pure Vigenère, consistent with the composite-cipher conclusion. Under a keyed alphabet or after transposition reversal, these may resolve to recognizable patterns.

---

## 9. Questions — 11 total, all resolved (2026-09-30)

Questions 7–11 were open when this list was written (2026-08-12). All five were then run as frontier attacks P1–P5, and all were null; the answers are added in place.

1. ~~What transposition permutation P maps EAST+NORTHEAST to a recognizable keystream?~~ — Tested: no such permutation found in the grid+route space explored. Either the transposition is not grid-based, or the substitution layer is not Vigenère-equivalent.
2. ~~Does a keyed alphabet make the keystream structured?~~ — Tested KRYPTOS/PALIMPSEST/ABSCISSA: null result. If a keyed alphabet is involved, it's one not yet tried.
3. ~~Is the ENE diagonal the correct reading path?~~ — Tested in full sweep alongside columnar: null result for both. ENE diagonal is not the sole transposition mechanism under the assumptions tested.
4. ~~Could the clock be used as a Hill matrix key?~~ — Tested via `run_clock_hill_attack`: null result. ~100 invertible states all produced no crib match.
5. ~~Are there non-standard clock encodings?~~ — Tested via `run_clock_subrow_attack`: 4 sub-row schemes; null result.
6. ~~Beaufort cipher sweep~~ — Tested via `run_beaufort_sweep`: null result.
7. ~~Does the BERLIN+CLOCK keystream (MUYKLGKORNA) become recognizable after any transposition reversal?~~ — Tested as P5 with a 2-crib relaxed gate, against both the brute-force columnar family (34,560 candidates) and the geometric family (69,120): zero near-misses.
8. ~~Is there a masking/null-removal layer before the substitution?~~ — Tested as P2 (8 masking variants, 6,144 candidates, null) and, as a family, by the nulls-between-cribs check in `structural_checks` (eliminated). Masking that inserts or drops letters inside words is still open.
9. ~~Are 3-layer composites (e.g., keyed-alphabet → clock-Vigenère → columnar transposition) anywhere near exhausted?~~ — Tested as P1 (3-layer composite, then the geometric variant in the Physical/Geometric Pivot): null. These were sampled, not exhaustive; two non-periodic layers together remain on the open list.
10. ~~Do K2 coordinate digits constrain the clock state?~~ — Tested as P3 (K2 coordinate digits as HH:MM clock states): null.
11. ~~Does the 6-hour Berlin→CIA timezone offset (UTC+1 → UTC-5) act as a cipher shift modifier?~~ — Tested as P4 (±6h offsets, 10 states): null.

---

## 10. Related Documents

- [`docs/archive/K4-CLOCKS.html`](../archive/K4-CLOCKS.html) — Archived 2026-09-01, superseded by K4_ACTIVE_RESEARCH.md. Clock-based composite cipher theories (note: position labels for NORTHEAST in that document are incorrect; see Section 1 above)
- [`docs/archive/K4-T1.md`](../archive/K4-T1.md) — Archived 2026-09-01, superseded by K4_ACTIVE_RESEARCH.md. Physical-geometric resolver specification with toggle matrix
- [`docs/sources/CLOCK.md`](../sources/CLOCK.md) — World Clock geographic interpretation
- [`docs/sources/SANBORN.md`](../sources/SANBORN.md) — Sanborn clue research checklist
- [`docs/analysis/30_YEAR_GAP_COVERAGE.md`](30_YEAR_GAP_COVERAGE.md) — Classical cipher coverage assessment
- [`docs/analysis/K4_NEGATIVE_SPACE.md`](K4_NEGATIVE_SPACE.md) — Family-level eliminations and what is still open
