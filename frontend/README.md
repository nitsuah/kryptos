# Kryptos dashboard (frontend)

A single-page React app over the kryptos FastAPI backend (`src/kryptos/api/`), styled after the Ghost in the Shell
interfaces. It is one fixed-height screen: five modules sit on a ring, each laid out to fit the viewport, and only long
lists scroll inside their own panel. Switch with the dock, the ring dial, the side previews, `←`/`→`, or a swipe. The
active module is in the URL hash (`#ledger`).

| Code | Module | Main endpoints |
|------|--------|----------------|
| K4 | Ciphertext with cribs, ledger gauge, open fronts, and the Weltzeituhr drawing | `/api/k4/ledger` |
| LG | Ledger: every hypothesis family by tier, with detail | `/api/k4/ledger` |
| AT | Attacks: the P1–P22 queue, run controls, recent jobs | `/api/k4/attacks/frontier`, `POST /api/k4/attacks/run`, `/api/k4/attacks/jobs` |
| LB | Lab: K1–K3 decoder, ad-hoc decrypt, vault | `POST /api/decrypt`, `/api/vault/*` |
| SY | System: API and database, run history, live log, pivot status | `/api/status`, `/api/runs`, `/api/stream/logs`, `/api/k4/attacks/pivot-status` |

Design notes (layout, scaling rules, colours, when the CAUTION tag appears, accessibility):
[`docs/reference/DASHBOARD.md`](../docs/reference/DASHBOARD.md). Endpoint details:
[`docs/reference/API_REFERENCE.md`](../docs/reference/API_REFERENCE.md).

## Source layout

```text
src/
  App.tsx              shell: HUD, carousel stage, dock, keyboard/swipe/hash navigation
  shell/data.tsx       shared polling (status, ledger, attack registry, jobs)
  shell/deco.tsx       barcodes, glyph blocks, rings, ONLINE arc, CAUTION tag
  shell/nav.tsx        lets a module jump to another
  modules/registry.tsx the module list: code, title, preview numbers, alert rule
  modules/*.tsx        one file per module
  components/*.tsx     shared pieces (cipher matrix, World Clock, tier gauge, run panel, log tail, …)
  k4.ts                K4 ciphertext, crib positions, tier labels
  worldclock.ts        Weltzeituhr panels: UTC offsets and engraved city names
  theme.css            all styling; tokens at the top
```

To add a module, write the component under `modules/` and add an entry to `MODULES` in `modules/registry.tsx`. The
dock, dial, previews and hash routing pick it up.

## Develop

The backend and the Vite dev server run separately; Vite proxies `/api` and `/health` to `http://localhost:8000`
(see `vite.config.ts`).

```bash
# 1. backend (from the repo root), API on :8000
kryptos serve

# 2. frontend dev server on :5173
cd frontend && npm install && npm run dev
```

Or in Docker:

```bash
docker run --rm -it -p 5173:5173 \
  -v "$(pwd)/frontend:/app" -w /app node:22-alpine \
  sh -c "npm install && npm run dev -- --host"
```

## Build and typecheck

```bash
cd frontend && npm ci && npm run build    # tsc + vite build → frontend/dist/
```

CI runs the same command (the `frontend` job in `.github/workflows/ci-fast.yml`).

`frontend/dist/` is gitignored. FastAPI serves it automatically: `create_app()` mounts it at `/` when a build is
present, so the API and dashboard ship from one container. The dist location is resolved from
`KRYPTOS_FRONTEND_DIST`, then `<repo>/frontend/dist`, then `<cwd>/frontend/dist`. The root `Dockerfile` builds the SPA in
a `node:22-alpine` stage and sets `KRYPTOS_FRONTEND_DIST=/app/frontend/dist`.

## Deploy on Netlify

The root `netlify.toml` builds from `frontend/` and publishes `frontend/dist/`. Netlify doesn't run the FastAPI process,
so deploy the backend separately (Render, see `render.yaml`) and set `VITE_API_BASE_URL` to its public origin. Without
the variable the dashboard calls `/api/*` on its own origin, which is right for the single-container deployment.

## Stack

Vite, React 18 and TypeScript, with no UI framework and no runtime dependencies beyond React. Fonts (Barlow Condensed,
Share Tech Mono) load from Google Fonts with system fallbacks. Light and dark chassis follow the system setting; the
◐ button in the header overrides it (stored in `localStorage`).
