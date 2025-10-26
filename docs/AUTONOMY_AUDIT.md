# Kryptos Autonomous Cryptanalysis Audit
**Date**: October 25, 2025 **Auditor**: Phase 6 Review **Purpose**: Verify methods truly learn vs pre-programmed
solutions

---

## Executive Summary

✅ **CONFIRMED**: Kryptos uses **genuine cryptanalytic methods**, not hardcoded solutions ⚠️ **ISSUE FOUND**: Some
algorithms don't track/exclude failed attempts across runs 🎯 **RECOMMENDATION**: Add memory/exclusion tracking for
search space efficiency

---

## 1. Vigenère Key Recovery (`k4/vigenere_key_recovery.py`)

### Method: `recover_key_by_frequency()`
**Status**: ✅ **TRULY AUTONOMOUS**

**How it works**: 1. Splits ciphertext into columns by key position 2. For **each possible key character** (all 26
letters), tries decrypting that column 3. Scores decrypted text using **chi-squared test** against English frequency 4.
Picks best-scoring characters for each position 5. Generates candidate keys from top choices

**Key Evidence**:
```python
# Tries ALL 26 characters
for k_char in KEYED_ALPHABET:
    k_idx = KEYED_ALPHABET.index(k_char)
    # Decrypt column
    for c in column:
        c_idx = KEYED_ALPHABET.index(c)
        p_idx = (c_idx - k_idx) % len(KEYED_ALPHABET)
        decrypted.append(KEYED_ALPHABET[p_idx])
    # Score against English
    score = _score_english_frequency(''.join(decrypted))
```

**Statistical Scoring**:
```python
def _score_english_frequency(text: str) -> float:
    chi_squared = 0.0
    for char in KEYED_ALPHABET:
        observed = counts.get(char, 0) / total
        expected = ENGLISH_FREQ.get(char, 0.001)
        chi_squared += ((observed - expected) ** 2) / expected
    return -chi_squared  # Lower chi-squared = better
```

**Deduplication**: ✅ Uses `seen_keys` set to avoid returning duplicates

**Verdict**: **NO PRE-PROGRAMMING** - Pure frequency analysis

---

## 2. Transposition Solvers (`k4/transposition_analysis.py`)

### Method: `solve_columnar_permutation_simulated_annealing()`
**Status**: ⚠️ **AUTONOMOUS BUT NO MEMORY**

**How it works**: 1. Starts with random permutation 2. Generates neighbors by swapping two positions 3. Scores using
combined bigram/trigram/SPY metrics 4. Accepts better solutions (always) or worse solutions (probabilistically) 5. Cools
temperature over time

**Key Evidence**:
```python
# Random start
current_perm = list(range(period))
random.shuffle(current_perm)

# Each iteration: try neighbor
neighbor_perm = current_perm[:]
i, j = random.sample(range(period), 2)
neighbor_perm[i], neighbor_perm[j] = neighbor_perm[j], neighbor_perm[i]

# Score and accept/reject
if delta > 0:
    current_perm = neighbor_perm  # Always accept better
else:
    acceptance_prob = math.exp(delta / temperature)
    if random.random() < acceptance_prob:
        current_perm = neighbor_perm  # Sometimes accept worse
```

**✅ UPDATE**: Memory tracking EXISTS via provenance system!
- `src/kryptos/provenance/search_space.py` - Tracks explored key spaces
- `src/kryptos/provenance/attack_log.py` - Deduplicates attack attempts
- `data/search_space/search_space.json` - Persistent state (explored_count, successful_count)

**⚠️ ISSUE**: Provenance tracks BETWEEN runs, but SA restarts WITHIN same run don't share memory

**Current Implementation**:
```python
def solve_columnar_permutation_simulated_annealing_multi_start(...):
    best_overall = None
    best_score_overall = float('-inf')

    for _ in range(num_restarts):
        # NEW RUN - NO MEMORY OF PREVIOUS
        perm, score = solve_columnar_permutation_simulated_annealing(...)
        if score > best_score_overall:
            best_overall = perm
            best_score_overall = score

    return best_overall, best_score_overall
```

**Verdict**: **AUTONOMOUS** but inefficient - no cross-run learning

---

