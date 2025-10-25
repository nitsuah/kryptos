# Autonomous Cryptanalysis System

## Overview

The Kryptos autonomous system is a self-sustaining, 24/7 cryptanalysis framework that combines multiple specialized
agents to continuously work toward solving K4 with minimal human intervention.

**Philosophy:** *"Human expertise to build the system, machine endurance to run it."*

## Architecture

```
┌──────────────────────────────────────────────┐
│      Autonomous Coordinator                  │
│  - Main control loop                         │
│  - Agent messaging                           │
│  - Progress tracking                         │
│  - Strategic decision execution              │
└──────────────────────────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼────┐    ┌────▼────┐    ┌────▼────┐
│   SPY   │    │   OPS   │    │    Q    │
│  v2.0   │    │Strategic│    │Research │
│         │    │Director │    │Assistant│
└─────────┘    └─────────┘    └─────────┘
     │               │               │
     ├──> NLP        ├──> Strategy   ├──> Tools
     ├──> Web Intel  ├──> Decisions  └──> Knowledge
     └──> Validation └──> Reports
```

## Key Components

### 1. SPY v2.0 - Linguistic Intelligence

- **NLP Analysis:** NER, POS tagging, dependency parsing, semantic analysis
- **Poetry Detection:** Rhyme, alliteration, assonance, meter, word shapes
- **Fragment Analysis:** Works on incomplete sentences and short texts
- **Web Intelligence:** Scrapes Kryptos sources for new cribs and intel
- **Validation:** Distinguishes real English from gibberish

**Location:** `src/kryptos/agents/spy_nlp.py`, `src/kryptos/agents/spy_web_intel.py`

### 2. OPS Strategic Director - Decision Making
- **Progress Monitoring:** Tracks attack attempts, scores, improvement rates
- **Agent Insight Synthesis:** Combines discoveries from all agents
- **Strategic Decisions:** CONTINUE, PIVOT, BOOST, REDUCE, STOP, START_NEW
- **Resource Allocation:** Optimizes CPU/time across attacks
- **Daily Reports:** Human-readable progress summaries

**Location:** `src/kryptos/agents/ops_director.py`

### 3. K123 Pattern Analyzer - Sanborn's Fingerprint

- **Spelling Analysis:** Q↔I, U↔O substitutions, intentional errors
- **Thematic Analysis:** Location, discovery, archaeology, communication, secrecy
- **Artistic Elements:** Poetic language, historical quotes, metaphor
- **Structural Markers:** X delimiters, coordinates, word lengths
- **Cipher Evolution:** K1→K2→K3→K4 complexity progression

**Output:** 13 high-confidence patterns (0.75-1.00) with K4 hypotheses

**Location:** `src/kryptos/agents/k123_analyzer.py`

### 4. Autonomous Coordinator - Orchestration
- **Coordination Loop:** Runs every N minutes
- **Agent Messaging:** Inter-agent communication protocol
- **State Persistence:** Never loses progress across sessions
- **Progress Reports:** Generates markdown reports periodically
- **Error Recovery:** Graceful handling of failures

**Location:** `src/kryptos/autonomous_coordinator.py`

## Quick Start

### Basic Usage

Run autonomous system for 24 hours with 5-minute cycles:

```bash
python -m kryptos.cli.main autonomous --max-hours 24 --cycle-interval 5
```

### Recommended Configuration

For overnight/weekend runs:

```bash
python -m kryptos.cli.main autonomous \
  --max-hours 48 \
  --cycle-interval 5 \
  --ops-cycle 60 \
  --web-intel-hours 6
```

**Parameters:**

- `--max-hours 48`: Run for 48 hours (weekend)
- `--cycle-interval 5`: Coordination cycle every 5 minutes
- `--ops-cycle 60`: OPS strategic analysis every hour
- `--web-intel-hours 6`: Check for new web intel every 6 hours

### Infinite Run

For truly autonomous 24/7 operation:

```bash
python -m kryptos.cli.main autonomous --cycle-interval 5
```

Stop with `Ctrl+C` - state is automatically saved.

## What It Does

### Every Coordination Cycle (default: 5 minutes)

