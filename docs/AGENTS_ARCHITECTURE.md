# Agents Architecture: Intelligence Layer for K4 Cryptanalysis

**Version:** 3.0 **Date:** 2025-10-24 **Status:** All agents implemented and operational

---

## 🎯 Vision

The **Agents Triumvirate** provides an intelligent orchestration layer above the hypothesis testing framework. Each
agent has specialized expertise:

- **SPY** (Pattern Recognition) - Detects linguistic/structural patterns in candidates
- **OPS** (Operations) - Orchestrates parallel execution, resource management, workflow
- **Q** (Quality Assurance) - Validates results, detects artifacts, ensures rigor

Together they form an **autonomous cryptanalysis system** that iterates toward K4 solution with minimal human
intervention.

---

## 🕵️ SPY Agent: Pattern Recognition Specialist

### Current Implementation (v1.0)

**Status:** ✅ Implemented (`src/kryptos/agents/spy.py`, 435 lines, 10 tests passing)

**Capabilities:**

- Repeating substring detection (may indicate period)
- Palindrome finding (symmetric patterns)
- Crib matching (BERLIN, CLOCK, KRYPTOS)
- Common word detection (THE, AND, FOR, etc.)
- Acrostic analysis (first letters of blocks)
- Frequency anomaly detection
- Anagram finding
- Spacing pattern analysis
- Confidence-scored insights
- Pattern quality scoring

**Example Usage:**

```python
from kryptos.agents.spy import SpyAgent, spy_report

spy = SpyAgent(cribs=['BERLIN', 'CLOCK'])
analysis = spy.analyze_candidate("THEBERLINCLOCKISHERE")

print(analysis['pattern_score'])  # 45.2
print(len(analysis['crib_matches']))  # 2
print(spy_report(plaintext))  # Human-readable report
```

### Planned Enhancement (v2.0) - LLM/NLP Integration

**Goal:** Transform SPY from regex-based to AI-powered pattern recognition

**Phase 1: Classic NLP (No LLM API required)**

- **spaCy** for proper tokenization, POS tagging, dependency parsing
  - Detect real word boundaries (not just substring matches)
  - Identify grammatical structures (noun phrases, verb phrases)
  - Named entity recognition (BERLIN = LOC, CLOCK = ARTIFACT?)

- **NLTK** for additional linguistic features
  - WordNet for semantic similarity
  - Syllable counting (accurate, not heuristic)
  - Phonetic transcription (IPA)

- **CMU Pronouncing Dictionary** for phonetics
  - Check if candidate is pronounceable
  - Detect alliteration, rhyme schemes
  - Match stress patterns

**Phase 2: Transformer Embeddings (Local, no API)**

- **sentence-transformers** (`all-MiniLM-L6-v2` or similar)
  - Compute embeddings for candidate plaintexts
  - Cluster similar candidates (may indicate partial decryption families)
  - Detect semantic coherence (even if not dictionary words)

- **Cross-candidate correlation**
  - Compare embeddings of top 100 candidates across hypotheses
  - Find candidates that are semantically "close" despite different text
  - May reveal composite cipher structures

**Phase 3: LLM Integration (Optional, API-based)**

- **OpenAI GPT-4 / Anthropic Claude API** for high-confidence candidates
  - Prompt: "Analyze this potential decryption: {plaintext}. Does it look like English? What patterns do you see? Rate
    confidence 0-100."
  - Use for candidates scoring >2σ threshold
  - LLM can detect subtle linguistic features humans notice but scoring misses

- **Cost management**
  - Only send top 50 candidates per hypothesis to LLM
  - Cache LLM responses
  - Estimate: ~$0.01-0.10 per full hypothesis batch

- **Prompt Engineering**

  ```text
  You are an expert cryptanalyst analyzing a potential plaintext decryption
  of the Kryptos K4 sculpture cipher. Known clues: BERLIN, CLOCK.

  Candidate plaintext: "{plaintext}"

  Analysis:
  1. Does this resemble English text? (0-100)
  2. List any recognizable words or word-like sequences
  3. Note any unusual patterns (repeats, structure, anomalies)
  4. Does BERLIN or CLOCK appear (even partially)?
  5. Overall confidence this is correct plaintext: (0-100)

  Respond in JSON format.
  ```

