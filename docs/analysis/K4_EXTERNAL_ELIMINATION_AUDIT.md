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
| Arbitrary-alphabet periodic key | At audited revision `00696f393c861db2dcfaf3adfef29823c601cf7a`, `scripts/anyalpha.py`'s `runall()` invokes identity and transposition scans with the default `Pmax=12`; the direct no-transposition diagnostic discussed in README §5 considers periods 1–24 separately. The README itself calls period 19 underconstrained. | Do not describe the `runall()` transposition campaign as periods 1–24. The independent direct crib-pair check contradicts periods 1–7, 9–10, 14–15, 17, and 21 under the tested bijective model; periods with no same-residue crib pair remain underdetermined, including period 19. These are distinct results and should not be conflated. |
| Weltzeituhr face transcription | The README gives a photo-based 2017 upper/lower transcription and discusses a pre-1997 problem. | This is a useful candidate data set, not a historical 1990 transcript. See [the source audit](K4_WORLD_CLOCK_HISTORICAL_SOURCES.md). |

## Reproducibility caveats

- The issue body says every test has both a planted positive control and a shuffled null. The inspected running-key/transposition script contains a planted control, but the shown main routine does not run a shuffled-ciphertext null for that branch. Verify all branches individually before repeating the blanket statement.
- A positive control proves the checker can recover the planted construction represented by that control; it does not prove that the search space matches every interpretation of a broader cipher-family name.
- A shuffled null is most informative for statistical or score-based claims. For an exact constraint search, the key audit is instead whether the constraints are complete for the claimed family and whether a planted valid construction is recovered.
- “Zero matches” is not the same as “no valid solution” when some configurations are underconstrained, omitted, sampled rather than exhaustive, or fail to represent all possible mappings.
- Source comments and README summaries are evidence of author intent, not substitutes for rerunning commands and preserving outputs.

## Second-pass checks against the published scripts (2026-10-22)

