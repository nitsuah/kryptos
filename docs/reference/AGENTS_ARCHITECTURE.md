# Agents Architecture

Breadcrumb: Home > Docs > Reference > Agents


_Last updated: 2026-06-10_

## Purpose

The agent layer coordinates K4-oriented research. It is designed to prioritize reproducible experimentation, preserve strategic decision trails, and support long-running autonomous loops.

---

## Core agents

### SPY — pattern and language analysis

Detects linguistic patterns, crib hits, rhyme/meter, and thematic vocabulary in candidate plaintexts.

| Module | Role |
|--------|------|
| `agents/spy.py` | `SpyAgent` — pattern matching, crib search, poetry detection. `PatternInsight` dataclass. Convenience: `quick_spy_analysis`, `spy_report`. Constructs `SpyNLP` internally with a `try/except` fallback (`nlp_available = False`) if the spaCy model is missing. |
| `agents/spy_nlp.py` | `SpyNLP` — spaCy-powered NLP scoring. `NLPInsight` dataclass. **Requires `en_core_web_sm`.** Used only via `SpyAgent`'s guarded construction, not instantiated directly by `AutonomousCoordinator`. |
| `agents/spy_web_intel.py` | `SpyWebIntel` — scrapes public sources for new crib candidates. `gather_intelligence(force_refresh: bool = False) -> dict` (keys: `new_cribs`, `updates`, `timestamp`); `get_top_cribs(min_confidence: float = 0.6, category: str | None = None) -> list[str]`. Upserts to Neon `discovered_cribs` table; falls back to `artifacts/spy_web_intel/cribs.json`. |

### OPS — strategic direction

Analyzes attack progress and makes resource-allocation decisions (CONTINUE / BOOST / REDUCE / PIVOT / STOP / START_NEW). Supports LLM-backed (OpenAI / Anthropic) or rule-based fallback.

| Module | Role |
|--------|------|
| `agents/ops.py` | Lightweight ops utilities |
| `agents/ops_director.py` | `OpsStrategicDirector` — full strategic decision engine. `update_attack_progress(attack_type: str, attempts: int, best_score: float)`. `analyze_situation(force_decision: bool = False) -> StrategicDecision \| None` — returns `None` when no decision is needed yet (the common case on early/healthy cycles). Writes `StrategicDecision` records to Neon `ops_decisions` table (fallback: `artifacts/ops_strategy/decisions.jsonl`). Reads accumulated knowledge from `strategy_kb` table. |

### Q — validation and quality thresholds

Validates candidate plaintexts against configurable quality gates. Acts as the final filter before a candidate is surfaced.

| Module | Role |
|--------|------|
| `agents/q.py` | `QAgent`, `QConfig`, `ValidationResult`. Convenience: `q_report`. |

### LINGUIST — linguistic deep analysis

Corpus-style linguistic scoring using Sanborn's known plaintext as reference material.

| Module | Role |
|--------|------|
| `agents/linguist.py` | `LinguistAgent`, `LinguisticScore`, `SanbornCorpusAnalysis`. Optional enhanced-scoring pass wired into `pipeline/validator.py` stage 3 via `PlaintextValidator(enable_linguist=True)` (default `False`). When enabled, `_init_linguist()` requires `torch`/`transformers`; if unavailable or initialization fails, degrades gracefully to `linguist_available=False` and stage 3 behaves exactly as before. `LinguistAgent` offers transformer-based (with heuristic fallback) perplexity/coherence scoring via `validate_candidate`/`batch_validate`, exposed as `PlaintextValidator._linguist_score`/`batch_validate_linguist`. |

### K123 Analyzer — pattern extraction from solved sections

Extracts cipher patterns, misspelling conventions, theme vocabulary, and structural hints from K1–K3 to guide K4 strategy.

| Module | Role |
|--------|------|
| `agents/k123_analyzer.py` | `K123Analyzer` |

---

## Coordinator integration

`AutonomousCoordinator` wires the K123 analyzer, SPY web intel, and OPS strategic
director into a control loop. Each `_coordination_cycle()`:
- loads K1-K3 pattern context from `K123Analyzer` (once, cached via `k123_patterns_loaded`)
- checks `SpyWebIntel` for new cribs on a configurable interval (`_check_web_intelligence`)
- runs `OpsStrategicDirector.analyze_situation()` on a configurable interval
  (`_run_ops_strategic_analysis`), reporting per-attack progress via
  `update_attack_progress(attack_type, attempts, best_score)`; a `None` result means
  no decision is needed yet and is logged, not treated as an error
- executes an autopilot exchange (SPY → OPS → Q cycle) via `run_exchange(autopilot=True)`
- persists state to `artifacts/autonomous_state.json` and logs under `artifacts/logs/`

`SpyNLP` is **not** constructed directly by `AutonomousCoordinator` — NLP-based
scoring is only available via `SpyAgent`'s guarded construction (see SPY table
above).

`MetaCoordinator` provides higher-level task scheduling and resource allocation across multiple agents and attack families.

| Module | Role |
|--------|------|
| `autonomous_coordinator.py` | `AutonomousCoordinator`, `AutonomousState` |
| `meta_coordinator.py` | `MetaCoordinator` |
| `autopilot.py` | `run_exchange`, `run_autopilot_loop`, `recommend_next_action` |

---

## DB integration (current)

| Agent | Table written | Fallback |
|-------|--------------|---------|
| `OpsStrategicDirector` | `ops_decisions` | `artifacts/ops_strategy/decisions.jsonl` |
| `SpyWebIntel` | `discovered_cribs` | `artifacts/spy_web_intel/cribs.json` |

Strategy knowledge (`strategy_kb` table) is read by `OpsStrategicDirector` on init; write path is not yet automated — populate manually or via future agent extension.

---

## Dependencies

- **`spy_nlp`** requires spaCy model: `python -m spacy download en_core_web_sm`. This
  model is **not** installed in the runtime Docker image; `SpyAgent` degrades
  gracefully (`nlp_available = False`) when it is missing.
- **`ops_director` LLM paths** require `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`; both fall back to rule-based logic if absent
- **DB writes** require `DATABASE_URL` in environment (see `kryptos.db`)

---

## Test coverage

| Test file | Covers |
|-----------|--------|
| `tests/e2e/test_autonomous_coordinator.py` | Full coordinator cycle |
| `tests/e2e/test_autopilot_flow.py` | Autopilot exchange loop |
| `tests/e2e/test_autopilot_crib_update.py` | Crib update propagation |
| `tests/functional/test_ops_agent.py` | OPS strategic decisions |
| `tests/functional/test_q_agent.py` | Q validation thresholds |
| `tests/functional/test_linguist.py` | Linguist scoring |
| `tests/functional/test_validator_linguist.py` | LINGUIST integration in `pipeline/validator.py` stage 3 (opt-in, graceful degradation) |
| `tests/functional/test_spy_*.py` | SPY pattern analysis |
| `tests/smoke/test_cli_subcommands.py` | CLI entry points |

---

## Module review

See `docs/analysis/AGENT_MODULE_REVIEW.md` for the Post-K4 audit of `spy_nlp.py`,
`spy_web_intel.py`, `linguist.py`, and `ops_director.py`, including bugs found and
fixed in `AutonomousCoordinator`'s integration with these modules.
