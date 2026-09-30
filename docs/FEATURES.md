
# KRYPTOS Features

> 🧭 [kryptos](../README.md) · [Index](./INDEX.md) · **Features** · [Roadmap](./ROADMAP.md) · [Tasks](./TASKS.md) · [Changelog](./CHANGELOG.md) · [Metrics](./METRICS.md) <!-- nav -->
>
> Cryptographic research toolkit for solving the K4 cipher puzzle

---
**Last Updated:** 2026-09-30
---


## Core Cryptanalysis Capabilities

### 🔐 Cipher Implementations

- **Vigenère Cipher**: Polyalphabetic substitution with keyed alphabet (KRYPTOS set)
- **Hill Cipher (2×2 to 5×5)**: Matrix-based; crib-constrained key solving, exhaustive to 4×4, beam search at 5×5
- **Columnar & Route Transposition**: Permutation ciphers with geometric and partial-score/crib pruning
- **Double Rotational Transposition**: 24×14 grid K3 solution
- **Beaufort Cipher**: Reciprocal variant
- **ADFGVX & Nihilist**: Fractionating ciphers (Polybius + transposition/nihilist key)
- **Keyed Alphabet Realignment**: Auto-selection and realignment (KRYPTOS, PALIMPSEST, ABSCISSA)


### 📊 Scoring & Analysis

- **Frequency & N-gram Analysis**: English 2/3/4-gram tables from 8.9M letters of public-domain text (`data/ngrams/english_*grams.tsv`), letter frequency, chi-squared, index of coincidence
- **Calibrated English score**: `english_model.english_z` puts random text at 0 and English of the same length at 1, so scores compare across lengths
- **Dictionary & Linguistic Metrics**: Wordlist hit rate, trigram entropy, bigram gap variance, repeating bigram fraction
- **Crib-Based & Pattern Scoring**: Known plaintext/crib validation, pattern matching
- **Composite & Multi-Stage Scoring**: Weighted fusion, adaptive weights, and pipeline profiling


### 🎯 Search & Optimization

- **Simulated Annealing & Genetic Algorithms**: Fast probabilistic solvers for transposition/Hill ciphers
- **Exhaustive & Adaptive Search**: Optimal solutions for small spaces, sampling heuristics for large
- **Constraint & Multi-Start Optimization**: Crib-constrained, multi-restart, and partial-score pruning
- **Composite Chain Execution**: Chained hypothesis classes (e.g., S→T→S via `CompositeChainExecutor`)
- **Search-Space Fuzzy Dedup**: Levenshtein near-miss deduplication via `SearchSpaceTracker.already_tried_fuzzy`


## K4 Analysis Toolkit

### 🔬 Specialized K4 Modules