**Implementation Plan:**

```python
# src/kryptos/agents/spy_nlp.py

from sentence_transformers import SentenceTransformer
import spacy
import openai  # optional

class SpyAgentNLP(SpyAgent):
    """Enhanced SPY with NLP/LLM capabilities."""

    def __init__(self, use_llm: bool = False, llm_provider: str = 'openai'):
        super().__init__()
        self.nlp = spacy.load('en_core_web_sm')  # 14MB model
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')  # 80MB
        self.use_llm = use_llm
        self.llm_provider = llm_provider

    def analyze_with_nlp(self, plaintext: str) -> dict:
        """Enhanced analysis using spaCy."""
        doc = self.nlp(plaintext)

        return {
            'tokens': [t.text for t in doc],
            'pos_tags': [(t.text, t.pos_) for t in doc],
            'entities': [(e.text, e.label_) for e in doc.ents],
            'noun_phrases': [chunk.text for chunk in doc.noun_chunks],
            'is_parseable': not doc.has_annotation('DEP'),
        }

    def compute_embedding(self, plaintext: str) -> np.ndarray:
        """Get semantic embedding for cross-candidate comparison."""
        return self.embedder.encode(plaintext)

    def llm_analysis(self, plaintext: str, threshold: float = 0.7) -> dict:
        """Send high-confidence candidates to LLM for expert analysis."""
        if not self.use_llm:
            return {}

        prompt = f"""You are an expert cryptanalyst analyzing Kryptos K4.

        Candidate: "{plaintext}"

        Analysis (JSON format):
        {{"english_score": 0-100, "words_found": [], "patterns": [],
          "crib_evidence": "", "confidence": 0-100}}
        """

        # Call OpenAI/Anthropic API
        # return parsed JSON response
        pass
```

**Dependencies to add:**

```toml
# pyproject.toml
[tool.poetry.dependencies]
spacy = "^3.7"  # Core NLP
sentence-transformers = "^2.3"  # Embeddings
openai = {version = "^1.3", optional = true}  # LLM (optional)
anthropic = {version = "^0.8", optional = true}  # Alternative LLM

[tool.poetry.extras]
llm = ["openai", "anthropic"]  # Install with: poetry install -E llm
```

---

## ⚙️ OPS Agent: Execution Orchestrator

### Current Implementation (v1.0)

**Status:** ✅ Implemented (`src/kryptos/agents/ops.py`, 350 lines, 9 tests passing)

**Capabilities:**

- Parallel hypothesis execution (ProcessPoolExecutor)
- Job queue management with timeout enforcement
- Result aggregation and reporting
- Error handling (exceptions, timeouts)
- Resource monitoring (configurable max workers)
- Job summary statistics

**Example Usage:**

```python
from kryptos.agents.ops import OpsAgent, OpsConfig

agent = OpsAgent(config=OpsConfig(max_workers=8, job_timeout_seconds=300))

jobs = [
    {"name": "hill_2x2", "class": HillCipher2x2Hypothesis},
    {"name": "vigenere", "class": VigenereHypothesis, "params": {"max_key_length": 30}},
]

results = agent.run_parallel(jobs, ciphertext="OBKR...")

summary = agent.summarize()
print(f"Tested {summary['total_jobs']} hypotheses")
print(f"Best: {summary['best_hypothesis']} scored {summary['best_score']}")
```

**Architecture:**

