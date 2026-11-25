# Changelog

> 🧭 [kryptos](../README.md) · [Index](./INDEX.md) · [Features](./FEATURES.md) · [Roadmap](./ROADMAP.md) · [Tasks](./TASKS.md) · **Changelog** · [Metrics](./METRICS.md) <!-- nav -->

All notable changes to the KRYPTOS project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added

- Added direct tests for the spy phrase aggregator (#339).
- Added direct edge-case tests for K4 segmentation helpers (#337).

- Added a typed frontend client for `POST /api/k4/hypothesis` (#338).
- Added rate-limited `POST /api/k4/hypothesis` for keyed Vigenère and Beaufort checks against K4 (#334).

- Added a pure K4 hypothesis checker for keyed Vigenère and Beaufort decryption with positional crib verdicts (#333).

- Dashboard browser journeys (#328): `frontend/e2e/journeys.spec.ts` + `frontend/playwright.config.ts` (`npm run test:e2e`) cover the K4 grid (97 cell buttons, 24 labelled known-plaintext cells), module deep links (`#k4 #ledger #attacks #lab #system`, legacy aliases) and the next arrow, and the API-down state, with all `/api` calls stubbed through `page.route()`. A new `frontend-e2e` job in `ci-fast.yml` runs them in the Playwright 1.65.1 image.
- Cold-start banner: shows "Waking the server… (free instance cold start)" with `role="status"` when the first `/api/status` request exceeds 3000 ms; clears on first success; keeps existing offline UI on failure.

### Security