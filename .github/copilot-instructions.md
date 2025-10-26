# Kryptos Cryptanalysis System - AI Agent Instructions

## Project Overview

**Kryptos** is a research toolkit for solving the K4 cipher (the last unsolved section of the CIA's Kryptos sculpture).
The system combines classical cryptanalysis with autonomous agents, linguistic scoring, and exhaustive search
strategies. **Current Status:** Phase 6 - K1 works 100%, K2/K3 need fixes before K4 is attempted.

**Core Philosophy:** *"Human expertise to build, machine endurance to run."* This is production-grade cryptanalysis
infrastructure with 564 passing tests, full provenance tracking, and 24/7 autonomous operation capability.

## Critical Architecture Patterns

### 1. Pipeline-Based Search Architecture

All cryptanalysis uses **modular pipeline stages** that transform ciphertexts through hypothesis spaces:

```python
# Pattern: Always use make_*_stage() factory functions
from kryptos.k4.pipeline import make_hill_constraint_stage, make_transposition_stage

stages = [
    make_hill_constraint_stage(partial_len=50, partial_min=-850.0),
    make_transposition_adaptive_stage(min_cols=5, max_cols=6)
]
```

**Key Files:**
- `src/kryptos/k4/pipeline.py` - Core `Pipeline` class and stage factories
- `src/kryptos/stages/interface.py` - `Stage` protocol definition
- `src/kryptos/k4/composite.py` - Multi-stage fusion with weighted scoring

**Critical Pattern:** Stages return `StageResult` with `candidates` list. Each candidate has `text`, `score`, `source`,
and `lineage` (transformation chain). Never mutate candidates in-place.

### 2. Agent Triumvirate (SPY, OPS, Q)

Three specialized agents orchestrate cryptanalysis:

- **SPY v2.0** (`agents/spy_nlp.py`) - Pattern recognition with NLP (spaCy, embeddings, optional LLM)
- **OPS Strategic Director** (`agents/ops_director.py`) - Attack orchestration and strategic decisions
- **Q Research Assistant** (`agents/q.py`) - Statistical validation (2σ/3σ thresholds, anomaly detection)

**Integration Point:** `autonomous_coordinator.py` runs coordination loop, calls agents, executes attacks via
`autopilot.py`.

**Critical:** Agents communicate via `CoordinationMessage` dataclass. See `autonomous_coordinator.py` lines 1-81 for
message types.

### 3. Scoring System (Chi-Square + Enhanced Linguistics)

Scoring uses **chi-square with n-gram frequencies** as baseline, enhanced by dictionary hits and linguistic features:

```python
from kryptos.k4.scoring import quadgram_score, baseline_stats

score = quadgram_score(plaintext)  # Lower is better (log-likelihood)
stats = baseline_stats(plaintext)  # Returns dict with 'wordlist_hit_rate', 'trigram_entropy', etc.
```

**Data Files:** `data/quadgrams_high_quality.tsv`, `data/trigrams.tsv`, `data/bigrams.tsv`, `data/letter_freq.tsv`

**Critical:** Scores are **negative log-likelihood** - more negative = worse. Random English ~-355.92 (σ=14.62). Target:
better than -320 for significance.

### 4. Provenance & Reproducibility

Every attack is logged with full transformation history:

```python
from kryptos.provenance.attack_log import AttackLog, AttackResult

log = AttackLog()
log.log_result(AttackResult(
    attack_name="vigenere_period_5_key_HELLO",
    plaintext=result,
    score=score,
    metadata={"key": "HELLO", "period": 5}
))
```

**Persistence:** `kryptos k4-attempts --label k4` writes timestamped JSON to `reports/attempts_k4_YYYYMMDDTHHMMSS.json`

**Critical:** Use `attack_log.deduplicate()` before persisting - K4 search generates millions of duplicates.

## Developer Workflows

### Running Tests

```bash
# All tests (564 should pass, ~5 min)
pytest tests/ -v

# Skip slow tests (for rapid iteration)
pytest tests/ -m "not slow" -v

# Specific module
pytest tests/test_k4_pipeline.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

**Test Markers:** `@pytest.mark.slow` for >10s tests, `@pytest.mark.integration` for multi-component tests.

### CLI Commands

```bash
# List sections (K1-K4 ciphertexts)
kryptos sections

# Decrypt K4 (composite pipeline)
kryptos k4-decrypt --cipher data/k4_cipher.txt --limit 40 --adaptive --report

# Persist attempt logs
kryptos k4-attempts --label k4

# Tuning workflows
kryptos tuning-crib-weight-sweep --weights 0.5,1.0,1.5 --cribs BERLIN,CLOCK
```

**Entry Point:** `src/kryptos/cli/main.py` - uses argparse, delegates to subcommand functions.

### Autonomous Operation

```bash
# Start 24-hour autonomous search
python -m kryptos.cli.main autonomous --max-hours 24 --cycle-interval 5

# Monitor progress
tail -f artifacts/logs/kryptos_*.log
```

**Artifacts:** All output goes to `artifacts/` subdirectories (see `src/kryptos/paths.py` for canonical paths).

## Code Conventions

### Naming Patterns

- **Stage factories:** `make_<cipher>_stage()` (e.g., `make_hill_constraint_stage`)
- **Agents:** `<Name>Agent` classes (e.g., `SpyAgent`, `OpsAgent`)
- **Hypothesis modules:** `src/kryptos/k4/<cipher>.py` (e.g., `vigenere_key_recovery.py`, `hill_cipher.py`)
- **Tests:** `test_<module>.py` mirrors source structure

### Import Style

```python
# ✅ Good: Explicit local imports
from kryptos.k4.pipeline import Pipeline, make_hill_constraint_stage
from kryptos.k4.scoring import quadgram_score

# ❌ Bad: Avoid star imports (hurts IDE autocomplete)
from kryptos.k4 import *
```

**Critical:** Never create files named `logging.py`, `collections.py`, `typing.py` - they shadow stdlib!

### Data Classes & Protocols

Use `@dataclass` for data structures, `Protocol` for interfaces:

```python
from dataclasses import dataclass
from typing import Protocol

@dataclass
class StageResult:
    candidates: list[dict]
    metadata: dict

class Stage(Protocol):
    def __call__(self, ciphertext: str, context: dict) -> StageResult: ...
```

**Pattern:** Slots (`@dataclass(slots=True)`) for high-frequency objects (scoring, candidates).

### Error Handling

```python
# Pattern: Fail gracefully in search loops, crash hard in setup
try:
    result = decrypt_with_key(cipher, key)
    candidates.append(result)
except ValueError as e:
    logger.debug("Invalid key %s: %s", key, e)  # Continue search
    continue

# Setup failures should crash with clear messages
if not quadgrams_file.exists():
    raise FileNotFoundError(f"Required data file missing: {quadgrams_file}")
```

## Key Integration Points

### Adding a New Cipher Hypothesis

1. **Create module:** `src/kryptos/k4/my_cipher.py` with `encrypt()` and `decrypt()` functions 2. **Add stage factory:**
In `pipeline.py`, create `make_my_cipher_stage()` 3. **Wire to composite:** Add to `src/kryptos/k4/composite.py` stage
list 4. **Add tests:** `tests/test_my_cipher.py` with known plaintext/ciphertext pairs 5. **Update exports:** Add to
`src/kryptos/k4/__init__.py`

### Extending Scoring

All scoring functions should accept `str` and return `float`:

```python
def my_custom_score(text: str) -> float:
    """Lower scores are better."""
    return -sum(1 for word in WORDLIST if word in text)
```

Add to `baseline_stats()` in `k4/scoring.py` for composite scoring.

### Agent Communication

```python
from kryptos.autonomous_coordinator import CoordinationMessage, MessageType

# Agent sends insight to coordinator
message = CoordinationMessage(
    type=MessageType.INSIGHT,
    source="SPY",
    content={"pattern": "BERLIN found at position 64", "confidence": 0.85}
)
coordinator.handle_message(message)
```

## Known Issues & Workarounds

### Phase 6 Critical Gaps (from PHASE_6_ROADMAP.md)

1. **K3 Transposition:** Only 27.5% success on known solution (should be >95%)
   - **Workaround:** Increase SA iterations to 100k-200k, tune cooling schedule
   - **File:** `src/kryptos/k4/transposition.py` (simulated annealing solver)

2. **K2 Alphabet Variants:** Code exists but not wired to orchestrator
   - **File:** `src/kryptos/k4/vigenere_key_recovery.py` has alphabet enumeration
   - **Action:** Wire to `attack_generator.py` and `k4_campaign.py`

3. **Placeholder Comments:** `ops.py` line 360 says "placeholder" but code IS implemented
   - **Action:** Validate `_execute_vigenere()` (lines 490-530) and update comment

### Test Infrastructure

- **564/564 tests passing** but code audit found 688 test functions defined
- **Action:** Some tests may be skipped or not collected - check pytest markers

### Performance

- **Sequential:** 2.5 attacks/second baseline
- **Parallel target:** 10-15 attacks/second (implement multiprocessing in `ops.py`)

## Quick Reference

### Most Important Files

| Path | Purpose |
|------|---------|
| `src/kryptos/k4/pipeline.py` | Core pipeline system, all stage factories |
| `src/kryptos/k4/composite.py` | Multi-stage fusion and weighted scoring |
| `src/kryptos/k4/scoring.py` | Chi-square, n-gram scoring, linguistic metrics |
| `src/kryptos/autonomous_coordinator.py` | 24/7 autonomous orchestration loop |
| `src/kryptos/agents/spy_nlp.py` | Pattern recognition with NLP |
| `src/kryptos/agents/ops_director.py` | Strategic attack orchestration |
| `docs/PHASE_6_ROADMAP.md` | Current status, critical gaps, sprint plan |

### Data Flow

```
Ciphertext → Pipeline Stages → Candidates (scored) → Agent Validation →
  → Attack Logging → Report Generation → Human Review
```

### Debugging Tips

1. **Score looks wrong?** Check `baseline_stats(plaintext)` - returns full diagnostic dict 2. **Pipeline stuck?** Add
`logger.debug()` in stage `__call__()` methods 3. **Test failing?** Use `pytest -vv --tb=short` for concise tracebacks
4. **Autonomous loop issues?** Check `artifacts/autonomous_state.json` for persisted state

## Project-Specific Gotchas

1. **Scores are negative:** -320 is better than -355. Closer to 0 = better. 2. **K4 has no spaces:** All Kryptos
ciphertexts are uppercase, no spaces/punctuation 3. **Cribs are hints, not guarantees:** BERLIN and CLOCK may appear
transformed (transposed, shifted) 4. **Duplicate candidates:** Use `attack_log.deduplicate()` - K4 generates millions of
near-duplicates 5. **Test duration:** Full test suite is 5 minutes - use `-m "not slow"` for <30s runs 6. **Autonomous
state persists:** Coordinator saves state to JSON - delete `artifacts/autonomous_state.json` to reset

## Getting Help

- **Architecture:** Read `docs/reference/AGENTS_ARCHITECTURE.md`
- **API reference:** `docs/reference/API_REFERENCE.md`
- **Phase status:** `docs/PHASE_6_ROADMAP.md`
- **K1-K3 patterns:** `docs/analysis/K123_PATTERN_ANALYSIS.md`
- **Contributing:** `CONTRIBUTING.md` (includes code guidelines)

---

## Phase 6 Priority Todo List

See comprehensive breakdown in root `TODO_PHASE_6.md` - focuses on: 1. **Learning & Memory** - Cross-run search space
exclusion, adaptive solver tuning 2. **K2/K3 Reliability** - Fix alphabet variants (3.8%→100%), transposition SA
(27.5%→95%) 3. **Composite Attacks** - V→T and T→V chaining with provenance tracking 4. **Test Coverage** - Add
autonomous solve tests, integration tests, edge cases (65%→90%) 5. **Production Ready** - Remove placeholders, wire OPS
execution, optimize performance (2.5→10+ attacks/sec)

---

**Last Updated:** 2025-10-25 | **Phase:** 6 (Operational Readiness) | **Test Status:** 564/564 passing
