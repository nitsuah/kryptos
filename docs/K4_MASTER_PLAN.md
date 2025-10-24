# K4 Master Plan

**Last Updated:** 2025-10-24 **Status:** Active cryptanalysis phase - systematic hypothesis elimination

---

## Executive Summary

**Mission:** Solve Kryptos K4 through systematic cipher hypothesis testing and elimination.

**Current State:**

- ✅ Infrastructure operational (281 tests passing, 85% coverage)
- ✅ 9 hypotheses tested (Hill 2x2, Vigenère, Playfair, Autokey, FourSquare, Bifid, Berlin Clock, Transposition, Simple
substitution)
- ✅ Agent triumvirate deployed: SPY (435L, 10T), OPS (350L, 9T), Q (310L, 17T)
- ✅ Random baseline established (mean: -355.92, σ: 14.62)
- 🟡 Hill 2x2 weak signal (-329.45, 2σ above random) - requires validation
- 🎯 Composite hypotheses next (layered encryption testing)

**Next Priorities:** 1. Test composite methods (Transposition → Hill, Vigenère → Transposition) 2. Expand Hill to 3x3
matrices (genetic algorithm approach) 3. Add LLM/NLP intelligence to SPY (Phase 2 enhancement) 4. Optimize test
performance (currently 335s full suite, target <180s)

**Success Criteria:** Find plaintext candidate with score > -312.06 (3σ threshold) AND contains recognizable words
(BERLIN, CLOCK, or coherent English)

**Stretch Goals:**
- 90%+ test coverage (current: 85%)
- Sub-180s test suite runtime (current: 335s)
- 100% hypothesis parameter space exploration
- Full composite hypothesis matrix (layered ciphers)

---

## Strategic Context

### Why K4 is Hard

**The Challenge:**

- **Length**: Only 97 characters (statistical methods need more data)
- **Sculptor's Intent**: Jim Sanborn designed K4 to be "extremely difficult"
- **No Known Plaintext**: Unlike K1-K3, no confirmed cribs
- **Multiple Possibilities**: Could be any classical cipher or custom variant
- **Time**: Unsolved since 1990 (34+ years)

**What We Know:**

- K1: Simple substitution (PALIMPSEST keyword)
- K2: Vigenère (ABSCISSA keyword)
- K3: Transposition (columnar)
- K4: Contains "BERLIN" and references to "clock" (per Sanborn hints)
- Final passage: 97 characters on the sculpture

**Why Others Failed:**

- NSA, CIA cryptanalysts couldn't break it
- Academic researchers tried standard methods
- Brute force unfeasible for many cipher types
- K4 may use custom method or multiple layers

### Our Approach

**Philosophy:** Systematic elimination > random guessing

**Core Principles:** 1. **Evidence-Based**: Every hypothesis tested generates artifacts 2. **Statistical Rigor**:
Compare to random baseline (mean: -355.92, σ: 14.62) 3. **Negative Results Matter**: Ruling out methods narrows search
space 4. **Automation First**: Infrastructure enables rapid testing 5. **Agent Assistance**: SPY/OPS/Q triumvirate for
scale + intelligence

**Advantages:**

- Modern infrastructure (Python 3.12, pytest, pyproject.toml)
- Standardized scoring (`combined_plaintext_score()`)
- Hypothesis protocol (pluggable cipher testing)
- Artifact trails (full provenance in `artifacts/`)
- Test coverage (249 tests, 100% passing)

---

## Hypothesis Pipeline

### Phase 1: Existing Hypothesis Expansion (Weeks 1-2)

**Goal:** Exhaust parameter spaces for implemented hypotheses

**Initiatives:**

1. **Vigenère Extended Search** (HIGH PRIORITY)
   - Current: Key lengths 1-20, 10 keys per length
   - Target: Key lengths 1-30, 50 keys per length
   - Add: BERLIN, CLOCK, KRYPTOS as explicit key candidates
   - Candidates: ~1,500 total
   - Duration: ~5 minutes
   - Rationale: Most common classical cipher, fast to test

