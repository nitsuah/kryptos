# Quick Start: Autonomous Cryptanalysis System

## 🚀 Launch in 30 Seconds

```bash
# Navigate to project
cd C:\Users\ajhar\code\kryptos

# Start autonomous system (24-hour run)
python -m kryptos.cli.main autonomous --max-hours 24 --cycle-interval 5
```

That's it! The system will:
- ✅ Load K123 patterns from solved sections
- ✅ Check web for new Sanborn intelligence
- ✅ Run OPS strategic analysis every hour
- ✅ Execute cryptanalysis attempts
- ✅ Validate candidates with SPY v2.0
- ✅ Save progress continuously
- ✅ Generate periodic reports

## 📊 Monitor Progress

**Live Logs:**
```bash
tail -f artifacts/logs/kryptos_*.log
```

**Latest Report:**
```bash
# Find and view most recent progress report
ls -lt artifacts/logs/progress_*.md | head -1 | xargs cat
```

**System State:**
```bash
# View current state (JSON)
cat artifacts/autonomous_state.json | jq .
```

## ⚙️ Configuration Options

### Standard 24-Hour Run
```bash
python -m kryptos.cli.main autonomous --max-hours 24 --cycle-interval 5
```

### Weekend Run (48 hours)
```bash
python -m kryptos.cli.main autonomous --max-hours 48 --cycle-interval 5 --ops-cycle 60
```

### Fast Development Testing (1 hour, quick cycles)
```bash
python -m kryptos.cli.main autonomous --max-hours 1 --cycle-interval 1 --ops-cycle 15
```

### Infinite 24/7 Operation
```bash
python -m kryptos.cli.main autonomous
# Stop with Ctrl+C when needed
```

## 🎛️ All Options

```bash
python -m kryptos.cli.main autonomous --help
```

- `--max-hours HOURS` - Maximum runtime (default: infinite)
- `--max-cycles N` - Maximum coordination cycles (default: infinite)
- `--cycle-interval MIN` - Minutes between cycles (default: 5)
- `--ops-cycle MIN` - Minutes between OPS strategic analysis (default: 60)
- `--web-intel-hours HOURS` - Hours between web intelligence checks (default: 6)

## 🛑 Stop Gracefully

Press `Ctrl+C` - state is automatically saved!

## 🔄 Resume After Interruption

Just run the same command again - it loads the saved state:
```bash
python -m kryptos.cli.main autonomous
```

## 📁 Important Files

**System State:**
- `artifacts/autonomous_state.json` - Current state (auto-saved)

**Progress Reports:**
- `artifacts/logs/progress_*.md` - Periodic progress reports
- `artifacts/logs/kryptos_*.log` - Detailed logs

**Strategic Intelligence:**
- `docs/K123_PATTERN_ANALYSIS.md` - 13 patterns from solved sections
- `data/ops_strategy/` - OPS decision history

**Web Intelligence:**
- `data/web_intel/` - Cached web scraping results

## 📖 Full Documentation

- `docs/AUTONOMOUS_SYSTEM.md` - Complete system documentation
- `docs/SESSION_PROGRESS.md` - What we built and why
- `docs/AGENT_EVOLUTION_ROADMAP.md` - Future enhancements
- `docs/OPS_V2_STRATEGIC_DIRECTOR.md` - OPS design

## 🎯 What Success Looks Like

**Look for in logs:**
```
🚀 Starting autonomous coordination loop
✅ K123 patterns loaded: 13 patterns, 47 cribs
🎯 OPS Decision: CONTINUE/PIVOT/BOOST
📊 Progress report: artifacts/logs/progress_20251025_020015.md
💤 Sleeping 5 minutes until next cycle
```

**Key Metrics:**
- Coordination cycles completed
- Best score ever achieved
- Total candidates tested
- Strategic decisions made
- Agent insights collected

## 💡 Pro Tips

1. **First run?** Let it run for 1 hour with `--cycle-interval 5` to verify everything works

2. **Monitoring?** Use `tail -f` on logs to watch real-time progress

3. **Debugging?** Check `artifacts/autonomous_state.json` to inspect state

4. **Optimization?** Adjust `--ops-cycle` and `--web-intel-hours` based on how often you want strategic analysis

5. **Background run?** Use `nohup` or `screen` for long sessions:
   ```bash
   nohup python -m kryptos.cli.main autonomous --max-hours 48 &
   ```

## 🚨 Troubleshooting

### System won't start
```bash
# Check imports
python -c "from kryptos.autonomous_coordinator import AutonomousCoordinator; print('✅ OK')"
```

### No progress after hours
```bash
# Check OPS decisions
grep "OPS Decision" artifacts/logs/kryptos_*.log | tail -10
```

### High CPU usage
This is expected! Cryptanalysis is CPU-intensive. To reduce:
```bash
# Increase cycle interval (fewer attacks per hour)
python -m kryptos.cli.main autonomous --cycle-interval 15
```

## 🎉 Ready to Solve K4!

The system is now operational and ready to run 24/7. It combines:
- ✅ Sanborn's patterns from K1-K3 (narrow search space)
- ✅ Linguistic validation (distinguish real English)
- ✅ Web intelligence (catch new clues)
- ✅ Strategic decisions (pivot when stuck)
- ✅ Continuous operation (never gives up)

**Philosophy:** *"Human expertise to build, machine endurance to run."*

Start it up and let it churn! 🚀
