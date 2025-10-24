# Logging Guidelines

This document describes the Kryptos logging conventions, setup helper, and migration policy.

## Goals

- Consistent, structured logging across CLI, tuning, and daemon scripts.
- Zero `print()` calls inside library modules (only scripts may use prints for direct JSON emission
or PowerShell-friendly output).
- Idempotent handler setup: calling `setup_logging()` multiple times never duplicates handlers.
- Simple opt-in verbosity control via `--log-level` and quiet suppression via `--quiet` in CLI
contexts.

## Setup Helper

Use `kryptos.logging.setup_logging`:

```python
from kryptos.logging import setup_logging
log = setup_logging(level="INFO", logger_name="kryptos.demo")
log.info("demo started")
```

Parameters:
- level: int|str (default "INFO"). Accepts standard names (DEBUG, INFO, WARNING, ERROR).
- logger_name: namespaced logger (e.g. `kryptos.tuning`, `kryptos.autopilot`).
- fmt: override format string (`%(asctime)s %(levelname)s %(name)s: %(message)s`).
- propagate: False by default to avoid duplicate upstream handlers.
- force: True to rebuild the Kryptos handler (rare; used in tests).

Idempotence marker: handlers created by setup_logging are tagged with `_kryptos_handler` to detect
duplicates.

## Logger Naming

| Area          | Logger Name          | Notes |
|---------------|----------------------|-------|
| CLI entry     | `kryptos.cli`        | Top-level user actions and warnings. |
| Demo scripts  | `kryptos.demo`       | Short informative messages. |
| Tuning sweeps | `kryptos.tuning`     | Artifact paths, parameter summaries. |
| Autopilot     | `kryptos.autopilot`  | Planning decisions, loop iterations. |
| Spy extractor | `kryptos.spy`        | Extraction summaries (precision-focused). |

## Script Migration Policy

Phases: 1. Dev scripts (completed): added deprecation headers + logging warnings. 2. Tuning scripts
(completed subset): replaced prints with logging in four core scripts. 3. Demo & examples: convert
prints (run_k4_demo done; others pending). 4. Experimental tools: optional conversion; prints
acceptable for educational output but prefer logging for CI. 5. Legacy shims removal after two minor
releases (spy_eval, deprecated daemons).

## Quiet Mode & Levels

CLI global options:
- `--log-level LEVEL` sets root Kryptos logger (default INFO).
- `--quiet` suppresses non-error log lines; errors still emitted.

Recommended usage in scripts:

```python
log = setup_logging("INFO", "kryptos.tuning")
log.debug("internal detail for troubleshooting")
log.info("artifact written: %s", path)
log.warning("retrying after transient failure")
log.error("operation failed: %s", exc)
```

## No Prints Rule (Library)

Library modules MUST NOT use `print()`. If user-facing structured output is required (e.g. JSON
artifact summary) return data or raise a well-defined exception; the CLI layer prints or serializes.

Allowed print exceptions:
- PowerShell or bash helper scripts under `scripts/lint/` (explicit tooling output).
- Transitional scripts marked DEPRECATED (will be removed).
- Test fixtures intentionally emitting sample content (document with `# intentional print`).

## Testing

Add tests to verify:
- Calling `setup_logging()` twice does not duplicate handlers.
- `--quiet` suppresses INFO/DEBUG while preserving ERROR.
- Daemon or tuning script logs contain an identifying prefix (logger name).

## Deprecation Timeline

| Item                    | Action            | Target Removal Version |
|-------------------------|-------------------|------------------------|
| `ask_best_next.py`      | Remove            | v0.X+2                 |
| `run_plan.py`           | Remove            | v0.X+2                 |
| `autopilot_daemon.py`   | Merge into CLI    | v0.X+1                 |
| `manager_daemon.py`     | Remove            | v0.X+1                 |
| `cracker_daemon.py`     | Refactor/remove   | v0.X+1                 |
| `spy_eval` shim         | Remove            | v0.X+2                 |

## Future Enhancements

- Structured JSON logging option (`--log-format json`).
- Rate-limited progress logger for high-frequency pipeline stages.
- Central context filter (add run id / provenance hash to all log records).
- Optional file handler for long-running experiments.

## Quick Reference

| Scenario                            | Call |
|------------------------------------|------|
| Basic script                       | `setup_logging()` then `log.info(...)` |
| Force reconfigure in a test        | `setup_logging(force=True)` |
| Use DEBUG for a narrow module      | `setup_logging("DEBUG", "kryptos.tuning")` |
| Quiet mode via CLI                 | `--quiet` (suppresses <= INFO) |
| Structured pipeline run (internal) | Logging inside stages; aggregated externally |

## FAQ

Q: Why not configure root logging once at import? A: Side-effect configuration on import makes
integration brittle and causes duplicate handlers in embedding environments. Explicit setup is
safer.

Q: Why restrict prints? A: Prints bypass log levels and structured emission; they complicate testing
and CI. Logging is filterable and consistent.

Q: How to add contextual metadata (e.g. run id)? A: Implement a `logging.Filter` subclass and attach
it to the Kryptos handler in a future enhancement.

--- Last updated: 2025-10-23
