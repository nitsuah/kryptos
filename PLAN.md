# Plan for 2025-10-22

Short goal: Close remaining high-impact coverage gaps in `src/k4/scoring.py` and `src/k4/transposition.py`, then run an initial tuning sweep on a tiny parameter grid to validate the pipeline end-to-end.

Top priorities (day-of):

- [ ] 1) Add focused unit tests for `src/k4/scoring.py` to cover the remaining branches (approx lines 135-157 and related edge cases). Target 95%+ file coverage for scoring.
- [ ] 2) Add 3–4 unit tests for `src/k4/transposition.py` exercising early-exit paths, route edge-cases, and constraint fall-throughs to push that file >90% coverage.
- [ ] 3) Wire a deterministic tiny tuning sweep (in `scripts/tune_pipeline.py`) that runs with minimal budgets and writes a CSV of run results to `artifacts/tuning_runs/` for quick inspection.
- [ ] 4) Run full test suite with coverage and confirm overall coverage remains >= 92% and that new tests are stable.

Stretch tasks (if time permits):

- [ ] 5) Add one integration smoke test that executes the pipeline on a short ciphertext and asserts artifact files exist and contain expected headers/keys.
- [ ] 6) Remove deprecated autofix stubs after a quick code review (or move them to `tools/deprecated/`).

Execution plan and acceptance criteria:

- For scoring tests: aim to add small isolated inputs that trigger chi-square early returns, quadgram fallbacks, baseline_stats branches, and letter_entropy edge cases.
- For transposition: create compact fixtures with constrained column ranges and cribs to force the transposition code into the missing branches.
- For tuning sweep: run 4 quick parameter combinations and assert CSV produced with 4 rows; sweep must complete in < 30s locally.

Notes:

- I'll update the todo list and start with the scoring tests. I expect to complete priorities 1–3 within today's session.
- After finishing, I'll write a short summary and update `PLAN_ARCHIVE` with the day's close-up.
