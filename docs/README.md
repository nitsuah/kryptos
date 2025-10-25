# Kryptos K4 Documentation# Kryptos K4 Documentation

**Systematic cryptanalysis framework for solving Kryptos K4****Systematic cryptanalysis framework for solving Kryptos
K4**

------

## 🎯 Quick Start## 🎯 Quick Start

**New to this project?****New to this project?** Read [AUTONOMOUS_SYSTEM.md](AUTONOMOUS_SYSTEM.md) for the 24/7
autonomous cryptanalysis system.

1. Read **[PHASE_5_BRIEFING.md](PHASE_5_BRIEFING.md)** - Complete Phase 5 roadmap with Sanborn clues analysis

2. Check **[30_YEAR_GAP_COVERAGE.md](30_YEAR_GAP_COVERAGE.md)** - Coverage assessment of pre-1990 cryptography**Want to
run attacks?**

**Want to run attacks?**```bash

## Run autonomous coordination (recommended)

```bashpython -m kryptos.cli.main autonomous --max-cycles 100

# Run autonomous coordination (coming in Phase 5.3)

python -m kryptos.cli.main autonomous --max-cycles 100# Run single attack

python -m kryptos.cli.main k4-decrypt --hypothesis vigenere_northeast

# Run specific hypothesis (current)

python -m kryptos.cli.main k4-decrypt --hypothesis vigenere_northeast# List all available attacks

python -m kryptos.cli.main k4-decrypt --list

# List all available attacks```

python -m kryptos.cli.main k4-decrypt --list

```**Check progress?** See test results in `artifacts/` or [CHANGELOG.md](CHANGELOG.md) for recent additions.



------



## 📚 Core Documentation## 📚 Core Documentation (6 Files)



### Phase 5: Pipeline Integration (Current Focus)

1. **[README.md](README.md)** (this file) - Project overview and navigation

1. **[K4_MASTER_PLAN.md](K4_MASTER_PLAN.md)** - Complete strategy, roadmap, hypothesis testing plan

1. **[PHASE_5_BRIEFING.md](PHASE_5_BRIEFING.md)** - Complete Phase 5
roadmap**[AGENTS_ARCHITECTURE.md](AGENTS_ARCHITECTURE.md)** - SPY/OPS/Q agent design and implementation status 4.

   - Executive summary: Intelligence layer complete, K4 odds 60-70%**[API_REFERENCE.md](API_REFERENCE.md)** - Python API
     documentation and CLI reference 5.

   - 30-year gap analysis: What Sanborn knew in 1990**[CHANGELOG.md](CHANGELOG.md)** - Version history and recent
     changes 6. **[TECHDEBT.md](TECHDEBT.md)** - Known issues,

   - Confirmed clues: BERLIN, CLOCK, NORTHEAST, EASTcleanup status, improvement roadmap

   - Strategic direction: Attack priorities based on Sanborn intelligence

   - Sprint 5.1: Attack Generation Engine---

   - Sprint 5.2: Validation Pipeline (SPY → LINGUIST → Q-Research)

   - Sprint 5.3: End-to-End K4 CLI## 🏗️ Project Architecture (10,000ft View)



2. **[30_YEAR_GAP_COVERAGE.md](30_YEAR_GAP_COVERAGE.md)** - Technical coverage assessment### Directory Structure

   - Overall: ~95% of pre-1990 classical cryptography

   - Strong coverage: Vigenère, Hill, transposition, composites```text

   - Moderate gaps: Beaufort, Porta, Gronsfeld, ADFGVX, Nihilistkryptos/

   - Strategic recommendations: Berlin Clock + Hill 2x2/3x3 priority├── src/kryptos/          # Core Python package

│   ├── agents/           # SPY v2.0, OPS Director, K123 Analyzer, Web Intel

3. **[K123_PATTERN_ANALYSIS.md](K123_PATTERN_ANALYSIS.md)** - Sanborn's fingerprint│   ├── k4/               #
K4-specific pipeline and scoring

   - 13 patterns extracted from K1-K3 (confidence 0.75-1.00)│   ├── autonomous_coordinator.py  # 24/7 autonomous
     orchestration

   - Cipher progression: K1 (Vigenère) → K2 (Vigenère + coords) → K3 (double transposition)│   ├── cli/              #
     CLI interface

   - Themes: Location, archaeology, secrecy, communication│   └── examples/         # Demo scripts

   - Intentional misspellings: IQLUSION, UNDERGRUUND, DESPARATLY├── scripts/              # Performance & tuning
     utilities (4 active)

   - Strategic recommendations for K4 attacks│   ├── benchmark_scoring.py

