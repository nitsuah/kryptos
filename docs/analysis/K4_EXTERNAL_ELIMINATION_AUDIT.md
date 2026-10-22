# Audit notes for external K4 elimination claims in issue #244

> 🧭 [kryptos](../../README.md) · [K4 Negative Space](K4_NEGATIVE_SPACE.md) · [World Clock source audit](K4_WORLD_CLOCK_HISTORICAL_SOURCES.md) <!-- nav -->

**Status:** source-level review; not an independent rerun of the external scripts.  
**Related issue:** [#244](https://github.com/nitsuah/kryptos/issues/244)  
**External repository:** [zeyeteam-debug/kryptos-k4-eliminations](https://github.com/zeyeteam-debug/kryptos-k4-eliminations)

## Purpose

Issue #244 describes several crib-constrained searches not yet fully represented in this repository's ledger. This note captures an initial audit of the published README and implementation scripts, narrows claims to the code inspected, and identifies the work needed before importing any negative result as a project-level elimination.

This is deliberately **not** a statement that the external results are wrong. It distinguishes (a) a reported result, (b) a scope visible in the implementation, and (c) an independently reproduced result. Only (c) should be promoted to the local elimination ledger.

## Initial source-level review

| Branch from issue #244 | What the inspected source indicates | Safe current conclusion |
|---|---|---|
| Five W's as segment separators | scripts/wseg.py compares key values at overlapping in-segment offsets under standard and KRYPTOS alphabets and common Vigenère/Beaufort-style arithmetic; scripts/anyalpha.py separately checks equality constraints for arbitrary alphabets. | The specific restart-key models can be tested exactly against repeated-plaintext-letter constraints. This does not prove every possible W-separated process impossible. The reported R→P same-offset coincidence is a hypothesis lead, not evidence of a key. |
| Grille/light masks over tableau or panel | scripts/mask.py enumerates specified grids, widths, offsets, starting rows and serpentine options, then checks whether the positions sharing a key column agree with crib-implied key characters. Its test code includes a planted example and shuffled inputs. | The tested finite mask family can be ruled out only for its explicit grid representations, parameter bounds and arithmetic rules. “Any possible grille” is too broad. |
| Hill matrices | scripts/hillx.py solves crib constraints over GF(2) and GF(13) for selected block sizes, alignments and a limited periodic-affine extension. | The code is a useful exact constraint approach, but the README/issue summary must be reconciled with actual widths, affine variants, transposition order and underconstrained cases before quoting one global “all matrices” elimination. |
| PK-style multi-layer pipelines | scripts/layers3.py uses a fixed word list and explicit transposition/substitution compositions; it includes positive-control constructions for PK4/PK6-like planted cases. | The result applies to the enumerated vocabulary, permutations, layer order and alphabet conventions. It does not cover arbitrary keys or every pipeline that might be called “PK-style.” |
| Running key + transposition | scripts/rk_trans.py loads specific text corpora, constructs a finite set of columnar permutations, and checks the crib-implied stream at candidate alignments. Its main routine includes a planted columnar/running-key control. | Zero matches excludes the supplied corpora, text normalization, widths, permutation set and key arithmetic only. The inspected main routine does not itself run a shuffled-ciphertext null for this branch, so do not repeat the issue's blanket “every test has a null” claim for it. |
| Arbitrary-alphabet periodic key, periods 1–24 | scripts/anyalpha.py encodes equality constraints for repeated letters within periodic classes and scans several transposition families. The script's own comment says period 19 is underconstrained. | Period 19 must remain explicitly unresolved where the crib constraints do not identify the class; absence of a hit elsewhere is limited to the listed transposition families and periods. |
| Weltzeituhr face transcription | The README gives a photo-based 2017 upper/lower transcription and discusses a pre-1997 problem. | This is a useful candidate data set, not a historical 1990 transcript. See [the source audit](K4_WORLD_CLOCK_HISTORICAL_SOURCES.md). |

## Reproducibility caveats

- The issue body says every test has both a planted positive control and a shuffled null. The inspected running-key/transposition script contains a planted control, but the shown main routine does not run a shuffled-ciphertext null for that branch. Verify all branches individually before repeating the blanket statement.
- A positive control proves the checker can recover the planted construction represented by that control; it does not prove that the search space matches every interpretation of a broader cipher-family name.
- A shuffled null is most informative for statistical or score-based claims. For an exact constraint search, the key audit is instead whether the constraints are complete for the claimed family and whether a planted valid construction is recovered.
- “Zero matches” is not the same as “no valid solution” when some configurations are underconstrained, omitted, sampled rather than exhaustive, or fail to represent all possible mappings.
- Source comments and README summaries are evidence of author intent, not substitutes for rerunning commands and preserving outputs.

## Reproduction plan

Before adding a row to docs/analysis/K4_NEGATIVE_SPACE.md or the machine-readable hypothesis ledger:

1. Pin the external repository to an immutable commit SHA and record the SHA in the run artifact.
2. Record the exact command, Python/runtime and dependencies, corpus versions and text-normalization rules.
3. Run each branch's positive control and confirm that the expected planted model is found.
4. Run the K4 search and preserve machine-readable outputs, including all underconstrained configurations and excluded ranges.
5. Run a shuffled null when interpreting scores or near-matches; report the number and distribution of controls rather than only a best score.
6. Independently review the mathematical coverage claim, especially modulus assumptions for Hill constraints and the repeated-letter invariants for arbitrary alphabets.
7. Compare the verified ranges against the existing ledger to avoid duplicating work or overstating coverage.

## Scope decision

Do not close issue #244 solely because PR #249 merged or because the external repository reports zero matches. PR #249 added useful 2017 transcription infrastructure, but this repository still needs a sourced historical transcription and a verified, scope-specific reproduction of the independent elimination claims before the whole issue can be considered complete.
