"""Performance optimization analysis and recommendations.

Based on profiling results from profile_scoring.py, this document identifies hotspots and proposes optimizations. """

# PROFILING RESULTS SUMMARY

## Top Hotspots (by cumulative time)

### 1. _score_ngrams() - 88ms / 52ms / 52ms (3 profile runs)
**Location:** `src/kryptos/k4/scoring.py:184` **Calls:** 600 / 300 / 200 **Issue:** High string join operations (68ms
cumulative across runs) **Impact:** Called by bigram_score, trigram_score, quadgram_score

**Optimization opportunities:**
- Cache ngram lookups (table.get() called 130K+ times)
- Vectorize string operations
- Use string slicing instead of join for single characters
- Consider Numba JIT compilation for hot loop

### 2. crib_bonus() - 56ms cumulative
**Location:** `src/kryptos/k4/scoring.py:231` **Calls:** 300 + 100 = 400 **Issue:** Repeated pattern matching across all
cribs **Impact:** Called once per combined_plaintext_score

**Optimization opportunities:**
- Cache _get_all_cribs() result (called 400 times, loads from disk each time)
- Precompile regex patterns
- Use Aho-Corasick for multi-pattern matching instead of individual searches

### 3. chi_square_stat() - 67ms + 20ms = 87ms total
**Location:** `src/kryptos/k4/scoring.py:168` **Calls:** 1000 + 200 = 1200 **Issue:** List comprehensions for frequency
counting (48ms total) **Impact:** Called once per combined_plaintext_score

**Optimization opportunities:**
- Use Counter directly instead of list comprehension
- Cache expected frequencies (LETTER_FREQ dict)
- Vectorize with numpy if available

### 4. index_of_coincidence() - 63ms + 9ms = 72ms total
**Location:** `src/kryptos/k4/scoring.py:485` **Calls:** 1000 + 100 = 1100 **Issue:** List comprehension for letter
counting (48ms + 7ms) **Impact:** Called in composite_score_with_stage_analysis

**Optimization opportunities:**
- Use Counter directly
- Cache intermediate results
- Early exit for texts with low letter count

### 5. wordlist_hit_rate() - 35ms
**Location:** `src/kryptos/k4/scoring.py:383` **Calls:** 100 **Issue:** Generates all possible n-grams for sliding
window search **Impact:** Moderate - only called in extended scoring

**Optimization opportunities:**
- Use trie structure for wordlist
- Limit n-gram generation with early termination
- Cache wordlist lookups


## HIGH-IMPACT OPTIMIZATIONS (Priority Order)

### Priority 1: Cache _get_all_cribs() result
**Estimated speedup:** 15-20% overall **Effort:** Low (5 minutes) **Code:**
```python
_CRIBS_CACHE = None

def _get_all_cribs() -> list[str]:
    global _CRIBS_CACHE
    if _CRIBS_CACHE is None:
        _CRIBS_CACHE = CONFIG_CRIBS + list(BERLIN_CLOCK_CRIBS.keys())
    return _CRIBS_CACHE
```

### Priority 2: Optimize _score_ngrams() with caching
**Estimated speedup:** 25-30% overall **Effort:** Medium (30 minutes) **Code:**
```python
from functools import lru_cache

@lru_cache(maxsize=1024)
def _score_ngrams_cached(text: str, size: int, unknown: float) -> float:
    # Same logic but with caching
    pass
```

### Priority 3: Use Counter instead of list comprehension
**Estimated speedup:** 10-15% for chi_square and IOC **Effort:** Low (10 minutes) **Code:**
```python
from collections import Counter

def chi_square_stat(text: str) -> float:
    clean = ''.join(c for c in text.upper() if c.isalpha())
    if len(clean) < 10:
        return 10000.0

    observed = Counter(clean)  # More efficient than list comp
    total = len(clean)
    # ... rest of function
```

### Priority 4: Precompile regex patterns in crib_bonus
**Estimated speedup:** 5-10% **Effort:** Low (10 minutes) **Code:**
```python
import re

_CRIB_PATTERNS = None

def _get_crib_patterns() -> dict[str, re.Pattern]:
    global _CRIB_PATTERNS
    if _CRIB_PATTERNS is None:
        _CRIB_PATTERNS = {crib: re.compile(crib) for crib in _get_all_cribs()}
    return _CRIB_PATTERNS

def crib_bonus(text: str) -> float:
    patterns = _get_crib_patterns()
    # Use pre-compiled patterns
```

### Priority 5: Numba JIT for _score_ngrams (if Numba available)
**Estimated speedup:** 2-5x for ngram scoring specifically **Effort:** High (2-3 hours, requires type annotations)
**Trade-off:** Adds dependency, may not work on all platforms


## IMPLEMENTATION PLAN

### Phase 1: Quick Wins (30 minutes)
1. Cache _get_all_cribs() result (5 min) 2. Use Counter in chi_square_stat (10 min) 3. Use Counter in
index_of_coincidence (10 min) 4. Add benchmarking to verify improvements (5 min)

**Expected combined speedup:** 25-35%

### Phase 2: Medium Effort (1 hour)
1. Add LRU cache to _score_ngrams (30 min) 2. Precompile regex patterns for crib matching (10 min) 3. Optimize
wordlist_hit_rate with trie (20 min)

**Expected combined speedup:** 40-50% total

### Phase 3: Advanced (Optional, 2-3 hours)
1. Numba JIT compilation for hottest loops 2. Profile Hill cipher operations 3. Vectorize with numpy where beneficial

**Expected combined speedup:** 2-5x total (if Numba works well)


## MEASUREMENT STRATEGY

Before/after benchmarks:
```bash
# Baseline
python scripts/profile_scoring.py > results/profile_before.txt

# After optimizations
python scripts/profile_scoring.py > results/profile_after.txt

# Compare
diff results/profile_before.txt results/profile_after.txt
```

Success criteria:
- 30%+ speedup for Phase 1 optimizations
- 50%+ total speedup for Phase 1+2
- All 30 tests still passing
- No regression in accuracy


## RISKS & MITIGATIONS

### Risk 1: Caching breaks if cribs change
**Mitigation:** Add cache invalidation, document cache behavior

### Risk 2: LRU cache memory usage
**Mitigation:** Set reasonable maxsize (1024 entries = ~100KB)

### Risk 3: Numba compilation overhead
**Mitigation:** Make Numba optional, fall back to pure Python

### Risk 4: Optimization breaks scoring accuracy
**Mitigation:** Run full test suite, compare scores before/after


## ESTIMATED TOTAL IMPACT

Conservative estimate (Phase 1 + 2 only):
- **Current:** 214s full test run
- **After:** ~110-130s (40-50% speedup)
- **Hypothesis execution:** 2-5x faster for ngram-heavy scoring

Aggressive estimate (with Numba in Phase 3):
- **Full test run:** ~50-70s (3-4x speedup)
- **Hypothesis execution:** 5-10x faster


## NEXT STEPS

1. Implement Phase 1 optimizations (30 min) 2. Run profile_scoring.py to measure improvement 3. Run full test suite to
verify correctness 4. Commit Phase 1 with benchmark results 5. Decide on Phase 2 based on Phase 1 results
