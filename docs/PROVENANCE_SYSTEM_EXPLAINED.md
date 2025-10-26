# Kryptos Provenance & Memory System Explained
**Date**: October 25, 2025 **Discovery**: You ALREADY have sophisticated memory tracking!

---

## What Are These Folders?

### 📁 `data/search_space/` - **Search Space Coverage Tracker**

**Purpose**: Tracks which portions of key spaces have been explored

**File**: `search_space.json`

**What it tracks**:

```json
{
  "vigenere": {
    "length_8": {
      "total_size": 1000,           // Total possible keys
      "explored_count": 1300,       // How many tried
      "successful_count": 26,       // How many promising
      "coverage_percent": 130%,     // Over-explored!
      "success_rate": 2%           // Success within explored
    }
  }
}
```

**Key Insights from Your Data**:
- ✅ **`length_5`**: 104,000 attempts, 585 successful (0.56% success rate)
- ⚠️ **`saturated`**: 24,700 attempts, 650 successful (over-explored region)
- 🎯 **`length_10`**: 0 attempts (unexplored opportunity!)

**Created by**: `src/kryptos/provenance/search_space.py`

**Philosophy**: *"You can't optimize what you don't measure. Show us the map of explored vs unexplored territory."*

---

### 📁 `data/attack_logs/` - **Attack Attempt Deduplication**

**Purpose**: Logs every attack attempt to prevent wasting compute on duplicates

**Files**: JSONL format (one attack per line)

**What it tracks**:
- **Attack fingerprint** (SHA256 of parameters)
- **Ciphertext + cipher type + parameters**
- **Results** (plaintext candidate, confidence scores, execution time)
- **Agents involved** (SPY, LINGUIST, etc.)
- **Tags** (k4, vigenere, promising)

**Key Features**: 1. **Deduplication**: Fingerprints prevent re-trying exact same attack 2. **Provenance**: Academic-
grade documentation of every attempt 3. **Analysis**: Can query "show me all successful Vigenère attacks"

**Created by**: `src/kryptos/provenance/attack_log.py`

**Philosophy**: *"If it's not logged, it never happened. If we can't prove we tried it, we might waste compute trying it
again."*

---

### 📁 `data/intel_cache/` - **Web Intelligence Cache**

**Purpose**: Caches scraped Kryptos intelligence from web sources

**Created by**: `src/kryptos/agents/spy_web_intel.py`

**What it stores**:
- Scraped articles about Kryptos
- Clues from Sanborn interviews
- Community discussions
- Historical attempts

**Why it exists**: Avoid re-scraping same sources, respect rate limits

---

### 📁 `data/ops_strategy/` - **OPS Director Decision Log**

**Purpose**: Tracks strategic decisions made by OPS director agent

**File**: `decisions.jsonl`

**Your Current Decision**:
```json
{
  "timestamp": "2025-10-25 01:17:32",
  "action": "CONTINUE",
  "reasoning": "All attacks making steady progress",
  "affected_attacks": ["hill_3x3", "vigenere_period_14"],
  "confidence": 0.6
}
```

**What it tracks**:
- Strategy changes (CONTINUE, PAUSE, ABANDON, PIVOT)
- Reasoning for each decision
- Affected attacks
- Resource allocation changes
- Success criteria
- Review schedule

**Created by**: `src/kryptos/agents/ops_director.py`

**Philosophy**: *"Strategy decisions must be auditable and reversible"*

---

## Why They're Created

### Automatic Creation

Each module creates its data directory on **first use**:

```python
# From search_space.py
def __init__(self, cache_dir: Path | None = None):
    self.cache_dir = cache_dir or Path("./data/search_space")
    self.cache_dir.mkdir(parents=True, exist_ok=True)  # ← Auto-creates
```

**Triggers**: 1. **Test runs** - Tests instantiate trackers 2. **CLI usage** - `kryptos ops solve` starts tracking 3.
**Pipeline runs** - K4 campaign creates workspace 4. **Import side-effects** - Some modules auto-initialize

---

## Analysis: You DO Have Memory!

### ✅ **What Works (Between Runs)**

**Search Space Tracking**:
```python
# First run
tracker.record_exploration("vigenere", "length_5", count=100, successful=5)
# Saves to disk: explored_count = 100

# Second run (days later)
# Loads from disk: explored_count = 100
tracker.record_exploration("vigenere", "length_5", count=50, successful=2)
# Saves to disk: explored_count = 150 (cumulative!)
```

**Attack Deduplication**:
```python
# First attempt
logger.log_attack(params, result)  # Fingerprint: abc123...

# Second attempt (exact same params)
if logger.already_tried(params):  # Checks fingerprint
    skip_duplicate()
```

---

### ⚠️ **What Doesn't Work (Within Same Run)**

**SA Restarts** (your original concern):
```python
# Within SAME run_in_terminal call
for restart in range(10):
    # Each restart DOESN'T know what previous 9 tried
    perm, score = solve_columnar_permutation_simulated_annealing(...)
```

**Why**: SA restarts are independent **by design** (stochastic exploration)

