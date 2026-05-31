# Frontend design spec

Breadcrumb: Home > Docs > Analysis > Frontend


## Summary

A dark terminal-aesthetic web interface and API layer for the Kryptos project. The goal is a self-contained tool that feels like a real CIA cryptanalysis workstation — monospace, green-on-black, dense with live data — while also serving as a public-facing explainer and a practical encrypted messaging utility.

The stack is intentionally minimal: one FastAPI process, one React SPA, one Docker container, one SQLite database. No sidecars required to start.

---

## Stack

| Layer | Choice | Rationale |
|---|---|---|
| Backend | FastAPI (Python) | Imports kryptos modules directly — no shell-out |
| Frontend | React (Vite) | Single-file bundle, served by FastAPI as static |
| Database | SQLite (`/data/kryptos.db`) | Replaces `artifacts/` + `data/` — persists across runs via Docker volume |
| Container | Single Docker image | `docker compose up -d` is the entire deployment |
| Log streaming | Server-Sent Events | Tails DB log rows — no WebSocket complexity needed |

The autonomous loop runs as a background `asyncio.Task` inside the FastAPI process. If isolation is needed later, promote it to a second `kryptos-worker` service in `docker-compose.yml` that shares the `/data` volume.

---

## Database schema

Replace `artifacts/` and `data/` with a single SQLite file at `/data/kryptos.db` (path overridable via `KRYPTOS_DB_PATH` env var). Docker volume mount: `./data:/app/data`.

