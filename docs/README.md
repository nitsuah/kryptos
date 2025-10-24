# Kryptos K4 Documentation

**Quick Navigation for the Kryptos K4 Cryptanalysis Project**

---

## 📍 Start Here

### Core Documents

- **[K4_MASTER_PLAN.md](K4_MASTER_PLAN.md)** ⭐
  - Complete strategy, roadmap, and expansion plan
  - Consolidated view of all hypotheses and priorities
  - Read this first for big picture

- **[K4_PROGRESS_TRACKER.md](K4_PROGRESS_TRACKER.md)**
  - Current status of all tested hypotheses
  - Weak signals and eliminations
  - Latest results and next actions

- **[AGENTS_ARCHITECTURE.md](AGENTS_ARCHITECTURE.md)**
  - SPY/OPS/Q agent design
  - LLM/NLP integration roadmap
  - Technical architecture for autonomous search

### Development

- **[API_REFERENCE.md](API_REFERENCE.md)**
  - Code documentation
  - Module structure
  - Function signatures

- **[CHANGELOG.md](CHANGELOG.md)**
  - Version history
  - Recent changes
  - Feature additions

- **[TECHDEBT.md](TECHDEBT.md)**
  - Known issues
  - TODOs
  - Improvement opportunities

### Configuration & Operations

- **[AUTOPILOT.md](AUTOPILOT.md)**
  - Autonomous operation mode
  - Agent coordination
  - Execution strategies

- **[MASTER_AGENT_PROMPT.md](MASTER_AGENT_PROMPT.md)**
  - Agent instructions
  - Decision criteria
  - Response patterns

---

## 📂 Additional Resources

### Specialized Docs

- **[CONSOLIDATION_PLAN.md](CONSOLIDATION_PLAN.md)** - How we reduced code/doc bloat
- **[EXPANSION_PLAN.md](EXPANSION_PLAN.md)** - Detailed 20-initiative roadmap
- **[EXPERIMENTAL_TOOLING.md](EXPERIMENTAL_TOOLING.md)** - Experimental features
- **[LOGGING.md](LOGGING.md)** - Logging configuration
- **[PERF.md](PERF.md)** - Performance optimization notes
- **[DEPRECATIONS.md](DEPRECATIONS.md)** - Deprecated features

### Reference

- **[10KFT.md](10KFT.md)** - High-level overview
- **[INDEX.md](INDEX.md)** - Full file listing
- **[ARCHIVED_SCRIPTS.md](ARCHIVED_SCRIPTS.md)** - Archived script documentation

### Historical

- **[archive/](archive/)** - Archived/superseded documents (reference only)

---

## 🎯 Quick Links by Task

**I want to...**

- **Understand the project** → Start with [K4_MASTER_PLAN.md](K4_MASTER_PLAN.md)
- **See current progress** → Check [K4_PROGRESS_TRACKER.md](K4_PROGRESS_TRACKER.md)
- **Run a hypothesis test** → See `../scripts/run_hypothesis.py --help`
- **Add a new hypothesis** → See [API_REFERENCE.md](API_REFERENCE.md) for Hypothesis protocol
- **Understand agents** → Read [AGENTS_ARCHITECTURE.md](AGENTS_ARCHITECTURE.md)
- **Fix technical debt** → Review [TECHDEBT.md](TECHDEBT.md)
- **Check recent changes** → See [CHANGELOG.md](CHANGELOG.md)

---

## 📊 Document Status

**Core (Always Current):**
- K4_MASTER_PLAN.md - Updated with each sprint
- K4_PROGRESS_TRACKER.md - Updated after each hypothesis test
- AGENTS_ARCHITECTURE.md - Updated as agents evolve

**Reference (Stable):**
- API_REFERENCE.md - Updated with code changes
- CHANGELOG.md - Updated with releases
- TECHDEBT.md - Updated as issues identified

**Operational (As Needed):**
- AUTOPILOT.md - Updated as autopilot evolves
- MASTER_AGENT_PROMPT.md - Updated as agent behavior changes

**Archived (Historical):**
- archive/ - No longer actively maintained, kept for reference

---

## 🤝 Contributing

When adding documentation:

1. **Update existing docs first** - Prefer editing over creating new files 2. **Check MASTER_PLAN** - Most strategic
content belongs there 3. **Use archive/** - Move superseded docs to archive/old_*/ 4. **Keep it lean** - Less is more,
single source of truth 5. **Update this README** - Add new docs to appropriate section

---

**Last Updated:** 2025-10-24
