# Agent Module Review (Post-K4, Pre-GUI)

Breadcrumb: Home > Docs > Analysis > Agent Module Review
**repo**: [[repos/kryptos|kryptos]]
_Date: 2026-06-10_

## Scope

Per `ROADMAP.md`'s "Agent Module Review (Post-K4, Pre-GUI)" section, this review
audits four agent modules under `src/kryptos/agents/` for usefulness, correctness,
and integration quality:

- `spy_nlp.py`
- `spy_web_intel.py`
- `linguist.py`
- `ops_director.py`

The review focused on `AutonomousCoordinator` (`src/kryptos/autonomous_coordinator.py`),
the 24/7 control loop that wires these agents together, since it is the primary
consumer of all four modules (directly or transitively).

## Methodology

Static review of each module's public API was followed by **empirical verification**
inside the project's Docker image (`kryptos-agent-review`, built from the repo
`Dockerfile`): each agent class was constructed and its methods called against the
real (unmocked) implementation, with source/tests bind-mounted so edits could be
iterated without rebuilding. This surfaced four bugs in `AutonomousCoordinator` that
were masked by existing unit tests, which mocked call sites with signatures that did
not match the real agent classes (API drift).

## Findings: bugs fixed in `autonomous_coordinator.py`

### Bug 1 — dead, crash-prone direct `SpyNLP()` instantiation

`AutonomousCoordinator.__init__` imported `SpyNLP` from `kryptos.agents.spy_nlp` and
constructed `self.spy_nlp = SpyNLP()` directly, alongside `OpsStrategicDirector()`,
`SpyWebIntel()`, and `K123Analyzer()`.

`SpyNLP.__init__(self, model_name="en_core_web_sm")` calls `spacy.load(model_name)`,
which raises `OSError: [E050] Can't find model 'en_core_web_sm'` if the spaCy model
is not downloaded. The runtime Docker image installs `spacy` (via
`config/requirements-dev.txt`) but never runs
`python -m spacy download en_core_web_sm`.

**Empirical verification**:
```
docker run --rm kryptos-agent-review python -c \
  "from kryptos.agents.spy_nlp import SpyNLP; SpyNLP()"
# -> OSError: [E050] Can't find model 'en_core_web_sm'
```
Before the fix, simply constructing `AutonomousCoordinator()` crashed with the same
error — the autonomous loop could not start at all in the production image.

The result of `self.spy_nlp` was also never read anywhere else in the file — it was
dead state even when it didn't crash.

**Fix**: removed the `SpyNLP` import and the `self.spy_nlp = SpyNLP()` line from
`__init__`. `SpyNLP` remains available and correctly used elsewhere via
`SpyAgent` (`agents/spy.py`), which already wraps construction in
`try/except Exception: ... self.nlp_available = False` — the correct
graceful-degradation pattern.

### Bug 2 — `_check_web_intelligence()` called `SpyWebIntel` with the wrong API

The coordinator called `self.web_intel.gather_intelligence(max_sources=3,
max_age_days=30)` and `self.web_intel.get_top_cribs(n=5)`, and assumed
`gather_intelligence()` returned a list of objects with a `.text` attribute.

The real signatures (`agents/spy_web_intel.py`) are:
```python
def gather_intelligence(self, force_refresh: bool = False) -> dict[str, Any]:
    ...
    return {"new_cribs": [...], "updates": [...], "timestamp": ...}

def get_top_cribs(self, min_confidence: float = 0.6, category: str | None = None) -> list[str]:
    ...  # returns deduplicated crib TEXT strings, sorted by confidence desc
```
`gather_intelligence` takes no `max_sources`/`max_age_days` kwargs, returns a dict
(not a list), and `new_cribs` holds `CribCandidate` objects internally — only
`get_top_cribs()` surfaces plain strings. `get_top_cribs` takes no `n` kwarg.

**Fix**: `_check_web_intelligence()` now calls `gather_intelligence()` with no
arguments, reads `results["new_cribs"]`, and calls `get_top_cribs()` with no
arguments to obtain the high-confidence crib strings for the insight metadata.

**Empirical verification**: with the fix applied, an unmocked call against the live
intel sources (Elonka Kryptos Page, CIA Kryptos, Reddit r/codes) returned 48 new
cribs and logged a `WEB_INTEL` insight without error.

### Bug 3 — `update_attack_progress()` called with the wrong arity

`_run_ops_strategic_analysis()` called
`self.ops_director.update_attack_progress(progress)` — a single `AttackProgress`
object.

The real signature (`agents/ops_director.py`) is:
```python
def update_attack_progress(self, attack_type: str, attempts: int, best_score: float):
```
a 3-argument method keyed by attack type, not a single dataclass.