│   ├── profile_scoring.py

### Reference Documentation│   ├── calibrate_scoring_weights.py

│   └── tuning.py

4. **[AGENTS_ARCHITECTURE.md](AGENTS_ARCHITECTURE.md)** - Multi-agent system design├── tests/                # Test
suite (30+ autonomous tests)

   - SPY, LINGUIST, K123 Analyzer, OPS Director, Q-Research architecture├── artifacts/            # Generated outputs
     (searches, runs, reports)

   - Communication patterns and coordination├── docs/                 # Documentation (11 active files)

   - Current status and capabilities```

└── docs/                 # Documentation (cleaned: 20→6 files)

5. **[AUTONOMOUS_SYSTEM.md](AUTONOMOUS_SYSTEM.md)** - 24/7 autonomous system```

   - Architecture, components, usage, monitoring

   - Checkpointing and incremental learning### Core Modules

   - How to run self-sustaining cryptanalysis

- `kryptos.autonomous_coordinator` - 24/7 autonomous orchestration with checkpointing

6. **[API_REFERENCE.md](API_REFERENCE.md)** - Python API documentation- `kryptos.agents.spy_nlp` - Advanced NLP with
poetry/semantic analysis (SPY v2.0)

   - Public interfaces and examples- `kryptos.agents.spy_web_intel` - Continuous web intelligence gathering

   - Module structure and usage- `kryptos.agents.k123_analyzer` - Sanborn pattern extraction from K1-K3

   - CLI reference- `kryptos.agents.ops_director` - Strategic attack decision-making

- `kryptos.k4.hypotheses` - Pluggable cipher testing framework

7. **[PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md)** - Performance tuning- `kryptos.k4.scoring` -
Statistical plaintext quality metrics

   - Test suite optimization (127x speedup achieved)- `kryptos.k4.pipeline` - Multi-stage decryption pipeline

   - Benchmarking and profiling guides

   - Future: pytest-xdist for 4:48 → 2:30 tests### Key Commands



8. **[SCORING_CALIBRATION.md](SCORING_CALIBRATION.md)** - Scoring system design- `kryptos autonomous` - Run 24/7
autonomous coordination loop

   - Random baseline establishment- `kryptos k4-decrypt` - Run specific attack hypothesis

   - Statistical thresholds (2σ, 3σ)- CLI reference: See [API_REFERENCE.md](API_REFERENCE.md)

   - Calibration methodology

---

9. **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes

## 🔬 Current Status

### Supporting Resources

**Infrastructure:** ✅ Fully Autonomous (30+ tests passing, continuous learning)

**[sources/](sources/)** - Sanborn intelligence

**Autonomous System:** SPY v2.0 + K123 Analyzer + Web Intel + OPS

Director + Checkpointing

    - `SANBORN.md` - Artist clues and research pointers**Agents:**

    - 4 operational agents with 120x faster iteration (15s cycles)

    - `sanborn_timeline.md` - Public statements chronology

    - **Lines of Code:** ~20,000+ (autonomous system + agents + core logic)

    - `sanborn_crib_candidates.txt` - Confirmed crib list

    - `ajax.pdf` - Reference materials**Recent Achievements (Oct 2025):**



---- ✅ 24/7 autonomous coordination system operational

- ✅ Incremental learning (never reprocess content)

## 🏗️ Project Architecture- ✅ Checkpoint system (never lose progress)

- ✅ 120x faster cycles (15s coordination, 30s OPS, 30min web intel)

### Directory Structure- ✅ 13 Sanborn patterns extracted from K1-K3

- ✅ Advanced NLP with poetry detection, semantic analysis

