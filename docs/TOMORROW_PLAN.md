KRYPTOS — Plan for Tomorrow (time-boxed)

Mission (one paragraph): The immediate goal is to stabilize and document the offline autopilot (Q /
OPS / SPY) so it's reliably runnable, well-tested, and easy for reviewers to understand. We'll lock
down packaging and imports so editable installs work consistently, ensure the test suite and linters
are clean, and add clear documentation and a minimal example that demonstrates the structured plan
contract. This will make the existing PR reviewable and reduce the risk of future regressions.

Top 3 tasks (priority order):

1) Run linters and auto-fix (1.5-2 hours)
- What: Run `pre-commit run --all-files`, accept automatic ruff/format fixes, and commit remaining
lint fixes. Focus on `scripts/` changes made by the autopilot feature and `src/kryptos/` shims.
- Commands:
  - `python -m pip install -U pre-commit ruff` (if needed)
  - `pre-commit run --all-files --show-diff-on-failure`
- Blockers: If pre-commit hooks are configured to a different Python or venv, ensure you're using
the repo Python (see `pyproject.toml` and local venv). Watch for editor integrations that skip
hooks.

2) Stabilize tests and CI parity (2-3 hours)
- What: Run `pytest -q`, fix deterministic test failures (missing directories, time-dependent
timestamps), and ensure the number of passed/skipped tests matches the last green run (~152 passed,
4 skipped).
- Commands:
  - `pytest -q -k "not slow"` (skip slow tests to iterate quickly)
  - `pytest tests/test_autopilot_flow.py::test_run_plan_check_writes_log -q` (reproduce the earlier
    failure if present)
- Blockers: Some tests expect external data files or environment variables (e.g., `SPY_MIN_CONF`).
Set conservative defaults or mock those dependencies in tests.

3) Document the autopilot usage + structured plan contract (1.5 hours)
- What: Update `docs/AUTOPILOT.md` with a succinct usage example showing how to call
`scripts/dev/ask_triumverate.py` programmatically and the expected structure of the plan dict:
`{action: str, params: dict, recommendation_text: str, justification: str, metadata: dict}`. Add an
example `scripts/examples/run_autopilot_demo.py` that produces a dry-run plan and prints it.
- Commands:
  - Edit `docs/AUTOPILOT.md` and add the example script to `scripts/examples/`.
- Blockers: Decide whether the `src/kryptos/` shims are kept or replaced; prefer minimal changes
during documentation.

Nice-to-have if time remains:
- Tidy `src/kryptos/` shims (remove duplicates) — 1-2 hours
- Flesh out PR description and changelog — 30-60 minutes

How we'll verify:
- `pre-commit run --all-files` passes locally
- `pytest -q` completes with a passing suite (match baseline)
- `docs/AUTOPILOT.md` contains usage + plan contract; `scripts/examples/run_autopilot_demo.py` runs
and prints a plan dict

Notes / decisions to defer:
- Major refactor of package layout (large invasive changes) — defer until after the PR review to
keep the review focused.
