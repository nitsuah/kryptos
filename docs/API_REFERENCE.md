# Kryptos Public API Reference

Reference version: 2025-10-23

Breadcrumb: Overview > API > Reference ---

This document enumerates the stable, supported Python entry points and CLI subcommands. Items not listed here are
considered internal and may change without notice.

## Stability Policy

- Stable: Semantic compatibility guaranteed across minor versions (only additive changes).
- Experimental: May change or be removed after one minor version; marked with warning in docstring.
- Deprecated: Emits `DeprecationWarning`; scheduled removal appears in `DEPRECATIONS.md`.

## Python Modules

### Core

- `kryptos.paths` — helpers for artifact directories, provenance hashing.
- `kryptos.logging.setup_logging(level="INFO", logger_name=None, ...)` — set up a namespaced logger.

### Sections

- `kryptos.k1.decrypt(ciphertext: str, **opts) -> DecryptResult`
- `kryptos.k2.decrypt(ciphertext: str, **opts) -> DecryptResult`
- `kryptos.k3.decrypt(ciphertext: str, **opts) -> DecryptResult`
- `kryptos.k4.decrypt_best(ciphertext: str, limit=25, adaptive=True, report=False) -> DecryptBatch`
- `kryptos.sections.SECTIONS` mapping {"K1": fn, ...}

### K4 Scoring

- `kryptos.k4.scoring.combined_plaintext_score(plaintext: str) -> float`
- `kryptos.k4.scoring.positional_letter_deviation_score(plaintext: str, period=5) -> float`
- `kryptos.k4.scoring.combined_plaintext_score_extended(plaintext: str) -> float`

### K4 Pipeline

- `kryptos.k4.pipeline.build_default(limit=50, adaptive=True) -> Pipeline`
- `kryptos.k4.composite.run_pipeline(ciphertext: str, pipeline: Pipeline) -> DecryptBatch`

### K4 Tuning

- `kryptos.k4.tuning.run_crib_weight_sweep(weights: list[float], run_dir: Path|None=None) -> list[CribWeightRow]`
- `kryptos.k4.tuning.pick_best_weight_from_rows(rows: list[CribWeightRow]) -> float`
- `kryptos.k4.tuning.tiny_param_sweep() -> list[TinyParamResult]`
- `kryptos.k4.tuning.holdout_score(weight: float, run_dir: Path|None=None) -> HoldoutSummary`
- `kryptos.k4.tuning.artifacts.end_to_end_process(run_dir: Path) -> Path`

### Reporting

- `kryptos.k4.report.write_condensed_report(run_dir: Path) -> Path`
- `kryptos.k4.report.write_top_candidates_markdown(run_dir: Path, limit=10) -> Path`

### Spy Extraction / Evaluation

- `kryptos.spy.extractor.extract(run_dir: Path, min_conf: float=0.3) -> list[str]`
- `kryptos.spy.extractor.scan_run(run_dir: Path) -> RunExtraction`

### Autopilot (Experimental)

- `kryptos.autopilot.run(plan: AutopilotPlan) -> AutopilotResult` (EXPERIMENTAL)
- `kryptos.autopilot.recommend_next_action(state: AutopilotState) -> ActionRecommendation` (EXPERIMENTAL)

## CLI Subcommands

Run `kryptos --help` for full usage; stable subcommands listed here.

| Subcommand | Status | Description |
|------------|--------|-------------|
| `sections` | Stable | List sections and brief info |
| `k4-decrypt` | Stable | Run K4 pipeline decrypt attempt |
| `k4-attempts` | Stable | Flush in-memory attempt log to artifacts |
| `tuning-crib-weight-sweep` | Stable | Sweep crib weights and record deltas |
| `tuning-pick-best` | Stable | Select best crib weight from CSV |
| `tuning-summarize-run` | Stable | Summarize a tuning run directory |
| `tuning-tiny-param-sweep` | Stable | Deterministic small parameter sweep |
| `tuning-holdout-score` | Stable | Evaluate chosen crib weight on holdout sentences |
| `tuning-report` | Planned | Combined condensed + top candidates report (future) |
| `spy-eval` | Stable | Evaluate SPY predictions across runs |
| `spy-extract` | Stable | Extract SPY phrases meeting confidence threshold |
| `autopilot` | Experimental | Run autopilot loop with persona strategy |

## Deprecated / Pending Removal

See `DEPRECATIONS.md` for timeline.

## Versioning Notes

Public API changes recorded in `CHANGELOG.md`. Breaking change proposals require prior deprecation window.

## Examples

Python usage snippet:

```python
from kryptos.k4 import decrypt_best
batch = decrypt_best("OBKRUOXOGHULBSOLIFB", limit=25, adaptive=True)
for cand in batch.candidates[:5]:
    print(cand.plaintext, cand.score)
```

CLI attempt:

```bash
kryptos k4-decrypt --cipher data/k4_cipher.txt --limit 25 --adaptive --report
```

Last updated: 2025-10-23T23:59Z