2. **Hill 2x2 Weak Signal Validation**
   - Current: Best score -329.45 (2σ above random)
   - Test: (a) Different plaintext positions, (b) with transposition pre-processing, (c) frequency normalization
   - Rationale: Verify signal is real, not artifact

3. **Playfair Keyword Expansion**
   - Current: KRYPTOS, BERLIN, CLOCK
   - Add: PALIMPSEST, ABSCISSA, INVISIBLE, SCULPTURE, SANBORN (50+ keywords)
   - Candidates: ~500 total
   - Duration: ~2 minutes

4. **Transposition Thorough Search**
   - Current: Berlin Clock periods only (9 widths)
   - Add: All widths 2-30, test with rectangle/spiral/diagonal routes
   - Candidates: ~10,000 total
   - Duration: ~10 minutes with pruning

### Phase 2: Composite Methods (Week 2)

**Goal:** Test layered encryption (Cipher A → Cipher B)

**Rationale:** Sanborn may have combined methods for increased difficulty

**Initiatives:**

1. **Transposition → Hill 2x2**
   - Top 20 transpositions × 1,000 Hill keys = 20,000 combinations
   - Duration: ~30 minutes
   - Tests: If weak Hill signal becomes strong after transposition

1. **Vigenère → Transposition**
   - Top 50 Vigenère keys × 100 transpositions = 5,000 combinations
   - Duration: ~20 minutes
   - Tests: If Vigenère partially decrypts, then transposition reveals plaintext

1. **Substitution → Transposition**
   - All simple substitutions × top 100 transpositions
   - Tests: Classic two-layer approach

1. **Hill 3x3 → Transposition**
   - Sampled 3x3 matrices × transposition
   - Much larger key space than 2x2

### Phase 3: New Cipher Families (Weeks 2-3)

**Goal:** Add cipher types not yet tested

**Initiatives:**

1. **Autokey Cipher**
   - Vigenère variant: uses plaintext as key stream after primer
   - Primers: KRYPTOS, BERLIN, CLOCK, alphabet
   - Harder to break than standard Vigenère

1. **Four-Square Cipher**
    - Uses 4 keyed grids for digraph substitution
    - Keywords: All combinations of KRYPTOS/BERLIN/CLOCK/ABSCISSA
    - ~100 combinations

1. **Bifid Cipher**
    - Combines Polybius square + transposition
    - Test periods 5-20 with KRYPTOS keyword
    - Classical cipher, period-dependent

1. **Homophonic Substitution**
    - Multiple ciphertext chars → one plaintext letter
    - Analyze frequency clusters
    - Common in Renaissance cryptography

1. **Fractional Morse Hypothesis**
    - Test if K4 encodes Morse (dots/dashes) then converts to letters
    - BERLIN → Morse → letter encoding
    - Matches sculptor's communication themes

1. **Berlin Clock Vigenère**
    - Use Berlin Clock lamp sequences as keys
    - Test all 24 hours (00:00-23:00)
    - Duration: ~5 minutes

### Phase 4: Advanced Search Strategies (Week 3)

**Goal:** Sophisticated search methods for large key spaces

**Initiatives:**

1. **Hill Genetic Algorithm**
    - Start from best Hill 2x2 (-329.45)
    - Mutate matrix elements, test offspring
    - Converge to local optimum
    - Useful for large matrices (3x3, 4x4)

1. **Crib-Guided Search**
    - Force BERLIN or CLOCK at specific positions (sliding window)
    - Dramatically reduces key space
    - Works for: Hill, Vigenère, Playfair, etc.

1. **Simulated Annealing**
    - Metaheuristic for key space exploration
    - Accept worse candidates probabilistically
    - Escape local optima

1. **Bayesian Key Recovery**
    - Use prior probabilities for key elements
    - Update beliefs based on partial decryptions
    - Intelligent search order

### Phase 5: Agent Triumvirate (Weeks 3-4)

