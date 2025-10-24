# K4 Hypothesis Testing: Expansion Plan
**Date:** 2025-10-24 **Status:** Ready to Execute **Goal:** Supercharge cryptanalysis infrastructure and explore 15+ new
cipher hypotheses

---

## 🎯 Executive Summary

**Current State:**
- ✅ 6 hypotheses tested (Hill 2x2, Transposition, Caesar, Vigenère, Playfair, Simple Sub)
- ✅ 2 weak signals detected: Hill 2x2 (-329.45), Vigenère len=13 (-326.64)
- ✅ Statistical baseline established (mean=-355.92, σ=14.62)
- ✅ 231 tests passing
- ✅ Infrastructure validated: 6 hypotheses in ~2 min compute time

**Next Phase Goals:** 1. **Expand search spaces** - test more keys, longer lengths, deeper searches 2. **Test composite
methods** - layered encryption (transposition + Hill, Vigenère + transposition) 3. **Add new cipher families** -
autokey, four-square, bifid, homophonic, fractional Morse 4. **Enhance scoring** - syllable structure, word boundaries,
phonetic rules 5. **Build agent triumvirate** - SPY (pattern analysis), OPS (orchestration), Q (QA/validation) 6. **Re-
validate weak signals** - confirm Hill 2x2 and Vigenère aren't artifacts

---

## 📊 Phase 1: Expand Existing Hypotheses (Est. 4 hours)

### 1.1 Vigenère Deep Dive
**Current:** Key lengths 1-20, 10 keys per length (200 candidates) **Expand to:**
- Key lengths 1-30 (cover longer periods)
- 50 best keys per length (better frequency analysis)
- Dictionary attack mode (test BERLIN, CLOCK, KRYPTOS, ABSCISSA as keys)
- **Expected:** ~1500 candidates, ~5 min compute

### 1.2 Hill 2x2 Weak Signal Validation
**Current:** -329.45 (between 2σ and 3σ) **Validation tests:**
- Test on different starting positions (offset by 1-10 chars)
- Pre-process with top 10 transposition permutations
- Normalize letter frequencies before scoring
- Check if signal persists across variations
- **Expected:** Confirm real signal vs. artifact

### 1.3 Hill 3x3 Targeted Search
**Current:** Not tested (key space ~10^14, infeasible to exhaust) **New approach:**
- Use BERLIN/CLOCK as crib constraints
- Force first 6 plaintext chars = "BERLIN" → reduces key space to ~10^6
- Sample 100k matrices from constrained space
- Use genetic algorithm if promising
- **Expected:** 100k candidates, ~1-2 hours compute

---

## 🔗 Phase 2: Composite Methods (Est. 6 hours)

### 2.1 Transposition → Hill 2x2
**Hypothesis:** K4 uses layered encryption like K1-K3 **Method:**
- Take top 20 transposition permutations
- Apply Hill 2x2 search (sample 1000 keys) to each
- 20 × 1000 = 20k combinations
- **Expected:** ~30 min compute

### 2.2 Vigenère → Transposition
**Hypothesis:** Vigenère weak signal is partial decryption **Method:**
- Take top 50 Vigenère candidates
- Apply transposition search (100 permutations each)
- 50 × 100 = 5k combinations
- **Expected:** ~15 min compute

### 2.3 Hill 2x2 → Vigenère
**Hypothesis:** Hill removes structure, Vigenère obscures pattern **Method:**
- Take top 50 Hill 2x2 candidates
- Apply Vigenère search (key lengths 1-10)
- 50 × 100 = 5k combinations
- **Expected:** ~15 min compute

---

## 🆕 Phase 3: New Cipher Families (Est. 8 hours)

### 3.1 Autokey Cipher
**Description:** Vigenère variant where plaintext becomes key stream **Implementation:**
- Test primers: KRYPTOS, BERLIN, CLOCK, ABSCISSA, alphabet
- Autokey is harder to break than standard Vigenère
- **Expected:** ~50 candidates, ~2 min compute

### 3.2 Four-Square Cipher
**Description:** Digraph substitution using 4 keyed 5×5 grids **Implementation:**
- Grid keywords: all combinations of KRYPTOS, BERLIN, CLOCK, ABSCISSA
- 4^4 = ~100 combinations (with repeats allowed)
- **Expected:** ~100 candidates, ~5 min compute

### 3.3 Bifid Cipher
**Description:** Combines Polybius square + transposition **Implementation:**
- Test periods 5-20 with KRYPTOS keyword
- Classical cipher, era-appropriate
- **Expected:** ~160 candidates, ~10 min compute

### 3.4 Homophonic Substitution
**Description:** One plaintext char → multiple ciphertext chars **Implementation:**
- Analyze frequency distribution for clusters
- Common letters (E, T, A) may map to 2-3 ciphertext symbols
- Use entropy analysis to detect homophonic patterns
- **Expected:** Statistical analysis + targeted search

