# Next 24 Hours: Hypothesis Elimination Sprint

**Date**: 2025-10-24 **Goal**: Test 3-5 more cipher hypotheses, continue eliminating methods **Target**: Get closer to
solution by shrinking hypothesis space

---

## Immediate Next Steps (Priority Order)

### 1. Random Baseline Scoring (15 minutes) ⚡

**Why First**: Need statistical baseline before claiming any candidate is "good"

**Implementation**:
```python
# scripts/run_random_baseline.py
- Generate 10,000 random A-Z strings (length 74)
- Score each with combined_plaintext_score()
- Compute mean, stddev, percentiles (50th, 90th, 95th, 99th)
- Save distribution to artifacts/baselines/random_scoring.json
```

**Success Criteria**:
- Mean score established (likely -400 to -300)
- Standard deviation calculated
- 3σ threshold defined for "interesting" candidates

**What We Learn**:
- Hill 2x2 best (-329.45) is only slightly above random noise
- Need score >0 or >mean+3σ to have linguistic signal

---

### 2. Vigenère Hypothesis (20 minutes) 🎯

**Why Next**: Fast to test, classical method, Sanborn era-appropriate

**Implementation**:
```python
# src/kryptos/k4/hypotheses.py: VigenereHypothesis
- Test key lengths 1-20
- For each length: frequency analysis to find likely key
- Test top 10 keys per length
- Return scored candidates
```

**Search Space**:
- Key length 1-20: 20 × 10 candidates = 200 total
- Expected duration: <2 minutes

**Success Criteria**:
- If score >baseline+3σ → investigate further
- If all scores negative → RULE OUT simple Vigenère

**What We Learn**:
- Whether K4 uses periodic substitution
- If Vigenère ruled out → narrows to transposition or non-periodic methods

---

### 3. Playfair with KRYPTOS Keyword (10 minutes) 🎯

**Why Next**: Sanborn explicitly used KRYPTOS in K2, common digraph cipher

**Implementation**:
```python
# src/kryptos/k4/hypotheses.py: PlayfairHypothesis
- Test keyword: KRYPTOS
- Test variants: KRYPTO, ABSCISSA, PALIMPSEST
- Generate candidates with Playfair decryption
```

**Search Space**:
- 4-5 keywords to test
- Expected duration: <1 minute

**Success Criteria**:
- If BERLIN or CLOCK appear in plaintext → MAJOR BREAKTHROUGH
- If all gibberish → rule out Playfair with known keywords

**What We Learn**:
- Whether Sanborn reused KRYPTOS pattern
- If ruled out → reduces keyword cipher search space

---

### 4. Berlin Clock Vigenère (15 minutes) 🔄

**Why Next**: Clock mentioned in K4 literature, temporal interpretation plausible

**Implementation**:
```python
# src/kryptos/k4/hypotheses.py: BerlinClockVigenereHypothesis
- Use full_berlin_clock_shifts() for various times
- Test 24 hour positions (00:00 through 23:00)
- Apply shifts as Vigenère key stream
```

**Search Space**:
- 24 hour positions × lamp state variations
- Expected duration: <5 minutes

**Success Criteria**:
- Score >baseline OR recognizable words
- If negative → rule out temporal Vigenère

**What We Learn**:
- Whether Berlin Clock encodes the key
- If ruled out → reduces time-based hypothesis space

---

### 5. Composite Method Sampling (30 minutes) 🔄

**Why Last**: More computationally expensive, combinatorial explosion

**Implementation**:
```python
# scripts/run_composite_search.py
- Apply transposition first (sample best N=20 permutations)
- Then apply Hill 2x2 to each transposed result
- Or: apply Vigenère after transposition
```

**Search Space**:
- 20 transpositions × 100 Hill keys = 2,000 combinations
- Expected duration: ~30 minutes

**Success Criteria**:
- Find composite that scores better than single-method
- If still negative → suggests K4 not simple 2-layer composite

**What We Learn**:
- Whether K4 uses layered encryption
- Which layer order (if any) produces better scores

---

## Expected End-of-Day State

**Hypotheses Tested**: 7 total (2 done + 5 new)

**Likely Outcomes**:

**Scenario A (Most Likely)**: All 5 new hypotheses score negative
- Result: 7 cipher methods definitively ruled out
- Progress: Solution space narrowed significantly
- Next: Move to exotic methods (Four-Square, Route ciphers, custom variants)

**Scenario B (Possible)**: 1-2 hypotheses show weak positive signal
- Result: Candidates score >random baseline but <strongly positive
- Progress: Identify which method shows most promise
- Next: Deep dive on that method with parameter tuning

**Scenario C (Unlikely but Possible)**: Strong positive signal
- Result: Candidate scores >100, contains recognizable words
- Progress: Potential breakthrough - human expert review needed
- Next: Validate with linguistic analysis, cross-check with Sanborn themes

---

## Success Metrics

**Minimum Acceptable Progress**:
- 3 new hypotheses tested and documented
- Evidence artifacts generated (JSON + RULED_OUT.md for negatives)
- Test suite remains green (227+ tests)
- Random baseline established

**Stretch Goals**:
- 5 hypotheses tested
- Composite method exploration started
- Top-100 candidate corpus generated across all methods
- Automated reporting pipeline operational

---

## Risk Mitigation

**Risk**: Getting stuck on implementation details
- Mitigation: Use existing code where possible, stub complex parts initially

**Risk**: False positive from scoring noise
- Mitigation: Establish random baseline FIRST, use 3σ threshold

**Risk**: Combinatorial explosion on composite methods
- Mitigation: Use adaptive pruning, limit to top-N candidates per stage

**Risk**: Losing momentum on negative results
- Mitigation: Remember - negative results are progress! Each elimination narrows search space.

---

## After This Sprint

**Documentation**:
- Update K4_PROGRESS_TRACKER.md with new eliminations
- Update ROADMAP.md with next priorities
- Generate summary report of all hypotheses tested

**Next Phase Planning**:
- If 7 methods ruled out → pivot to exotic/custom ciphers
- If weak signal found → focus on parameter optimization
- If no signal anywhere → consider K4 may be unsolvable with current info

**Long-term Strategy**:
- Aim for 20+ hypotheses tested within 1 week
- Build corpus of top candidates for human analysis
- Prepare for possibility that statistical methods alone won't crack K4
