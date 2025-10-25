# Kryptos Documentation Index

**Last Updated:** October 25, 2025 **Branch:** triumverate-upgrade **Phase:** 4 Complete → 5 Starting

## 🚀 Quick Start

- **[README.md](README.md)** - Project overview and getting started
- **[PHASE_5_BRIEFING.md](PHASE_5_BRIEFING.md)** - Complete Phase 5 roadmap (START HERE)
- **[30_YEAR_GAP_COVERAGE.md](30_YEAR_GAP_COVERAGE.md)** - Coverage assessment of pre-1990 cryptography

## 📚 Core Documentation

### Phase 5: Pipeline Integration (Current Focus)

- **[PHASE_5_BRIEFING.md](PHASE_5_BRIEFING.md)** - Complete Phase 5 roadmap
  - Executive summary: Intelligence layer complete, K4 odds 60-70%
  - Confirmed clues: BERLIN, CLOCK, NORTHEAST, EAST
  - Strategic direction: Attack priorities
  - Sprint 5.1: Attack Generation Engine
  - Sprint 5.2: Validation Pipeline
  - Sprint 5.3: End-to-End K4 CLI

- **[30_YEAR_GAP_COVERAGE.md](30_YEAR_GAP_COVERAGE.md)** - Technical coverage assessment
  - Overall: ~95% of pre-1990 classical cryptography
  - Strong coverage: Vigenère, Hill, transposition, composites
  - Strategic recommendations: Berlin Clock + Hill 2x2/3x3 priority

- **[K123_PATTERN_ANALYSIS.md](K123_PATTERN_ANALYSIS.md)** - Sanborn's fingerprint
  - 13 patterns extracted from K1-K3 (confidence 0.75-1.00)
  - Cipher progression: K1 (Vigenère) → K2 (Vigenère + coords) → K3 (double transposition)
  - Strategic recommendations for K4 attacks

### Reference Documentation

- **[AGENTS_ARCHITECTURE.md](AGENTS_ARCHITECTURE.md)** - Multi-agent system design
  - SPY, LINGUIST, K123 Analyzer, OPS Director, Q-Research architecture
  - Communication patterns and coordination

- **[AUTONOMOUS_SYSTEM.md](AUTONOMOUS_SYSTEM.md)** - 24/7 autonomous system
  - Architecture, components, usage, monitoring
  - Checkpointing and incremental learning

- **[API_REFERENCE.md](API_REFERENCE.md)** - Code API documentation
  - Public interfaces and examples
  - Module structure and usage

- **[PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md)** - Performance tuning
  - Test suite optimization (127x speedup achieved)
  - Future: pytest-xdist for 4:48 → 2:30 tests

- **[SCORING_CALIBRATION.md](SCORING_CALIBRATION.md)** - Scoring system design
  - Random baseline establishment
  - Statistical thresholds (2σ, 3σ)

- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes

### Supporting Resources

- **[sources/](sources/)** - Sanborn intelligence
  - SANBORN.md - Artist clues and research pointers
  - sanborn_timeline.md - Public statements chronology
  - sanborn_crib_candidates.txt - Confirmed crib list

## 📦 Archive

Old planning documents and historical context:

- **[archive/sessions/](archive/sessions/)** - Session progress reports (archived)
  - SESSION_PROGRESS_2025-10-25.md
  - SESSION_OPS_LLM_2025-10-25.md
  - CLEANUP_SUMMARY_2025-10-24.md

- **[archive/](archive/)** - Historical design documents
  - AGENT_EVOLUTION_ROADMAP_OLD.md
  - OPS_LLM_INTEGRATION_OLD.md
  - OPS_V2_STRATEGIC_DIRECTOR_OLD.md
  - META_COORDINATOR_OLD.md
  - k3_double_rotation.py (historical K3 exploration)

## 🎯 Document Status

### ✅ Active (Current Phase - Phase 5)

