# CHANGELOG

## [Unreleased]

- Pending: route scoring refinement, multiprocessing, advanced Hill assemblies.

## [2025-10-20] Adaptive & Route Expansion

- Added adaptive fusion weighting (wordlist_hit_rate + trigram_entropy heuristics).
- Added route transposition stage (spiral, boustrophedon, diagonal traversals).
- Implemented multi-crib positional transposition stage.
- Added 3x3 Hill key pruning (partial score).
- Added attempt logging & persistence for Hill, Clock, Transposition.
- Added advanced linguistic metrics (wordlist hit rate, trigram entropy, bigram gap variance).
- Added normalization safeguards (equal-score midpoint) & adaptive diagnostics.
- Corrected crib indices (EAST 22, NORTHEAST 25, BERLIN 64, CLOCK 69).

## [Earlier] Pre-adaptive foundation

- Core multi-stage pipeline (Hill, transposition, adaptive transposition, masking, Berlin Clock).
- Weighted multi-stage fusion & candidate artifacts.