1. **Load K123 Patterns** (first cycle only)
   - Extracts Sanborn's "fingerprint" from solved sections
   - Provides 13 actionable patterns with confidence scores
   - Generates thematic cribs for attack guidance

2. **Check Web Intelligence** (configurable frequency)
   - Scrapes Kryptos sources for new information
   - Extracts potential cribs from Sanborn interviews
   - Monitors forums for breakthrough discoveries

3. **Run OPS Strategic Analysis** (configurable frequency)
   - Analyzes progress across all active attacks
   - Synthesizes insights from SPY, Q, and other agents
   - Makes strategic decisions (continue, pivot, boost, stop)
   - Generates daily progress reports

4. **Execute Autopilot Exchange**
   - Runs triumvirate agents (SPY, OPS, Q)
   - Executes cryptanalysis attempts
   - Validates candidates with NLP
   - Logs all activity

5. **Update State & Save**
   - Persists progress to `artifacts/autonomous_state.json`
   - Tracks runtime, cycles, insights, decisions, best scores
   - Enables resume after interruption

6. **Generate Progress Report**
   - Writes markdown report to `artifacts/logs/progress_*.md`
   - Includes attack progress, agent insights, strategic decisions
   - Human-readable summary for periodic review

## State Persistence

### Automatic Checkpointing

State is automatically saved after every cycle to:
```
artifacts/autonomous_state.json
```

**Saved Information:**
- Session start time and total runtime
- Coordination cycle count
- Active attacks with progress metrics
- Agent insights (all discoveries)
- Strategic decisions history
- Web intel check timestamps
- Best score ever achieved
- Total candidates tested

### Resume After Interruption

If the system is stopped (Ctrl+C, crash, reboot), simply restart it:

```bash
python -m kryptos.cli.main autonomous
```

It will automatically:
- Load previous state
- Continue from last checkpoint
- Preserve all progress and insights
- Resume attacks where they left off

## Monitoring Progress

### Real-Time Logs

Watch live progress:

```bash
tail -f artifacts/logs/kryptos_*.log
```

Look for:
- `🚀 Starting autonomous coordination loop`
- `✅ Continuing current approach`
- `🔄 Pivoting to new approach`
- `⚡ Boosting current attack`
- `🎯 OPS Decision: CONTINUE/PIVOT/etc`

### Progress Reports

Check latest report:

```bash
# Find most recent report
ls -lt artifacts/logs/progress_*.md | head -1

# View it
cat artifacts/logs/progress_20251025_013045.md
```

**Report Contents:**
- Executive summary (attempts, best score, active attacks)
- Attack details (type, progress, improvement rate)
- Agent insights (discoveries from SPY, Q, web intel)
- Strategic decisions (what OPS recommended and why)
- Coordination statistics (runtime, cycles, patterns loaded)

### State Inspection

Check current state:

```bash
cat artifacts/autonomous_state.json | jq .
```

**Key Metrics:**
```json
{
  "total_runtime_hours": 47.3,
  "coordination_cycles": 568,
  "best_score_ever": 0.2847,
  "total_candidates_tested": 1847293,
  "k123_patterns_loaded": true,
  "strategic_decisions": [
    {"action": "pivot", "reasoning": "..."},
    {"action": "continue", "reasoning": "..."}
  ]
}
```

## Strategic Intelligence

### K123 Patterns (Loaded on First Cycle)

The system uses 13 patterns from K1-K3 to guide K4 attacks:

1. **NORTHEAST anchor** (confidence 1.00) - chars 26-34 known plaintext 2. **Spelling quirks** (0.95) - Q↔I, U↔O
substitutions expected 3. **Location theme** (0.95) - north, west, degrees, coordinates 4. **Discovery theme** (0.95) -
slowly, emerged, breach, peered 5. **Archaeology theme** (0.95) - debris, chamber, remains 6. **Cipher progression**
(0.90) - K4 likely supercipher 7. **X delimiters** (0.90) - structural markers 8. **Communication theme** (0.90) -
message, transmitted 9. **Secrecy theme** (0.85) - invisible, buried, unknown 10. **Poetic language** (0.85) - artistic,
metaphorical 11. **Coordinates** (0.85) - numeric encodings 12. **Historical quotes** (0.80) - King Tut reference in K3
13. **Word lengths** (0.75) - prefers 3-4 letter words