### 3.5 Fractional Morse Code
**Description:** Plaintext → Morse → letter encoding **Implementation:**
- BERLIN → -... . .-. .-.. .. -.
- Encode dots/dashes as letters (e.g., dot=A, dash=B)
- Matches Sanborn's communication/transmission themes
- **Expected:** ~50 variants, ~1 min compute

---

## 🧠 Phase 4: Agent Triumvirate (Est. 12 hours)

### 4.1 SPY Agent: Pattern Recognition Specialist
**Role:** Analyze candidate plaintexts for hidden patterns **Capabilities:**
- Detect repeating substrings (may indicate polyalphabetic period)
- Find palindromes, anagrams, acrostics
- Identify word boundaries (common 2-3 letter words)
- Score linguistic quality (syllable patterns, phonetics)
- Flag cribs (BERLIN, CLOCK) and their positions
- Output ranked insights with confidence scores

**Implementation:**
```python
class SpyAgent:
    def analyze_candidate(self, plaintext: str) -> dict[str, Any]:
        return {
            'repeats': self._find_repeats(plaintext),
            'palindromes': self._find_palindromes(plaintext),
            'word_boundaries': self._detect_words(plaintext),
            'syllable_score': self._score_syllables(plaintext),
            'cribs_found': self._find_cribs(plaintext),
            'linguistic_quality': self._nlp_score(plaintext),
        }
```

### 4.2 OPS Agent: Execution Orchestrator
**Role:** Manage hypothesis queue and parallel execution **Capabilities:**
- Priority queue (high-value hypotheses first)
- Resource allocation (CPU cores, memory limits)
- Parallel execution (multiprocessing for independent searches)
- Progress monitoring (ETA, throughput, completion %)
- Kill hung tasks (timeout detection)
- Result aggregation (merge artifacts, deduplicate)

**Implementation:**
```python
class OpsAgent:
    def __init__(self, max_workers: int = 8):
        self.queue = PriorityQueue()
        self.executor = ProcessPoolExecutor(max_workers=max_workers)

    def schedule(self, hypothesis: Hypothesis, priority: int):
        self.queue.put((priority, hypothesis))

    def run_all(self) -> list[SearchResult]:
        # Execute queue with parallelism, monitoring, timeouts
        pass
```

### 4.3 Q Agent: Quality Assurance & Validation
**Role:** Ensure rigor and catch false positives **Capabilities:**
- Run sanity tests on all candidates (positive controls)
- Statistical validation (chi-square, KS test, t-test)
- Detect artifacts (scoring function biases, edge cases)
- Flag anomalies (impossibly high scores, duplicate plaintexts)
- Cross-validate weak signals (re-run with different params)
- Generate confidence intervals for all results

**Implementation:**
```python
class QAgent:
    def validate_result(self, result: SearchResult) -> ValidationReport:
        return ValidationReport(
            sanity_checks=self._run_sanity_tests(result),
            statistical_tests=self._run_stats(result),
            anomalies=self._detect_anomalies(result),
            confidence_interval=self._compute_ci(result),
            recommendation='ACCEPT' | 'REJECT' | 'RETEST',
        )
```

---

## 📈 Phase 5: Enhanced Scoring & Analysis (Est. 6 hours)

### 5.1 Improve Scoring Function
**Current:** N-grams, IC, chi-square, cribs **Add:**
- **Syllable structure:** CV, CVC, CVCC patterns (English phonotactics)
- **Word boundaries:** Detect common 2-3 letter words (THE, AND, FOR)
- **Phonetic rules:** Avoid impossible clusters (QXZ, KWW)
- **Digraph frequencies:** Common pairs (TH, ER, ON, AN)
- **Position-specific frequencies:** E more common at end, Q always followed by U

