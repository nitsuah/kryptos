# Kryptos K4 Documentation

**Systematic cryptanalysis framework for solving Kryptos K4**

---

## 🎯 Quick Start

**New to this project?** Read [AUTONOMOUS_SYSTEM.md](AUTONOMOUS_SYSTEM.md) for the 24/7 autonomous cryptanalysis system.

**Want to run attacks?**

```bash
# Run autonomous coordination (recommended)
python -m kryptos.cli.main autonomous --max-cycles 100

# Run single attack
python -m kryptos.cli.main k4-decrypt --hypothesis vigenere_northeast

# List all available attacks
python -m kryptos.cli.main k4-decrypt --list
```

**Check progress?** See test results in `artifacts/` or [CHANGELOG.md](CHANGELOG.md) for recent additions.

---

## 📚 Core Documentation (6 Files)

1. **[README.md](README.md)** (this file) - Project overview and navigation 2.
**[K4_MASTER_PLAN.md](K4_MASTER_PLAN.md)** - Complete strategy, roadmap, hypothesis testing plan 3.
**[AGENTS_ARCHITECTURE.md](AGENTS_ARCHITECTURE.md)** - SPY/OPS/Q agent design and implementation status 4.
**[API_REFERENCE.md](API_REFERENCE.md)** - Python API documentation and CLI reference 5.
**[CHANGELOG.md](CHANGELOG.md)** - Version history and recent changes 6. **[TECHDEBT.md](TECHDEBT.md)** - Known issues,
cleanup status, improvement roadmap

---

## 🏗️ Project Architecture (10,000ft View)

### Directory Structure

```text
kryptos/
├── src/kryptos/          # Core Python package
│   ├── agents/           # SPY v2.0, OPS Director, K123 Analyzer, Web Intel
│   ├── k4/               # K4-specific pipeline and scoring
│   ├── autonomous_coordinator.py  # 24/7 autonomous orchestration
│   ├── cli/              # CLI interface
│   └── examples/         # Demo scripts
├── scripts/              # Performance & tuning utilities (4 active)
│   ├── benchmark_scoring.py
│   ├── profile_scoring.py
│   ├── calibrate_scoring_weights.py
│   └── tuning.py
├── tests/                # Test suite (30+ autonomous tests)
├── artifacts/            # Generated outputs (searches, runs, reports)
├── docs/                 # Documentation (11 active files)
```
└── docs/                 # Documentation (cleaned: 20→6 files)
```

### Core Modules

- `kryptos.autonomous_coordinator` - 24/7 autonomous orchestration with checkpointing
- `kryptos.agents.spy_nlp` - Advanced NLP with poetry/semantic analysis (SPY v2.0)
- `kryptos.agents.spy_web_intel` - Continuous web intelligence gathering
- `kryptos.agents.k123_analyzer` - Sanborn pattern extraction from K1-K3
- `kryptos.agents.ops_director` - Strategic attack decision-making
- `kryptos.k4.hypotheses` - Pluggable cipher testing framework
- `kryptos.k4.scoring` - Statistical plaintext quality metrics
- `kryptos.k4.pipeline` - Multi-stage decryption pipeline

### Key Commands

- `kryptos autonomous` - Run 24/7 autonomous coordination loop
- `kryptos k4-decrypt` - Run specific attack hypothesis
- CLI reference: See [API_REFERENCE.md](API_REFERENCE.md)

---

## 🔬 Current Status

**Infrastructure:** ✅ Fully Autonomous (30+ tests passing, continuous learning)
**Autonomous System:** SPY v2.0 + K123 Analyzer + Web Intel + OPS Director + Checkpointing
**Agents:** 4 operational agents with 120x faster iteration (15s cycles)
**Lines of Code:** ~20,000+ (autonomous system + agents + core logic)

**Recent Achievements (Oct 2025):**

- ✅ 24/7 autonomous coordination system operational
- ✅ Incremental learning (never reprocess content)
- ✅ Checkpoint system (never lose progress)
- ✅ 120x faster cycles (15s coordination, 30s OPS, 30min web intel)
- ✅ 13 Sanborn patterns extracted from K1-K3
- ✅ Advanced NLP with poetry detection, semantic analysis
- ✅ Continuous web intelligence gathering

## 🎯 Task Reference

**I want to...**

- **Run the autonomous system** → `python -m kryptos.cli.main autonomous`
- **Run a specific attack** → `python -m kryptos.cli.main k4-decrypt --hypothesis vigenere_northeast`
- **Understand the system** → [AUTONOMOUS_SYSTEM.md](AUTONOMOUS_SYSTEM.md)
- **Check agent architecture** → [AGENTS_ARCHITECTURE.md](AGENTS_ARCHITECTURE.md)
- **Add a new hypothesis** → See Hypothesis protocol in [API_REFERENCE.md](API_REFERENCE.md)
- **Review K123 patterns** → [K123_PATTERN_ANALYSIS.md](K123_PATTERN_ANALYSIS.md)
- **See recent changes** → [CHANGELOG.md](CHANGELOG.md)
- **Use the API** → [API_REFERENCE.md](API_REFERENCE.md)

---

## 📊 Historical Archive

**docs/archive/** contains `k3_double_rotation.py` (historical K3 exploration script) preserved for reference.

---

## 🤝 Contributing

When adding documentation:

1. **Update existing docs first** - Prefer editing over creating new files 2. **Check MASTER_PLAN** - Most strategic
content belongs there 3. **Use archive/** - Move superseded docs to archive/old_*/ 4. **Keep it lean** - Less is more,
single source of truth 5. **Update this README** - Add new docs to appropriate section

---

**Last Updated:** 2025-10-24
