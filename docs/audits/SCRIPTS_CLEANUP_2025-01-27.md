# Scripts Cleanup - January 27, 2025

## Summary

Cleaned up 6 development/debugging scripts that tested K1/K2 recovery. All functionality is now properly covered by
comprehensive tests in `tests/`.

---

## Scripts Deleted

### 1. `test_k1_recovery.py` (14 lines)
**Purpose:** Quick manual test of K1 (PALIMPSEST) recovery **Functionality:** Calls `recover_key_by_frequency()`, shows
top 10 keys, reports if PALIMPSEST found **Redundant with:**
- `tests/test_vigenere_key_recovery.py::test_k1_autonomous_recovery_no_key_provided`
- `tests/test_k1_k2_monte_carlo.py::test_k1_monte_carlo_50runs` (50 runs!)

**Decision:** ✅ DELETE - Covered by proper tests

---

### 2. `test_k2_recovery.py` (14 lines)
**Purpose:** Quick manual test of K2 (ABSCISSA) recovery **Functionality:** Calls `recover_key_by_frequency()`, shows
top 10 keys, reports if ABSCISSA found **Redundant with:**
- `tests/test_vigenere_key_recovery.py::test_k2_autonomous_recovery_no_key_provided`
- `tests/test_k1_k2_monte_carlo.py::test_k2_monte_carlo_50runs` (50 runs!)

**Decision:** ✅ DELETE - Covered by proper tests

---

### 3. `test_ranking.py` (48 lines)
**Purpose:** Test dictionary ranking impact on K2 recovery **Functionality:**
- Generates 5000 raw candidates with `_generate_key_combinations()`
- Shows ABSCISSA position before ranking
- Applies `_rank_by_word_likelihood()`
- Shows ABSCISSA position after ranking
- Demonstrates that ranking moves ABSCISSA to top

**Insights preserved:**
- Dictionary ranking is critical for K2 success
- ABSCISSA may not be #1 in raw candidates (based on frequency alone)
- `_rank_by_word_likelihood()` boosts candidates containing dictionary words

**Redundant with:**
- The Monte Carlo tests prove ranking works (100% success)
- Internal mechanism is tested by unit tests

**Decision:** ✅ DELETE - Insight: ranking is essential (now proven by Monte Carlo)

---

### 4. `test_raw_generation.py` (41 lines)
**Purpose:** Verify ABSCISSA is generated in raw candidates before ranking **Functionality:**
- Scores each column independently
- Gets top 5 candidates per position
- Generates 5000 combinations
- Checks if ABSCISSA appears in raw output

**Insights preserved:**
- Raw candidate generation includes correct key (confirmed)
- Top 5 per position is sufficient to include correct characters
- Generation step works correctly (ranking is what matters)

**Redundant with:**
- Monte Carlo tests confirm end-to-end pipeline works
- If ABSCISSA weren't generated, ranking couldn't help

**Decision:** ✅ DELETE - Generation is proven correct

---

### 5. `test_column_scoring.py` (50 lines)
**Purpose:** Deep debug of column 3 and 6 scoring for K2 **Functionality:**
- Splits K2 ciphertext into 8 columns
- Tests all 27 keys per column
- Shows score + decrypted preview
- Reports rank of correct key character

**Insights preserved:**
- Individual column scoring works (correct chars rank well)
- Hybrid scoring (absolute diff vs chi-squared) fixed any issues
- Columns 3 and 6 specifically were debugged (likely had issues pre-fix)

**Redundant with:**
- Monte Carlo tests prove column scoring is reliable
- Unit tests cover `_score_english_frequency()`

**Decision:** ✅ DELETE - Debugging complete, issue fixed

---

### 6. `debug_k2_positions.py` (32 lines)
**Purpose:** Show top 5 candidates per position for K2 **Functionality:**
- For each of 8 positions, scores all 27 keys
- Shows top 5 with scores
- Reports rank of correct character

**Insights preserved:**
- Per-position scoring is accurate
- All 8 correct characters rank in top 5 for their positions
- Combinatorial explosion requires smart generation (heap-based)

**Redundant with:**
- Monte Carlo tests prove positional scoring works
- `test_ranking.py` showed similar information

**Decision:** ✅ DELETE - Positional scoring validated

---

## Knowledge Preserved

### Key Insights from Scripts

1. **Dictionary ranking is essential**
   - Raw frequency scoring alone doesn't guarantee #1 rank
   - `_rank_by_word_likelihood()` boosts candidates with known words
   - This is why K2 achieves 100% success (not just 3.8%)

2. **Hybrid scoring fixed K1/K2**
   - Absolute difference for short columns (<10 chars)
   - Chi-squared for longer columns
   - This addressed issues seen in column debugging

3. **Generation strategy matters**
   - Top 5 per position is sufficient
   - Heap-based rank-prioritized generation
   - 5000 candidates is enough for K2 (8-char key)

4. **Per-column scoring is reliable**
   - All correct characters rank in top 5 for their positions
   - Column independence assumption holds for Vigenère

### Where Knowledge Lives Now

- **Tests:** `tests/test_k1_k2_monte_carlo.py` (100 runs validating end-to-end)
- **Tests:** `tests/test_vigenere_key_recovery.py` (unit tests for components)
- **Code:** `src/kryptos/k4/vigenere_key_recovery.py` (production implementation)
- **Docs:** `K1_K2_VALIDATION_RESULTS.md` (performance analysis)
- **Docs:** `AUDIT_2025-10-26.md` (K1 fix history)

---

## Scripts to Keep

**None.** All development/debugging scripts have been validated and their functionality integrated into proper tests.

---

## Decision Rationale

**Why delete instead of keeping?**

1. **Redundancy:** Every script tests something already covered by proper tests 2. **Maintenance burden:** Scripts don't
run in CI, can break silently 3. **Confusion:** Having both scripts and tests is unclear - which is authoritative? 4.
**Knowledge preserved:** All insights documented above 5. **Better coverage:** Monte Carlo tests (100 runs) > manual
scripts (1 run)

**What if we need to debug again?**

- Use proper pytest with `-xvs` flags for detailed output
- Add temporary debug prints to tests (remove after)
- Write new temporary scripts if needed, delete when done
- Follow maintenance guide: scripts are temporary

---

## Deletion Commands

```bash
rm scripts/test_k1_recovery.py
rm scripts/test_k2_recovery.py
rm scripts/test_ranking.py
rm scripts/test_raw_generation.py
rm scripts/test_column_scoring.py
rm scripts/debug_k2_positions.py
```

---

**Date:** January 27, 2025 **Deleted by:** Maintenance cleanup following validation completion **Rationale:** All
functionality superseded by comprehensive test suite
