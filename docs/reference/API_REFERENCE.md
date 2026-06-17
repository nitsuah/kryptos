# Kryptos Public API Reference

Breadcrumb: Home > Docs > Reference > API


_Last updated: 2026-05-31_

This document covers the stable, supported Python entry points and CLI subcommands. Items not listed here are internal and may change without notice.

---

## Stability policy

- **Stable** — Semantic compatibility guaranteed across minor versions (additive changes only).
- **Experimental** — May change or be removed after one minor version.
- **Deprecated** — Emits `DeprecationWarning`; removal schedule in docstring.

---

## Top-level entry point

### `kryptos.k4.decrypt_best`

```python
from kryptos.k4 import decrypt_best, DecryptResult

result: DecryptResult = decrypt_best(
    ciphertext: str,
    *,
    strategy: str = "default",   # only "default" currently supported
    limit: int = 50,
    weights: dict[str, float] | None = None,
    adaptive: bool = False,
    report: bool = False,
    report_dir: str = "reports",
    try_all_alphabets: bool = False,
)
```

`DecryptResult` fields:

| Field | Type | Description |
|-------|------|-------------|
| `plaintext` | `str` | Best plaintext candidate |
| `score` | `float` | Fused score of best candidate |
| `candidates` | `list[dict]` | Top candidates after aggregation |
| `profile` | `dict` | Stage durations and diagnostics |
| `artifacts` | `dict \| None` | Artifact file paths (when `report=True`) |
| `attempt_log` | `str \| None` | Path to attempt log |
| `lineage` | `list[str] \| None` | Ordered stage names executed |
| `metadata` | `dict \| None` | Strategy label, provenance hash |

Default stage bundle: `masking → transposition-adaptive → transposition → berlin-clock`.

---

## Sections

```python
from kryptos.sections import SECTIONS   # dict[str, callable]
from kryptos.k1 import decrypt as k1_decrypt
from kryptos.k2 import decrypt as k2_decrypt
from kryptos.k3 import decrypt as k3_decrypt
```

`SECTIONS` maps `{"K1": fn, "K2": fn, "K3": fn, "K4": fn}`. K1/K2 require a `key` argument; K3/K4 do not.

---

## K4 scoring

All scoring functions accept a plain `str` (uppercase alpha assumed) and return `float` unless noted.

### Core

```python
from kryptos.k4.scoring import (
    combined_plaintext_score,            # primary composite scorer
    combined_plaintext_score_cached,     # lru_cache-wrapped version
    combined_plaintext_score_extended,   # adds trigram entropy + wordlist
    combined_plaintext_score_with_positions,  # adds positional crib bonus
    combined_plaintext_score_with_external_cribs,
    composite_score_with_stage_analysis, # dict output with per-stage breakdown
    baseline_stats,                      # dict of all individual metrics
)
```

### N-gram / frequency

```python
from kryptos.k4.scoring import (
    bigram_score,
    trigram_score,
    quadgram_score,
    chi_square_stat,
    index_of_coincidence,
    letter_coverage,
    letter_entropy,
    repeating_bigram_fraction,
    bigram_gap_variance,
    trigram_entropy,
    positional_letter_deviation_score,  # period: int = 5
    segment_plaintext_scores,           # Iterable[str] → dict
    vowel_ratio,
)
```

### Crib bonuses

```python
from kryptos.k4.scoring import (
    crib_bonus,                   # unweighted substring match
    rarity_weighted_crib_bonus,   # weights uncommon cribs higher
    positional_crib_bonus,        # positional: dict[str, list[int]], window: int = 5
    wordlist_hit_rate,            # fraction of windows matching wordlist
)
```

### Instructional scorer (K4-specific)

```python
from kryptos.k4.scoring_instructional import (
    instructional_score,          # boosts geographic/imperative vocabulary
    combined_instructional_score, # composite with fuzzy Sanborn-misspelling matching
    entropy_gate,                 # bool — rejects candidates outside entropy band
)
```

Vocabulary categories: `cardinal`, `spatial`, `measurement`, `imperative`. Levenshtein ≤ 1 fuzzy matching covers Sanborn-style misspellings (e.g. DESPARATLY, IQLUSION).

### Enhanced linguistic scorer

```python
from kryptos.k4.scoring_enhanced import (
    combined_linguistic_score,
    enhanced_combined_score,
    linguistic_diagnostics,       # dict of all sub-scores
    syllable_structure_score,
    word_boundary_score,
    phonetic_rules_score,
    vowel_consonant_alternation_score,
    position_specific_frequency_score,
)
```

---

## K4 pipeline

### Stage factories

