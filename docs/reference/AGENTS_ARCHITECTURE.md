# Agents Architecture

_Last updated: 2026-05-31_

## Purpose

The agent layer coordinates K4-oriented research. It is designed to prioritize reproducible experimentation, preserve strategic decision trails, and support long-running autonomous loops.

---

## Core agents

### SPY — pattern and language analysis

Detects linguistic patterns, crib hits, rhyme/meter, and thematic vocabulary in candidate plaintexts.

| Module | Role |
|--------|------|
| `agents/spy.py` | `SpyAgent` — pattern matching, crib search, poetry detection. `PatternInsight` dataclass. Convenience: `quick_spy_analysis`, `spy_report`. |
| `agents/spy_nlp.py` | `SpyNLP` — spaCy-powered NLP scoring. `NLPInsight` dataclass. **Requires `en_core_web_sm`.** |
| `agents/spy_web_intel.py` | `SpyWebIntel` — scrapes public sources for new crib candidates. Upserts to Neon `discovered_cribs` table; falls back to `artifacts/spy_web_intel/cribs.json`. |

### OPS — strategic direction

Analyzes attack progress and makes resource-allocation decisions (CONTINUE / BOOST / REDUCE / PIVOT / STOP / START_NEW). Supports LLM-backed (OpenAI / Anthropic) or rule-based fallback.

| Module | Role |
|--------|------|
| `agents/ops.py` | Lightweight ops utilities |
| `agents/ops_director.py` | `OpsStrategicDirector` — full strategic decision engine. Writes `StrategicDecision` records to Neon `ops_decisions` table (fallback: `artifacts/ops_strategy/decisions.jsonl`). Reads accumulated knowledge from `strategy_kb` table. |

### Q — validation and quality thresholds

Validates candidate plaintexts against configurable quality gates. Acts as the final filter before a candidate is surfaced.

| Module | Role |
|--------|------|
| `agents/q.py` | `QAgent`, `QConfig`, `ValidationResult`. Convenience: `q_report`. |

### LINGUIST — linguistic deep analysis

Corpus-style linguistic scoring using Sanborn's known plaintext as reference material.

| Module | Role |
|--------|------|
| `agents/linguist.py` | `LinguistAgent`, `LinguisticScore`, `SanbornCorpusAnalysis`. |

### K123 Analyzer — pattern extraction from solved sections

Extracts cipher patterns, misspelling conventions, theme vocabulary, and structural hints from K1–K3 to guide K4 strategy.

| Module | Role |
|--------|------|
| `agents/k123_analyzer.py` | `K123Analyzer` |

---

## Coordinator integration

`AutonomousCoordinator` wires all agents into a control loop:
- loads historical pattern context from prior runs
- schedules strategic analysis cycles at configurable intervals
- executes autopilot exchanges (SPY → OPS → Q cycle)
- persists state to `artifacts/autonomous_state.json` and logs under `artifacts/logs/`

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

- **`spy_nlp`** requires spaCy model: `python -m spacy download en_core_web_sm`
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
| `tests/functional/test_spy_*.py` | SPY pattern analysis |
| `tests/smoke/test_cli_subcommands.py` | CLI entry points |
