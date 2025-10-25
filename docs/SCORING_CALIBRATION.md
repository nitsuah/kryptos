# Scoring Weight Calibration Results

**Date:** October 25, 2025 **Method:** Grid search on K1-K3 known plaintexts vs wrong-key decoys

## Summary

Grid search tested 46,656 weight combinations to optimize scoring function discrimination between correct plaintexts and
incorrect decryption attempts.

## Results

### Baseline Weights (Current)
```python
{
    "ioc": 0.0,
    "chi2": 0.1,
    "bigram": 0.1,
    "trigram": 0.2,
    "quadgram": 0.4,
    "crib": 0.2
}
```
- **Separation:** 1.15
- **Accuracy:** 33.3%

### Optimized Weights (Calibrated)
```python
{
    "ioc": 0.5,
    "chi2": 0.5,
    "bigram": 0.4,
    "trigram": 0.5,
    "quadgram": 0.2,
    "crib": 0.0
}
```
- **Separation:** 5.75 (+400% improvement)
- **Accuracy:** 33.3% (same, but better separation)

## Key Findings

1. **Chi-square weight should be 5x higher** (0.5 vs 0.1)
   - Chi-square stat is the strongest discriminator
   - Measures overall frequency distribution match

2. **IOC should be weighted** (0.5 vs 0.0)
   - Currently not used in combined_plaintext_score
   - Helps distinguish random text from structured language

3. **Crib bonus should be 0** (0.0 vs 0.2)
   - Wrong decryptions can contain crib words by chance
   - Not reliable for discrimination
   - More useful for human review than automated scoring

4. **Trigram weight should be higher** (0.5 vs 0.2)
   - Better than quadgrams for this task
   - Balances specificity with robustness

5. **Quadgram weight should be lower** (0.2 vs 0.4)
   - Too specific, can overfit to training data
   - Trigrams more generalizable

## Recommended Changes

### Option 1: Conservative (Safe)
Update `combined_plaintext_score()` with modest improvements:
```python
score = (
    0.2 * chi_square_stat_normalized(text) +  # Was 0.1 equivalent
    0.2 * index_of_coincidence(text) +        # Was 0.0 (new)
    0.1 * bigram_score(text) +                # Same
    0.3 * trigram_score(text) +               # Was 0.2
    0.3 * quadgram_score(text) +              # Was 0.4
    0.1 * crib_bonus(text)                    # Was 0.2
)
```

### Option 2: Aggressive (Use Calibrated)
Use exact calibrated weights:
```python
score = (
    0.5 * chi_square_stat_normalized(text) +
    0.5 * index_of_coincidence(text) +
    0.4 * bigram_score(text) +
    0.5 * trigram_score(text) +
    0.2 * quadgram_score(text) +
    0.0 * crib_bonus(text)  # Or remove entirely
)
```

### Option 3: Hybrid (Recommended)
Keep existing structure but adjust key weights:
```python
score = (
    0.3 * chi_square_stat_normalized(text) +  # 3x increase
    0.1 * index_of_coincidence(text) +        # Add IOC
    0.1 * bigram_score(text) +                # Same
    0.3 * trigram_score(text) +               # Increase
    0.3 * quadgram_score(text) +              # Decrease
    0.1 * crib_bonus(text)                    # Decrease
)
```

## Caveats

1. **Small sample size:** Only 3 correct + 15 decoy texts
   - Results may not generalize to all cipher types
   - K4 might have different characteristics

2. **Decoy quality:** Wrong-key decryptions may not represent all failure modes
   - Partial decryptions might score differently
   - Composite ciphers add complexity

3. **Component normalization:** Scores have different scales
   - Chi-square: ~50-500 range
   - IOC: 0.0-0.07 range
   - Ngrams: -1000 to 0 range
   - May need rescaling for fairness

## Next Steps

1. Test recommended weights on test suite 2. Verify no regression on existing hypothesis tests 3. Compare composite
hypothesis scores before/after 4. Document changes in CHANGELOG.md 5. Consider adding more test cases for weight
validation

## Implementation

See `scripts/calibrate_scoring_weights.py` for full calibration code.