```python
from kryptos.k4.pipeline import (
    Stage, StageResult, Pipeline,
    make_hill_constraint_stage,
    make_berlin_clock_stage,
    make_transposition_stage,
    make_transposition_adaptive_stage,
    make_masking_stage,
    make_transposition_multi_crib_stage,
    make_route_transposition_stage,
    get_clock_attempt_log,
)
```

### Composite runner

```python
from kryptos.k4.composite import (
    run_composite_pipeline,       # list[Stage] → pipeline_out dict
    aggregate_stage_candidates,
    fuse_scores_weighted,
    normalize_scores,
    adaptive_fusion_weights,
    CompositeChainExecutor,       # S→T→S chain with eureka halt
)
```

---

## K4 hypotheses

All hypothesis classes implement `generate_candidates(ciphertext: str, limit: int) -> list[Candidate]`.

### Single-stage

| Class | Description |
|-------|-------------|
| `HillCipher2x2Hypothesis(limit)` | Hill 2×2 exhaustive key search |
| `HillCipher3x3GeneticHypothesis(population_size, generations, mutation_rate, elite_fraction)` | Hill 3×3 genetic algorithm |
| `BerlinClockTranspositionHypothesis` | Berlin Clock lamp-pattern column widths |
| `BerlinClockVigenereHypothesis` | Berlin Clock shifts as Vigenère key |
| `SimpleSubstitutionHypothesis(variants)` | Monoalphabetic frequency analysis |
| `VigenereHypothesis(max_key_length, candidates_per_length)` | Vigenère with Kasiski + IC |
| `AutokeyHypothesis` | Self-keying Vigenère |
| `PlayfairHypothesis` | Playfair 5×5 grid |
| `FourSquareHypothesis` | Four-Square two-grid |
| `BifidHypothesis` | Bifid fractionating cipher |

### Composite (2-layer)

| Class | Layers |
|-------|--------|
| `TranspositionThenHillHypothesis` | Transposition → Hill 2×2 |
| `VigenereThenTranspositionHypothesis` | Vigenère → Columnar transposition |
| `SubstitutionThenTranspositionHypothesis` | Substitution → Transposition |
| `HillThenTranspositionHypothesis` | Hill → Transposition |
| `AutokeyThenTranspositionHypothesis` | Autokey → Transposition |
| `PlayfairThenTranspositionHypothesis` | Playfair → Transposition |
| `DoubleTranspositionHypothesis` | Double columnar transposition |
| `VigenereThenHillHypothesis` | Vigenère → Hill |

Extend `CompositeHypothesis(stage1_hypothesis, stage2_hypothesis, stage1_candidates, stage2_limit, hypothesis_name)` for custom chains.

---

## Fractionating ciphers

```python
from kryptos.k4 import (
    adfgvx_encrypt, adfgvx_decrypt, build_polybius_square,
    nihilist_encrypt, nihilist_decrypt,
)
from kryptos.k4.beaufort import beaufort_encrypt, beaufort_decrypt, recover_beaufort_key
```

`nihilist_encrypt/decrypt` operate on `list[int]`. Use `format_ciphertext` / `parse_ciphertext` (in `nihilist` module) for string conversion.

---

## Keystream and crib validation

```python
from kryptos.k4.keystream_validator import (
    compute_shifts_at_cribs,     # per-position shift dict from confirmed crib windows
    validate_keystreams,          # checks shift sequences against expected values
    validate_k4_cribs,            # validates all four confirmed cribs simultaneously
    crib_hit_count,               # integer count of crib matches
    keystream_summary,            # full keystream analysis dict
)
```

Confirmed crib positions (0-indexed): EAST 22–25, NORTHEAST 26–34, BERLIN 63–68, CLOCK 69–73.

---

## Inverse transposition sweep

```python
from kryptos.k4.inverse_transposition_sweep import (
    invert_permutation,
    sweep_grid,    # single grid geometry → candidate list
    full_sweep,    # all grid geometries (10×10, 7×14, 8×13) + ENE angle variants
)
```

---

## Eureka detection

```python
from kryptos.k4.eureka import (
    EurekaSignal,               # exception raised on breakthrough
    check_eureka,               # raises EurekaSignal if all cribs satisfied
    write_breakthrough_snapshot,
    eureka_check_and_capture,   # combined check + snapshot
)
```

`CompositeChainExecutor` calls `eureka_check_and_capture` automatically at each stage boundary.

---

## Provenance and search space

```python
from kryptos.provenance.attack_log import (
    AttackLogger, AttackRecord, AttackParameters, AttackResult,
)
from kryptos.provenance.search_space import SearchSpaceTracker, KeySpaceRegion
```

`AttackLogger` deduplicates by parameter hash; pass `skip_tried=True` to skip previously explored keys. `SearchSpaceTracker` tracks region coverage, exports heatmap data, and persists `tried_keys.jsonl` across runs under `artifacts/search_space/`.