```python
# src/kryptos/agents/ops.py

from concurrent.futures import ProcessPoolExecutor, TimeoutError
from queue import PriorityQueue
from dataclasses import dataclass
import psutil

@dataclass
class HypothesisTask:
    """A hypothesis to execute."""
    hypothesis_type: str  # 'vigenere', 'hill_2x2', etc.
    params: dict  # hypothesis-specific parameters
    priority: int  # lower number = higher priority
    timeout: int  # seconds before kill

class OpsAgent:
    """Orchestrates parallel hypothesis execution."""

    def __init__(self, max_workers: int = 4, memory_limit_gb: float = 8.0):
        self.queue = PriorityQueue()
        self.executor = ProcessPoolExecutor(max_workers=max_workers)
        self.memory_limit = memory_limit_gb * 1024**3  # bytes
        self.results = []

    def schedule(self, hypothesis_type: str, params: dict, priority: int = 5):
        """Add hypothesis to execution queue."""
        task = HypothesisTask(hypothesis_type, params, priority, timeout=3600)
        self.queue.put((priority, task))

    def execute_all(self) -> list[SearchResult]:
        """Execute all queued hypotheses with parallelism."""
        futures = []

        while not self.queue.empty():
            # Check resource limits
            if psutil.virtual_memory().used > self.memory_limit:
                print("Memory limit reached, waiting...")
                time.sleep(60)
                continue

            priority, task = self.queue.get()
            future = self.executor.submit(self._run_hypothesis, task)
            futures.append((task, future))

        # Collect results with timeout
        for task, future in futures:
            try:
                result = future.result(timeout=task.timeout)
                self.results.append(result)
            except TimeoutError:
                print(f"Timeout: {task.hypothesis_type}")
            except Exception as e:
                print(f"Error in {task.hypothesis_type}: {e}")

        return self.results

    def _run_hypothesis(self, task: HypothesisTask) -> SearchResult:
        """Run single hypothesis (called in subprocess)."""
        # Import hypothesis class dynamically
        # Execute search
        # Return results
        pass
```

**Integration with existing scripts:**

```python
# scripts/run_all_hypotheses.py

from kryptos.agents.ops import OpsAgent

ops = OpsAgent(max_workers=8)

# Schedule all hypotheses
ops.schedule('hill_2x2', {}, priority=1)  # High priority (weak signal)
ops.schedule('vigenere', {'min_length': 1, 'max_length': 30}, priority=1)
ops.schedule('transposition', {'widths': range(2, 21)}, priority=3)
ops.schedule('playfair', {'keywords': ['KRYPTOS', 'BERLIN']}, priority=5)

# Execute in parallel
results = ops.execute_all()

# Generate report
print(f"Tested {len(results)} hypotheses")
print(f"Best score: {max(r.best_score for r in results)}")
```

---

## 🔍 Q Agent: Quality Assurance

### Current Implementation (v1.0)

**Status:** ✅ Implemented (`src/kryptos/agents/q.py`, 310 lines, 17 tests passing)

**Capabilities:**

- Statistical validation (2σ/3σ significance thresholds)
- Random baseline comparison (mean: -355.92, σ: 14.62)
- Confidence scoring (68%, 95%, 99.7% levels)
- Result filtering (removes candidates below thresholds)
- Anomaly detection (impossible scores, duplicates)
- Validation reports with statistical context

**Example Usage:**

```python
from kryptos.agents.q import QAgent

q = QAgent()

# Validate candidate against random baseline
is_significant = q.validate_candidate(
    score=-329.45,
    confidence_level=0.95  # 2σ threshold
)

# Filter results
candidates = [...]
validated = q.filter_candidates(candidates, min_confidence=0.95)

print(f"Kept {len(validated)}/{len(candidates)} statistically significant results")
```

**Architecture:**

