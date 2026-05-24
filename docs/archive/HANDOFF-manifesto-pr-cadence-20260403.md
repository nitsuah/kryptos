# Handoff: Manifesto PR Cadence Enforcement (2026-04-03)

## Summary
Implemented recurring manifesto alignment checks in the PR flow so strategic changes consistently capture signal, reproducibility, and pruning context.

## Changes
- Updated `.github/pull_request_template.md`:
  - Added a dedicated **Manifesto Alignment** section.
  - Added required checklist items for signal impact, reproducibility evidence, and pruning/retirement notes.
- Added `.github/workflows/manifesto-pr-check.yml`:
  - Runs on pull request events for non-draft PRs.
  - Fails when required manifesto section/checklist tokens are missing from PR body.
- Updated `.github/workflows/pr-annotate.yml` comment to remind authors to complete manifesto alignment notes.

## Validation
- Parsed workflow YAML files in a Python Docker container to verify syntax and structure:
  - `.github/workflows/manifesto-pr-check.yml`
  - `.github/workflows/pr-annotate.yml`

## Tracking
- Marked manifesto cadence task complete in `TASKS.md`.
- Added roadmap completion note in `ROADMAP.md`.