```- ✅ Continuous web intelligence gathering

kryptos/

├── src/kryptos/          # Core Python package## 🎯 Task Reference

│   ├── agents/           # SPY, LINGUIST, K123 Analyzer, OPS Director, Q-Research

│   ├── k4/               # K4 attack hypotheses and scoring**I want to...**

│   ├── provenance/       # Attack logging and search space tracking

│   ├── research/         # Academic paper integration (Phase 4.2)- **Run the autonomous system** → `python -m kryptos.cli.main autonomous`

│   ├── analysis/         # Strategic coverage analysis (Phase 4.3)- **Run a specific attack** → `python -m kryptos.cli.main k4-decrypt --hypothesis vigenere_northeast`

│   ├── pipeline/         # Attack generation (Phase 5.1 - coming)- **Understand the system** → [AUTONOMOUS_SYSTEM.md](AUTONOMOUS_SYSTEM.md)

│   ├── cli/              # CLI interface- **Check agent architecture** → [AGENTS_ARCHITECTURE.md](AGENTS_ARCHITECTURE.md)

│   └── ciphers.py        # Core cipher implementations- **Add a new hypothesis** → See Hypothesis protocol in [API_REFERENCE.md](API_REFERENCE.md)

├── scripts/              # Performance & tuning utilities- **Review K123 patterns** → [K123_PATTERN_ANALYSIS.md](K123_PATTERN_ANALYSIS.md)

│   ├── benchmark_scoring.py       # Quick benchmarks- **See recent changes** → [CHANGELOG.md](CHANGELOG.md)

│   ├── profile_scoring.py         # cProfile analysis- **Use the API** → [API_REFERENCE.md](API_REFERENCE.md)

│   ├── calibrate_scoring_weights.py  # Weight optimization

│   ├── tuning.py                  # Main tuning orchestrator---

│   └── demo_provenance.py         # Demo attack provenance system

├── tests/                # Test suite (539 tests passing in 4:48)## 📊 Historical Archive

├── artifacts/            # Generated outputs (logs, checkpoints, reports)

├── docs/                 # Documentation (you are here)**docs/archive/** contains `k3_double_rotation.py` (historical K3 exploration script) preserved for reference.

│   ├── PHASE_5_BRIEFING.md        # Current roadmap

│   ├── 30_YEAR_GAP_COVERAGE.md    # Coverage assessment---

│   ├── K123_PATTERN_ANALYSIS.md   # Sanborn patterns

│   ├── sources/                   # Sanborn intelligence## 🤝 Contributing

│   └── archive/                   # Historical documents

└── config/               # Configuration filesWhen adding documentation:

```

1. **Update existing docs first** - Prefer editing over creating new files

1. **Check MASTER_PLAN** - Most strategic information belongs there

1. **Use archive/** - Move superseded docs to archive/old_*/

1. **Keep it lean** - Less is more,

single source of truth 5. **Update this README** - Add new docs to appropriate section

**Intelligence Layer (Phase 4 - Complete):**

- `kryptos.provenance.attack_log` - AttackLogger with deduplication---

- `kryptos.provenance.search_space` - SearchSpaceTracker with coverage metrics

- `kryptos.research.paper_search` - PaperSearch (arXiv/IACR)**Last Updated:** 2025-10-24

- `kryptos.research.attack_extractor` - Extract attack parameters from papers
- `kryptos.research.literature_gap` - LiteratureGapAnalyzer (cross-reference)
- `kryptos.analysis.strategic_coverage` - StrategicCoverageAnalyzer (saturation, heatmaps)

**Agent System:**

- `kryptos.agents.spy` - SPY pattern detection (NLP, cribs, anomalies)
- `kryptos.agents.linguist` - LINGUIST English validation
- `kryptos.agents.k123_analyzer` - K123 Analyzer (Sanborn patterns)
- `kryptos.agents.ops_director` - OPS Director (strategic decisions)
- `kryptos.agents.q_research` - Q-Research (cryptanalysis theory)

**Attack System:**
- `kryptos.k4.hypotheses` - 20 attack hypotheses (Vigenère, Hill, transposition, composites)
- `kryptos.k4.scoring` - Statistical plaintext quality metrics
- `kryptos.k4.pipeline` - Multi-stage decryption pipeline

---

## 🔬 Current Status

**Phase:** 4 Complete → 5 Starting **Tests:** 539/539 passing in 4:48 **Infrastructure:** Intelligence layer operational
(provenance + literature + coverage) **Next:** Attack Generation Engine (Phase 5.1)

**Recent Achievements (October 2025):**

✅ **Phase 4.1: Attack Provenance** (45 tests)
- AttackLogger: 100% deduplication, fingerprint-based
- SearchSpaceTracker: Coverage metrics, region registration
- Answer: "Have we tried this attack?"

✅ **Phase 4.2: Academic Paper Integration** (32 tests)
- PaperSearch: arXiv/IACR queries
- AttackExtractor: Extract cipher types, attack methods, parameters
- LiteratureGapAnalyzer: Cross-reference our attacks vs literature
- Answer: "What has academia tried that we haven't?"

✅ **Phase 4.3: Strategic Coverage Analysis** (14 tests)
- StrategicCoverageAnalyzer: Saturation detection, time-series tracking
- Coverage heatmaps: JSON + HTML visualization
- OPS recommendations: PIVOT/INTENSIFY/EXPLORE actions
- Answer: "Is this region saturated? Where should we pivot?"