```python
# src/kryptos/agents/q.py

from scipy import stats
import numpy as np

@dataclass
class ValidationReport:
    """QA validation report for a hypothesis result."""
    hypothesis_id: str
    passed_sanity: bool
    statistical_tests: dict[str, float]  # p-values
    anomalies: list[str]
    confidence_interval: tuple[float, float]
    recommendation: str  # 'ACCEPT', 'REJECT', 'RETEST'

class QAgent:
    """Quality assurance and validation specialist."""

    def __init__(self, baseline_path: str):
        self.baseline = self._load_baseline(baseline_path)

    def validate_result(self, result: SearchResult) -> ValidationReport:
        """Comprehensive validation of hypothesis result."""

        # 1. Sanity tests (positive controls)
        sanity_passed = self._run_sanity_tests(result)

        # 2. Statistical tests
        stat_tests = {
            't_test': self._t_test_vs_baseline(result),
            'ks_test': self._ks_test_vs_baseline(result),
            'chi_square': self._chi_square_test(result),
        }

        # 3. Detect anomalies
        anomalies = self._detect_anomalies(result)

        # 4. Confidence interval
        ci = self._bootstrap_ci(result)

        # 5. Recommendation
        recommendation = self._make_recommendation(
            sanity_passed, stat_tests, anomalies, ci
        )

        return ValidationReport(
            hypothesis_id=result.hypothesis_id,
            passed_sanity=sanity_passed,
            statistical_tests=stat_tests,
            anomalies=anomalies,
            confidence_interval=ci,
            recommendation=recommendation,
        )

    def _t_test_vs_baseline(self, result: SearchResult) -> float:
        """Test if result differs significantly from random baseline."""
        # Two-sample t-test
        t_stat, p_value = stats.ttest_ind(
            result.all_scores,
            self.baseline['scores']
        )
        return p_value

    def _detect_anomalies(self, result: SearchResult) -> list[str]:
        """Flag suspicious patterns in results."""
        anomalies = []

        # Duplicate plaintexts
        if len(set(result.plaintexts)) < len(result.plaintexts) * 0.9:
            anomalies.append("High duplicate rate in candidates")

        # Impossibly high score
        if result.best_score > self.baseline['mean'] + 5 * self.baseline['stddev']:
            anomalies.append("Score exceeds 5σ (may be artifact)")

        # All scores identical
        if len(set(result.all_scores)) == 1:
            anomalies.append("All candidates have identical scores")

        return anomalies
```

---

## 🔄 Workflow Integration

**Full autonomous cycle:**

```python
# scripts/autonomous_search.py

from kryptos.agents.spy import SpyAgent
from kryptos.agents.ops import OpsAgent
from kryptos.agents.q import QAgent

# 1. OPS schedules and executes hypotheses
ops = OpsAgent(max_workers=8)
ops.schedule_all_hypotheses()  # Vigenère, Hill, Transposition, etc.
results = ops.execute_all()

# 2. Q validates each result
q = QAgent(baseline_path='artifacts/baselines/random_scoring_latest.json')
validated_results = []
for result in results:
    report = q.validate_result(result)
    if report.recommendation in ['ACCEPT', 'RETEST']:
        validated_results.append((result, report))

# 3. SPY analyzes top candidates
spy = SpyAgent(cribs=['BERLIN', 'CLOCK'])
for result, report in validated_results:
    for candidate in result.top_candidates[:10]:
        analysis = spy.analyze_candidate(candidate.plaintext)
        if analysis['pattern_score'] > 20.0:
            print(f"🎯 High-pattern candidate found!")
            print(spy_report(candidate.plaintext))

# 4. Generate final report
generate_master_report(validated_results)
```

---

## 📊 Metrics & Monitoring

**OPS tracks:**

- Hypotheses per hour
- CPU/memory utilization
- Success/failure rates
- Average execution time

**Q tracks:**

- Validation pass rate
- Anomaly detection rate
- False positive filtering

**SPY tracks:**

- Patterns detected per candidate
- Crib match rate
- High-confidence insight frequency

---

## 🚀 Roadmap

**Phase 1 (Current):** ✅ SPY v1.0 complete **Phase 2 (Next):** Implement OPS agent **Phase 3:** Implement Q agent
**Phase 4:** SPY v2.0 with NLP/LLM

**Timeline:** 2-3 weeks to full autonomous system

---

## 💡 Why This Architecture?

**Separation of concerns:**

- SPY = Domain expertise (linguistics, patterns)
- OPS = Infrastructure (execution, resources)
- Q = Rigor (validation, statistics)

**Modularity:**

- Each agent works standalone
- Optional LLM integration (not required)
- Gradual enhancement path

**Testability:**

- 249 tests and growing
- Each agent independently validated
- Integration tests for full workflow

**Less is More:**

- No bloated monolithic framework
- Simple Python classes with clear APIs
- Easy to understand and extend