**Fix**: call sites now pass
`self.ops_director.update_attack_progress(attack_name, progress.attempts, progress.best_score)`
for each entry in `self.state.active_attacks`.

### Bug 4 — `analyze_situation()` returning `None` was not handled

`OpsStrategicDirector.analyze_situation(force_decision: bool = False) ->
StrategicDecision | None` returns `None` whenever `_needs_decision()` is `False`:

```python
def _needs_decision(self, situation: dict) -> bool:
    for attack_data in situation["active_attacks"].values():
        hours_since = (datetime.now() - attack_data["last_improvement"]).total_seconds() / 3600
        if hours_since > 6:
            return True
    actionable_insights = [i for i in self.recent_insights if i.actionable]
    if len(actionable_insights) >= 3:
        return True
    return False
```

This is the **common case** — on a freshly started or recently-improving attack
(`last_improvement` < 6 hours ago) with fewer than 3 actionable insights queued,
`analyze_situation()` returns `None`. The previous coordinator code unconditionally
accessed `decision.timestamp`, `decision.action`, etc., which would raise
`AttributeError: 'NoneType' object has no attribute 'timestamp'` on essentially
every early coordination cycle.

This bug was not caught by existing tests because every test mocked
`analyze_situation` to always return a non-`None` `StrategicDecision`.

**Fix**: added an early-return guard:
```python
decision = self.ops_director.analyze_situation()
if decision is None:
    self.logger.info("OPS: no strategic decision needed at this time")
    self.state.last_ops_decision = now
    return
```
(the duplicate `self.state.last_ops_decision = now` previously set later in the
function was removed, since it is now set once on both the early-return and
decision-made paths).

**Empirical verification**: an unmocked `_run_ops_strategic_analysis()` call on a
fresh coordinator state logged `OPS: no strategic decision needed at this time` and
left `state.strategic_decisions == []`, with no crash.

### Bug 5 — `run_autonomous_loop(max_hours=0.0, ...)` never terminates

`run_autonomous_loop` accepts `max_hours: float | None = None` and
`max_cycles: int | None = None`, documented as "`None` = infinite". The loop's
termination checks used Python truthiness instead of an explicit `None` check:

```python
if max_hours and runtime_hours >= max_hours:
    ...
    break
if max_cycles and self.state.coordination_cycles >= max_cycles:
    ...
    break
```

`0` and `0.0` are falsy in Python, so `max_hours=0.0` (and `max_cycles=0`) — a
caller asking for "run for zero hours / zero cycles", i.e. exit immediately — was
silently treated the same as `None` ("run forever"). Combined with
`cycle_interval_minutes=0` (so `time.sleep(0)` is a no-op), this produces a true
`while True:` busy-loop that calls `_coordination_cycle()` (and therefore the real,
unmocked `run_exchange(autopilot=True)`) over and over with no exit condition.

**Discovery**: this bug was masked on `main` by the (now-fixed) Bug 4 —
`_run_ops_strategic_analysis()` previously crashed with
`AttributeError: 'NoneType' object has no attribute 'timestamp'` on the very first
cycle whenever `analyze_situation()` returned `None` (the common case for a fresh
coordinator with `active_attacks={}`). That crash propagated to
`run_autonomous_loop`'s outer `except Exception` handler, which logged a fatal error
and exited the loop after exactly one cycle — accidentally terminating the loop
*for the wrong reason* before the `max_hours=0.0` bug could ever manifest.

After the Bug 4 fix, `_run_ops_strategic_analysis()` no longer crashes on a fresh
coordinator, so cycle 1 completes normally, the (still-buggy) `max_hours=0.0` check
never trips, and the loop runs forever. This was caught by CI: PR #89's "CI (fast)"
job hung for the full 6-hour GitHub Actions job timeout (twice) on
`tests/smoke/test_fast_coverage_autonomous_coordinator_extra.py::
test_state_key_error_paths_and_loop_reporting`, which calls
`c.run_autonomous_loop(max_hours=0.0, cycle_interval_minutes=0)` against an
unmocked coordinator.

**Fix**: changed both checks to explicit `is not None` comparisons:

```python
if max_hours is not None and runtime_hours >= max_hours:
    ...
    break
if max_cycles is not None and self.state.coordination_cycles >= max_cycles:
    ...
    break
```

`grep -rn "max_hours\s*=\s*0\|max_cycles\s*=\s*0"` confirms the only call site
passing `0`/`0.0` is the test above, so this is a pure bug fix with no other
call-site impact — `None` continues to mean "infinite", and `0`/`0.0` now correctly
mean "exit before the first cycle".

**Empirical verification**: the previously-hanging test now passes in 15.29s in
Docker (was: cancelled after 6h0m18s in GitHub Actions, twice).

