# KRYPTOS Features

> Cryptographic research toolkit for solving the K4 cipher puzzle

## Core Cryptanalysis Capabilities

### � Cipher Implementations

- **Vigenère Cipher**: Classical polyalphabetic substitution with keyed alphabet support (KRYPTOSABCDEFGHIJLMNQUVWXZ)
- **Hill Cipher (2×2 & 3×3)**: Matrix-based substitution cipher with encryption/decryption and key solving from cribs
- **Columnar Transposition**: Permutation cipher with partial-score pruning and crib-constrained inversion
- **Route Transposition**: Geometric transposition patterns with multiple route types
- **Double Rotational Transposition**: K3 solution method using 24×14 grid rotations
- **Beaufort Cipher**: Reciprocal cipher variant for additional analysis

### 📊 Scoring & Analysis

- **Frequency Analysis**: Letter frequency comparison with English baseline
- **N-gram Scoring**: Unigram, bigram, trigram, and high-quality quadgram tables for linguistic scoring
- **Chi-Squared Statistics**: Statistical goodness-of-fit testing for decryption candidates
- **Dictionary Scoring**: Word detection with 2.73× discrimination ratio improvement
- **Advanced Linguistic Metrics**: Wordlist hit rate, trigram entropy, bigram gap variance, repeating bigram fraction
- **Crib-Based Scoring**: Known plaintext pattern matching and validation
- **Index of Coincidence**: Polyalphabetic cipher detection and period estimation

### 🎯 Search & Optimization

- **Simulated Annealing**: 30-45% faster than hill-climbing for transposition solving
- **Genetic Algorithms**: Population-based Hill cipher key optimization
- **Exhaustive Search**: Guaranteed optimal solutions for small key spaces (periods ≤8)
- **Adaptive Search**: Sampling prefix caching heuristics for efficient exploration
- **Constraint-Based Search**: Crib-constrained Hill key derivation with single & pairwise combinations
- **Multi-Start Optimization**: Multiple random restarts for probabilistic solvers
- **Partial Score Pruning**: Early candidate elimination to reduce search space

## K4 Analysis Toolkit

### 🔬 Specialized K4 Modules

- **Hill Constraint Stage**: BERLIN/CLOCK crib-constrained 3×3 Hill cipher with partial length pruning
- **Transposition Adaptive Stage**: Dynamic column range exploration with sampling heuristics
- **Multi-Crib Positional Stage**: Anchor multiple cribs simultaneously in transposition search
- **Masking/Null-Removal**: Structural padding elimination with multiple removal patterns
- **Berlin Clock Hypothesis**: Full lamp state enumeration with dual-direction shift application
- **3×3 Hill Assembly**: Row/column/diagonal constructions with combinatorial search

### ⚙️ Pipeline Architecture

- **Modular Stage System**: Factory pattern for hypothesis families (Hill, transposition, masking, etc.)
- **Multi-Stage Fusion**: Weighted score aggregation across different cipher hypotheses
- **Adaptive Fusion Weighting**: Dynamic weight adjustment based on wordlist hits and entropy
- **Pipeline Profiling**: Per-stage duration tracking and performance metrics
- **Transformation Lineage**: Complete audit trail of cipher operations applied to each candidate
- **Memoized Scoring**: LRU cache for repeated candidate evaluation

## Autonomous Solving System

### 🤖 Intelligence Agents

- **SPY Agent**: Pattern recognition and linguistic analysis (464 lines + 474 NLP lines)
- **LINGUIST Agent**: Advanced language detection and validation (562 lines)
- **OPS Agent**: Orchestration and attack execution (603 lines + 609 director lines)
- **Q Agent**: Research validation and confidence scoring (359 lines)
- **K123 Analyzer**: Historical cipher analysis (333 lines)
- **Web Intelligence**: External research integration

### 🔄 Autonomous Coordination

- **Attack Generation**: 46 attacks from Q-hints with gap analysis
- **K4 Campaign**: Production orchestration achieving 2.5 attacks/second throughput
- **4-Stage Validation Pipeline**: SPY → LINGUIST → Q → Human review with 96% confidence
- **Autonomous Solving**: 24/7 operation with cross-run memory and learning
- **Triumvirate Decision Loop**: Coordinated intelligence across SPY/OPS/Q agents

## Provenance & Tracking

### 📝 Research Integrity

- **Attack Provenance Logging**: Complete history with deduplication (435 lines)
- **Search Space Coverage**: Metrics and visualization for exploration tracking (401 lines)
- **Attempt Persistence**: Timestamped JSON logs for all Hill, Clock, and Transposition attempts
- **Transformation Trace**: Each candidate records full stage + operation chain
- **Cross-Run Memory**: Prevent duplicate attempts across sessions
- **Coverage Tracking**: Identify explored, unexplored, and oversaturated key spaces

### 📊 Reporting & Artifacts

- **Candidate Reports**: JSON summaries with optional CSV exports
- **Coverage Heatmaps**: Visual exploration status by key space
- **Performance Profiling**: Per-stage timing and throughput metrics
- **Validation Reports**: Monte Carlo test results with statistical confidence
- **Academic Documentation**: Comprehensive methodology and results (3,500+ lines)

## Validation & Quality

### ✅ Proven Success Rates

- **K1 Vigenère**: 100% success rate (deterministic, 50/50 runs)
- **K2 Vigenère**: 100% success rate (deterministic, 50/50 runs)
- **K3 Transposition**: 68-95% success rate (probabilistic, period-dependent)
- **Test Coverage**: 607 tests total (583 fast / 24 slow)
- **Monte Carlo Validation**: Comprehensive statistical validation framework
- **Edge Case Coverage**: 119 test files with extensive boundary testing

### 🛠️ Development Tools

- **CLI Interface**: Comprehensive command-line tools for all workflows
- **Example Demos**: Runnable examples for common analysis patterns
- **Configuration System**: JSON-driven ciphertext and parameter management
- **Pre-commit Hooks**: Automated linting and formatting
- **Performance Benchmarks**: Measured throughput and optimization tracking

## Data & Resources

### 📚 Linguistic Data

- **High-Quality Quadgrams**: Auto-loaded TSV tables for optimal scoring
- **N-gram Frequency Tables**: Unigram, bigram, trigram distributions
- **English Dictionary**: Word validation with frequency rankings
- **Fallback Distributions**: Graceful degradation when data files missing

### 🔧 Configuration & Setup

- **Config-Driven**: Centralized JSON configuration (config/config.json)
- **Artifact Management**: Organized output directory structure (artifacts/)
- **Virtual Environment**: Isolated dependency management (.venv)
- **Requirements Management**: Pinned dependencies (requirements.txt)
- **Project Packaging**: PyPI-compatible setup (pyproject.toml)