**Goal:** Scale to thousands of hypotheses with quality assurance

**Initiatives:**

1. **OPS Agent: Execution Orchestrator**
    - Queue management for hypothesis pipeline
    - Parallel execution (multiprocessing)
    - Resource monitoring (CPU/memory)
    - Timeout enforcement
    - Progress tracking
    - Result aggregation

1.  **Q Agent: Quality Assurance**
    - Sanity tests (all candidates)
    - Statistical validation (compare to baseline)
    - Anomaly detection (unusual patterns)
    - False positive filtering
    - Confidence scoring

1.  **SPY Agent v2.0: LLM/NLP Intelligence**
    - Phase 1: Classic NLP (spaCy, NLTK, CMU Dict) - no API costs
    - Phase 2: Transformer embeddings (sentence-transformers) - local execution
    - Phase 3: LLM integration (OpenAI/Anthropic) - optional, ~$0.01-0.10 per batch
    - Features: POS tagging, NER, semantic similarity, phonetic analysis

---

## Testing Strategy

### Statistical Baseline

**Random Scoring Distribution** (10,000 samples):

- Mean: -355.92
- Std Dev: 14.62
- 2σ threshold (95% confidence): -326.68
- 3σ threshold (99.7% confidence): -312.06

**Interpretation:**

- Scores < -326.68: Not significant (within random noise)
- Scores -326.68 to -312.06: Weak signal (investigate)
- Scores > -312.06: Strong signal (likely real)
- Scores > 0: Very strong (linguistic structure detected)

### Weak Signal Validation

**When to Investigate:** 1. Score exceeds 2σ threshold 2. Multiple related keys produce similar candidates 3. Patterns
detected by SPY agent (cribs, repeats, words) 4. Cross-hypothesis correlation (same substring in multiple methods)

**Validation Steps:** 1. Test parameter variations (±10% on key values) 2. Apply SPY analysis (pattern recognition) 3.
Check for known words (BERLIN, CLOCK, CIA, etc.) 4. Human expert review 5. If validated → deep dive with exhaustive
search

### Positive Controls

**Known Plaintext Tests:**

- Encrypt known English text with each hypothesis
- Verify decryption recovers original
- Ensures implementation correctness

**Cross-Validation:**

- Test on K1-K3 with known keys
- Should reproduce documented solutions

---

## Statistical Analysis & Correlation

### Cross-Hypothesis Analysis

**Goal:** Find patterns across different cipher methods

**Initiatives:**

1. **Score Distribution Comparison**
    - Plot histograms per hypothesis
    - Look for bimodal distributions (signal + noise)
    - Identify which methods show clustering

1. **Substring Correlation**
    - Extract top 100 candidates per hypothesis
    - Find common substrings (length ≥5)
    - Reveals partial decryptions

1. **Pattern Overlap**
    - Apply SPY to all top candidates
    - Find common patterns (repeats, palindromes, cribs)
    - May indicate composite method

### Hypothesis Ranking Dashboard

**Automated Report:**

- All hypotheses tested
- Best scores per hypothesis
- Signals detected (2σ, 3σ)
- Compute time
- Status (ruled out, weak signal, strong signal)
- Next actions

---

## Immediate Next Steps

### This Week (Priority Order)

