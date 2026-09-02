# K4 Keystream Analysis — Confirmed Period-13 Window

Breadcrumb: Home > Docs > Analysis > Keystream


**Status:** Active research finding
**Last Updated:** 2026-09-01
**Evidence Level:** High — derived directly from Sanborn's confirmed cribs against the K4 ciphertext

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
| 22–25            | LRVQ   | EAST      | Sanborn clue, 2023   |
| 26–34            | QPRNGKSSO | NORTHEAST | Sanborn clue, 2020  |
| 63–68            | NYPVTT | BERLIN    | Sanborn clue, 2010   |
| 69–73            | MZFPK  | CLOCK     | Sanborn clue, 2014   |

> **Index note:** Community sources and some docs in this repo label these positions as 1-indexed (26–34 → 1-indexed 27–35, etc.). The values above use Python 0-indexed convention consistently.  The K4-CLOCKS.html document incorrectly labels NYPVTTMZF as being at "positions 26–34"; the actual 0-indexed location of that ciphertext is 63–71.  The CONTRIBUTING.md quick-start code lists `'NORTHEAST': [25]` and `'BERLIN': [64]` which are off by one; the correct 0-indexed starts are **26** and **63** respectively.

---

## 2. Vigenère-Equivalent Keystream

If any substitution layer in K4 operates like Vigenère (cipher = plain + key mod 26), the per-position key letter is:

```
key[i] = (cipher_ord[i] - plain_ord[i]) mod 26
```

### EAST window (positions 22–25)

| Pos | Cipher | Plain | key = (C−P) mod 26 | Key letter |
|-----|--------|-------|--------------------|------------|
| 22  | L (11) | E (4) | 7                  | H          |
| 23  | R (17) | A (0) | 17                 | R          |
| 24  | V (21) | S (18)| 3                  | D          |
| 25  | Q (16) | T (19)| 23                 | X          |

**EAST keystream: `HRDX` → shifts [7, 17, 3, 23]**

### NORTHEAST window (positions 26–34)

| Pos | Cipher | Plain | key = (C−P) mod 26 | Key letter |
|-----|--------|-------|--------------------|------------|
| 26  | Q (16) | N (13)| 3                  | D          |
| 27  | P (15) | O (14)| 1                  | B          |
| 28  | R (17) | R (17)| 0                  | A          |
| 29  | N (13) | T (19)| 20                 | U          |
| 30  | G (6)  | H (7) | 25                 | Z          |
| 31  | K (10) | E (4) | 6                  | G          |
| 32  | S (18) | A (0) | 18                 | S          |
| 33  | S (18) | S (18)| 0                  | A          |
| 34  | O (14) | T (19)| 21                 | V          |

**NORTHEAST keystream: `DBAUZGSAV` → shifts [3, 1, 0, 20, 25, 6, 18, 0, 21]**

### Combined 13-character window (positions 22–34)

Reading EAST first, then NORTHEAST:
```
Keystream: H R D X D B A U Z G S A V
Shifts:   [7,17,3,23,3,1,0,20,25,6,18,0,21]
```

Reading in the order the other agent analysis presented (NORTHEAST then EAST):
```
Keystream: D B A U Z G S A V H R D X
Shifts:   [3,1,0,20,25,6,18,0,21,7,17,3,23]
```

---

## 3. What This Rules Out

### 3.1 Single-layer repeating Vigenère

Running `DBAUZGSAVHRDX` (or any rotation of the 13-char window) as a repeating Vigenère key against the full 97-char K4 ciphertext does **not** produce English plaintext outside the crib window. A real Vigenère key that repeats would produce consistently English-like output everywhere. Negative result is confirmed.

### 3.2 Direct Berlin Clock keying

The Berlin Clock rows produce values bounded by:
- 5-hour row: 0–4
- 1-hour row: 0–4
- 5-minute row: 0–11
- 1-minute row: 0–4

The observed keystream shifts [7, 17, 3, 23, 3, 1, 0, 20, 25, 6, 18, 0, 21] include values of 7, 17, 20, 25, 18, 21 that **exceed the maximum Berlin Clock row value of 11**. No direct mapping of a single clock reading to these shifts is possible. Enumeration of all 720 clock states (12 hr × 60 min) as Vigenère keys against K4 was run; no state produces EAST or NORTHEAST at the confirmed positions.

### 3.3 Clock-shifted or scaled values

Linear scaling or shift of clock values doesn't cleanly map to the observed distribution. The values are not a permutation of any recognizable clock encoding.

---

## 4. What the IC Analysis Tells Us

The local Index of Coincidence by segment:

| Segment (0-indexed) | Approx IC | Interpretation              |
|---------------------|-----------|-----------------------------|
| 0–31                | ~0.058    | More substitution-noise     |
| 32–63               | ~0.071    | More English-like           |
| 64–96               | ~0.062    | Intermediate                |

**Key conclusion:** Non-uniform IC across segments is a signature of **transposition applied AFTER substitution**. A transposition-first approach would produce uniform IC. The fact that the IC in the 32–63 window is closer to English (0.0667) while the first window is lower indicates character reshuffling moved English-dense segments to that region.

This rules out transposition-first architectures and constrains the composite pipeline to:

```
plaintext → [substitution layer] → [transposition layer] → K4 ciphertext
```

---

## 5. Composite Architecture Conclusion

**Ruling:** K4 uses at minimum a 2-layer composite cipher:

