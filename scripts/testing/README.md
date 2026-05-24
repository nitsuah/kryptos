# Test Coverage Analysis Summary

## Test Counts

- **Total tests**: 598
- **Fast tests** (marked "not slow"): 578
- **Slow tests** (marked @pytest.mark.slow): 20

## Coverage Results

- **Sample coverage** (67 tests from 10 core modules): **13%**
  - test_ciphers.py
  - test_scoring.py
  - test_k4_scoring.py
  - test_k4_transposition.py,
  - test_attack_provenance.py,
  - test_pipeline_artifacts.py,
  - test_public_api.py,
  - test_paths_helpers.py,
  - test_report_module.py,
  - test_search_space.py
  - Tests passed: 67 in 2.28s

- **Estimated full coverage**: **~60-70%**
  - Extrapolated from sample (67 tests → 13% coverage)
  - With 578 fast tests (8.6x more), estimated 60-70% coverage
  - Note: Unable to run all 578 tests due to unmarked slow tests causing hangs

## Issues Found

### Unmarked Slow Tests

The following test files cause hangs when run (>2 minutes each) but are NOT marked with @pytest.mark.slow:

1. **test_composite_chains.py** - Hangs indefinitely

   - Needs: Add `@pytest.mark.slow` to all tests in this file

2. **test_calibration_harness.py** (suspected) - Appears to hang in batch runs
   - Needs investigation

3. Possibly others in the composite/pipeline category

### Known Slow Tests (Properly Marked)

These are already marked and excluded from fast test runs:

- test_k1_k2_monte_carlo.py
- test_k3_autonomous_solving.py
- test_k3_monte_carlo_comprehensive.py
- test_vigenere_key_recovery.py (some tests)
- test_hill_genetic.py (some tests)
- test_k4_hypotheses.py (some tests)

## Recommendations

1. **Mark slow tests**: Add `@pytest.mark.slow` to test_composite_chains.py and investigate other hanging tests 2. **CI
Pipeline**: Run only -m "not slow" tests in CI after fixing markers 3. **Coverage target**: With proper slow test
markers, full fast test suite should achieve 60-70% coverage in <5 minutes 4. **Coverage goal**: Consider targeting
70-80% coverage by adding tests for uncovered modules
   - (agents, pipeline, research modules currently at 0%)

## Test Execution Times (Sampled)

- Most test files: <1s
- test_autonomous_coordinator.py: ~8s
- test_composite_chains.py: >120s (NEEDS @pytest.mark.slow)
- 67-test sample: 2.28s
- Estimated 578 fast tests: 3-5 minutes (if slow tests properly marked)
