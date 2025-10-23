PACKAGE LAYOUT DECISION

Context

- During the autopilot implementation we introduced thin shims under `src/kryptos/` to make
editable installs and imports reliable while working in-place. This created duplicate modules
between top-level `src/` modules and `src/kryptos/` shims.
- We must decide the canonical package layout to avoid long-term maintenance friction and CI
confusion.

Options

1) Keep `src/kryptos/` shims (current state)
   - Pros: Minimal change, current editable installs tested; no further refactor required.
   - Cons: Duplicate files, potential confusion for contributors, long-term drift.

2) Remove shims and migrate imports to canonical `src/` layout
   - Pros: Cleaner package layout, single source of truth.
   - Cons: Risky and invasive; may require many import edits across the tree; needs careful test
     run.

3) Convert repo to single `kryptos/` package under `src/` and remove top-level modules
   - Pros: Simplest canonical import path for users.
   - Cons: Non-trivial refactor; may break history/packaging assumptions; requires CI updates.

Recommendation (conservative)

- Defer large structural refactor until after PR review. For this PR, keep the `src/kryptos/` shims
but mark them clearly with headers and a `TODO` pointing to this decision file.
- Open a follow-up PR for a controlled migration: create codemod scripts to update imports,
run full test suite, and include a rollback plan.

Migration plan (follow-up PR)

1. Create an automated codemod (python script) that finds `from kryptos...` and `import kryptos...`
usages and replaces with canonical `from k4...` or `from src.k4...` as the target. 2. Add tests/CI
gating: run full test suite and pre-commit hooks on a migration branch. 3. Submit migration PR with
clear changelog and reviewers assigned. 4. If issues appear, revert codemod commit and re-run more
conservative codemod patterns.

Acceptance criteria

- Documentation updated: `CONTRIBUTING.md` and `docs/ISSUES/PACKAGE_LAYOUT_DECISION.md` reference
the chosen plan.
- Migration tooling exists and runs locally.
- Full test suite passes on migration branch.

Rollback plan

- Keep the shims in the codebase until migration is verified.
- If migration introduces test failures that cannot be quickly fixed, revert the migration PR and
keep the shims active.

Next steps

- Create an issue on GitHub linking this document and assign an owner for the migration.
- If you want, I can implement the codemod and open the migration PR after this review is merged.