### 5.2 Statistical Distribution Analysis
**Goal:** Compare score distributions across hypotheses **Analysis:**
- Plot histograms for each hypothesis (bin width = 5 score units)
- Identify bimodal distributions (signal + noise)
- Use KS test to compare hypothesis distributions
- Flag hypotheses with unusually high variance
- Compute effect sizes (Cohen's d) for weak signals

### 5.3 Cross-Hypothesis Correlation
**Goal:** Find shared patterns across top candidates **Analysis:**
- Extract top 50 candidates from each hypothesis
- Find common substrings (length ≥ 4 chars)
- Build co-occurrence matrix (which hypotheses agree?)
- Check if BERLIN/CLOCK appear in multiple top candidates
- Identify consensus regions (all methods agree on these chars)

---

## 🎯 Phase 6: Advanced Search Strategies (Est. 10 hours)

### 6.1 Crib-Guided Search Mode
**Method:** Force BERLIN or CLOCK at specific positions **Implementation:**
- Sliding window: test all positions for crib placement
- For Hill: constrain matrix such that decryption produces crib
- For Vigenère: derive key characters from crib alignment
- Dramatically reduces key space (~10^6 → ~10^3)

### 6.2 Genetic Algorithm for Hill Matrices
**Method:** Evolve high-scoring matrices **Implementation:**
- Start population: top 100 Hill 2x2 candidates + random
- Fitness: combined_plaintext_score()
- Crossover: mix matrix elements from two parents
- Mutation: ±1 to random matrix element (preserve invertibility)
- Generations: 1000, population=200
- **Expected:** May find better local optimum

### 6.3 Simulated Annealing for Substitutions
**Method:** Optimize substitution ciphers **Implementation:**
- Start: random key
- Perturb: swap two letters
- Accept: always if better, probabilistically if worse (T=temperature)
- Cool: reduce T over time
- Good for homophonic substitution, complex polyalphabetic

---

## 📊 Phase 7: Reporting & Visualization (Est. 4 hours)

### 7.1 Hypothesis Ranking Dashboard
**Output:** Markdown + JSON report **Contents:**
- All hypotheses ranked by best score
- Statistical significance levels (color-coded: 🔴 >3σ, 🟡 >2σ, ⚪ <2σ)
- Compute time per hypothesis
- Top 10 candidates per hypothesis
- Weak signals flagged for re-testing
- Definitively ruled out methods

### 7.2 Progress Tracking Metrics
**Metrics:**
- Total hypotheses tested
- Total candidates generated
- Total compute time
- Hypotheses per hour (velocity)
- Signal detection rate (% with >2σ)
- Test coverage (231/231 passing)

---

## 🚀 Execution Strategy

### Week 1: Foundation Expansion
- Days 1-2: Phase 1 (expand existing hypotheses)
- Days 3-4: Phase 2 (composite methods)
- Day 5: Phase 5.2-5.3 (statistical analysis of results so far)

### Week 2: New Methods
- Days 1-3: Phase 3 (new cipher families)
- Days 4-5: Phase 5.1 (improve scoring)

### Week 3: Infrastructure
- Days 1-3: Phase 4 (SPY, OPS, Q agents)
- Days 4-5: Phase 6 (advanced search strategies)

### Week 4: Validation & Reporting
- Days 1-2: Re-run all weak signals with enhanced scoring
- Days 3-4: Phase 7 (dashboard & reports)
- Day 5: Final analysis, next steps planning

---

## 🎓 Success Criteria

**Minimum Success:**
- Test 20+ cipher hypotheses
- Generate 10k+ candidate plaintexts
- Identify 5+ weak signals (>2σ)
- Build SPY/OPS/Q agent framework
- Achieve 300+ tests passing

**Ideal Success:**
- Find strong signal (>3σ) from composite method
- Detect BERLIN or CLOCK in top 10 candidates
- Validate that weak signals are real (not artifacts)
- Achieve <1 hour compute time for all hypotheses
- Publish comprehensive K4 hypothesis elimination report

**Breakthrough Success:**
- Decrypt K4 🎉

---

## 📚 Resources

**Papers to Review:**
- "Attacks on the Vigenère Cipher" (Kasiski, Friedman tests)
- "Hill Cipher Cryptanalysis" (known plaintext attacks)
- "Genetic Algorithms for Cryptanalysis" (apply to Hill, transposition)
- "Natural Language Processing for Ciphertext" (linguistic scoring)

**Tools to Integrate:**
- NLTK (word boundaries, syllable counting)
- scipy.stats (statistical tests, distributions)
- multiprocessing (parallel hypothesis execution)
- plotly/matplotlib (score distribution visualization)

---

## 🔄 Risk Mitigation

**Risk:** False positives from improved scoring **Mitigation:** Q agent validates all results, cross-checks with
baseline

**Risk:** Compute time explodes with composite methods **Mitigation:** OPS agent enforces timeouts, samples key space
intelligently

**Risk:** Weak signals are scoring artifacts **Mitigation:** Re-test with variations, check statistical robustness

**Risk:** Infrastructure complexity slows down iteration **Mitigation:** Agents are optional, can still run scripts
directly

---

## 📝 Next Immediate Actions

1. ✅ Create this expansion plan document 2. ⏭️ Start Phase 1.1: Expand Vigenère search (key lengths 1-30) 3. ⏭️
Implement Phase 5.1: Enhanced scoring with syllable structure 4. ⏭️ Build Phase 4.1: SPY agent for pattern analysis 5.
⏭️ Execute Phase 2.1: Transposition → Hill 2x2 composite

**Let's GO! 🚀**