See `docs/K123_PATTERN_ANALYSIS.md` for full details.

### Web Intelligence

Monitors these sources every 6 hours (configurable):
- **elonka.com** - Kryptos researcher with extensive documentation
- **CIA Kryptos page** - Official source, updates rare but critical
- **Reddit r/codes** - Community discoveries and theories

Extracts:
- Quoted text (potential cribs)
- Proper nouns (NORTHEAST, BERLIN, CLOCK)
- Coordinates and dates
- Sanborn interview quotes

### OPS Strategic Decisions

Every hour (configurable), OPS analyzes:
- Attack improvement rates
- Time since last progress
- Agent insights (linguistic, mathematical, external)
- Resource allocation efficiency

Makes decisions:
- **CONTINUE:** Current approach working, keep going
- **PIVOT:** Stuck, try different cipher technique
- **BOOST:** Promising, increase CPU/resources
- **REDUCE:** Diminishing returns, scale back
- **STOP:** Dead end, abandon this approach
- **START_NEW:** Begin completely new attack type
- **EMERGENCY_STOP:** Human intervention required

## Architecture Details

### Message Passing

Agents communicate via `CoordinationMessage`:

```python
message = CoordinationMessage(
    msg_type=MessageType.INSIGHT,
    source="SPY",
    target="COORDINATOR",
    timestamp=datetime.now(),
    priority=8,  # 1-10, 10=highest
    content={
        "category": "linguistic",
        "description": "Found rhyme pattern",
        "confidence": 0.85,
        "actionable": True,
    }
)
```

**Message Types:**
- **INSIGHT:** Agent discovered something interesting
- **ALERT:** Urgent finding (priority 9-10)
- **STATUS:** Routine update
- **REQUEST:** Agent needs something
- **DIRECTIVE:** Coordinator instructs agent
- **QUERY:** Coordinator asks for information
- **CONFIG:** Configuration update

### Coordination Cycle

```python
def _coordination_cycle(self):
    # 1. Load K123 patterns (once)
    if not self.state.k123_patterns_loaded:
        self._load_k123_patterns()

    # 2. Check web intelligence (periodically)
    self._check_web_intelligence()

    # 3. Run OPS strategic analysis (periodically)
    self._run_ops_strategic_analysis()

    # 4. Execute autopilot exchange
    run_exchange(autopilot=True)

    # 5. Update state
    self.state.coordination_cycles += 1
    self.state.total_runtime_hours += cycle_duration

    # 6. Save state
    self._save_state()
```

### Error Handling

- **Graceful Degradation:** If one agent fails, others continue
- **Automatic Retry:** Transient errors (network, file I/O) retried
- **State Preservation:** State saved even on crash
- **Logging:** All errors logged to `artifacts/logs/`

## Next Steps

### Current Capabilities ✅

- ✅ SPY v2.0 with advanced NLP and poetry detection
- ✅ K123 pattern analysis (13 patterns discovered)
- ✅ Web intelligence for dynamic crib discovery
- ✅ OPS strategic framework (rule-based decisions)
- ✅ Autonomous coordination layer
- ✅ State persistence and recovery
- ✅ CLI integration (`kryptos autonomous`)

### In Progress 🔄

- ⏳ LLM integration for OPS (GPT-4/Claude strategic analysis)
- ⏳ Agent messaging protocol (full inter-agent communication)
- ⏳ LINGUIST agent (transformer-based validation)

### Planned 📋

- 📋 Distributed computing (Ray/Dask for parallelism)
- 📋 Q research integration (academic paper search)
- 📋 Meta-Agent coordinator (high-level orchestration)
- 📋 Real-time web dashboard (progress visualization)
- 📋 Notification system (email/Slack on breakthroughs)

## Philosophy

### Human-in-Loop vs Autonomous

**Human Expertise (One-Time):**
- Design agent architecture
- Implement NLP algorithms
- Define strategic decision framework
- Configure K123 pattern extraction
- Set termination conditions

**Machine Endurance (24/7):**
- Run coordination loops continuously
- Execute cryptanalysis attempts
- Validate candidates linguistically
- Monitor web for new intelligence
- Make strategic pivots
- Track progress meticulously
- Never get tired or bored