1. ✅ **Consolidate scripts/** (DONE)
   - Created unified `run_hypothesis.py`
   - Reduced 544 lines → 130 lines (76% reduction)

2. 🔄 **Consolidate docs/** (IN PROGRESS)
   - This document consolidates: ROADMAP, K4_STRATEGY, EXPANSION_PLAN, NEXT_24_HOURS
   - Keep: README.md, K4_MASTER_PLAN.md, AGENTS_ARCHITECTURE.md, API_REFERENCE.md, CHANGELOG.md, TECHDEBT.md,
     AUTOPILOT.md
   - Archive rest to `docs/archive/`

3. **Expand Vigenère** (2 hours)
   - Implement extended key lengths
   - Add dictionary-based key guessing
   - Test explicit keywords (BERLIN, etc.)

4. **Hill 3x3 Targeted** (3 hours)
   - Use crib constraints (BERLIN/CLOCK positions)
   - Sample 100k keys
   - Genetic algorithm for refinement

5. **Validate Hill 2x2 weak signal** (1 hour)
   - Test positional variations
   - Test with transposition pre-processing

### Next 2 Weeks

1. **Composite methods** (8 hours)
   - Transposition → Hill
   - Vigenère → Transposition
   - Substitution → Transposition

1. **New cipher families** (12 hours)
   - Autokey, Four-Square, Bifid, Homophonic, Morse

1. **OPS agent** (16 hours)
   - Parallel execution framework
   - Queue + resource management
   - Result aggregation

1. **Q agent** (12 hours)
   - Statistical validation
   - Anomaly detection
   - Confidence scoring

1. **SPY v2.0 upgrade** (20 hours)
    - Phase 1: spaCy/NLTK integration
    - Phase 2: Transformer embeddings
    - Phase 3: LLM API (optional)

---

## Long-Term Vision

### Breakthrough Criteria

**We will know K4 is solved when:** 1. Candidate scores significantly positive (>50) 2. Contains recognizable English
words 3. BERLIN and/or CLOCK appear in plaintext 4. Makes thematic sense with K1-K3 5. Sanborn confirms (or matches
leaked hints)

### Full Autonomous Search

**End Goal:** Agent-driven hypothesis discovery

**Components:**

- OPS: Orchestrates 24/7 hypothesis testing
- SPY: Analyzes all candidates, flags interesting patterns
- Q: Validates results, filters false positives
- Hypothesis Generator: Creates new cipher variants programmatically
- Learning System: Adapts search based on weak signals

**Timeline:** 2-3 months to full automation

### Publication & Documentation

**When Solved:** 1. Document complete solution path 2. Write technical report 3. Submit to cryptography journals 4. Open
source all code 5. Create educational materials

---

## Decision Points

### If All Tested Hypotheses Fail (Score < 2σ)

**Options:** 1. Test exotic ciphers (Gronsfeld, ADFGVX, Double Columnar) 2. Custom cipher design (Sanborn may have
invented method) 3. Assume K4 requires external information (book code, date-based key) 4. Consider K4 may be
intentionally unsolvable

### If Weak Signal Found (2σ < Score < 3σ)

**Actions:** 1. Parameter sweep around weak signal 2. Apply SPY analysis 3. Test composite with weak method as first
stage 4. Human expert review

### If Strong Signal Found (Score > 3σ)

**Actions:** 1. Immediate validation with fresh data 2. SPY deep dive 3. Alert user for manual review 4. Prepare
detailed analysis report 5. Cross-check with Sanborn themes

---

## Resources & Constraints

### Compute Budget

- Local machine: sufficient for most searches
- Parallel execution: 8 cores available
- Cloud: can scale if needed (AWS/GCP)

### Time Budget

- Active development: 20-40 hours/week
- Timeline: 2-3 months for comprehensive search

### Cost Budget

- Infrastructure: $0 (local execution)
- LLM API (Phase 3): ~$10-50 for batch analysis
- Cloud compute (if needed): ~$50-100/month

---

## Success Metrics

### Weekly Targets

- Hypotheses tested: 5-10 per week
- Test suite: Maintain 100% pass rate
- Documentation: Keep current with each sprint

### Monthly Targets

- Hypotheses tested: 25-50 cumulative
- Agent implementation: OPS + Q operational
- SPY upgrade: Phase 1 NLP complete

### Project Success

- K4 solved OR
- Comprehensive elimination (50+ hypotheses ruled out with evidence) OR
- Strong signal identified requiring human expert analysis

---

**Remember:** Every hypothesis tested—whether successful or not—is progress. Negative results eliminate possibilities
and narrow the search space. This is how cryptanalysis works.