---

## Pipeline (campaign level)

```python
from kryptos.pipeline.k4_campaign import K4CampaignOrchestrator, CampaignResult
from kryptos.pipeline.attack_generator import AttackGenerator, AttackSpec
from kryptos.pipeline.attack_executor import AttackExecutor
```

`K4CampaignOrchestrator` wires generator → executor → provenance in a managed campaign loop. Reads ciphertexts and cribs from `config/config.json`.

---

## Agents

```python
from kryptos.agents.spy import SpyAgent, PatternInsight, quick_spy_analysis, spy_report
from kryptos.agents.spy_nlp import SpyNLP, NLPInsight          # requires spaCy en_core_web_sm
from kryptos.agents.spy_web_intel import SpyWebIntel            # upserts to discovered_cribs (Neon)
from kryptos.agents.ops_director import (
    OpsStrategicDirector, StrategicDecision, StrategyAction,
    AttackProgress, AgentInsight,
)
from kryptos.agents.q import QAgent, QConfig, ValidationResult, q_report
from kryptos.agents.linguist import LinguistAgent, LinguisticScore, SanbornCorpusAnalysis
from kryptos.agents.k123_analyzer import K123Analyzer
```

`OpsStrategicDirector` writes decisions to the Neon `ops_decisions` table (fallback: `artifacts/ops_strategy/decisions.jsonl`). `SpyWebIntel` upserts discovered crib candidates to the Neon `discovered_cribs` table.

---

## Autonomous coordination

```python
from kryptos.autonomous_coordinator import AutonomousCoordinator, AutonomousState
from kryptos.meta_coordinator import MetaCoordinator
from kryptos.autopilot import run_exchange, run_autopilot_loop, recommend_next_action
```

---

## Infrastructure

```python
from kryptos.paths import (
    get_repo_root, get_artifacts_root, get_logs_dir,
    get_decisions_dir, get_tuning_runs_root,
    ensure_reports_dir, provenance_hash, get_provenance_info,
)
from kryptos.db import get_conn, get_db_url   # Neon psycopg2 helper (reads DATABASE_URL env var)
from kryptos.log_setup import setup_logging
```

---

## Ciphers (low-level)

```python
from kryptos.ciphers import (
    vigenere_decrypt,
    k3_decrypt,
    double_rotational_transposition,
    rotate_matrix_right_90,
    transposition_decrypt,
    polybius_decrypt,
    beaufort_decrypt, beaufort_encrypt,
)
```

---

## CLI subcommands

```
kryptos sections
kryptos k4-decrypt [--cipher PATH] [--limit N] [--adaptive] [--report] [--no-auto-alphabet]
kryptos sections-decrypt --section K1|K2|K3|K4 [--cipher PATH] [--key KEY] [--explain] [--json]
kryptos k4-attempts [--label LABEL]
kryptos keyspace-stats [--cipher TYPE] [--top-n N] [--json]
kryptos tuning-crib-weight-sweep [--weights CSV] [--cribs CSV] [--samples PATH] [--json]
kryptos tuning-pick-best --csv PATH
kryptos tuning-summarize-run --run-dir PATH [--no-write]
kryptos tuning-tiny-param-sweep
kryptos tuning-holdout-score --weight FLOAT [--out PATH] [--no-write]
kryptos tuning-report --run-dir PATH [--top-n N] [--no-markdown]
kryptos spy-eval [--labels PATH] [--runs PATH] [--thresholds CSV]
kryptos spy-extract [--runs PATH] [--min-conf FLOAT]
kryptos autopilot [--plan TEXT] [--dry-run] [--loop] [--iterations N] [--interval SECS] [--force]
kryptos autonomous [--max-hours H] [--max-cycles N] [--cycle-interval M] [--ops-cycle M] [--web-intel-hours H]
kryptos examples-smoke [--limit N] [--keep N]
```

`--cipher` is optional on `k4-decrypt` and `sections-decrypt`; omitting it loads the ciphertext from `config/config.json`.

---

## HTTP API (`kryptos serve`)

FastAPI app (`kryptos.api.app:create_app`), served with `kryptos serve [--host H] [--port P] [--reload]`.

### RAG (turbovec search over `artifacts/`)

| Method & path | Purpose |
|---------------|---------|
| `GET /health` | Liveness check → `{"status": "ok"}` |
| `GET /api/rag/status` | turbovec index status |
| `POST /api/rag/reindex` | Rebuild the artifact index |
| `GET /api/rag/search?q=&k=` | Semantic search (409 if index not built) |

### Dashboard (`kryptos.api.dashboard`)