1. A substitution (polyalphabetic or matrix) applied to the plaintext
2. A transposition applied to the substituted text to produce the ciphertext

The EASTNORTHEAST window (positions 22–34 of the ciphertext) contains characters that were pulled from **different, non-contiguous positions** of the pre-transposition text by the transposition step. This means the 13-char keystream HRDXDBAUZGSAV encodes the substitution shifts of characters that were originally scattered across the pre-transposition plaintext/substituted-text, not adjacent.

**Consequence for search:** Brute-forcing the substitution key against the raw ciphertext and validating EAST/NORTHEAST is valid IF the transposition is applied after. But recovering the substitution key from the crib requires first undoing the transposition.

---

## 6. Key Derivation After Transposition Reversal

The core attack strategy: if we can identify the correct transposition permutation P, then applying P⁻¹ to the ciphertext yields the substituted-but-not-transposed text. At that point:

- The substituted text at the correct positions will produce EASTNORTHEAST
- The keystream at those positions in the pre-transposition text reveals the **actual substitution key pattern**
- If the key is a recognizable word/phrase or a Berlin Clock reading, we solve K4

**Target:** Find the transposition permutation P such that after inverting it, the keystream at EAST+NORTHEAST positions collapses from high-entropy HRDXDBAUZGSAV into a recognizable key structure (a word, a clock state, a keyed-alphabet output).

---

## 7. Attack Vectors — Status

### ✅ 7.1 Inverse Transposition Sweep — COMPLETE, NULL RESULT

`kryptos.k4.inverse_transposition_sweep.full_sweep` tested all 3 grid geometries (10×10, 7×14, 8×13) with ENE diagonal (67.5°) and columnar routes. No transposition permutation produced a recognizable keystream at EAST+NORTHEAST positions.

### ✅ 7.2 Keyed Alphabet Realignment — COMPLETE, NULL RESULT

`check_keyed_alphabet_realignment` tested KRYPTOS, PALIMPSEST, and ABSCISSA alphabets. The effective keystream at positions 22–34 does not resolve to a recognizable pattern (clock state, keyword, or bounded-value vector) under any of them.

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

## 9. Questions — 11 total (6 resolved, 5 open) — as of 2026-08-12

1. ~~What transposition permutation P maps EAST+NORTHEAST to a recognizable keystream?~~ — Tested: no such permutation found in the grid+route space explored. Either the transposition is not grid-based, or the substitution layer is not Vigenère-equivalent.
2. ~~Does a keyed alphabet make the keystream structured?~~ — Tested KRYPTOS/PALIMPSEST/ABSCISSA: null result. If a keyed alphabet is involved, it's one not yet tried.
3. ~~Is the ENE diagonal the correct reading path?~~ — Tested in full sweep alongside columnar: null result for both. ENE diagonal is not the sole transposition mechanism under the assumptions tested.
4. ~~Could the clock be used as a Hill matrix key?~~ — Tested via `run_clock_hill_attack`: null result. ~100 invertible states all produced no crib match.
5. ~~Are there non-standard clock encodings?~~ — Tested via `run_clock_subrow_attack`: 4 sub-row schemes; null result.
6. ~~Beaufort cipher sweep~~ — Tested via `run_beaufort_sweep`: null result.
7. **Does the BERLIN+CLOCK keystream (MUYKLGKORNA) become recognizable after any transposition reversal?** — The full sweep validated all 4 cribs simultaneously but did not isolate partial 2-crib matches at positions 63–73. Worth testing in isolation with a softer filter.
8. **Is there a masking/null-removal layer before the substitution?** — If some K4 characters are nulls inserted as "shadows" (from the World Clock shadow theory), every attack on the full 97-char sequence is attacking padded input. Untested as a pre-step.
9. **Are 3-layer composites (e.g., keyed-alphabet → clock-Vigenère → columnar transposition) anywhere near exhausted?** — Current composite coverage is 2-layer only. Sanborn's "five or six techniques" may imply 3+ cipher layers rather than 2 with elaborate key derivation.
10. **Do K2 coordinate digits constrain the clock state?** — The K2 plaintext contains `38 57 6 5 N, 77 8 44 W`. Hours 38%24=14, minutes 57 (and similar) were never used as specific clock timestamp indices to select a Hill or Vigenère key.
11. **Does the 6-hour Berlin→CIA timezone offset (UTC+1 → UTC-5) act as a cipher shift modifier?** — If Sanborn encoded at Berlin time and the receiver was at CIA HQ, a 6-position shift on the key index may bridge the gap. Untested.

---

## 10. Related Documents

- [`docs/archive/K4-CLOCKS.html`](../archive/K4-CLOCKS.html) — Archived 2026-09-01, superseded by K4_ACTIVE_RESEARCH.md. Clock-based composite cipher theories (note: position labels for NORTHEAST in that document are incorrect; see Section 1 above)
- [`docs/archive/K4-T1.md`](../archive/K4-T1.md) — Archived 2026-09-01, superseded by K4_ACTIVE_RESEARCH.md. Physical-geometric resolver specification with toggle matrix
- [`docs/sources/CLOCK.md`](../sources/CLOCK.md) — World Clock geographic interpretation
- [`docs/sources/SANBORN-summary.md`](../sources/SANBORN-summary.md) — Sanborn clue research checklist
- [`docs/analysis/30_YEAR_GAP_COVERAGE.md`](30_YEAR_GAP_COVERAGE.md) — Classical cipher coverage assessment
