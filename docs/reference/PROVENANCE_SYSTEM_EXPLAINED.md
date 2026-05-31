# Provenance and Search-Space Tracking

Breadcrumb: Home > Docs > Reference > Provenance


_Last updated: 2026-05-31_

## Purpose

Kryptos tracks two related things to prevent redundant work and enable strategic pruning:

- **Attempt provenance** — what was tried, with which parameters, and what score it produced
- **Search-space coverage** — which key regions have been explored and how densely

Without this, autonomous campaign runs repeat prior work and can't tell when a region is saturated.

---

## Components

### AttackLogger (`provenance/attack_log.py`)

Stores normalized attack records with deduplication by parameter hash.

```python
from kryptos.provenance.attack_log import AttackLogger, AttackRecord, AttackParameters, AttackResult

logger = AttackLogger()
logger.log(AttackRecord(
    parameters=AttackParameters(cipher_type="vigenere", key="KRYPTOS", key_length=7),
    result=AttackResult(score=0.42, plaintext="...", rank=1),
))
```

Key behaviors:
- Deduplicates on `(cipher_type, key, key_length)` hash — same attack never runs twice in a session
- `skip_tried=True` on `recover_key_by_frequency` skips keys already in the log
- Supports downstream reporting and analysis workflows

### SearchSpaceTracker (`provenance/search_space.py`)

Tracks which key regions have been explored and how many successes each region has produced.

```python
from kryptos.provenance.search_space import SearchSpaceTracker, KeySpaceRegion

tracker = SearchSpaceTracker()
tracker.register_region(KeySpaceRegion(cipher_type="vigenere", name="length_5", total_size=1000))
tracker.record_explored("vigenere", "length_5", count=100, successes=3)
recommendations = tracker.get_recommendations(top_n=5)
heatmap = tracker.export_heatmap_data("vigenere")
```

Key behaviors:
- Region coverage metrics (explored count, success rate, saturation detection)
- `get_recommendations` returns under-explored regions ranked by expected value
- Heatmap export for the `keyspace-stats` CLI command
- `tried_keys.jsonl` persisted under `artifacts/search_space/` for cross-run deduplication

---

## Storage locations

| Path | Contents |
|------|----------|
| `artifacts/attack_logs/` | Per-session attack records |
| `artifacts/search_space/` | Region coverage state + `tried_keys.jsonl` |
| `artifacts/intel_cache/` | SpyWebIntel page-fetch cache |
| `artifacts/ops_strategy/decisions.jsonl` | Strategy decision fallback (primary: Neon `ops_decisions`) |

---

## Cross-run memory

The baseline cross-run mechanism:
- `recover_key_by_frequency(..., skip_tried=True, tracker=SearchSpaceTracker())` skips previously tried keys
- `tried_keys.jsonl` is appended-to and loaded on each new run

Broader adaptive usage across all solver families (not just Vigenère recovery) is a tracked roadmap item — see `ROADMAP.md`.

---

## Neon DB integration

Runtime decision and crib data is now also written to Neon (more queryable than JSON files):

| Table | Source | Description |
|-------|--------|-------------|
| `ops_decisions` | `OpsStrategicDirector` | Strategy decisions with reasoning and confidence |
| `discovered_cribs` | `SpyWebIntel` | Crib candidates with source provenance |
| `strategy_kb` | Manual | Accumulated knowledge: successful/failed strategies, lessons |
| `k4_research_findings` | Manual research | Confirmed facts and ruled-out hypotheses |

Query examples:
```sql
-- What has been definitively ruled out?
SELECT claim, evidence FROM k4_research_findings WHERE kind = 'ruled_out';

-- What cribs do we have high confidence in?
SELECT text, source, confidence FROM discovered_cribs WHERE confidence > 0.8 ORDER BY confidence DESC;

-- What strategic decisions were made in the last campaign?
SELECT timestamp, action, reasoning, confidence FROM ops_decisions ORDER BY timestamp DESC LIMIT 20;
```

---

## CLI

```bash
kryptos keyspace-stats --cipher vigenere --top-n 5
kryptos keyspace-stats --json
```

---

## Test coverage

| Test | Tier |
|------|------|
| `tests/functional/test_attack_generator.py` | functional |
| `tests/functional/test_attack_provenance.py` | functional |
| `tests/functional/test_cross_run_memory.py` | functional |
| `tests/functional/test_search_space.py` | functional |
| `tests/functional/test_search_space_heuristics.py` | functional |

---

## Related docs

- [`docs/reference/AGENTS_ARCHITECTURE.md`](AGENTS_ARCHITECTURE.md) — agent layer that consumes provenance
- [`docs/reference/AUTONOMOUS_SYSTEM.md`](AUTONOMOUS_SYSTEM.md) — runtime loop that generates provenance
- [`docs/reference/API_REFERENCE.md`](API_REFERENCE.md) — `AttackLogger` and `SearchSpaceTracker` API details