```sql
-- all scored decryption attempts
CREATE TABLE candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT,
    stage TEXT,
    cipher TEXT,
    plaintext TEXT,
    score REAL,
    fused_score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- one row per autonomous campaign run
CREATE TABLE campaign_runs (
    id TEXT PRIMARY KEY,
    started_at DATETIME,
    finished_at DATETIME,
    max_hours INTEGER,
    cycle_interval INTEGER,
    log_text BLOB,
    artifact_json TEXT
);

-- provenance trail (replaces attempt_log JSON files)
CREATE TABLE attempt_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT,
    stage TEXT,
    params_json TEXT,
    score REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- n-gram and frequency data (replaces data/*.tsv)
-- imported once at container init, never re-read from TSV at runtime
CREATE TABLE ngram_freq (
    gram TEXT PRIMARY KEY,
    frequency INTEGER,
    source TEXT
);

-- vault sealed payloads
CREATE TABLE vault_payloads (
    id TEXT PRIMARY KEY,
    cipher_type TEXT,
    ciphertext TEXT,
    expires_at DATETIME,
    reads_remaining INTEGER,
    key_hint TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Migration from current layout

| Source | Destination |
|---|---|
| `artifacts/reports/*.json` | `candidates` table |
| `artifacts/tuning_runs/run_*` | `campaign_runs` table |
| `artifacts/logs/` | `campaign_runs.log_text` (BLOB) |
| `artifacts/decisions/*.json` | `campaign_runs.artifact_json` |
| `data/*.tsv` | `ngram_freq` table (one-time import at init) |

A migration script should be provided at `scripts/dev/migrate_to_db.py` with a `--dry-run` flag, matching the pattern of the existing `migrate_run_artifacts.py`.

---

## API routes

All routes live under `/api`. The React bundle is served from `/` via FastAPI's `StaticFiles`.

```
GET  /api/status                     — agent states, runtime, cycle info
GET  /api/candidates?limit=20        — top fused candidates from DB
GET  /api/runs                       — campaign run history
GET  /api/stream/logs                — SSE stream of live log rows
POST /api/decrypt                    — one-shot composite pipeline call
POST /api/vault/seal                 — encrypt + store a vault payload
POST /api/vault/unseal               — decrypt + decrement reads, enforce TTL
GET  /api/vault/{id}                 — payload metadata (no plaintext)
```

Example integration — `POST /api/decrypt` calls Python directly, no subprocess:

```python
from kryptos.k4.composite import run_composite_pipeline
from kryptos.k4.pipeline import make_hill_constraint_stage, make_masking_stage

@router.post("/decrypt")
async def decrypt(cipher: str, stages: list[str]):
    result = run_composite_pipeline(cipher, build_stages(stages), report=True)
    return result["fused"][:10]
```

---

## Pages / navigation

### 1. Ops center (default)

The main dashboard. Shows everything happening in the current autonomous campaign.

- Live UTC clock in topbar
- Agent status row: SPY / OPS / Q — dot color (green/amber/purple) reflects actual state polled from `/api/status`
- Three metric cards: campaign runtime, total candidates scored, best fused score this run
- K4 ciphertext strip — color-coded by section (K1–K3 solved in green, active probe position in purple, unsolved remainder in default)
- Pipeline stages panel — all active stages with adaptive weights visualized as bars
- Top fused candidates table — stage attribution, score, fused score, monospace plaintext so letter patterns jump out
- Letter frequency chart — K4 distribution vs English baseline, side-by-side per letter
- Live log tail — last 20 rows from SSE stream, color-coded by agent
- Ad-hoc decrypt input — paste any ciphertext, select stages, execute against the pipeline via `POST /api/decrypt`

### 2. K1–K3 decode

An animated, step-by-step visual explainer of how each solved section was encrypted and cracked. Intended as both a demo and a teaching tool.

Three sub-sections selectable by tab: K1, K2, K3.

**K1 — Vigenère with keyed alphabet**
- Show the raw ciphertext
- Step 1: build the keyed alphabet (KRYPTOS letters highlighted, remainder in order, duplicates removed). Animate letters appearing one by one.
- Step 2: letter-by-letter substitution — each cipher letter lights up, its position in the keyed alphabet is found, the offset is applied, the plaintext letter appears below. Run at ~200ms per letter with a play/pause control.
- Step 3: final plaintext revealed with `IQLUSION` called out as intentional

**K2 — Vigenère / ABSCISSA**
- Same animation pattern
- Explain why X/Y letters are structural nulls, not errors — visually isolate and grey them out before decryption runs
- Show the embedded geospatial coordinates in the result

**K3 — double rotational transposition**
- Visualize the 24×14 grid being filled left-to-right
- Animate the 90° rotation — columns become rows
- Show the reshape to 8 columns
- Animate the second 90° rotation
- Reveal plaintext with `DESPARATLY` called out

All three sections include a "how it was encrypted" toggle — reverse the animation to show the encryption direction for educational context.

### 3. Vault

An encrypted messaging utility built on top of the existing Kryptos cipher implementations.

**Encrypt panel**
- Plaintext textarea
- Cipher selector: Vigenère (K1 method), Vigenère/ABSCISSA (K2), Hill 2×2, Columnar transposition
- Key input
- TTL slider: 1 hour to 7 days
- Max reads slider: 1–10 (server-enforced, not client-enforced)
- On seal: calls `POST /api/vault/seal`, stores ciphertext + metadata in `vault_payloads` table, returns a short opaque token (not the raw ciphertext)

**Sealed payload display**
- Shows the token — safe to copy and paste anywhere
- Expiry timestamp and read count displayed below
- Amber progress bar showing time remaining
- Copy-to-clipboard button
- "Open in decoder" shortcut that pre-fills the decrypt panel

**Decrypt panel**
- Paste token input
- Key input
- On unseal: calls `POST /api/vault/unseal` — server checks TTL, decrements `reads_remaining`, returns plaintext or destroys the row if TTL or reads are exhausted
- Expired/destroyed payloads return a clear terminal error: `[ PAYLOAD EXPIRED · DESTROYED ]`

The token format is a UUID referencing the DB row. The ciphertext never leaves the server inside the token itself — enforcement is fully server-side.

### 4. Database

An internal admin view, not user-facing in production.

- Connection status and DB path
- Row counts per table
- Migration status checklist (artifacts/ → DB, data/ → ngram_freq)
- One-click "scaffold migration script" that generates the `migrate_to_db.py` command
- Environment variable reference for `KRYPTOS_DB_PATH`

---

## Aesthetic

Terminal. Monospace throughout. Dark green on near-black. No gradients, no rounded pill shapes, no consumer SaaS feel.

```
background:  #04342C  (deep teal-black)
surface:     #085041
border:      rgba(29, 158, 117, 0.25)
text:        #9FE1CB  (muted green)
accent:      #1D9E75  (primary green)
highlight:   #7F77DD  (purple — active probes, agent Q)
warning:     #EF9F27  (amber — running states, expiry bars)
danger:      #E24B4A  (red — expired payloads, errors)
font:        monospace (system or Courier New fallback)
border-radius: 3–4px max — no pill shapes
```

All borders are `0.5px`. Scan-line texture optional (CSS `repeating-linear-gradient` overlay, low opacity). Topbar carries the live UTC clock and agent pip dots at all times.

---

## Docker

```yaml
# docker-compose.yml
services:
  kryptos:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data       # SQLite DB — survives restarts
    environment:
      - KRYPTOS_DB_PATH=/app/data/kryptos.db
      - KRYPTOS_AUTONOMOUS=1
      - KRYPTOS_MAX_HOURS=24
      - KRYPTOS_CYCLE_INTERVAL=5
```

Single container. No Nginx, no Redis, no sidecars to start. If the autonomous loop needs isolation, add a `kryptos-worker` service later that shares the `/data` volume.

---

## File layout (proposed additions)

```
src/kryptos/
  api/
    main.py             # FastAPI app, mounts static/, starts bg task
    routes/
      decrypt.py
      vault.py
      status.py
      stream.py
    db.py               # SQLite connection, table init, migration helpers

frontend/
  src/
    pages/
      OpsCenter.jsx
      Decode.jsx        # K1–K3 animated explainer
      Vault.jsx
      Database.jsx
    components/
      CipherStrip.jsx   # color-coded ciphertext display
      AgentRow.jsx
      LogTail.jsx       # SSE consumer
      FreqChart.jsx
      AnimatedAlphabet.jsx  # K1 keyed-alphabet builder
      GridRotation.jsx      # K3 transposition visualizer
    App.jsx
    main.jsx
  index.html
  vite.config.js

scripts/dev/
  migrate_to_db.py      # --dry-run flag, mirrors migrate_run_artifacts.py

Dockerfile
docker-compose.yml
```

---

## What this replaces / removes

| Current | Replaced by |
|---|---|
| `artifacts/` folder (local memory, not git-tracked) | `campaign_runs`, `candidates`, `attempt_log` tables in SQLite |
| `data/*.tsv` read at runtime | `ngram_freq` table, imported once at container init |
| Manual `python -m kryptos.cli.main` invocations | FastAPI background task + `/api/decrypt` endpoint |
| No UI | React SPA served from the same process |

Nothing in `src/kryptos/` is removed or restructured. The API layer imports existing modules as-is. The frontend is purely additive.