- **Hill Constraint & Assembly**: BERLIN/CLOCK crib-constrained 3×3 Hill, row/col/diag combinatorics
- **Transposition Adaptive & Multi-Crib**: Dynamic column range, multi-crib anchoring
- **Masking/Null-Removal**: Structural padding elimination, multiple patterns
- **Berlin Clock Hypothesis**: Lamp state enumeration, dual-direction shifts; all 720 states tested (null result)
- **Composite Parameter Sweep**: Full grid × alphabet × clock × angle sweeps (`run_composite_sweep`); null result artifact written
- **Instructional Scorer**: Geographic/imperative vocabulary boost + Levenshtein fuzzy match for Sanborn-style misspellings + entropy gate (`scoring_instructional.py`)
- **Inverse Transposition Sweep**: All 3 grid geometries (10×10, 7×14, 8×13), ENE diagonal (67.5°) and columnar routes (`inverse_transposition_sweep.py`); null result
- **Keystream Validator**: Per-position shift computation and simultaneous 4-crib validation (`keystream_validator.py`)
- **Eureka Capture Protocol**: Raises `EurekaSignal` on simultaneous 4-crib match; writes breakthrough snapshot; wired into `CompositeChainExecutor` (`eureka.py`)
- **Keyed Alphabet Realignment**: Tests KRYPTOS, PALIMPSEST, ABSCISSA alphabets against confirmed crib positions (`vigenere_key_recovery.check_keyed_alphabet_realignment`); null result
- **Quagmire I–IV Solver + Sweep**: Canonical encrypt/decrypt for all four Quagmire variants (ground-truth verified against K1/K2); 6,240-combination K4 sweep with positional crib gating + Eurek[...]
- **Physical-Grid Tableau Walk**: Walks the 26×26 KRYPTOS Vigenère tableau along 108 geometric routes into the Quagmire III solver against K4 (`k4.physical_grid`); null result
- **Berlin Clock Attack Suite**: Clock→Hill 2×2 invertibility pre-filter, 4-char clock→Vigenère with NORTHEAST anchor, non-standard sub-row encodings, and lamp-count transposition widths (`k[...]
- **Beaufort K4 Sweep**: Systematic reciprocal-Beaufort pass over KRYPTOS/PALIMPSEST/BERLIN/CLOCK/ABSCISSA keys (`k4.beaufort_sweep`); null result
- **Crib-Constraint Engine (P21)**: Tests whole cipher families against the 24 crib key values, each check with a positive control: autokey, linear/progressive/digit keys, sculpture-corpus running keys, dictionary Quagmire I–III (231,933 alphabets), and columnar/geometric transposition × periodic key in both layer orders (`k4.crib_constraints`, `kryptos crib-constraints`)
- **Structural Checks**: Output-alphabet eliminations, nulls between cribs, Hill 2×2/3×3, K3-style double rotation, columnar + autokey / running key, Chaocipher; plus double-periodic keys, Quagmire IV and error-tolerant scans against shuffled controls (`k4.structural_checks`, `k4.crib_constraints`)
- **IC Profile**: Overall/segment IC with a reshuffle significance test (`k4.ic_profile`)
- **Frontier Checks (P22)**: Recurrence, mixed-alphabet, dial, bearing-route and phrase keys; Hill 4×4 (exhaustive) and 5×5 (sampled + beam search); columnar widths 10–14 by exact backtracking; running keys from any English text; the full-plaintext reconstruction tested against every family (`k4.frontier_checks`, `kryptos frontier`)
- **Hypothesis Ledger**: every cipher family tagged `eliminated` / `statistical` / `sampled_null` / `open` with scope, evidence, module and test (`k4.hypothesis_ledger`, `kryptos ledger`, `GET /api/k4/ledger`)

### ⚙️ Pipeline Architecture

- **Modular Stage System**: Factory pattern for hypothesis families
- **Composite & Multi-Stage Fusion**: Weighted aggregation, adaptive weights
- **Profiling & Provenance**: Per-stage timing, operation lineage, memoized scoring


## Autonomous Solving System

### 🤖 Intelligence Agents & Coordination

- **SPY, LINGUIST, OPS, Q Agents**: Pattern recognition, language validation, orchestration, research validation
- **K123 Analyzer & Web Intelligence**: Historical pattern analysis, external research
- **Attack Generation & Campaign Orchestration**: Coverage-driven queue, provenance, and hooks
- **Autonomous Solving Loop**: Persisted, long-running coordination (tri-agent decision loop)


## Provenance, Tracking & Reporting

### 📝 Research Integrity & Coverage

- **Attack Provenance Logging**: Deduplicated, replay-friendly metadata
- **Search Space & Attempt Persistence**: Tried-key tracking, timestamped logs, cross-run memory
- **Transformation Trace**: Full operation chain per candidate
- **Coverage Tracking**: Explored/unexplored/oversaturated key spaces

### 📊 Reporting & Artifacts

- **Candidate Reports & Heatmaps**: JSON/CSV summaries, ASCII bar heatmaps
- **Performance Profiling**: Per-stage timing, throughput, and reliability gates
- **Validation Reports**: Monte Carlo/statistical confidence, academic documentation



## Database & Persistence

### 🗄️ Neon PostgreSQL Integration

- **`kryptos.db`**: Shared connection helper — reads `DATABASE_URL`, yields psycopg2 connection with local-file fallback
- **`ops_decisions`**: Strategy decision log written by `OpsStrategicDirector` at runtime
- **`discovered_cribs`**: Crib candidates with source provenance; upserted by `SpyWebIntel` and seeded from Sanborn research
- **`strategy_kb`**: Accumulated attack knowledge (successful/failed strategies, lessons learned)
- **`sanborn_timeline`**: Structured log of Jim Sanborn's public statements (12 entries)
- **`k4_research_findings`**: Confirmed facts and ruled-out hypotheses (19 entries, queryable by kind/confidence)
- **`k4_keystream`**: Per-position crib/cipher/plain/shift data for all four confirmed cribs (24 rows)
- **`source_chunks`**: Smithsonian 2009 oral history transcript chunked for semantic search (51 chunks)

---

## 🔍 RAG & Semantic Search (turbovec)

- **`kryptos serve`**: Minimal FastAPI app exposing semantic search over `artifacts/` (decisions, hypotheses, logs, reports)
- **turbovec-backed index**: Compressed vector index (`IdMapIndex`, 4-bit quantization) stored under `data/turbovec/`
- **`sentence-transformers` embeddings**: `all-MiniLM-L6-v2` (384-dim, CPU-friendly) for chunk and query encoding
- **Endpoints**: `GET /health`, `GET /api/rag/status`, `POST /api/rag/reindex`, `GET /api/rag/search?q=...&k=...`
- **On-demand indexing**: Index is built via `/api/rag/reindex`, not automatically at startup — keeps the API lightweight until search is needed

---

## 🖥️ Dashboard, Web UI & HTTP API

### React SPA (single page, Ghost in the Shell style)

- **One screen, no tabs**: a rotating ring of modules you switch with swipes, arrow keys, the dial or the module ring; the active module fills the stage and the neighbours stay visible at the sides on wide screens
- **Modules**: Overview (K4 ciphertext with cribs, ledger totals, clocks), Ledger (every family by tier), Attacks (P1–P22 queue with run buttons and live job progress), Jobs (recent attack jobs), Runs (campaign history and top candidates), Console (ad-hoc decrypt and the live log), Decoder (K1–K3 animated), Vault, System (API, database tables, Physical/Geometric Pivot)
- **Responsive**: fluid type and spacing, a single column on phones, reduced motion honoured
- **Single-container delivery**: FastAPI serves the built `frontend/dist` bundle via `StaticFiles(html=True)`; the root `Dockerfile` builds the SPA in a `node:22-alpine` stage and ships it alongside the API
- **Stack**: Vite + React 18 + TypeScript, no runtime UI framework. Design notes: `docs/reference/DASHBOARD.md`

### HTTP API (FastAPI)

- **Dashboard endpoints**: `GET /api/status`, `GET /api/runs`, `GET /api/runs/{id}/candidates`, `GET /api/candidates`, `POST /api/decrypt`, `GET /api/attack-vectors`
- **Vault endpoints**: `POST /api/vault/seal`, `POST /api/vault/unseal`, `GET /api/vault/{token}` (503/404/410/403 error mapping for unavailable/missing/gone/wrong-key)
- **RAG endpoints**: `GET /api/rag/status`, `POST /api/rag/reindex`, `GET /api/rag/search`
- **SSE log tail**: `GET /api/stream/logs` — `StreamingResponse` (`text/event-stream`) backed by a thread-safe ring buffer fed by a `kryptos`-logger handler; `LogTail` EventSource component on [...]
- **K4 hypothesis ledger**: `GET /api/k4/ledger[?tier=]` — every family tagged eliminated / statistical / sampled_null / open, with scope, evidence, module and test
- **K4 attack jobs**: `GET /api/k4/attacks/frontier`, `GET /api/k4/attacks/pivot-status`, `POST /api/k4/attacks/run` (incl. `p21_crib_constraints` and `p22_frontier_checks`, one at a time), `GET /api/k4/attacks/jobs`, `GET /api/k4/attacks/jobs/{id}`; finished jobs persist to Neon (`k4_attack_jobs`)
- **Health**: `GET /health`

### Persistence

- **`campaign_runs` + `candidates` tables**: Best-effort write path persists live campaign runs and their candidates to Neon (graceful no-op without `DATABASE_URL`)
- **`vault_payloads` table**: Token-addressed ciphertext with verifier, max-reads, and expiry; atomic read-decrement guarantees one-shot semantics
- **`strategy_kb` write path**: `OpsStrategicDirector.record_strategy()` + `_record_strategy_from_decision()` persist BOOST/PIVOT/STOP/START_NEW decisions to Neon `strategy_kb` with JSONL fallbac[...]

---

## Development Tools

- **CLI Interface**: 22 subcommands covering decryption, tuning, provenance, autonomous runs, reporting, the K4 constraint suites (`crib-constraints`, `frontier`) and the ledger
- **Optional `--cipher` flag**: `k4-decrypt` and `sections-decrypt` read from `config/config.json` by default — no file path required
- **Example Demos**: Runnable analysis patterns and usage examples
- **Config System**: JSON-driven (`config/config.json`) — single source of truth for all ciphertexts, cribs, and parameters
- **Pre-commit Hooks**: Automated linting and formatting
- **Performance Benchmarks**: Throughput and optimization tracking
- **Test Tier Structure**: Tests organized into `smoke/` (fast sanity), `functional/` (unit/module), and `e2e/` (campaign/pipeline) tiers

## Validation & Quality

### ✅ Test Coverage & Reliability

- **K1/K2 Vigenère**: 100% deterministic (50-run Monte Carlo validated)
- **K3 Transposition**: 62–95% (Monte Carlo, parameter-dependent; stochastic SA solver)
- **Test Suite**: about 1,770 fast tests, tiered smoke/functional/e2e structure, reliability gates for K1/K2/K3 Sanborn misspellings, a positive control for every eliminated ledger entry (current counts: `docs/METRICS.md`)

### ⚠️ Operational Note
- NLP dependencies (spaCy/NLTK/transformers) are optional; robust fallback logic

---



## 🧪 Completed K4 Attack Campaigns (2026, all null)

Condensed from the ROADMAP/TASKS removed in the 2027 planning reset (verbatim text: `docs/archive/2026-completed-roadmap-and-tasks.md`; living detail: `docs/analysis/K4_ACTIVE_RESEARCH.md`, `docs/analysis/K4_CAPABILITY_TABLE.md`).

### 🧾 Attack Phases

- **Phase 1 — 14 prior vectors**: single/2-layer composites exhausted (repeating Vigenère, Berlin Clock Vigenère, keyed alphabets, Hill 2×2/3×3, Beaufort, Quagmire I–IV, physical tableau walk, ADFGVX, Nihilist) — all null
- **Phase 2 — P1–P7 frontier attacks**: 3-layer composite, shadow/null masking, K2 coordinate clocks, ±6h offsets, 2-crib soft filter, K3 running key, Gronsfeld — all null; live at `POST /api/k4/attacks/run`
- **Phase 3 — P11–P20**: alternative/misspelling keyword alphabets, magnetic declination, CIA→Berlin bearing, straddling checkerboard, corpus fragment mining, QQ/SS bigram constraints, repeating-key CSP, advisory names, Cyrillic Projector crossover — all null
- **Phase 4 — Dashboard & tooling**: React/Vite SPA, K4 Attack Dashboard, frontier queue, REST API, Ops Center, K1–K3 decoder, Vault, SSE log tail
- **Phase 6 — Physical/Geometric Pivot** (PRs #192–#196): 24-column geometric front-end × reflections × rotations × physical tableau, precise WGS84 geodesy (`kryptos.k4.geodesy`), Mengenlehreuhr→Weltzeituhr bearing, Nov 9 1989 clock state, Myszkowski, Trifid, SA substitution search — all null
- **Phase 7 — Shape-changing transposition + shadow hypothesis**: transpose family wired, `solar_geometry` (topper rotation + NOAA/Meeus solar azimuth), World Clock city keywords (130/146 sourced), cross-vector consensus scoring (zero anchors), overnight sweep runner — 2,420,928 candidates, all null
- **Phase 8 follow-ups (2026-09-03)**: `plaintext_evidence` confidence tiers, known-plaintext inversion over geometric + rectangular grids (3,674,160 permutations), mirrored "read from the back" tableau, reconstructed-plaintext and K0 Morse keyword sources, `classical_cipher_sweep` (Playfair/Four-Square/Bifid/Autokey), `physical_geometry` schema, `constraint_chain` — all null
- **Negative-space passes (2026-09-27 → 09-28)**: IC audit, P21 crib-constraint engine, structural checks and P22 frontier checks: 26 families eliminated over stated ranges, 7 statistical, each with a positive control; details in `docs/analysis/K4_NEGATIVE_SPACE.md`

## 🚀 Planned & Upcoming

Ranked in `docs/ROADMAP.md` (2027 Q1) and `docs/analysis/K4_NEGATIVE_SPACE.md`:

- **Cryptanalysis**: irregular transpositions, length-changing masking, two non-periodic layers, named running-key sources under transposition, Hill 6×6+, per-letter Weltzeituhr lookups
- **Platform**: a "try a hypothesis" endpoint and dashboard module, a candidate submission gate for Paradigm's $1 checker, re-scoring stored candidates
- **Post-solution**: document the attack path and narrative once K4 is solved

## Data & Resources

### 📚 Linguistic Data
- **English N-gram Tables**: 2-, 3- and 4-gram log probabilities built from the NLTK Gutenberg selection (`scripts/data/build_english_ngrams.py`); the older `quadgrams_high_quality.tsv` is still loaded when present
- **English Dictionary**: 261k-word list (`english-words`, MIT) for word scoring and dictionary keyword scans
- **Fallback Distributions**: Graceful degradation if missing

### 🔧 Configuration & Setup
- **Centralized Config**: JSON-driven (config/config.json)
- **Artifact Management**: Structured outputs (artifacts/)
- **Requirements Management**: `config/requirements.txt` (runtime), `config/requirements-dev.txt` (dev)
- **PyPI Packaging**: pyproject.toml