| Document | Purpose | Last Updated |
|----------|---------|--------------|
| PHASE_5_BRIEFING.md | Phase 5 roadmap | 2025-10-25 |
| 30_YEAR_GAP_COVERAGE.md | Coverage assessment | 2025-10-25 |
| K123_PATTERN_ANALYSIS.md | Pattern analysis | 2025-10-25 |
| README.md | Project overview | 2025-10-25 |

### 📚 Reference (Stable)

| Document | Purpose | Status |
|----------|---------|--------|
| AGENTS_ARCHITECTURE.md | Agent design | Reference |
| AUTONOMOUS_SYSTEM.md | Autonomous system | Reference |
| API_REFERENCE.md | Code API | Updated as code changes |
| PERFORMANCE_OPTIMIZATION.md | Performance | Historical benchmarks |
| SCORING_CALIBRATION.md | Scoring system | Established baseline |

### 📦 Archived (Historical)

| Document | Reason | Location |
|----------|--------|----------|
| SESSION_PROGRESS_2025-10-25.md | Session complete | archive/sessions/ |
| SESSION_OPS_LLM_2025-10-25.md | Session complete | archive/sessions/ |
| CLEANUP_SUMMARY_2025-10-24.md | Session complete | archive/sessions/ |
| AGENT_EVOLUTION_ROADMAP_OLD.md | Superseded by PHASE_5_BRIEFING | archive/ |
| OPS_LLM_INTEGRATION_OLD.md | Historical design | archive/ |
| OPS_V2_STRATEGIC_DIRECTOR_OLD.md | Historical design | archive/ |
| META_COORDINATOR_OLD.md | Historical design | archive/ |
| k3_double_rotation.py | Historical code | archive/ |

## 🔍 Finding Information

### "How do I...?"

- **Run the Phase 5 pipeline?** → PHASE_5_BRIEFING.md
- **Understand K4 odds?** → PHASE_5_BRIEFING.md (60-70% for classical)
- **Check coverage gaps?** → 30_YEAR_GAP_COVERAGE.md (95% complete)
- **See K123 patterns?** → K123_PATTERN_ANALYSIS.md
- **Learn about agents?** → AGENTS_ARCHITECTURE.md
- **Use the API?** → API_REFERENCE.md

### "What are...?"

- **Confirmed K4 clues?** → PHASE_5_BRIEFING.md (BERLIN, CLOCK, NORTHEAST, EAST)
- **Attack priorities?** → PHASE_5_BRIEFING.md (Berlin Clock + Hill first)
- **Coverage gaps?** → 30_YEAR_GAP_COVERAGE.md (Beaufort, ADFGVX, etc.)

### "What changed...?"

- **Recently (Oct 25)?** → archive/sessions/SESSION_PROGRESS_2025-10-25.md
- **All time?** → CHANGELOG.md
- **Why archived?** → archive/ directories

### "What's next...?"

- **Phase 5 Sprints?** → PHASE_5_BRIEFING.md
  - Sprint 5.1: Attack Generation Engine
  - Sprint 5.2: Validation Pipeline
  - Sprint 5.3: End-to-End K4 CLI

## 📝 Documentation Standards

### File Naming

- `UPPERCASE.md` - Major documentation
- `lowercase.md` - Supporting docs
- Underscores for multi-word: `K123_PATTERN_ANALYSIS.md`

### Status Labels

- ✅ **Active** - Current focus, frequently updated
- 📚 **Reference** - Stable, updated as needed
- 📦 **Archived** - Historical, moved to archive/

### Update Frequency

- **Active docs:** Updated per session
- **Reference docs:** Updated with code changes
- **Archived docs:** Frozen, context preserved

## 🤝 Contributing

When adding new documentation:

1. Choose appropriate name and location 2. Add entry to this INDEX.md 3. Update "Last Updated" dates 4. Archive outdated
docs (don't delete) 5. Update related doc links

## 📧 Questions?

Check existing docs first, then:
- Review archive for historical context
- Check CHANGELOG.md for version history
- Consult code comments and docstrings