**Human Intervention (As Needed):**
- Review weekly progress reports
- Adjust strategy based on meta-analysis
- Respond to EMERGENCY_STOP alerts
- Celebrate breakthrough discoveries! 🎉

### Success Criteria

The system is working if: 1. ✅ Runs 24/7 without crashes 2. ✅ State persists across interruptions 3. ✅ Makes intelligent
strategic pivots (not stuck on dead ends) 4. ✅ Discovers new cribs from web sources 5. ✅ Validates candidates using
Sanborn's fingerprint 6. ✅ Exhausts search space systematically 7. ✅ Generates actionable progress reports 8. ✅
Eventually solves K4! 🏆

## Troubleshooting

### System Won't Start

```bash
# Check dependencies
python -c "from kryptos.autonomous_coordinator import AutonomousCoordinator; print('✅ OK')"

# Verify state file
cat artifacts/autonomous_state.json
```

### No Progress

Check if attacks are actually running:
```bash
# Check autopilot logs
tail -f artifacts/logs/kryptos_*.log

# Verify OPS is making decisions
grep "OPS Decision" artifacts/logs/kryptos_*.log | tail -5
```

### High CPU Usage

This is expected! Cryptanalysis is CPU-intensive. To reduce:

```bash
# Increase cycle interval (less frequent attacks)
python -m kryptos.cli.main autonomous --cycle-interval 15

# Or reduce OPS cycle frequency
python -m kryptos.cli.main autonomous --ops-cycle 120
```

### Want Faster Results

```bash
# Decrease cycle interval (more attempts per hour)
python -m kryptos.cli.main autonomous --cycle-interval 1

# More frequent OPS pivots
python -m kryptos.cli.main autonomous --ops-cycle 30
```

## Example Session

```bash
$ python -m kryptos.cli.main autonomous --max-hours 24 --cycle-interval 5

🚀 Starting autonomous coordination loop
   Max runtime: 24.0 hours
   Max cycles: ∞
   Cycle interval: 5 minutes

2025-10-25 02:00:00 INFO Loading K123 patterns...
2025-10-25 02:00:01 INFO K123 patterns loaded: 13 patterns, 47 cribs
2025-10-25 02:00:01 INFO Running OPS strategic analysis...
2025-10-25 02:00:02 INFO 🎯 OPS Decision: START_NEW
2025-10-25 02:00:02 INFO    Reasoning: No active attacks, start vigenere_northeast
2025-10-25 02:00:02 INFO    Confidence: 0.85
2025-10-25 02:00:02 INFO Running autopilot exchange...
2025-10-25 02:00:15 INFO Coordination cycle 1 complete (0.3 min)
2025-10-25 02:00:15 INFO 📊 Progress report: artifacts/logs/progress_20251025_020015.md
2025-10-25 02:00:15 INFO 💤 Sleeping 5 minutes until next cycle

2025-10-25 02:05:15 INFO Running autopilot exchange...
2025-10-25 02:05:28 INFO Coordination cycle 2 complete (0.2 min)
2025-10-25 02:05:28 INFO 💤 Sleeping 5 minutes until next cycle

[... continues for 24 hours ...]

2025-10-26 02:00:00 INFO ⏰ Max runtime reached (24.0 hours)
2025-10-26 02:00:00 INFO 🏁 Autonomous coordination stopped after 24.0 hours, 288 cycles
```

## Contributing

To extend the autonomous system:

1. **New Agent:** Implement in `src/kryptos/agents/` 2. **Register with Coordinator:** Add to
`autonomous_coordinator.py` 3. **Message Protocol:** Use `CoordinationMessage` for communication 4. **State Tracking:**
Update `AutonomousState` dataclass 5. **CLI Integration:** Add subcommand if needed

See `docs/AGENT_EVOLUTION_ROADMAP.md` for planned enhancements.

---

**Built with the philosophy:** *"This system rules out most of what folks have tried over the past 30+ years."*

The autonomous system exhaustively explores the search space using Sanborn's fingerprint from K1-K3, makes intelligent
strategic pivots, and never gives up. It's not just throwing compute at the problem - it's thinking, learning, and
adapting toward solving K4.
