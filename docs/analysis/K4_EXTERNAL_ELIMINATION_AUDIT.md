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

## Second-pass checks against the published scripts (2026-10-22)

**Inspected upstream revision:** [`00696f393c861db2dcfaf3adfef29823c601cf7a`](https://github.com/zeyeteam-debug/kryptos-k4-eliminations/commit/00696f393c861db2dcfaf3adfef29823c601cf7a) (latest commit returned by GitHub when this pass was made). The shell environment could not reach GitHub to clone the external repository, so this is a source audit plus independent small constraint checks, not a full dependency-backed execution of their campaign. Relevant file blobs at that revision include `stack.py` (`ea039c5f5061e8950fe0c200f7efde8139bca412`), `gen.py` (`24615f881c2ff5ff5d17caeb447fb0e1693a50ca`), `anyalpha.py` (`d57d9346de17b3cbe1121af9272cef61f056f908`), `hillx.py` (`5877b1cee459a0b6a333b226732979b3d867a136`), and `rk_trans.py` (`5a7963c531edfe94cb9031ee888e173ecea6d4c3`).

### Independently checked: W-segment equality constraints

I reimplemented the pairwise condition directly from the ciphertext and the 24 confirmed crib letters. The five W positions are zero-based 20, 36, 48, 58, and 74; segment lengths are 20, 15, 11, 9, 15, and 22. Comparing the two crib blocks at equal within-segment offsets yields **9 cross-block pairs**. There are **0 equality contradictions** and exactly **1 same-plaintext/same-ciphertext coincidence**: plaintext R at positions 27 and 65 (zero-based) corresponds to ciphertext P at both positions. This reproduces the reported R→P observation, but it is one post-hoc coincidence, not a key recovery. The shuffle/null significance in the external README was not independently rerun.

### Any-alphabet periodic key: the visible runner does not certify every prose label

The current `scripts/anyalpha.py` defines `run(..., Pmax=12, strong=4)`; `runall()` calls it without overriding `Pmax`. Therefore its main transposition campaign covers periods **1–12**, consistent with README section 5, not periods 1–24. The issue's compact summary can be read more broadly than that actual campaign. README section 5 separately lists some direct periods as inconsistent and says the other periods have no check; it must not be summarized as an elimination of all direct periods 1–24.

I also independently enumerated the equality-preservation constraints from the 24 known letters for direct position-modulo periods 1–24. The result is:
- **Contradictory under a bijective per-period alphabet:** periods 1–7, 9, 10, 14, 15, 17, and 21.
- **Underdetermined by these crib pairs:** periods 8, 11–13, 16, 18, and 20, 22–24 (there are no crib pairs in the same residue class to compare).
- **Period 19 remains underdetermined:** one same-letter pair, R at positions 27 and 65, has the same ciphertext P at both positions and creates no contradiction. The two positions are 38 apart, exactly (2\times19).

This small independent check supports the README's period-19 caution and identifies why the remaining direct periods must not be called eliminated. There is a reproducibility nuance: the visible `anyalpha.py` runner only evaluates a class when it meets a configurable minimum of same-plaintext coincidences. Some periods that are contradicted solely by an injectivity violation have zero such coincidences and are skipped by that runner; the README's broader direct-period classification therefore needs a separate emitted certificate or an explicit pairwise audit like the one above. The exact direct result can be derived, but the existing runner output alone does not document all those eliminations.

### Running key + transposition: bounded corpus, no null in the inspected entry point

`scripts/rk_trans.py` searches a finite set of local corpora: NLTK Gutenberg texts, inaugural addresses, State of the Union texts, and concatenated K1–K3 plaintext. It strips non-A–Z characters and inserts separators between files. It enumerates the requested columnar permutations and three key arithmetic rules against the 24 crib-implied key values. Its `__main__` path constructs and checks a planted width-6 running-key control, then runs the K4 searches; it does **not** run a shuffled-ciphertext null in that path. Thus the defensible result is “no match in these loaded sources, normalizations, widths, permutations, and arithmetic rules,” not “no running key exists.” A full independent rerun also requires the external NLTK corpus files, which were not present in this environment.

### Hill script: distinguish a strong hit from every consistent system

`scripts/hillx.py` tests direct aligned Hill blocks of sizes 2–5, all offsets, ST/KA, and an affine/block-period extension parameter (L=0\ldots6). It only includes blocks whose positions are all within the known crib positions; it does not itself compose Hill with transposition. It reports a “hit” only when a consistent system has redundancy at least 2, while separately retaining lower-redundancy consistency in the `tested` list. Accordingly, a count of zero **strong hits** is not, by itself, proof that every matrix/affine configuration is inconsistent. The broader README claim about Hill plus columnar transposition depends on other scripts and needs to be audited separately, including the exact width/order ranges and all underconstrained cases.

### Period-19 experiment: scope and clean-checkout inputs

The current README's section 35 points to `p19sa.py` and `numcode.py`; both exist at the inspected upstream revision. Although the latest upstream commit deleted `scripts/q4p19.py` and `scripts/trisa.py`, those deletions alone do **not** invalidate section 35. The current references need to be distinguished from older script names rather than treating a deletion as proof that the result disappeared.

There is, however, a concrete clean-checkout reproducibility detail: the README's generic run instructions mention `quad.pkl`, while `p19sa.py` reads or creates `quad.npy` and builds the quadgram model from `texts/nltk_data/packages/corpora/gutenberg/*.txt` if that file is absent. Its planted control also reads `texts/carter_vol1.txt`. Those corpus inputs and the generated/model file must be present or documented for the advertised control and period-19 run to reproduce. The reported 1-success-in-12 planted-control rate is itself a material limitation: the README estimates about a 35% chance that 12 runs would all miss a valid solution at that observed success rate. Therefore “no crib-consistent English decryption found in these annealing runs” is a bounded stochastic result, not an exhaustive elimination of period-19 Quagmire IV.

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
