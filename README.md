# KRYPTOS

> 🧭 **kryptos** · [Index](./docs/INDEX.md) · [Features](./docs/FEATURES.md) · [Roadmap](./docs/ROADMAP.md) · [Tasks](./docs/TASKS.md) · [Changelog](./docs/CHANGELOG.md) · [Metrics](./docs/METRICS.md) <!-- nav -->

[![CI fast](https://github.com/nitsuah/kryptos/actions/workflows/ci-fast.yml/badge.svg)](https://github.com/nitsuah/kryptos/actions)
[![CI (smoke)](https://github.com/nitsuah/kryptos/actions/workflows/demo-smoke.yml/badge.svg)](https://github.com/nitsuah/kryptos/actions)
[![CI (slow)](https://github.com/nitsuah/kryptos/actions/workflows/ci-slow.yml/badge.svg)](https://github.com/nitsuah/kryptos/actions)
[![Netlify Status](https://api.netlify.com/api/v1/badges/0fb1be42-e131-4cf6-ae74-d139c671e1e3/deploy-status)](https://app.netlify.com/projects/kryptos-k4/deploys)

Inspired by *The Unexplained* with William Shatner, I set out to solve Kryptos using Python.

Kryptos is the copper sculpture Jim Sanborn installed at CIA headquarters in 1990. Three of its four passages (K1–K3)
were solved in the 1990s. The last 97 letters, K4, are still unsolved. Sanborn has published 24 of its plaintext
letters as hints: `EAST`, `NORTHEAST`, `BERLIN` and `CLOCK`.

This repository is a research toolkit for K4. It solves K1–K3 end to end, and for K4 it does two kinds of work:

- **Eliminates cipher families.** For each family (periodic keys, autokey, Hill, columnar transposition plus a key,
  and so on) it checks whether *any* key over a stated range could produce the 24 known letters. Each check ships a
  positive control that plants a real solution and shows the check finds it.
- **Tracks what is left.** A hypothesis ledger tags every family as `eliminated`, `statistical`, `sampled_null` or
  `open`, and serves it to the dashboard and the CLI.

---

## Where K4 stands (2026-09-30)

- **What the ciphertext tells us.** K4's index of coincidence is **0.0361**, close to random text (0.0385) and far
  from English (≈0.066). So at least one layer flattens letter frequencies. Whether there is also a transposition, and
  in which order the layers were applied, is **not** established.
- **Ruled out over stated ranges** (26 ledger entries, each with a positive control):
  - Periodic keys up to period 26 in four families (Vigenère, Beaufort, Variant Beaufort, KRYPTOS-keyed Quagmire III),
    and the sum of two periodic keys with p1 + p2 ≤ 24.
  - Autokey, linear, progressive, digit, recurrence and dial keys.
  - Quagmire I–IV over a 231,933-word dictionary, and a periodic key over *any* mixed alphabet (periods 1–12 with the
    alphabet on the plaintext side, 1–15 on the ciphertext side).
  - The geometric grids, K3's double rotation and compass-bearing routes, and columnar transposition of widths 2–9,
    each combined with a periodic key of period 1–22 in either order.
  - Columnar widths 10–14 with a periodic key: key first, periods 1–22 except 17 (widths 12–14) and 18 (width 14);
    transposition first, periods 1–17. The column orders that do fit at those exceptions decrypt to noise.
  - Hill 2×2 to 4×4, nulls between the cribs, and the 25-letter-output ciphers.
- **No signal against shuffled-ciphertext controls:** running keys from any English text, Hill 5×5, and scans that
  allow one or two wrong crib letters.
- **The published full-plaintext reconstruction** ("THE COMPASS ROSE IS HERE…", from solvekryptos.com, not Sanborn)
  fits none of the tested families when used as 97 known letters.
- **Still open** (ranked in [`docs/analysis/K4_NEGATIVE_SPACE.md`](./docs/analysis/K4_NEGATIVE_SPACE.md)):
  irregular transpositions (disrupted columnar, keyed routes, grilles), masking that inserts or drops letters, two
  non-periodic layers together, key rules nobody has named yet, Hill 6×6 and up, and per-letter lookups from the Berlin
  Weltzeituhr, which need photographs of its city ring.

The live version of this list: `kryptos ledger` or `GET /api/k4/ledger`. The narrative log with every run:
[`docs/analysis/K4_ACTIVE_RESEARCH.md`](./docs/analysis/K4_ACTIVE_RESEARCH.md).

### K1–K3

| Section | Plaintext opens | Method | Deliberate misspelling |
|---------|-----------------|--------|------------------------|
| K1 | "Between subtle shading and the absence of light lies the nuance of iqlusion" | Vigenère, KRYPTOS-keyed alphabet, key `PALIMPSEST` | IQLUSION |
| K2 | "It was totally invisible. How's that possible?" | Vigenère, KRYPTOS-keyed alphabet, key `ABSCISSA` | UNDERGRUUND |
| K3 | "Slowly, desperately slowly, the remains of passage debris…" | Double rotational transposition (24×14 grid, rotate, 8 columns, rotate) | DESPARATLY |

K2 also carries `X` characters as separators between sentences. Treat them as structure, not errors, when looking for
patterns.

---

## Quick start

```bash
pip install -r config/requirements.txt
pip install -e . --no-deps

kryptos sections                      # list K1–K4
kryptos sections-decrypt --section K3 # decrypt a solved section
kryptos ledger                        # what is eliminated / statistical / sampled / open for K4
kryptos crib-constraints              # P21: family-level eliminations (a few minutes)
kryptos frontier --quick              # P22: frontier checks without Hill 5×5 and the reconstruction suite
kryptos serve --port 8000             # API + dashboard (if frontend/dist is built)
```

Every subcommand is listed in [`docs/reference/API_REFERENCE.md`](./docs/reference/API_REFERENCE.md#cli-subcommands)
and with `kryptos --help`.

From Python:

```python
from kryptos.k4 import decrypt_best
from kryptos.k4.hypothesis_ledger import ledger

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
result = decrypt_best(K4, limit=40, adaptive=True)   # composite pipeline, best-scoring candidate
print(result.plaintext, result.score)

open_families = ledger("open")                       # what the ledger still lists as untested
```

---

## Dashboard

A single-page React app over the FastAPI backend, styled after the Ghost in the Shell interfaces. Five modules sit on
a ring (K4, Ledger, Attacks, Lab, System), and each is laid out to fit the screen without scrolling. The K4 module
includes a drawing of the Weltzeituhr, the Berlin World Clock that K4 names. Switch modules with the dock, arrow keys
or a swipe. It scales from a phone to a wide monitor. Design notes:
[`docs/reference/DASHBOARD.md`](./docs/reference/DASHBOARD.md); build and deploy: [`frontend/README.md`](./frontend/README.md).

```bash
docker compose -f config/docker-compose.yml up -d   # API + built dashboard on http://localhost:8000
```

---

## How the K4 work is organised

| Layer | Where | What it does |
|-------|-------|--------------|
| Family eliminations (P21) | `kryptos.k4.crib_constraints`, `structural_checks` | Periodic, autokey, linear, progressive, digit and running keys; dictionary Quagmires; transposition × periodic key; nulls; Hill 2×2/3×3; error-tolerant scans against controls |
| Frontier checks (P22) | `kryptos.k4.frontier_checks` | Recurrence, mixed-alphabet, dial, bearing-route and phrase keys; Hill 4×4/5×5; wide columnar (10–14); English running keys; the full-plaintext reconstruction |
| Hypothesis ledger | `kryptos.k4.hypothesis_ledger` | One entry per family with tier, scope, evidence, module and test |
| Scoring | `kryptos.k4.scoring`, `english_model` | English 2/3/4-gram tables from 8.9M letters of public-domain text; `english_z` puts random text at 0 and English at 1 |
| Earlier sweeps (P1–P20, Phases 1–8) | `kryptos.k4.*` | Clock, geometric, keyed-alphabet, masking and composite sweeps. All null; see the capability table |
| Agents | `kryptos.agents` | SPY / OPS / Q / LINGUIST for autonomous campaigns ([architecture](./docs/reference/AGENTS_ARCHITECTURE.md)) |
| API | `kryptos.api` | Dashboard, ledger, attack jobs, vault, RAG search, SSE log tail |

Rules that keep the ledger honest are in [`docs/GOVERN.md`](./docs/GOVERN.md) and enforced by tests: an `eliminated`
entry needs a positive control, and the attack registry must match the dispatcher.

---

## Principles

Kryptos is a long-horizon cryptanalysis program, not a promise machine.

1. **Truth over narrative.** Prefer uncomfortable results. "Did it improve validated signal?" comes first.
2. **Reproducibility over heroics.** Every claim is backed by deterministic commands, artifacts and provenance.
3. **Known ciphers before unknown ones.** K1–K3 reliability is the gate for K4 campaigns.
4. **AI as amplifier, not oracle.** AI output is a proposal that has to survive measurement.
5. **Small, compounding iterations** with clear acceptance criteria.
6. **Kill weak hypotheses quickly,** and record why, so they are not re-argued without new evidence.
7. **Say how strong a "ruled out" is.** Candidate counts are not coverage; use the ledger tiers.

---

## Testing

```bash
pytest -m "not slow"          # fast suite (about 1,770 tests)
pytest tests/smoke/           # seconds
KRYPTOS_RUN_SLOW_MONTE_CARLO=1 pytest -m slow   # opt-in slow suites
```

In Docker:

```bash
docker run --rm -v "${PWD}:/app" -w /app python:3.13-slim sh -lc \
  "pip install --no-cache-dir -r config/requirements.txt pytest pytest-cov && \
   python -m spacy download en_core_web_sm && \
   pip install --no-cache-dir -e . --no-deps && \
   pytest tests/ -m 'not slow' --cov=kryptos --cov-report=term"
```

Test tiers are described in [`tests/README.md`](./tests/README.md); current counts and coverage in
[`docs/METRICS.md`](./docs/METRICS.md).

---

## Deployment

- **Frontend:** Netlify, https://kryptos-k4.netlify.app, built from `frontend/` (`netlify.toml`). `VITE_API_BASE_URL`
  points it at the backend.
- **Backend:** Render free-tier Docker service `kryptos-api`, https://kryptos-kg8t.onrender.com (`render.yaml`). CORS is
  limited to the Netlify origin via `KRYPTOS_CORS_ORIGINS`. The free plan sleeps after about 15 minutes idle, and the
  first request can take up to a minute.
- **Single container:** the root `Dockerfile` builds the SPA and serves it from FastAPI alongside `/api/*`.
- **Optional:** `DATABASE_URL` (Neon/Postgres) enables run history, attack-job persistence and the vault; without it
  the API reports `db_enabled: false` and everything else works. LLM keys are optional; without them the ops director
  uses rule-based logic.

---

## Data and artifacts

- `config/config.json`: ciphertexts, cribs and parameters (the single source for section data).
- `data/ngrams/english_{2,3,4}grams.tsv`: the scoring tables, rebuilt by `scripts/data/build_english_ngrams.py`.
- `artifacts/` and `K4_*_NULL.json`: run outputs. Both are gitignored and regenerated by the commands that write them.
- `data/turbovec/`: the RAG index over `artifacts/` (gitignored; build with `POST /api/rag/reindex`).

---

## References

- [Kryptos on Wikipedia](https://en.wikipedia.org/wiki/Kryptos)
- [UCSD Crypto Project by Karl Wang](https://mathweb.ucsd.edu/~crypto/Projects/KarlWang/index2.html)
- [Kryptosfan blog, K3 solution](https://kryptosfan.wordpress.com/k3/k3-solution-3/)
- [Elonka Dunin's Kryptos pages](https://elonka.com/kryptos/)
- Sanborn's statements, with citations: [`docs/sources/SANBORN_QUOTES.md`](./docs/sources/SANBORN_QUOTES.md)
- [Vigenère cipher](https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher) ·
  [Hill cipher](https://en.wikipedia.org/wiki/Hill_cipher) ·
  [Index of coincidence](https://en.wikipedia.org/wiki/Index_of_coincidence) ·
  [Weltzeituhr](https://en.wikipedia.org/wiki/Weltzeituhr)

<!-- docs-index:start -->

## Docs Index

Every committed Markdown doc in this repo (other than this README, `.github/` and `templates/`), the same set mirrored into the Obsidian vault, so none of them is orphaned.

**`docs/`**

- [Changelog](./docs/CHANGELOG.md) — `docs/CHANGELOG.md`
- [KRYPTOS Features](./docs/FEATURES.md) — `docs/FEATURES.md`
- [Governance and Maintenance Notes](./docs/GOVERN.md) — `docs/GOVERN.md`
- [Kryptos Docs Index](./docs/INDEX.md) — `docs/INDEX.md`
- [Metrics](./docs/METRICS.md) — `docs/METRICS.md`
- [Kryptos Roadmap](./docs/ROADMAP.md) — `docs/ROADMAP.md`
- [Tasks](./docs/TASKS.md) — `docs/TASKS.md`

**`docs/analysis/`**

- [30-YEAR GAP COVERAGE ANALYSIS](./docs/analysis/30_YEAR_GAP_COVERAGE.md) — `docs/analysis/30_YEAR_GAP_COVERAGE.md`
- [Agent Module Review (Post-K4, Pre-GUI)](./docs/analysis/AGENT_MODULE_REVIEW.md) — `docs/analysis/AGENT_MODULE_REVIEW.md`
- [K1-K3 PATTERN ANALYSIS REPORT](./docs/analysis/K1_2_3_PATTERN_ANALYSIS.md) — `docs/analysis/K1_2_3_PATTERN_ANALYSIS.md`
- [K1/K2 Autonomous Recovery Validation Results](./docs/analysis/K1_K2_VALIDATION_RESULTS.md) — `docs/analysis/K1_K2_VALIDATION_RESULTS.md`
- [K3 Autonomous Solving Validation Results](./docs/analysis/K3_VALIDATION_RESULTS.md) — `docs/analysis/K3_VALIDATION_RESULTS.md`
- [K4 Active Research State](./docs/analysis/K4_ACTIVE_RESEARCH.md) — `docs/analysis/K4_ACTIVE_RESEARCH.md`
- [K4 Capability Table](./docs/analysis/K4_CAPABILITY_TABLE.md) — `docs/analysis/K4_CAPABILITY_TABLE.md`
- [K4 Keystream Analysis — Confirmed Period-13 Window](./docs/analysis/K4_KEYSTREAM_ANALYSIS.md) — `docs/analysis/K4_KEYSTREAM_ANALYSIS.md`
- [K4 Negative Space](./docs/analysis/K4_NEGATIVE_SPACE.md) — `docs/analysis/K4_NEGATIVE_SPACE.md`

**`docs/archive/`**

- [2026 Completed Roadmap Phases & Done Tasks (Archive)](./docs/archive/2026-completed-roadmap-and-tasks.md) — `docs/archive/2026-completed-roadmap-and-tasks.md`
- [Comprehensive Structure Audit - October 26, 2025](./docs/archive/AUDIT_2025-10-26.md) — `docs/archive/AUDIT_2025-10-26.md`
- [Kryptos Repository Audit](./docs/archive/AUDIT_2026-05-24.md) — `docs/archive/AUDIT_2026-05-24.md`
- [src/ Audit — Kryptos Toolkit (2026-06-01)](./docs/archive/AUDIT_2026-06-01.md) — `docs/archive/AUDIT_2026-06-01.md`
- [Frontend design spec](./docs/archive/K4-FRONTEND.md) — `docs/archive/K4-FRONTEND.md`
- [K4 Theories: Composite Pipeline & Physical-Geometric Resolver Specification](./docs/archive/K4-T1.md) — `docs/archive/K4-T1.md`
- [K4 makeover](./docs/archive/K4-v2.md) — `docs/archive/K4-v2.md`
- [K4 Attack Landscape — 3D Fingerprint](./docs/archive/K4_ATTACK_LANDSCAPE.md) — `docs/archive/K4_ATTACK_LANDSCAPE.md`

**`docs/reference/`**

- [Agents Architecture](./docs/reference/AGENTS_ARCHITECTURE.md) — `docs/reference/AGENTS_ARCHITECTURE.md`
- [Kryptos Public API Reference](./docs/reference/API_REFERENCE.md) — `docs/reference/API_REFERENCE.md`
- [Autonomous Cryptanalysis System](./docs/reference/AUTONOMOUS_SYSTEM.md) — `docs/reference/AUTONOMOUS_SYSTEM.md`
- [Dashboard](./docs/reference/DASHBOARD.md) — `docs/reference/DASHBOARD.md`
- [Provenance and Search-Space Tracking](./docs/reference/PROVENANCE_SYSTEM_EXPLAINED.md) — `docs/reference/PROVENANCE_SYSTEM_EXPLAINED.md`

**`docs/sources/`**

- [The World Clock (Weltzeituhr) in Kryptos K4](./docs/sources/CLOCK.md) — `docs/sources/CLOCK.md`
- [Jim Sanborn — notes and research pointers](./docs/sources/SANBORN.md) — `docs/sources/SANBORN.md`
- [Sanborn: Statements on the Record](./docs/sources/SANBORN_QUOTES.md) — `docs/sources/SANBORN_QUOTES.md`

**`benchmarks/`**

- [Attack-sweep benchmarks](./benchmarks/README.md) — `benchmarks/README.md`

**`frontend/`**

- [Kryptos dashboard (frontend)](./frontend/README.md) — `frontend/README.md`

**`scripts/`**

- [Scripts Directory](./scripts/README.md) — `scripts/README.md`

**`scripts/lint/`**

- [Lint Tools](./scripts/lint/README.md) — `scripts/lint/README.md`

**`scripts/testing/`**

- [Testing Notes](./scripts/testing/README.md) — `scripts/testing/README.md`

**`tests/`**

- [Test Suite](./tests/README.md) — `tests/README.md`

<!-- docs-index:end -->

## Contributing and community

Shared policies live in [nitsuah/.github](https://github.com/nitsuah/.github):
[Contributing](https://github.com/nitsuah/.github/blob/main/CONTRIBUTING.md) ·
[Code of Conduct](https://github.com/nitsuah/.github/blob/main/CODE_OF_CONDUCT.md) ·
[Security](https://github.com/nitsuah/.github/blob/main/SECURITY.md)

## License

MIT. See `LICENSE`.
