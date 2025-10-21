# K4 Roadmap

Detailed plan for advancing Kryptos K4 analysis.

## High-Level Planned Modules / Enhancements

- Layered / composite transposition + substitution search pruning.
- Expanded Berlin Clock enumeration (full lamp state/time modeling, parity & quarter markers).
- Recursive masking / null removal heuristics.
- Probable word placement scoring (additional cribs beyond BERLIN/CLOCK/EASTNORTHEAST).
- Composite reporting (persist top-N candidate plaintexts & metrics to JSON/CSV).
- Extended Hill cipher exploration (3x3 & larger constrained key search under crib anchors).
- Overlay & spiral path grid traversal experiments.

## Candidate Reporting (Planned)

A forthcoming pipeline reporting stage will persist ranked candidates (key/source metadata + metrics). JSON schema example:

```json
{
  "cipher": "K4",
  "stage": "hill_constraints",
  "generated_at": "2025-10-20T12:00:00Z",
  "candidates": [
    {
      "rank": 1,
      "score": 1234.56,
      "source": "pair:BERLIN+CLOCK",
      "key": [[a,b],[c,d]],
      "text": "PLAINTEXT...",
      "metrics": {
        "chi_square": 101.2,
        "bigram_score": 500.0,
        "trigram_score": 700.0,
        "crib_bonus": 30.0,
        "index_of_coincidence": 0.066,
        "vowel_ratio": 0.38,
        "letter_coverage": 0.85
      }
    }
  ]
}
```

## Berlin Clock Enumeration (Upcoming)

Current simplified shift vector will be expanded:

- Full lamp state modeling (hours 5s row, hours 1s row, minutes 5s row w/ quarter markers, minutes 1s row, seconds lamp).
- Deterministic encoding to multi-length shift sequences (e.g., concatenated lamp counts & parity bits).
- Integration point: clock-derived Vigenère-like shifts pre/post transposition stage.

## Transposition Pruning Heuristics (Planned)

Mitigating factorial growth:

- Early partial n-gram scoring on initial rows.
- Chi-square / entropy deltas for early rejection.
- Adaptive permutation sampling biased by continuity improvements.
- Prefix score caching.

## Search Strategy Evolution

1. Establish baseline brute-force (done).
2. Introduce heuristic pruning.
3. Add multi-stage composite pipeline (transposition → substitution → shift overlay → scoring).
4. Integrate Berlin Clock enumeration as an optional stage.
5. Add persistence/reporting and comparative metrics tracking.

## Metrics Expansion

Potential future metrics:

- Quadgram scoring (if performance acceptable).
- Repeated digram/spacing analysis vs English norms.
- Positional crib weighting (crib near plausible structural indices).

## Status Tracking

Use issues to map each bullet to deliverables; close with test evidence and README/roadmap updates.

## Baseline Section Anomalies Reference

- K1: Deliberate misspelling `IQLUSION` retained.
- K2: No deliberate spelling anomalies; apparent `X` characters in historic presentations function as separators/padding, not errors.
- K3: Deliberate misspelling `DESPARATLY` retained.

---
Last updated: 2025-10-20