✅ **Phase 5 Planning: Comprehensive Briefing**
- PHASE_5_BRIEFING.md: Complete roadmap with Sanborn clues
- 30_YEAR_GAP_COVERAGE.md: 95% coverage of pre-1990 cryptography
- Strategic direction: BERLIN + CLOCK + NORTHEAST anchors

**K4 Cracking Odds:**
- Classical cipher variant: **60-70%** (our strength)
- Novel cryptanalysis needed: 20-30%
- Unknown cipher type: 5-10%

## 🎯 Phase 5 Roadmap

### Sprint 5.1: Attack Generation Engine (Next - 6-8 hours)

**Goal:** Q-Research hints → executable attack parameters

**Deliverables:** 1. `AttackGenerator` class: Convert Q-Research hints to AttackParameters 2. Coverage-gap targeting:
Generate attacks for unexplored key space 3. Literature-informed generation: Suggest new techniques from papers 4. 100%
deduplication: Check AttackLogger before generating

**Success Criteria:**
- Q hints auto-convert to runnable attacks
- Attack queue prioritized by coverage gap + Q confidence
- 15-20 tests passing

### Sprint 5.2: Validation Pipeline (1-2 weeks)
**Goal:** Multi-stage filtering: SPY → LINGUIST → Q-Research → Human

**Architecture:**
```
Raw Output (100K candidates)
  → SPY Pre-Filter (90% rejected - crib check)
  → LINGUIST Scoring (90% rejected - English metrics)
  → Q-Research Deep Validation (90% rejected - cryptanalytic soundness)
  → Human Review Queue (10-100 final candidates)
```

**Success Criteria:**
- <1% false positive rate at human review
- Real solution survives all filters
- 25-30 tests passing

### Sprint 5.3: End-to-End K4 Pipeline (2-3 weeks)
**Goal:** Single-command orchestration

**CLI:**
```bash
kryptos k4 --attack-budget 10000 --max-runtime 24h
```

**Flow:** 1. OPS Director → Strategy planning (PIVOT/INTENSIFY/EXPLORE) 2. Q-Research → Cryptanalysis hints (Vigenère
metrics, transposition periods) 3. AttackGenerator → Parameter generation + deduplication 4. Execution → Hypothesis
runner (parallel workers) 5. Validation → SPY → LINGUIST → Q-Research → Human 6. Reporting → Progress bars, heatmaps,
top candidates

**Success Criteria:**
- Single command solves K4 (if classical cipher)
- Checkpoint/resume works
- 10-15 integration tests passing

---

## 📊 Historical Archive

**docs/archive/** contains superseded documents:

- **sessions/** - Session progress reports (SESSION_PROGRESS_2025-10-25.md, etc.)
- **AGENT_EVOLUTION_ROADMAP_OLD.md** - Superseded by PHASE_5_BRIEFING.md
- **OPS_LLM_INTEGRATION_OLD.md** - Historical OPS design
- **OPS_V2_STRATEGIC_DIRECTOR_OLD.md** - Historical OPS v2 design
- **META_COORDINATOR_OLD.md** - Historical coordinator design
- **k3_double_rotation.py** - Historical K3 exploration script

Archive preserved for historical context, not actively maintained.

---

## 🤝 Contributing

When adding documentation:

1. **Update existing docs first** - Prefer editing PHASE_5_BRIEFING.md over creating new files 2. **Archive superseded
content** - Move old docs to archive/ with datestamp 3. **Keep it lean** - Single source of truth, less is more 4.
**Update this README** - Add new docs to appropriate section 5. **Update INDEX.md** - Maintain navigation index

---

## 📖 Finding Information

**"How do I...?"**
- Run attacks? → This README (Quick Start section)
- Understand Phase 5? → PHASE_5_BRIEFING.md
- Check coverage gaps? → 30_YEAR_GAP_COVERAGE.md
- See K123 patterns? → K123_PATTERN_ANALYSIS.md
- Learn about agents? → AGENTS_ARCHITECTURE.md
- Use the API? → API_REFERENCE.md

**"What are the...?"**
- Confirmed clues? → PHASE_5_BRIEFING.md (BERLIN, CLOCK, NORTHEAST)
- Attack priorities? → PHASE_5_BRIEFING.md (Berlin Clock + Hill first)
- Coverage gaps? → 30_YEAR_GAP_COVERAGE.md (Beaufort, ADFGVX, etc.)
- K4 odds? → PHASE_5_BRIEFING.md (60-70% for classical)

**"Where is...?"**
- Sanborn intelligence? → sources/ directory
- Old session notes? → archive/sessions/
- Historical code? → archive/

---

**Last Updated:** October 25, 2025 **Status:** Phase 4 Complete, Phase 5 Ready to Execute
