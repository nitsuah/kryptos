# Kryptos Manifesto

Last Updated: 2026-04-03

## Purpose

Kryptos exists to build trustworthy cryptanalysis infrastructure for long-horizon research on K4.

This project is successful when it improves the quality, speed, and honesty of evidence, even when no immediate
breakthrough occurs.

## Core Principles

1. Truth over narrative
   - We prioritize measured outcomes over optimistic interpretation.
   - Negative results are first-class outputs, not failures to hide.

2. Reproducibility over heroics
   - Claims must be reproducible from committed code, pinned data, and documented commands.
   - Provenance and artifacts are required for significant campaign claims.

3. Baseline rigor before frontier claims
   - K1-K3 are continuous calibration tests.
   - No K4 strategy is promoted unless it is stable on known-cipher controls.

4. AI as multiplier, not authority
   - AI helps generate hypotheses, improve code, and speed operations.
   - AI proposals must pass statistical and engineering validation before adoption.

5. Compounding iteration over big-bang rewrites
   - Prefer small, testable changes with clear acceptance criteria.
   - Preserve velocity by reducing complexity and pruning dead branches.

6. Transparent decision trails
   - Keep records of what was tried, what failed, what changed, and why.
   - Retired hypotheses should stay retired unless new evidence appears.

## Non-Negotiable Standards

1. Every substantial change has evidence
   - Unit or integration tests, benchmark deltas, or deterministic artifact output.

2. Every campaign run leaves a trail
   - Attempts, lineage, and scoring context written under artifacts.

3. Every roadmap statement is testable
   - Use concrete thresholds, rates, or runtime targets.

4. Every phase defines subtraction
   - At least one explicit item to stop, remove, or de-prioritize.

## Decision Rubric

Use this before merging strategy-level changes:

1. Does it improve validated metrics on K1-K3 or campaign throughput quality?
2. Is the gain reproducible in CI or documented run commands?
3. Is provenance complete enough for independent audit?
4. Does this reduce future search waste (dedupe, pruning, or better ranking)?
5. If this fails, is rollback simple and low-risk?

If three or more answers are no, do not merge as strategic advancement.

## Definition of Progress

Progress is not "more hypotheses attempted." Progress is:

- Better calibrated scoring against controls
- Better hit quality in top-ranked candidates
- Better reproducibility and lower operational friction
- Better exclusion of known-dead search regions

## Anti-Patterns We Reject

- Metric shopping without controls
- Unbounded brute force without pruning strategy
- "AI says so" merges without measured validation
- Architecture growth without corresponding benchmark gain
- Reintroducing previously failed ideas without new evidence

## Cadence Expectations

- Weekly: summarize experiments, failures, and promoted learnings
- Monthly: review metrics and retire low-yield tracks
- Quarterly: re-evaluate roadmap priorities against measured outcomes
