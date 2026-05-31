
# KRYPTOS Features

> Cryptographic research toolkit for solving the K4 cipher puzzle

---
**Last Updated:** 2026-06-01
---


## Core Cryptanalysis Capabilities

### 🔐 Cipher Implementations

- **Vigenère Cipher**: Polyalphabetic substitution with keyed alphabet (KRYPTOS set)
- **Hill Cipher (2×2, 3×3)**: Matrix-based, supports crib-constrained key solving
- **Columnar & Route Transposition**: Permutation ciphers with geometric and partial-score/crib pruning
- **Double Rotational Transposition**: 24×14 grid K3 solution
- **Beaufort Cipher**: Reciprocal variant
- **ADFGVX & Nihilist**: Fractionating ciphers (Polybius + transposition/nihilist key)
- **Keyed Alphabet Realignment**: Auto-selection and realignment (KRYPTOS, PALIMPSEST, ABSCISSA)


### 📊 Scoring & Analysis

- **Frequency & N-gram Analysis**: Unigram–quadgram scoring, letter frequency, chi-squared, index of coincidence
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

## Development Tools

- **CLI Interface**: 18 subcommands covering decryption, tuning, provenance, autonomous runs, and reporting
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
- **Test Suite**: 829 tests, tiered smoke/functional/e2e structure, reliability gates for K1/K2/K3 Sanborn misspellings

### ⚠️ Operational Note
- NLP dependencies (spaCy/NLTK/transformers) are optional; robust fallback logic

---



## 🚀 Planned & Upcoming

### 🔑 K4 Untested Attack Vectors
- **Clock → Hill 2×2 pre-filter**: Use clock state lamp values as a Hill matrix key (~100 invertible states to test)
- **4-char clock key → Vigenère**: Derive 4-char keys from clock states, test with NORTHEAST positional anchor
- **Non-standard clock encodings**: Sub-row variants (hour-only, minute-only, row sums)
- **Clock lamp counts as transposition widths**: Use lamp values as column widths, not Vigenère shifts
- **Beaufort cipher sweep**: `kryptos.k4.beaufort` implemented; no systematic K4 sweep run yet

### 🖥️ Dashboard & UI
- **Ops Center Dashboard**: Live campaign monitoring, agent status, top candidates, letter frequency chart
- **K1–K3 Animated Decoder**: Step-by-step visual explainer of each solved section
- **K4 Attack Dashboard**: Real-time pipeline progress, scoring breakdowns, evidence artifacts
- **Vault**: Demo encrypt/decrypt interface for all supported ciphers
- **FastAPI + React SPA**: Single-container deployment via `docker compose up`
- See `docs/analysis/K4-FRONTEND.md` for full spec (note: SQLite schema in that doc is superseded by Neon)

### 📡 API & Data
- **REST API**: Endpoints for decryption, candidate queries, run history, live log streaming (SSE)
- **`strategy_kb` write path**: Automate writing successful/failed strategies back to the Neon table
- **K3 double-transposition Monte Carlo**: Full double-rotational K3 algorithm not yet validated statistically

### 🧠 AI/ML & Community
- **LLM-Driven Hypothesis Generation**: Use LLMs to propose new attacks and scoring strategies
- **Post-Solution Analysis**: Document attack path, key insights, and solution narrative once K4 is solved

## Data & Resources

### 📚 Linguistic Data
- **High-Quality Quadgrams**: Auto-loaded TSV for scoring
- **N-gram Tables**: Unigram, bigram, trigram
- **English Dictionary**: Word validation with frequency
- **Fallback Distributions**: Graceful degradation if missing

### 🔧 Configuration & Setup
- **Centralized Config**: JSON-driven (config/config.json)
- **Artifact Management**: Structured outputs (artifacts/)
- **Virtual Environment**: Isolated deps (.venv)
- **Requirements Management**: Pinned deps (requirements.txt)
- **PyPI Packaging**: pyproject.toml
