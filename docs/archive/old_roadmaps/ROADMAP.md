# K4 Roadmap
Breadcrumb: Overview > Roadmap > Roadmap

Detailed plan for advancing Kryptos K4 analysis.

---

## ⚡ CURRENT FOCUS: HYPOTHESIS ELIMINATION (2025-10-24)

**Status**: Active cryptanalysis in progress **Goal**: Systematically eliminate cipher methods with evidence
**Momentum**: 2 hypotheses ruled out in <1 hour

### Recently Eliminated (with Evidence)

1. ✅ **Hill 2x2 cipher** (2025-10-24)
   - Search: 158,000 invertible matrices exhaustively tested
   - Duration: 37 seconds
   - Best score: -329.45 (highly negative)
   - Evidence: `artifacts/hill_2x2_searches/RULED_OUT.md`

2. ✅ **Simple columnar transposition** (2025-10-24)
   - Search: Berlin Clock period widths (5, 6, 7, 8, 10, 11, 12, 15, 24)
   - Duration: 0.87 seconds with adaptive pruning
   - Best score: -350.80 (highly negative)
   - Evidence: `artifacts/transposition_searches/RULED_OUT.md`

### Next 5 Hypotheses to Test (Priority Order)

1. 🎯 **Vigenère with key lengths 1-20** (HIGH PRIORITY)
   - Rationale: Standard classical cipher, fast to test
   - Implementation: Enumerate all key lengths, test top N keys per length
   - Expected duration: <2 minutes
   - Success criteria: Find candidate with score >0 OR eliminate definitively

2. 🎯 **Playfair with KRYPTOS keyword** (HIGH PRIORITY)
   - Rationale: Sanborn used KRYPTOS as K2 key, common in classical crypto
   - Implementation: Test KRYPTOS + common variants (KRYPTO, ABSCISSA, etc.)
   - Expected duration: <1 minute
   - Success criteria: Known words (BERLIN, CLOCK) appear in plaintext

3. 🎯 **Random baseline scoring** (INFRASTRUCTURE)
   - Rationale: Need statistical threshold to distinguish signal from noise
   - Implementation: Generate 10,000 random A-Z plaintexts, score distribution
   - Expected duration: <5 minutes
   - Success criteria: Establish mean, σ, percentiles for null hypothesis

4. 🔄 **Berlin Clock Vigenère** (MEDIUM PRIORITY)
   - Rationale: Clock referenced in K4 literature, temporal key stream plausible
   - Implementation: Test lamp state sequences as shift keys
   - Expected duration: <5 minutes
   - Success criteria: Score significantly above random baseline

5. 🔄 **Composite: Transposition → Hill 2x2** (MEDIUM PRIORITY)
   - Rationale: K4 may use layered methods (K1-K3 combined transposition + substitution)
   - Implementation: Apply transposition first, then Hill search on result
   - Expected duration: ~30 minutes (combinatorial)
   - Success criteria: Find candidate with linguistic structure

---

## Roadmap Guidelines


High-level milestones for the next phases. This is intentionally short and actionable.

1. Stabilize core scoring & transposition tests

- Add focused unit tests for `kryptos/k4/scoring.py` and `kryptos/k4/transposition.py`.
- Acceptance: tests green and file coverage targets met (scoring >=95%, transposition >=90%).

1. Tuning harness and deterministic sweeps

- Wire and validate a tiny deterministic tuning sweep harness (now provided by
`kryptos.k4.tuning.run_crib_weight_sweep`). A thin legacy script wrapper remains temporarily.
- Acceptance: reproducible CSV artifacts in `artifacts/tuning_runs/` for small grids (invoked via
API or forthcoming CLI `kryptos tuning crib-weight-sweep`).

1. Autopilot & SPY integration

- Ensure `scripts/dev/ask_triumverate.py` computes or uses a conservative SPY `min_conf` and that
`kryptos.spy.extractor` writes curated hints (legacy script removed).

1. Demos, CI and reproducibility

- Add demo runner artifacts and CI steps to validate example runs produce expected artifact shapes.

1. Long-run automation

- Implement the long-loop daemon/runner to rotate parameter sets and retain run history.

### Notes

- Keep changes small and test-driven. Each milestone should have a clear acceptance criterion and a
smoke test.

## High-Level Planned Modules / Enhancements

