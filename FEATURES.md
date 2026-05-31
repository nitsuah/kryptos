
# KRYPTOS Features

> Cryptographic research toolkit for solving the K4 cipher puzzle

---
**Last Updated:** 2026-05-25
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
- **Composite Chain Execution**: Chained hypothesis classes (e.g., S→T→S)


## K4 Analysis Toolkit

### 🔬 Specialized K4 Modules

- **Hill Constraint & Assembly**: BERLIN/CLOCK crib-constrained 3×3 Hill, row/col/diag combinatorics
- **Transposition Adaptive & Multi-Crib**: Dynamic column range, multi-crib anchoring
- **Masking/Null-Removal**: Structural padding elimination, multiple patterns
- **Berlin Clock Hypothesis**: Lamp state enumeration, dual-direction shifts
- **Composite Parameter Sweep**: Full grid/alphabet/clock/angle sweeps

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



## Development Tools

- **CLI Interface**: Comprehensive command-line tools for all workflows
- **Example Demos**: Runnable analysis patterns and usage examples
- **Config System**: JSON-driven ciphertext and parameter management
- **Pre-commit Hooks**: Automated linting and formatting
- **Performance Benchmarks**: Throughput and optimization tracking

## Validation & Quality

### ✅ Test Coverage & Reliability

- **K1/K2 Vigenère**: 100% deterministic
- **K3 Transposition**: 60–95% (Monte Carlo, parameter-dependent)
- **Test Suite**: 800+ tests, 95% coverage, fast/slow partitions, reliability gates

### ⚠️ Operational Note
- NLP dependencies (spaCy/NLTK/transformers) are optional; robust fallback logic

---



## 🚀 Planned & Upcoming

### 🧠 AI/ML & Community
- **LLM-Driven Hypothesis Generation**: Use LLMs to propose new attacks/scoring
- **Community Leaderboard**: Track top contributors and attack runs
- **Experiment Diary**: Public log of research and findings
- **How to Contribute a New Attack**: Step-by-step guide

### 🔬 Research & Pipeline
- **Operator-Grade Triage Tools**: Enhanced result review and artifact annotation (in progress)
- **Post-Solution Analysis**: Document attack path, insights, and solution narrative (planned)

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
