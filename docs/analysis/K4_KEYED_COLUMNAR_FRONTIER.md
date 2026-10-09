# K4 Keyed-Columnar Frontier: Long Clue-Derived Keys

**Status:** bounded exact crib test; current result is a null, not a family-wide elimination.

## Question

Could a World Clock city label (or a combination of a city label and a known K1/K2 key) determine a conventional column-read order for a wide grid, while a periodic substitution supplies the other layer?

The ordinary columnar search has exhaustively covered all column permutations for widths 2–14, but cannot enumerate every permutation at widths 15–26. A keyword-derived order gives one explicit permutation per key, making a finite exact test possible without sampling random column orders.

## What the new check tests

The implementation is `kryptos.k4.keyed_columnar_frontier`.

- **Transposition-key candidates:** city labels already transcribed in `world_clock_cities.CONFIRMED_CITIES`, plus each such label concatenated in both orders with `KRYPTOS`, `PALIMPSEST`, or `ABSCISSA`.
- **Widths:** 15–26 only. Widths 2–14 are excluded because the existing all-permutations scans already cover those widths.
- **Column order:** stable alphabetical ranking of the keyword's letters, with repeated letters retaining their left-to-right order.
- **Substitution layer:** Vigenère, Beaufort, Variant Beaufort, and the two existing KRYPTOS-tableau Quagmire III variants.
- **Alphabet seeds:** KRYPTOS, PALIMPSEST, and ABSCISSA.
- **Layer order:** substitution before transposition and transposition before substitution.
- **Periods:** 1–22.
- **Acceptance gate:** all 24 confirmed K4 crib letters must agree, and at least eight of the crib constraints must be repeated-key-slot constraints for the candidate layer order. We report underconstrained crib-consistent matches separately instead of treating them as discoveries. Language scoring is not used to rescue a mismatch.

Equivalent keywords that induce the same column permutation are deduplicated. The result reports the number of candidate strings, unique permutations, checks, raw crib-consistent candidates, and any underconstrained examples so coverage is auditable.

## Validation

The tests include a planted positive control using a known 16-character World Clock city label as a columnar keyword. It encrypts a known 97-character plaintext with a periodic Vigenère key and requires the checker to recover the exact order and period. A second test runs the same finite family against K4.

Run:

```bash
pytest tests/functional/test_k4_keyed_columnar_frontier.py -q
```

## Interpretation and limits

A null result means only that none of the explicitly generated long keyword-derived column orders satisfies the confirmed cribs under the stated substitution families, alphabet seeds, periods, and layer orders.

It does **not** rule out:

- all possible width-15–26 column orders;
- disrupted, incomplete, route-based, or other irregular transpositions;
- country names, since the repository does not yet have a sourced city-to-country mapping for the full clock;
- a per-character lookup into the World Clock's 24 sectors;
- length-changing masking or a transformation outside the tested cipher families.

The city list is a photographed, partial transcription, not a complete authoritative list of all 146 plates. No missing labels are fabricated. This test is meant to close one finite branch before physical capture work, not to claim K4 is exhausted.