Short term (0-7 days):
- Harden autopilot (OPS / SPY / Q) with conservative defaults and evaluation-driven thresholds.
- Add tiny tuning sweep and demo pipelines; wire to `artifacts/k4_runs/` and
`artifacts/tuning_runs/` for traceability.
- Improve test coverage around scoring and transposition components (increase positional deviation
coverage).
- Calibrate positional letter deviation weight (collect distribution stats across historical runs).
- Implement adaptive transposition sampling (bootstrap batch, conditional expansion, early cutoff)
with per-column metrics.
- Integrate rarity-weighted crib scoring multiplier (frequency-indexed) and perform k sweep
calibration.

- Layered / composite transposition + substitution search pruning. (IN PROGRESS: basic columnar
partial-score pruning added)
- Expanded Berlin Clock enumeration (full lamp state/time modeling, parity & quarter markers).
(PARTIALLY IMPLEMENTED: full lamp state & enumeration utilities; pipeline stage added `make_berlin_clock_stage`)
- Recursive masking / null removal heuristics. (PENDING)
- Probable word placement scoring (additional cribs beyond BERLIN/CLOCK/EASTNORTHEAST). (PENDING)
- Composite reporting (persist top-N candidate plaintexts & metrics to JSON/CSV). (IMPLEMENTED:
reporting.py JSON/CSV artifacts)
- Extended Hill cipher exploration (3x3 & larger constrained key search under crib anchors).
(PARTIAL: 3x3 ops present, constraint search still 2x2)
- Overlay & spiral path grid traversal experiments. (PENDING)

## Candidate Reporting (Status: IMPLEMENTED)

A forthcoming pipeline reporting stage will persist ranked candidates (key/source metadata + metrics). JSON schema
example:

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

Current simplified shift vector expanded with full lamp modeling & enumeration functions (`full_clock_state`,
`full_berlin_clock_shifts`, `enumerate_clock_shift_sequences`). Next: integrate as pipeline stage with scoring
comparison.

## Transposition Pruning Heuristics (Status: INITIAL)

Added optional partial segment scoring (parameters: prune, partial_length, partial_min_score) to skip low-quality
permutations early. Future: adaptive sampling & prefix caching.

## Search Strategy Evolution

1. Establish baseline brute-force (done). 2. Introduce heuristic pruning. 3. Add multi-stage composite pipeline
(transposition → substitution → shift overlay → scoring). 4. Integrate Berlin Clock enumeration as an optional stage. 5.
Add persistence/reporting and comparative metrics tracking.

## Metrics Expansion (Status: PARTIAL)

Positional crib weighting implemented (`positional_crib_bonus`, `combined_plaintext_score_with_positions`). Quadgram
support added (`quadgram_score`). Positional letter deviation metric added (distribution balance). Future metrics:
spacing analysis, entropy refinement, positional deviation weight calibration study, rarity-weighted crib bonus
multiplier.

## Status Tracking

Use issues to map each bullet to deliverables; close with test evidence and README/roadmap updates.

## Baseline Section Anomalies Reference

- K1: Deliberate misspelling `IQLUSION` retained.
- K2: No deliberate spelling anomalies; apparent `X` characters in historic presentations function
as separators/padding, not errors.
- K3: Deliberate misspelling `DESPARATLY` retained.

--- Completed (2025-10-21):

- Extended plaintext scoring (berlin_clock_pattern_validator, pattern bonus integration).
- Pipeline executor with candidate pruning & artifact logging (attempt_log.jsonl + summary.json).
- Automated spacing / lint autofix tooling (pep8_spacing_autofix.py) for consistent style
compliance.
- Pruning logic & pattern bonus tests (test_executor_pruning_and_pattern.py).
- CLI provides runnable samples (`kryptos sections`, `kryptos k4-decrypt ...`) replacing legacy
wrappers.

Next Iteration Targets:

- Parallel hill variants differentiation (vary key space slices / scoring weights).
- Tuning harness (parameter sweep + summary aggregation CSV/JSON).
- Additional artifacts (per-stage candidate CSV export integrated into executor flow).
- Adaptive gating refinement (dynamic threshold adjustment based on previous stage score deltas).
- Caching of expensive permutation searches (persistent prefix/permutation caches across runs).
- Integration test chaining multiple transposition + masking stages.
- Berlin Clock deep pattern alignment scoring (lamp temporal sequencing bonuses beyond ordering
stub).

Last updated: 2025-10-24 (added breadcrumbs index, tiny weight sweep example migration)