## Module-by-module recommendations

### `spy_nlp.py` — **keep, no source changes**

Healthy module with a correct optional-dependency pattern when used via `SpyAgent`
(`agents/spy.py`), which catches construction failures and sets
`self.nlp_available = False`. The only issue was `AutonomousCoordinator`'s
unguarded direct instantiation (Bug 1), now removed. `SpyNLP` continues to provide
NLP-based scoring (`NLPInsight`) when `en_core_web_sm` is available (e.g. local dev
environments where the model has been downloaded).

### `spy_web_intel.py` — **keep, now correctly integrated**

Provides crib discovery from external sources (Elonka Kryptos Page, CIA Kryptos,
Reddit r/codes) with per-source scrape throttling and a Neon `discovered_cribs`
table (file fallback `artifacts/spy_web_intel/cribs.json`). After the Bug 2 fix,
`AutonomousCoordinator._check_web_intelligence()` correctly calls
`gather_intelligence()` / `get_top_cribs()` and surfaces a `WEB_INTEL` agent insight
when new cribs are found.

### `linguist.py` — **keep as standalone/optional, document integration gap**

`LinguistAgent` (with `LinguisticScore`, `SanbornCorpusAnalysis`,
`validate_candidate`, `analyze_sanborn_style`, `batch_validate`,
`cross_validate_with_spy`, perplexity/coherence/grammar scoring with a lazy
`torch`/`transformers`/`sentence-transformers` import and heuristic fallback) is
extensively unit-tested (`tests/functional/test_linguist.py`, ~30+ tests) but is
**not imported anywhere in production `src/`** outside itself.

The main pipeline (`pipeline/validator.py`, `stage3_linguistic_validation`) instead
uses `scoring_enhanced.combined_linguistic_score` / `linguistic_diagnostics` — a
separate, simpler heuristic. The string `"LINGUIST"` that appears in
`tests/smoke/test_fast_coverage_final_push.py` and
`tests/smoke/test_fast_coverage_strategic_and_ops_director.py` is just an
`AgentInsight`/`MetaCoordinator` agent-name label, unrelated to the `LinguistAgent`
class.

**Recommendation**: keep `linguist.py` as a standalone, well-tested module rather
than removing it — `_calculate_perplexity` (transformer-based) offers materially
richer scoring than the current heuristic-only `scoring_enhanced` path. A future
integration could wire `LinguistAgent.cross_validate_with_spy` or
`batch_validate` into `pipeline/validator.py` stage 3 as an optional enhanced-scoring
pass, gated on `torch`/`transformers` availability (mirroring `SpyAgent`'s graceful
fallback for `spacy`). No changes made in this review beyond documenting the gap.

### `ops_director.py` — **keep, core dependency, now correctly integrated**

`OpsStrategicDirector` is the strategic decision engine
(CONTINUE / BOOST / REDUCE / PIVOT / STOP / START_NEW) used by
`AutonomousCoordinator._run_ops_strategic_analysis()`, with LLM-backed (OpenAI /
Anthropic) or rule-based decision-making and Neon `ops_decisions` /
`strategy_kb` persistence (file fallback `artifacts/ops_strategy/decisions.jsonl`).
After the Bug 3 and Bug 4 fixes, the coordinator correctly reports per-attack
progress with the real 3-argument signature and correctly handles the
`Optional[StrategicDecision]` return of `analyze_situation()`, including the common
"no decision needed yet" case.

## Summary of changes in this PR

- `src/kryptos/autonomous_coordinator.py`: 5 bug fixes (above), all empirically
  verified against the real agent implementations in Docker. Bug 5 was discovered
  via a CI hang (PR CI job cancelled after the 6-hour GitHub Actions job timeout,
  twice) caused by the Bug 4 fix exposing a pre-existing latent bug.
- `tests/smoke/test_fast_coverage_autonomous_coordinator_extra.py`: updated mocks to
  match real `SpyWebIntel`/`OpsStrategicDirector` signatures; fixed 2 pre-existing
  flake8 violations (unused import, line-too-long) in the touched file.
- `tests/e2e/test_autonomous_coordinator.py`: updated `gather_intelligence` mock
  return value to match the real dict-shaped return.
- `docs/reference/AGENTS_ARCHITECTURE.md`: updated to reflect the corrected
  coordinator integration and module statuses.
- `ROADMAP.md` / `TASKS.md`: marked the Agent Module Review checklist complete with
  a findings summary.

No modules were removed. All four are kept; three (`spy_nlp`, `spy_web_intel`,
`ops_director`) are now correctly integrated into `AutonomousCoordinator`, and one
(`linguist`) remains a standalone, well-tested module with a documented future
integration path.
