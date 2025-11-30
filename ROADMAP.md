# 🗺️ KRYPTOS Roadmap

## 🏗️ Phase 6.2 - Composite Attacks

- [ ] Implement V→T composite chain (Vigenère + transposition)
- [ ] Implement T→V composite chain
- [ ] Multi-stage validation pipeline (SPY → LINGUIST → Q)
- [ ] Confidence threshold system
- [ ] Synthetic composite test cases (100% target)
- [ ] Optimize CI: fast pipeline runs with module-level slow tests skipped; full Monte Carlo gated to separate job
- [ ] Improve Coverage: gate temporarily set to 60% to keep CI actionable while we add coverage-increasing tests

## 📚 Phase 6.3 - Adaptive Learning

- [ ] Learning from failures system
- [ ] Failure pattern detection
- [ ] Coverage-guided attack generation
- [ ] Visual coverage heatmaps
- [ ] Smart pruning of saturated search spaces
- [ ] 50% reduction in duplicate attacks (target)

## 🎯 Phase 6.4 - Production K4 Campaign

- [ ] Extended K4 attack campaign (10,000+ attacks)
- [ ] Performance optimization (4× speedup target)
- [ ] Multiprocessing parallel execution
- [ ] Production-scale validation pipeline
- [ ] Coverage reports and candidate export

### Phase 6.5 - Cross-Run Memory System

- [ ] Extend SearchSpaceTracker to persist tried keys
- [ ] Integrate with Vigenère key recovery exclusion
- [ ] Integrate with transposition SA exclusion
- [ ] Integrate with Hill cipher matrix fingerprinting
- [ ] Create AdaptiveSolverConfig class
- [ ] Implement success pattern detection
- [ ] Implement failure pattern detection

### Phase 7 - Future Enhancements

- [ ] K3 double transposition autonomous solving
- [ ] Performance optimization (4× speedup target)
- [ ] Extended logging and diagnostics
- [ ] Enhanced CLI reporting
- [ ] Visual coverage dashboards
