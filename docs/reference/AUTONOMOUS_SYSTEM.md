# Autonomous Cryptanalysis System

Breadcrumb: Home > Docs > Reference > Autonomous System


_Last updated: 2026-05-31_

## Overview

The autonomous system runs a continuous K4-oriented experimentation loop by combining the SPY, OPS, Q, and Linguist agents under `AutonomousCoordinator`. It can run unattended for hours or days, self-directing resource allocation and pivoting strategies based on measured progress.

Primary implementation entry points:

| Module | Role |
|--------|------|
| `src/kryptos/autonomous_coordinator.py` | Main orchestration loop (`AutonomousCoordinator`) |
| `src/kryptos/agents/ops_director.py` | Strategic decisioning (`OpsStrategicDirector`) |
| `src/kryptos/agents/spy_nlp.py` | NLP candidate analysis (`SpyNLP`) |
| `src/kryptos/agents/spy_web_intel.py` | Live crib discovery (`SpyWebIntel`) |
| `src/kryptos/meta_coordinator.py` | Higher-level task scheduling (`MetaCoordinator`) |
| `src/kryptos/autopilot.py` | Single-exchange and loop autopilot |

---

## Launching

```bash
# Standard autonomous run
kryptos autonomous --max-hours 24 --cycle-interval 5

# With options
kryptos autonomous \
  --max-hours 48 \
  --max-cycles 200 \
  --cycle-interval 5 \
  --ops-cycle 10 \
  --web-intel-hours 1
```

| Option | Default | Description |
|--------|---------|-------------|
| `--max-hours` | None (infinite) | Hard stop after N hours |
| `--max-cycles` | None (infinite) | Hard stop after N coordination cycles |
| `--cycle-interval` | 0.25 min (15 s) | Pause between cycles |
| `--ops-cycle` | 0.5 min (30 s) | Pause between OPS strategic analyses |
| `--web-intel-hours` | 0.5 h (30 min) | Gap between web-intel scrape runs |

Single-exchange autopilot:

```bash
kryptos autopilot [--plan "..."] [--dry-run] [--loop] [--iterations N]
```

---

## State and artifacts

All runtime state is persisted under `artifacts/` so runs can be inspected and resumed.

| Path | Contents |
|------|----------|
| `artifacts/autonomous_state.json` | Coordinator cycle state, last-known scores, active attack map |
| `artifacts/logs/kryptos_*.log` | Timestamped run logs |
| `artifacts/logs/progress_*.md` | Human-readable progress snapshots |
| `artifacts/intel_cache/` | SpyWebIntel page-fetch cache |
| `artifacts/ops_strategy/decisions.jsonl` | Strategy decision fallback log (primary: Neon `ops_decisions`) |
| `artifacts/search_space/` | SearchSpaceTracker region coverage and `tried_keys.jsonl` |

---

## DB integration

The autonomous system writes to Neon during runs:

| Table | Written by | When |
|-------|-----------|------|
| `ops_decisions` | `OpsStrategicDirector._save_decision` | Every strategic decision |
| `discovered_cribs` | `SpyWebIntel._save_cache` | After each web-intel scrape |

Both paths have local-file fallbacks so a DB outage never kills a campaign run.

---

## Dependencies

**spaCy model** — required for NLP-based candidate scoring:

```bash
python -m spacy download en_core_web_sm
```

Without it, `spy_nlp` paths are skipped and `test_autonomous_coordinator.py` will fail.

**LLM keys** — OPS strategic decisions are richer with an LLM backend:

```bash
OPENAI_API_KEY=...     # or
ANTHROPIC_API_KEY=...
```

Without either, `OpsStrategicDirector` falls back to rule-based decision logic (still functional).

**DATABASE_URL** — for Neon DB writes (see `kryptos.db`). Without it, local-file fallbacks are used.

---

## Test coverage

| Test | Tier | Covers |
|------|------|--------|
| `test_autonomous_coordinator.py` | e2e | Full coordinator cycle |
| `test_autopilot_flow.py` | e2e | Autopilot exchange loop |
| `test_autopilot_crib_update.py` | e2e | Crib propagation through loop |
| `test_fast_coverage_autonomous_coordinator_extra.py` | smoke | Edge cases, quick coverage |
| `test_fast_coverage_campaign_autopilot.py` | smoke | Campaign/autopilot quick paths |

---

## Related docs

- [`docs/reference/AGENTS_ARCHITECTURE.md`](AGENTS_ARCHITECTURE.md)
- [`docs/reference/PROVENANCE_SYSTEM_EXPLAINED.md`](PROVENANCE_SYSTEM_EXPLAINED.md)
- [`docs/reference/API_REFERENCE.md`](API_REFERENCE.md)
- [`docs/analysis/K4_ACTIVE_RESEARCH.md`](../analysis/K4_ACTIVE_RESEARCH.md)
- `ROADMAP.md`, `TASKS.md`