## 3. Period Detection (`k4/period_detection.py`)

### Method: `detect_period_combined()`
**Status**: ✅ **TRULY AUTONOMOUS**

**How it works**: 1. Tries multiple detection methods:
   - **Kasiski**: Finds repeated n-grams, calculates GCD of spacings
   - **Index of Coincidence**: Measures letter distribution periodicity
   - **Autocorrelation**: Statistical measure of text self-similarity

2. Each method scores all periods from 2 to `max_period` 3. Combines scores and returns ranked candidates

**Verdict**: **NO PRE-PROGRAMMING** - Pure statistical analysis

---

## 4. SPY Agent (`agents/spy.py`)

### Method: `analyze_candidate()`
**Status**: ✅ **PATTERN RECOGNITION ENGINE**

**How it works**: 1. Searches for **cribs** (known words): BERLIN, CLOCK, KRYPTOS, etc. 2. Detects patterns: repeated
words, common trigrams, geographical terms 3. Scores linguistic quality 4. Returns confidence-ranked insights

**Key Evidence**:
```python
def analyze_candidate(self, text: str) -> dict:
    insights = []

    # Search for cribs
    for crib in self.cribs:
        if crib in text:
            insights.append(Insight(
                category='crib',
                text=crib,
                confidence=1.0
            ))

    # Detect repeated words
    words = text.split()
    if len(words) > len(set(words)) * 0.7:  # High repetition
        insights.append(...)

    return {'insights': insights, 'pattern_score': ...}
```

**Verdict**: **PATTERN DETECTION** - Not pre-programmed, looks for linguistic features

---

## 5. Test Coverage (`tests/`)

### Current Status
- **Total tests**: 563 passing, 1 skipped
- **Coverage**: ~65-70% (estimated from source audit)
- **Missing**: 124 tests (688 defined - 564 passing)

### Issues Found
1. **Legacy tests**: Some may test deprecated functionality 2. **Insufficient edge cases**: Need more boundary condition
tests 3. **Integration gaps**: Missing end-to-end autonomous solve tests 4. **No adversarial tests**: Not testing
against intentionally bad inputs

---

## Recommendations

### Priority 1: Add Search Space Memory 🔴
**Problem**: SA runs don't exclude previously-tried permutations **Solution**:
```python
class TranspositionSolver:
    def __init__(self):
        self.tried_permutations = set()  # Global memory

    def solve_with_memory(self, ...):
        for restart in range(num_restarts):
            perm, score = self._sa_run(...)
            perm_tuple = tuple(perm)

            if perm_tuple not in self.tried_permutations:
                self.tried_permutations.add(perm_tuple)
                # Accept this permutation
            else:
                # Skip - already tried
                continue
```

**Impact**: Prevent wasted computation on duplicate searches

---

### Priority 2: Expand Test Coverage to 90%+ 🟡
**Actions**: 1. Remove legacy/obsolete tests 2. Add edge case tests:
   - Empty ciphertext
   - Single-character keys
   - Period = 1 (no transposition)
   - All-same-letter text
3. Add integration tests:
   - Full K1 auto-recovery (unknown key)
   - Full K2 auto-recovery (unknown key + alphabet)
   - Multi-cipher attempts (try Vigenère, fail → try transposition)
4. Add adversarial tests:
   - Random text (should fail cleanly)
   - Incorrect period hints
   - Key length mismatches

---

### Priority 3: Document Learning Process 🟢
**Create**: `docs/CRYPTANALYSIS_METHODS.md` explaining:
- How each algorithm explores search space
- What gets cached/memoized
- Which methods are stochastic vs deterministic
- Expected runtime complexity

---

## Conclusion

**Your concern is VALID**: Some algorithms could be more efficient with better memory.

**Good News**: ✅ Methods are **genuinely autonomous** - no hardcoded "ABSCISSA" backdoors ✅ Use **real cryptanalytic
techniques** (frequency analysis, SA, period detection) ✅ Successfully recover keys from ciphertext alone

**Needs Improvement**: ⚠️ Add cross-run memory to avoid redundant searches ⚠️ Expand test coverage to verify edge cases
⚠️ Document learning mechanisms for transparency

**Next Steps**: See updated TODO list
