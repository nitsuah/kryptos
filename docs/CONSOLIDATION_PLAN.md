# Project Consolidation Plan: Less is More

**Date:** 2025-10-24 **Goal:** Reduce cognitive load, eliminate redundancy, create navigable structure

---

## 🎯 Problem Statement

We've been **adding faster than consolidating**:

- **scripts/** has 7+ individual hypothesis runners (should be 1 unified)
- **docs/** has 24 markdown files (should be ~5 core docs)
- Duplicate information across ROADMAP.md, NEXT_24_HOURS.md, EXPANSION_PLAN.md
- Hard to find "source of truth" for strategy, progress, status

**Principle:** Less is more. Consolidate, archive, simplify.

---

## 📁 Part 1: Consolidate scripts/

### Current State

```
scripts/
├── run_hill_2x2_search.py
├── run_vigenere_search.py
├── run_playfair_search.py
├── run_transposition_search.py
├── run_transposition_thorough.py
├── run_simple_substitution_search.py
├── run_random_baseline.py
├── demo/
├── dev/
├── experimental/
├── lint/
└── tuning/
```

**Issue:** 7 nearly-identical scripts that differ only in hypothesis type

### Target State

```
scripts/
├── run_hypothesis.py          # UNIFIED runner for all hypotheses
├── run_all_hypotheses.py      # Batch runner (uses OPS agent)
├── analyze_results.py         # Result analysis/reporting
└── dev/                       # Development utilities
    ├── run_baseline.py
    ├── create_pr.py
    └── (archived individual runners)
```

### Implementation

**New unified runner:**
```python
# scripts/run_hypothesis.py
"""Unified hypothesis test runner.

Usage:
    python run_hypothesis.py hill_2x2
    python run_hypothesis.py vigenere --min-length 1 --max-length 30
    python run_hypothesis.py playfair --keywords KRYPTOS,BERLIN
    python run_hypothesis.py --list  # Show all available hypotheses
"""

import argparse
from kryptos.k4.hypotheses import (
    HillCipher2x2Hypothesis,
    VigenereHypothesis,
    PlayfairHypothesis,
    # ... etc
)

HYPOTHESIS_REGISTRY = {
    'hill_2x2': (HillCipher2x2Hypothesis, {}),
    'vigenere': (VigenereHypothesis, {
        'min_key_length': 1,
        'max_key_length': 20,
        'keys_per_length': 10,
    }),
    'playfair': (PlayfairHypothesis, {
        'keywords': ['KRYPTOS', 'BERLIN', 'CLOCK'],
    }),
    # ... etc
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('hypothesis', help='Hypothesis type to run')
    parser.add_argument('--list', action='store_true', help='List available hypotheses')
    # Add common args that can override defaults
    parser.add_argument('--limit', type=int, default=50)
    parser.add_argument('--output-dir', default='artifacts')

    args = parser.parse_args()

    if args.list:
        print("Available hypotheses:")
        for name in HYPOTHESIS_REGISTRY.keys():
            print(f"  - {name}")
        return

    # Load hypothesis class and params
    hyp_class, default_params = HYPOTHESIS_REGISTRY[args.hypothesis]

    # Run search
    hypothesis = hyp_class(**default_params)
    candidates = hypothesis.generate_candidates(K4_CIPHER, limit=args.limit)

    # Save results (standardized)
    save_results(args.hypothesis, candidates, args.output_dir)

    # Print summary
    print_summary(args.hypothesis, candidates)
```

**Migration:** 1. Create `scripts/run_hypothesis.py` with unified interface 2. Test with each hypothesis type 3. Move
old runners to `scripts/dev/archived/` 4. Update all documentation to reference new unified script

---

## 📚 Part 2: Consolidate docs/

### Current State (24 files)
```
docs/
├── 10KFT.md                    # High-level overview
├── API_REFERENCE.md            # API docs
├── AUTOPILOT.md                # ?
├── CHANGELOG.md                # Change history
├── DEPRECATIONS.md             # Deprecated features
├── EXPANSION_PLAN.md           # 🆕 Just created (hypothesis expansion)
├── EXPERIMENTAL_TOOLING.md     # Experimental features
├── INDEX.md                    # Directory index
├── K4_STRATEGY.md              # K4-specific strategy
├── LOGGING.md                  # Logging config
├── MASTER_AGENT_PROMPT.md      # Agent prompts
├── NEXT_24_HOURS.md            # 24-hour plan
├── PERF.md                     # Performance notes
├── PLAN.md                     # ?
├── README_CORE.md              # ?
├── REORG.md                    # Reorganization notes
├── RESIDUAL_WRITE_SCAN.md      # ?
├── ROADMAP.md                  # Project roadmap
├── SECTIONS.md                 # ?
├── TECHDEBT.md                 # Technical debt
├── ARCHIVED_SCRIPTS.md         # Script archive list
└── archive/                    # Archived docs
```

**Issues:**
- ROADMAP.md, NEXT_24_HOURS.md, EXPANSION_PLAN.md overlap heavily
- Unclear which is "source of truth"
- Many files undated or abandoned mid-update

### Target State (5-7 core docs)
```
docs/
├── README.md                   # Start here (navigation guide)
├── K4_MASTER_PLAN.md          # ⭐ CONSOLIDATED strategy + roadmap + expansion
├── AGENTS_ARCHITECTURE.md      # 🆕 Agent design (SPY/OPS/Q)
├── API_REFERENCE.md            # Code API docs
├── CHANGELOG.md                # Version history
├── TECHDEBT.md                 # Known issues/TODOs
└── archive/                    # Everything else
    ├── old_roadmaps/
    ├── old_strategies/
    └── deprecated/
```

### K4_MASTER_PLAN.md Structure

**Consolidates:** ROADMAP.md, K4_STRATEGY.md, EXPANSION_PLAN.md, NEXT_24_HOURS.md

```markdown
# K4 Master Plan

## Executive Summary
- Current status (6 hypotheses tested, 2 weak signals)
- Next priorities (expand Vigenère, test composites)
- Success criteria

## Strategic Context
- Why K4 is hard (from K4_STRATEGY.md)
- Our approach (systematic elimination)
- Infrastructure advantages

## Hypothesis Pipeline
- Phase 1: Existing hypothesis expansion
- Phase 2: Composite methods
- Phase 3: New cipher families
- Phase 4: Advanced search strategies

## Testing Strategy
- Statistical baseline (random scores)
- Weak signal validation
- Positive controls

## Immediate Next Steps
- Next 3 actions to take right now
- Expected outcomes
- Decision points

## Long-term Vision
- Full autonomous search
- Agent integration
- Breakthrough criteria
```

### Migration Plan

1. **Create K4_MASTER_PLAN.md** - consolidate strategy content 2. **Archive old docs:**
   ```bash
   mkdir -p docs/archive/old_roadmaps
   mv docs/ROADMAP.md docs/archive/old_roadmaps/
   mv docs/NEXT_24_HOURS.md docs/archive/old_roadmaps/
   mv docs/K4_STRATEGY.md docs/archive/old_roadmaps/
   # Keep EXPANSION_PLAN.md for now (just created, still relevant)
   ```

3. **Create docs/README.md** - navigation guide:
   ```markdown
   # Kryptos Documentation

   ## Start Here
   - **K4_MASTER_PLAN.md** - Overall strategy and roadmap
   - **AGENTS_ARCHITECTURE.md** - SPY/OPS/Q design
   - **EXPANSION_PLAN.md** - Detailed expansion initiatives

   ## Reference
   - **API_REFERENCE.md** - Code documentation
   - **CHANGELOG.md** - Version history
   - **TECHDEBT.md** - Known issues

   ## Archive
   - **archive/** - Historical documents (reference only)
   ```

4. **Update root README.md** to point to docs/

5. **Delete or archive:**
   - AUTOPILOT.md (concept abandoned)
   - PLAN.md (superseded by MASTER_PLAN)
   - README_CORE.md (merge into docs/README.md)
   - REORG.md (this consolidation completes it)
   - SECTIONS.md (obsolete)
   - RESIDUAL_WRITE_SCAN.md (temp file)
   - 10KFT.md (merge into MASTER_PLAN executive summary)

---

## 📊 Part 3: Consolidate Progress Tracking

### Current State
- `K4_PROGRESS_TRACKER.md` (in root, good)
- Results scattered across `artifacts/` subdirectories
- No unified view of all hypotheses tested

### Target State
- Keep `K4_PROGRESS_TRACKER.md` in root
- Add automated report generation
- Create `artifacts/SUMMARY.md` with latest results

### Auto-generated Summary

```python
# scripts/generate_summary.py
"""Generate consolidated results summary."""

import json
from pathlib import Path

def main():
    artifacts_root = Path('artifacts')

    # Scan all hypothesis search directories
    hypotheses = {}
    for search_dir in artifacts_root.glob('*_searches'):
        hypothesis_name = search_dir.name.replace('_searches', '')

        # Find latest result
        results = sorted(search_dir.glob('search_*.json'))
        if results:
            with open(results[-1]) as f:
                data = json.load(f)
                hypotheses[hypothesis_name] = {
                    'tested': len(data['top_candidates']),
                    'best_score': data['top_candidates'][0]['score'],
                    'timestamp': data['timestamp'],
                }

    # Generate markdown report
    report = ["# K4 Hypothesis Testing Summary\n"]
    report.append(f"**Updated:** {datetime.now()}\n")
    report.append("## All Hypotheses Tested\n")
    report.append("| Hypothesis | Best Score | Status | Timestamp |")
    report.append("|------------|-----------|---------|-----------|")

    for name, data in sorted(hypotheses.items(), key=lambda x: x[1]['best_score'], reverse=True):
        status = '🟡 Weak Signal' if data['best_score'] > -326.68 else '⚪ No Signal'
        report.append(f"| {name} | {data['best_score']:.2f} | {status} | {data['timestamp']} |")

    # Write to artifacts/SUMMARY.md
    with open('artifacts/SUMMARY.md', 'w') as f:
        f.write('\n'.join(report))
```

---

## ✅ Success Criteria

**scripts/ consolidated:** ✓ 1 unified runner instead of 7 **docs/ streamlined:** ✓ 5-7 core docs instead of 24 **Easy
navigation:** ✓ Clear entry points (README, MASTER_PLAN) **Less redundancy:** ✓ Single source of truth for strategy
**Maintainable:** ✓ New hypotheses add 0 scripts, 1 registry entry

---

## 🚀 Execution Order

1. ✅ Create AGENTS_ARCHITECTURE.md (done) 2. ✅ Create this consolidation plan (done) 3. ⏭️ Create unified
`run_hypothesis.py` 4. ⏭️ Test with all existing hypothesis types 5. ⏭️ Create K4_MASTER_PLAN.md (consolidate strategy
docs) 6. ⏭️ Create docs/README.md (navigation) 7. ⏭️ Archive old docs to docs/archive/ 8. ⏭️ Move old scripts to
scripts/dev/archived/ 9. ⏭️ Update all cross-references 10. ⏭️ Generate artifacts/SUMMARY.md

**Timeline:** 2-3 hours to complete consolidation

---

## 💡 Guiding Principles

1. **Less is More** - Every file should justify its existence 2. **Single Source of Truth** - No duplicate information
3. **Clear Navigation** - User should know where to look 4. **Progressive Disclosure** - Start simple, drill down if
needed 5. **Maintainability** - Easy to keep updated

**Result:** Clean, navigable, professional repository structure