**Inspected upstream revision:** [`00696f393c861db2dcfaf3adfef29823c601cf7a`](https://github.com/zeyeteam-debug/kryptos-k4-eliminations/commit/00696f393c861db2dcfaf3adfef29823c601cf7a) (latest commit returned by GitHub when this pass was made). The shell environment could not reach GitHub to clone the external repository, so this is a source audit plus independent small constraint checks, not a full dependency-backed execution of their campaign. Relevant file blobs at that revision include `stack.py` (`ea039c5f5061e8950fe0c200f7efde8139bca412`), `gen.py` (`24615f881c2ff5ff5d17caeb447fb0e1693a50ca`), `anyalpha.py` (`d57d9346de17b3cbe1121af9272cef61f056f908`), `hillx.py` (`5877b1cee459a0b6a333b226732979b3d867a136`), `hillT.py` (`79714bcde57077225baecc645708dbb8570ae16d`), `hillchk.py` (`e6648a8d7911a24f8507571e381b33095add1bdd`), `stack2ct.py` (`4e2456c9f7cb31721a305575808ceeb34c24186b`), `stackT.py` (`6146b2788335ebcb8af7838ab3c2fe2f4862ae5a`), `rk_trans.py` (`5a7963c531edfe94cb9031ee888e173ecea6d4c3`), `carter_run.py` (`e955e975183e7a836c95cc40dfd9aa33343a8a39`), `p19sa.py` (`4165340a33ce4042f4b3fb73e308502966f2e16e`), and `numcode.py` (`7041b42a64fccde5b8c6d575b5c85e267217f748`).

### Independently checked: W-segment equality constraints

I reimplemented the pairwise condition directly from the ciphertext and the 24 confirmed crib letters. The five W positions are zero-based 20, 36, 48, 58, and 74; segment lengths are 20, 15, 11, 9, 15, and 22. Comparing the two crib blocks at equal within-segment offsets yields **9 cross-block pairs**. I separately calculated the standard key value required at each paired position for all three arithmetic rules (Vigenère, Beaufort, and Variant Beaufort): for ST, only **2/9** pairs agree and **7/9** contradict a single restart key; for KA, only **1/9** agree and **8/9** contradict. This independently reproduces the exact ST/KA elimination for the stated W-restart model. For independent arbitrary alphabets per in-segment offset, there are **0 equality contradictions** and exactly **1 same-plaintext/same-ciphertext coincidence**: plaintext R at positions 27 and 65 (zero-based) corresponds to ciphertext P at both positions. This reproduces the reported R→P observation, but it is one post-hoc coincidence, not a key recovery. The shuffle/null significance in the external README was not independently rerun.

### Any-alphabet periodic key: the visible runner does not certify every prose label

The current `scripts/anyalpha.py` defines `run(..., Pmax=12, strong=4)`; `runall()` calls it without overriding `Pmax`. Therefore its main transposition campaign covers periods **1–12**, consistent with README section 5, not periods 1–24. The issue's compact summary can be read more broadly than that actual campaign. README section 5 separately lists some direct periods as inconsistent and says the other periods have no check; it must not be summarized as an elimination of all direct periods 1–24.

I also independently enumerated the equality-preservation constraints from the 24 known letters for direct position-modulo periods 1–24. The result is:
- **Contradictory under a bijective per-period alphabet:** periods 1–7, 9, 10, 14, 15, 17, 21, and 25.
- **Underdetermined by these crib pairs:** periods 8, 11–13, 16, 18, 20, and 22–24 (there are no crib pairs in the same residue class to compare).
- **Period 19 remains underdetermined:** one same-letter pair, R at positions 27 and 65, has the same ciphertext P at both positions and creates no contradiction. The two positions are 38 apart, exactly (2\times19).

This small independent check supports the README's period-19 caution and identifies why the remaining direct periods must not be called eliminated. There is a reproducibility nuance: the visible `anyalpha.py` runner only evaluates a class when it meets a configurable minimum of same-plaintext coincidences. Some periods that are contradicted solely by an injectivity violation have zero such coincidences and are skipped by that runner; the README's broader direct-period classification therefore needs a separate emitted certificate or an explicit pairwise audit like the one above. The exact direct result can be derived, but the existing runner output alone does not document all those eliminations.

### PK4-style two-period-key stack: the wrapper's threshold hides consistent width-7 cases

The issue's convention defines “excluded” as **no configuration in the stated space consistent with all 24 cribs**. The external `scripts/stack2ct.py` does not report every consistent configuration: it calls the exact union-find `check`, which returns `-1` on a contradiction and a nonnegative cycle/redundancy count for a consistent system, but `scan` only records results when `r >= thr` with `thr=4`. Therefore “zero hits” from this wrapper means zero configurations meeting the four-redundant-check threshold, not necessarily zero consistent key assignments.

The README reports a shuffled-null result for this family (six threshold-level hits), but the inspected `stack2ct.py` `__main__` path only runs its planted control and the K4 scan; it contains no shuffle/null invocation. The same is true of the visible `stackT.py` entry point. Those null figures may have been generated in a separate manual run, but the exact command and output artifact are not in the audited scripts. This does not change the exact consistency check above; it does mean the null claim is not reproducible from the published entry points as-is.

The actual `stack2ct.py` loop is narrower than “any key lengths ≤12”: it starts at a=2, requires b>a, and skips pairs where `b % a == 0`. The skipped commensurate cases reduce to a single period-b stream because the period-a contribution repeats inside period b; period a=1 is likewise absorbable into the other key, but those reductions should be stated rather than hidden in “any keys.”

I independently ported `stackT.check` and the published `gen.colperms` permutation generator, then enumerated the width-7 columnar orders and inverses against the confirmed crib. At width 7, across ST/KA, both signs, and all permitted key lengths, I found **17 consistent cases** for periods (a=11,b=12), each with only 2 or 3 redundant checks. They are intentionally filtered out by the wrapper's threshold. The cases are underconstrained and do not constitute a recovered plaintext, but they contradict a strict reading of “no configuration consistent with all 24 cribs.” The claim should be scoped to “no candidate with at least four redundant checks”; the under-threshold consistent cases should be retained in the audit ledger rather than silently treated as eliminated.

| Alphabet | Columnar order (0-based columns) | Direction/sign (e) in (D=C-eP) | Redundancy |
|---|---|---:|---:|
| ST | (2, 5, 0, 3, 1, 6, 4) | -1 | 2 |
| ST | (3, 1, 6, 5, 0, 4, 2) | +1 | 3 |
| ST | (4, 2, 5, 3, 1, 0, 6) | -1 | 2 |
| ST | (6, 0, 2, 3, 5, 1, 4) | +1 | 2 |
| ST | inverse of order (1, 4, 0, 2, 3, 5, 6) | +1 | 2 |
| ST | inverse of order (2, 4, 0, 1, 3, 5, 6) | +1 | 2 |
| KA | (1, 4, 5, 0, 2, 6, 3) | -1 | 2 |
| KA | (1, 6, 4, 0, 5, 3, 2) | -1 | 2 |
| KA | (4, 1, 3, 2, 5, 0, 6) | +1 | 3 |
| KA | (4, 6, 2, 1, 5, 3, 0) | +1 | 2 |
| KA | (6, 5, 2, 4, 0, 3, 1) | +1 | 2 |
| KA | inverse of order (0, 3, 5, 1, 4, 6, 2) | +1 | 2 |
| KA | inverse of order (0, 3, 5, 2, 4, 6, 1) | +1 | 2 |
| KA | inverse of order (1, 3, 5, 0, 4, 6, 2) | +1 | 2 |
| KA | inverse of order (1, 3, 5, 2, 4, 6, 0) | +1 | 2 |
| KA | inverse of order (2, 3, 5, 0, 4, 6, 1) | +1 | 2 |
| KA | inverse of order (2, 3, 5, 1, 4, 6, 0) | +1 | 2 |

One of the width-7 cases is a concrete witness to the consistency claim. Using the forward columnar order `(2, 5, 0, 3, 1, 6, 4)` (where (M[i]) is the ciphertext position of plaintext position (i)), ST arithmetic, Beaufort sign, and ciphertext-indexed periods 11 and 12, one union-find assignment gives:

- period-11 key: `QQWQUPTBQLT`
- period-12 key: `FAMTEATDSNDO`
- decrypted text: `GAHMEOYOJPEYCYDXYEKLJEASTNORTHEASTGLOBFNSYFMPDWHURWQPPBGZRCMZIKBERLINCLOCKSGPUATAUAYWVUSPQQAREQET`

The resulting text has `EASTNORTHEAST` at zero-based positions 21–33 and `BERLINCLOCK` at positions 63–73, exactly. It is not plausible English; its value here is narrowly logical: **a consistent key/transposition assignment exists**, so this family is not exactly eliminated under the issue's stated definition. This witness was independently generated from the published union-find constraints, not copied from the external README.

This is a source-level scope correction backed by an independent reproduction of the small exact constraint check. It does not claim that these low-redundancy fits are plausible English decryptions or that the broader PK family is solved.

### Companion PK-style stack: (Q(a)_{PT} ightarrow T ightarrow Q(b)_{CT}) is inconsistent in the stated range

To keep the previous under-threshold result from being overgeneralized, I separately ported `stackT.py`'s model, where the first periodic key is indexed by plaintext position, then a columnar transposition is applied, then the second key is indexed by ciphertext position. For widths 2–7, every column order and inverse, periods (a,b=2\ldots8), both ST/KA alphabets, and both signs, the independent check evaluated **2,317,504 configurations and found zero consistent systems**. Unlike `stack2ct.py`, this wrapper's result is not just a four-redundancy filter: the union-find check returned contradiction for every configuration in the stated search range.

This is a bounded exact elimination for **(Q(a)_{PT} ightarrow T ightarrow Q(b)_{CT})** under those width/period/alphabet constraints. It is a different model from the preceding **(T ightarrow Q(a)_{CT} ightarrow Q(b)_{CT})** search, which has 17 under-threshold consistent width-7 cases and must not be called exactly eliminated. The published `stackT.py` planted control uses periods 5 and 9, so its second period lies just outside this scan's (b\leq8) range; that control validates the solver path but not every searched parameter combination.

### Running key + transposition: bounded corpus, no null in the inspected entry point

`scripts/rk_trans.py` searches a finite set of local corpora: NLTK Gutenberg texts, inaugural addresses, State of the Union texts, and concatenated K1–K3 plaintext. It strips non-A–Z characters and inserts separators between files. It enumerates the requested columnar permutations and three key arithmetic rules against the 24 crib-implied key values. Its `__main__` path constructs and checks a planted width-6 running-key control, then runs the K4 searches; it does **not** run a shuffled-ciphertext null in that path. Thus the defensible result is “no match in these loaded sources, normalizations, widths, permutations, and arithmetic rules,” not “no running key exists.” A full independent rerun also requires the external NLTK corpus files, which were not present in this environment.

The separate Carter Vol. I campaign in `scripts/carter_run.py` loads `texts/carter_vol1.txt`, searches both forward and reversed text (separated so matches cannot cross the join), and enumerates K3-style rotations, cylinder routes, opposite-direction rotations, and columnar widths 2–9. Its own `__main__` path does **not** run a planted control or shuffled null. The shared search function is exercised by the Moby Dick control in `rk_trans.py`, but that is one width-6 control, not a per-family Carter control. The exact negative result is still scoped to the loaded Carter text and enumerated permutations; the blanket issue claim that every test has its own control and null is not supported by this entry point.

### Dictionary-scale PK9 pipeline: exact scope depends on the invocation

The visible `scripts/dictsearch.py` is an exact crib-hash lookup, not a score threshold. It builds word keys from `texts/dwyl/words.txt`, uppercases them, and filters to lengths **2–30**; “370k words” is therefore the source-list scale, not literally every entry regardless of length. It generates the 752 documented spiral read/write routes and tests both route/columnar orders.

One reproducibility detail matters: the script's default column widths are `[2,3,4,5,6]`; widths 7 and 8 are included only when supplied as command-line arguments. The README claims widths 2–8 but does not record the exact command line used for that run. The code supports the claimed range, but a clean reproduction must explicitly invoke it with `2,3,4,5,6,7,8`. This is a command-documentation gap, not evidence that the wider run was not performed. I did not independently rerun the 370k-word campaign because the dictionary file is part of the external repository and the shell could not clone it.

### Hill script: distinguish a strong hit from every consistent system

`scripts/hillx.py` tests direct aligned Hill blocks of sizes 2–5, all offsets, ST/KA, and an affine/block-period extension parameter (L=0\ldots6). It only includes blocks whose positions are all within the known crib positions; it does not itself compose Hill with transposition. It reports a “hit” only when a consistent system has redundancy at least 2, while separately retaining lower-redundancy consistency in the `tested` list. Accordingly, a count of zero **strong hits** is not, by itself, proof that every matrix/affine configuration is inconsistent. The broader README claim about Hill plus columnar transposition depends on other scripts and needs to be audited separately, including the exact width/order ranges and all underconstrained cases.

### Independent port of `hillx.py`: underconstrained systems are being filtered out

I independently ported the visible `solve_mod`, block-selection, and `test` logic from `stack.py` / `hillx.py` and ran its declared scan against the confirmed cribs. Across **196 testable configurations**, 118 return mathematically consistent row systems, but **every one has zero redundant equations** and therefore fails the script's “strong hit” threshold. Breakdown by block size: 2×2 = 0 consistent / 28 tested; 3×3 = 11 / 42; 4×4 = 41 / 56; 5×5 = 66 / 70. The 11 consistent 3×3 cases directly contradict a blanket reading of “inconsistent for 2×2 and 3×3” unless a separate test proves those 3×3 systems cannot yield an invertible matrix.

Why this happens: `hillx.py` only uses blocks fully contained inside the known crib positions, then adds up to six block-class offset variables. It does not use known crib letters that fall in a partial block for a given alignment; for example, the offset-0 3×3 scan uses 21 of the 24 crib letters and leaves positions 33, 72, and 73 out of its equations. It also ignores any trailing incomplete ciphertext block. For 3×3 and larger, the equations it does use often do not constrain the row coefficients enough to produce even one redundant equation. The code reports a hit only when redundancy is at least 2, and it does not impose the Hill invertibility condition while solving these systems. Thus the reproducible conclusion from this script is **no strongly constrained candidate found**, not “all 3×3–5×5 matrix systems are inconsistent.” A separate invertibility-aware solve would be required before classifying the consistent 3×3 cases as eliminated.

### Hill + columnar: a README/code dimension mismatch at width 9

The external README's section 3 says the Hill-3×3 → columnar family has no hits at widths 2–8, then describes width-9 hits with “3 equations for 2 unknowns” and 276 invertible matrices that decrypt to gibberish. The code resolves the dimension ambiguity: `scripts/hillchk.py` calls `run(CT0,[9],(2,),'K4')`, so the width-9 follow-up is specifically **2×2 Hill**, not 3×3 Hill. In `scripts/hillT.py`, the transposition-first `orderA` path is only invoked for `n == 2` or widths `W <= 8`, so the 3×3 width-9 path is not executed there.

This means the issue body's compressed statement “Hill ... with columnar widths 2–9 in both orders: 0 valid” is too broad. The README itself describes a width-9 case with **276 invertible matrix candidates that satisfy the crib equations**, then rejects them on English-scoring grounds. That can support “no plausible English output among these tested width-9 fits,” not “zero valid configurations.” The 3×3 width-9 path should remain explicitly untested unless another source file supplies that run.

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

## Closure gate for issue #244

Progress from this PR is deliberately split between completed checks and outstanding closure requirements:

- [x] Pin an immutable external source revision and the audited script blob SHAs.
- [x] Independently verify W-restart key mismatches and direct arbitrary-alphabet period constraints.
- [x] Independently reproduce the Hill row-system scan and distinguish underconstrained systems from contradictions.
- [x] Independently reproduce both PK-style two-period-key models, including the 17 under-threshold consistent cases and one explicit gibberish witness.
- [x] Add dated archival leads, a provisional 1970 partial read, and the unresolved 1991-captioned-photo provenance conflict.
- [ ] Re-run the full external campaign from a clean checkout with exact commands, corpus hashes/versions, positive controls, shuffled nulls, and machine-readable outputs; the dictionary-scale PK9 width-7/8 command and running-key corpora are not independently reproduced yet.
- [ ] Verify a complete pre-1997 city-plate transcription from original-resolution imagery or a primary schedule, with a second reader, exact line order, and plate orientation.
- [ ] Resolve the 80-versus-97 original-count conflict and the current 146-versus-148 discrepancy against the original designer/restoration documentation or another primary record.
- [ ] Only then decide whether each remaining family can be moved into the local “eliminated” ledger and whether issue #244 is complete.

The photo captioned 1991 is **not** accepted as a verified pre-1997 source until the apparent post-1997 label conflict is resolved. The 1970 plate list is explicitly provisional and cannot satisfy the 1990 transcription requirement by itself.

## Scope decision

Do not close issue #244 solely because PR #249 merged or because the external repository reports zero matches. PR #249 added useful 2017 transcription infrastructure, but this repository still needs a sourced historical transcription and a verified, scope-specific reproduction of the independent elimination claims before the whole issue can be considered complete.
