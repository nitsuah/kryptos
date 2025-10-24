# Kryptos K4 Documentation

**Systematic cryptanalysis framework for solving Kryptos K4**

---

## 🎯 Quick Start

**New to this project?** Read [K4_MASTER_PLAN.md](K4_MASTER_PLAN.md) for the complete strategy.

**Want to run a hypothesis?**

```bash
python scripts/run_hypothesis.py --list
python scripts/run_hypothesis.py berlin_clock
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
│   ├── agents/           # SPY (implemented), OPS/Q (planned)
│   ├── k4/               # K4-specific pipeline and scoring
│   ├── examples/         # Demo scripts (moved from scripts/demo/)
│   └── ...
├── scripts/              # Consolidated utilities
│   ├── run_hypothesis.py     # Unified hypothesis runner ✅
│   ├── run_random_baseline.py
│   ├── dev/              # Development tools (3 files)
│   ├── tuning/           # Tuning harnesses
│   └── lint/             # Code quality tools
├── tests/                # Test suite (249 passing)
├── artifacts/            # Generated outputs (searches, runs, reports)
└── docs/                 # Documentation (cleaned: 20→6 files)
```

### Core Modules

- `kryptos.k4.hypotheses` - Pluggable cipher testing framework
- `kryptos.k4.scoring` - Statistical plaintext quality metrics
- `kryptos.k4.pipeline` - Multi-stage decryption pipeline
- `kryptos.agents.spy` - Pattern recognition agent (✅ implemented)
- `kryptos.agents.ops` - Parallel execution orchestrator (⏳ planned)
- `kryptos.agents.q` - Quality validation module (⏳ planned)

### Key Scripts

- `scripts/run_hypothesis.py` - Run any hypothesis by name (unified interface)
- `scripts/tuning/crib_weight_sweep.py` - Optimize scoring weights
- `scripts/dev/orchestrator.py` - Agent coordination harness

---

## 🔬 Current Status

**Infrastructure:** ✅ Operational (249 tests passing) **Hypotheses Tested:** 9 (Hill 2x2, Vigenère, Playfair,
Transposition, Substitution, Autokey, Four-square, Bifid, Berlin Clock)
**Agents:** SPY ✅ | OPS ⏳ | Q ⏳
**Lines of Code:** ~15,000 (down from ~20,000 after cleanup)

**Recent Cleanup (Oct 2024):**

- ✅ Deleted `scripts/experimental/` (100% bloat)
- ✅ Cleaned `scripts/dev/` (8→3 files)
- ✅ Moved `scripts/demo/` → `src/kryptos/examples/`
- ✅ Docs consolidation (20→6 files, 70% reduction)

---

## 🎯 Task Reference

**I want to...**

- **Understand the strategy** → [K4_MASTER_PLAN.md](K4_MASTER_PLAN.md)
- **Run a hypothesis test** → `python scripts/run_hypothesis.py --list`
- **Add a new hypothesis** → See Hypothesis protocol in [API_REFERENCE.md](API_REFERENCE.md)
- **Check agent status** → [AGENTS_ARCHITECTURE.md](AGENTS_ARCHITECTURE.md)
- **Review technical debt** → [TECHDEBT.md](TECHDEBT.md)
- **See recent changes** → [CHANGELOG.md](CHANGELOG.md)
- **Use the API** → [API_REFERENCE.md](API_REFERENCE.md)

---

## 📊 Historical Archive

**archive/** folder contains superseded plans, dated milestones, and historical decision logs. These are kept for
provenance but not actively maintained.

---

## 🤝 Contributing

When adding documentation:

1. **Update existing docs first** - Prefer editing over creating new files 2. **Check MASTER_PLAN** - Most strategic
content belongs there 3. **Use archive/** - Move superseded docs to archive/old_*/ 4. **Keep it lean** - Less is more,
single source of truth 5. **Update this README** - Add new docs to appropriate section

---

**Last Updated:** 2025-10-24
