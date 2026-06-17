# Kryptos dashboard (frontend)

Terminal-aesthetic React SPA over the kryptos FastAPI backend
(`src/kryptos/api/`). Consumes the dashboard endpoints documented in
`docs/reference/API_REFERENCE.md` (`/api/status`, `/api/runs`,
`/api/runs/{id}/candidates`, `/api/candidates`, `POST /api/decrypt`).

Shipped pages: **Ops Center** (status, metric cards, top candidates,
campaign run history with drill-down, ad-hoc decrypt panel), **Decode**
(K1–K3 animated decoder), **Database** (Neon connection + per-table row
counts), and **Vault** (seal a secret under the keyed-alphabet Vigenère,
share the opaque token, unseal once with the key, and check status). The
SSE live-log tail from `docs/analysis/K4-FRONTEND.md` is a planned follow-up.

## Develop (Docker)

The backend and the Vite dev server run separately; Vite proxies `/api`
and `/health` to `http://localhost:8000` (see `vite.config.ts`).

```bash
# 1. backend (from repo root) — serves the API on :8000
kryptos serve            # or: docker run ... kryptos serve

# 2. frontend dev server on :5173, proxying to the backend
docker run --rm -it -p 5173:5173 \
  -v "$(pwd)/frontend:/app" -w /app node:22-alpine \
  sh -c "npm install && npm run dev -- --host"
```

## Build / typecheck (Docker)

```bash
docker run --rm -v "$(pwd)/frontend:/app" -w /app node:22-alpine \
  sh -c "npm ci && npm run build"
```

The production bundle is emitted to `frontend/dist/` (gitignored). FastAPI
serves it automatically: `create_app()` mounts `frontend/dist` at `/`
(via `StaticFiles(..., html=True)`) when a build is present, so the API
and SPA ship from a single container. The dist location is discovered from
`KRYPTOS_FRONTEND_DIST`, then `<repo>/frontend/dist`, then
`<cwd>/frontend/dist`. The root `Dockerfile` builds the SPA in a
`node:22-alpine` stage and copies it into the runtime image with
`KRYPTOS_FRONTEND_DIST=/app/frontend/dist` set.

## Stack

Vite + React 18 + TypeScript. No runtime UI framework — plain components
and the palette in `src/theme.css` (from the frontend design spec).