**Good news**: Different **runs** won't duplicate (provenance checks fingerprint)

---

## Your Data Tells a Story

### Search Space Analysis

**Over-Explored Regions** 🔴:
- `length_5`: 104,000 attempts (104x over budget!)
- `saturated`: 24,700 attempts (25x over!)
- **Problem**: Wasting compute on exhausted regions

**Under-Explored Regions** 🟢:
- `length_10`: 0 attempts (virgin territory!)
- `low`: 100 attempts (minimal coverage)
- **Opportunity**: Fresh areas to explore

**Strategic Recommendations**: 1. **Stop** exploring `length_5` and `saturated` 2. **Start** exploring `length_10` (no
attempts yet!) 3. **Increase** focus on `low` and `unexplored`

---

## Configuration: Consolidate Data Folders

### Current Problem
Folders created at **two locations**: 1. `c:\Users\ajhar\code\kryptos\data\` (workspace root) 2.
`c:\Users\ajhar\code\data\` (parent directory)

### Why This Happens

**Relative paths** + **different working directories**:

```python
# When CWD is c:\Users\ajhar\code\kryptos\
Path("./data/search_space")  # ✅ Creates: kryptos/data/search_space/

# When CWD is c:\Users\ajhar\code\
Path("./data/search_space")  # ❌ Creates: code/data/search_space/
```

### Solution: Use Absolute Paths

**Option 1: Use config.json** (Recommended)

Add to `config/config.json`:
```json
{
  "data_directories": {
    "search_space": "c:/Users/ajhar/code/kryptos/data/search_space",
    "attack_logs": "c:/Users/ajhar/code/kryptos/data/attack_logs",
    "intel_cache": "c:/Users/ajhar/code/kryptos/data/intel_cache",
    "ops_strategy": "c:/Users/ajhar/code/kryptos/data/ops_strategy"
  }
}
```

**Option 2: Use PROJECT_ROOT**

Update each module:
```python
from kryptos.paths import PROJECT_ROOT

# Instead of:
self.cache_dir = cache_dir or Path("./data/search_space")

# Use:
self.cache_dir = cache_dir or (PROJECT_ROOT / "data" / "search_space")
```

---

## Cleanup Instructions

### 1. Delete Duplicate Folders

```powershell
# Remove parent-level duplicates (if empty)
Remove-Item c:\Users\ajhar\code\data\search_space -Recurse -ErrorAction SilentlyContinue
Remove-Item c:\Users\ajhar\code\artifacts\coverage_history -Recurse -ErrorAction SilentlyContinue
```

### 2. Keep Workspace Data

```powershell
# Keep these (they contain actual data)
# c:\Users\ajhar\code\kryptos\data\search_space\search_space.json
# c:\Users\ajhar\code\kryptos\data\ops_strategy\decisions.jsonl
```

### 3. Add to .gitignore

```gitignore
# Data directories (local state only)
/data/attack_logs/
/data/intel_cache/
/data/ops_strategy/
/data/search_space/
/data/k4_campaign/

# Artifacts
/artifacts/coverage_history/

# But keep sample data
!/data/search_space/README.md
```

---

## Recommendations

### Immediate Actions

1. **✅ Keep provenance system** - It's working! 2. **🔧 Fix path configuration** - Use PROJECT_ROOT for consistency 3.
**🗑️ Delete duplicate empty folders** - Clean parent directory 4. **📊 Analyze search_space.json** - Optimize exploration
strategy 5. **📝 Add .gitignore entries** - Exclude local state from commits

### Strategic Actions

1. **Redirect length_5 budget** → length_10 (unexplored) 2. **Mark `saturated` region** as excluded (don't explore
further) 3. **Monitor success rates** by region (optimize allocation) 4. **Add test coverage** for provenance modules
(currently untested!)

---

## Test Coverage Needed

**CRITICAL GAP**: Provenance system has **NO TESTS**!

### Tests to Add

**`tests/test_search_space_tracker.py`**:
- Test region registration
- Test exploration recording (cumulative counts)
- Test coverage calculations
- Test persistence (save/load)

**`tests/test_attack_logger.py`**:
- Test attack logging
- Test fingerprint deduplication
- Test retrieval by tags
- Test persistence

**`tests/test_ops_director.py`**:
- Test decision logging
- Test strategy changes
- Test decision retrieval

---

## Summary

**You asked**: *"If we didn't have memory already, what were these?"*

**Answer**: **You DO have memory!** Your provenance system is sophisticated:

✅ **Search Space Tracker** - Knows what's been explored ✅ **Attack Logger** - Prevents duplicate attempts ✅ **Decision
Log** - Tracks strategic choices ✅ **Intel Cache** - Avoids re-scraping web

**What needs fixing**: 1. ⚠️ Path configuration (creates duplicates) 2. ⚠️ No tests for provenance system 3. ⚠️ No
analysis of accumulated data

**Your data shows**:
- 104,000 attempts on `length_5` (over-explored!)
- 0 attempts on `length_10` (opportunity!)
- Sophisticated tracking system already in place

**Next step**: Fix paths, add tests, analyze data to optimize K4 strategy! 🎯