Read endpoints query Neon via `kryptos.persistence` and degrade gracefully when `DATABASE_URL`
is unset (they return `db_enabled: false` with empty results rather than erroring).

| Method & path | Purpose |
|---------------|---------|
| `GET /api/status` | `db_enabled`, per-table row counts, latest run summary |
| `GET /api/runs?limit=` | Recent `campaign_runs` (newest first) |
| `GET /api/runs/{run_id}/candidates?limit=` | Candidates for a run, ranked |
| `GET /api/candidates?limit=` | Highest-scoring candidates across all runs |
| `POST /api/decrypt` | Body `{section, ciphertext, key?}` → `{section, plaintext}`. K1/K2 require `key`; K3 ignores it; unknown section → 422 |

### Live log tail (SSE — `kryptos.api.log_stream`)

| Method & path | Purpose |
|---------------|---------|
| `GET /api/stream/logs?backlog=&follow=` | Server-Sent Events stream of `kryptos` log records |

`create_app()` installs an idempotent `SSELogHandler` on the `kryptos` logger that
appends formatted records to a process-wide bounded ring (`LogBuffer`, 1000 lines).
The endpoint replays the recent backlog, then (when `follow=true`) polls the ring and
streams new lines as `data:` frames, emitting `: keep-alive` comments every 15s so
proxies don't drop idle connections.

- `backlog` (default `200`, `0`–`1000`): number of recent lines to replay first.
- `follow` (default `true`): keep the connection open and stream new lines; `false`
  replays the backlog and closes. The stream also ends when the client disconnects.
- Response is `text/event-stream` with `Cache-Control: no-cache` and
  `X-Accel-Buffering: no` (disables proxy buffering so events flush immediately).

### Vault (`kryptos.api.vault_routes` / `kryptos.vault`)

Seal a secret under a keyed-alphabet Vigenère cipher, store it in Neon with a TTL
and a server-enforced read limit, and get back an opaque UUID token. The **key is
never stored** (only the ciphertext), so the database alone cannot reveal the
plaintext. A short verifier hash lets a wrong key be rejected **without consuming
a read**. The vault requires `DATABASE_URL`; without it every endpoint returns 503.

| Method & path | Purpose |
|---------------|---------|
| `POST /api/vault/seal` | Body `{plaintext, key, ttl_seconds?=86400, max_reads?=1}` → `{token, cipher, max_reads, expires_at}` |
| `POST /api/vault/unseal` | Body `{token, key}` → `{token, plaintext, reads_remaining, expires_at}`. Consumes one read |
| `GET /api/vault/{token}` | Metadata only (no decrypt, no read consumed): `{status, max_reads, reads_used, reads_remaining, sealed_at, expires_at}` |

Error mapping: unknown token → 404; expired/exhausted → 410; wrong key → 403;
invalid arguments → 422; no database → 503. `ttl_seconds: 0` means no expiry.

### Frontend SPA (static serving)

When a built frontend bundle is present, `create_app()` mounts it at `/` via
`StaticFiles(directory=..., html=True)`, so the dashboard SPA and the API ship
from one process. The mount is added **last**, so `/api/*` and `/health` always
take precedence; `html=True` serves `index.html` for unknown paths (client-side
routing). The dist directory is resolved in order: `KRYPTOS_FRONTEND_DIST`, then
`<repo>/frontend/dist`, then `<cwd>/frontend/dist` (a candidate counts only if it
contains `index.html`). If no build is found, the API is served alone. The root
`Dockerfile` builds the SPA in a `node:22-alpine` stage and sets
`KRYPTOS_FRONTEND_DIST=/app/frontend/dist`.

---

## Neon DB tables (runtime storage)

Schema defined in `kryptos.db_schema`; create with `kryptos db-init`.

| Table | Written by | Purpose |
|-------|-----------|---------|
| `campaign_runs` | `kryptos.persistence` (via `k4.reporting`) | One row per candidate-generating run |
| `candidates` | `kryptos.persistence` (via `k4.reporting`) | Ranked candidate decryptions per run |
| `vault_payloads` | `kryptos.vault` (via `POST /api/vault/seal`) | Sealed secrets: ciphertext, verifier, TTL, read limit |
| `ops_decisions` | `OpsStrategicDirector` | Strategy decision log |
| `strategy_kb` | Manual / future agents | Accumulated attack knowledge |
| `discovered_cribs` | `SpyWebIntel` | Crib candidates with source provenance |
| `sanborn_timeline` | Manual research | Public Sanborn statement log |
| `k4_research_findings` | Manual research | Confirmed facts and ruled-out hypotheses |
| `k4_keystream` | Manual research | Per-position crib/cipher/plain/shift data |
| `source_chunks` | Migration script | Chunked primary source material (Smithsonian) |
