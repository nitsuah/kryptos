# K4 Roadmap

Detailed plan for advancing Kryptos K4 analysis.

## High-Level Planned Modules / Enhancements

- Layered / composite transposition + substitution search pruning. (IN PROGRESS: basic columnar partial-score pruning added)
- Expanded Berlin Clock enumeration (full lamp state/time modeling, parity & quarter markers). (PARTIALLY IMPLEMENTED: full lamp state & enumeration utilities; pipeline stage added `make_berlin_clock_stage`)
- Recursive masking / null removal heuristics. (PENDING)
- Probable word placement scoring (additional cribs beyond BERLIN/CLOCK/EASTNORTHEAST). (PENDING)
- Composite reporting (persist top-N candidate plaintexts & metrics to JSON/CSV). (IMPLEMENTED: reporting.py JSON/CSV artifacts)
- Extended Hill cipher exploration (3x3 & larger constrained key search under crib anchors). (PARTIAL: 3x3 ops present, constraint search still 2x2)
- Overlay & spiral path grid traversal experiments. (PENDING)

## Candidate Reporting (Status: IMPLEMENTED)

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

## Berlin Clock Enumeration (Status: PARTIAL)

Current simplified shift vector expanded with full lamp modeling & enumeration functions (`full_clock_state`, `full_berlin_clock_shifts`, `enumerate_clock_shift_sequences`). Next: integrate as pipeline stage with scoring comparison.

## Transposition Pruning Heuristics (Status: INITIAL)

Added optional partial segment scoring (parameters: prune, partial_length, partial_min_score) to skip low-quality permutations early. Future: adaptive sampling & prefix caching.

## Search Strategy Evolution

1. Establish baseline brute-force (done).
2. Introduce heuristic pruning.
3. Add multi-stage composite pipeline (transposition → substitution → shift overlay → scoring).
4. Integrate Berlin Clock enumeration as an optional stage.
5. Add persistence/reporting and comparative metrics tracking.

## Metrics Expansion (Status: PARTIAL)

Positional crib weighting implemented (`positional_crib_bonus`, `combined_plaintext_score_with_positions`). Quadgram support added (`quadgram_score`). Future metrics: spacing analysis, entropy refinement.

## Status Tracking

Use issues to map each bullet to deliverables; close with test evidence and README/roadmap updates.

## Baseline Section Anomalies Reference

- K1: Deliberate misspelling `IQLUSION` retained.
- K2: No deliberate spelling anomalies; apparent `X` characters in historic presentations function as separators/padding, not errors.
- K3: Deliberate misspelling `DESPARATLY` retained.

---
Completed (2025-10-21):

- Extended plaintext scoring (berlin_clock_pattern_validator, pattern bonus integration).
- Pipeline executor with candidate pruning & artifact logging (attempt_log.jsonl + summary.json).
- Automated spacing / lint autofix tooling (pep8_spacing_autofix.py) for consistent style compliance.
- Pruning logic & pattern bonus tests (test_executor_pruning_and_pattern.py).
- Minimal runnable sample script (scripts/tools/run_pipeline_sample.py).

Next Iteration Targets:

- Parallel hill variants differentiation (vary key space slices / scoring weights).
- Tuning harness (parameter sweep + summary aggregation CSV/JSON).
- Additional artifacts (per-stage candidate CSV export integrated into executor flow).
- Adaptive gating refinement (dynamic threshold adjustment based on previous stage score deltas).
- Caching of expensive permutation searches (persistent prefix/permutation caches across runs).
- Integration test chaining multiple transposition + masking stages.
- Berlin Clock deep pattern alignment scoring (lamp temporal sequencing bonuses beyond ordering stub).

Last updated: 2025-10-21
