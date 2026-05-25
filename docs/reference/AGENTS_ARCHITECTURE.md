# Agents Architecture

Last Updated: 2026-05-24

## Purpose

This reference documents the current agent-layer architecture used by Kryptos for K4-oriented research orchestration.

The agent layer is designed to:
- prioritize reproducible experimentation
- preserve strategic decision trails
- support long-running autonomous loops

## Core Agents

### SPY

Primary role: candidate pattern/language analysis.

Current code surfaces:
- `src/kryptos/agents/spy.py`
- `src/kryptos/agents/spy_nlp.py`
- `src/kryptos/agents/spy_web_intel.py`

### OPS

Primary role: orchestration and strategic direction.

Current code surfaces:
- `src/kryptos/agents/ops.py`
- `src/kryptos/agents/ops_director.py`

### Q

Primary role: validation and quality thresholds.

Current code surface:
- `src/kryptos/agents/q.py`

### K123 Analyzer

Primary role: pattern extraction from solved sections to guide K4 strategy.

Current code surface:
- `src/kryptos/agents/k123_analyzer.py`

## Coordinator Integration

`AutonomousCoordinator` wires agent outputs into a control loop:
- loads historical pattern context
- schedules strategic analysis cycles
- executes autopilot exchanges
- persists state + reports

Code surface:
- `src/kryptos/autonomous_coordinator.py`

## Current Constraints

1. NLP model dependency
- `spy_nlp` currently relies on spaCy model `en_core_web_sm` in this environment.

2. Runtime wiring gaps from historical phase plans
- Some optional phase-era ideas (for example broader adaptive configuration layers) remain roadmap items rather than fully implemented runtime defaults.

See `ROADMAP.md`, `TASKS.md`, and `AUDIT.md` for tracked gaps.

## Test Coverage Pointers

Relevant tests include:
- `tests/test_autonomous_coordinator.py`
- `tests/test_autopilot_flow.py`
- `tests/test_autopilot_crib_update.py`
- `tests/test_cli_subcommands.py`

For latest validation outcomes and environment-specific blockers, see root `AUDIT.md`.
