# Kryptos dashboard (frontend)

Terminal-aesthetic React SPA over the kryptos FastAPI backend
(`src/kryptos/api/`). Consumes the dashboard endpoints documented in
`docs/reference/API_REFERENCE.md` (`/api/status`, `/api/runs`,
`/api/runs/{id}/candidates`, `/api/candidates`, `POST /api/decrypt`).

This first slice ships the **Ops Center** page (status, metric cards, top
candidates, campaign run history with drill-down, and an ad-hoc decrypt
panel). The K1–K3 animated decoder, Vault, Database admin, and the SSE
live-log tail from `docs/analysis/K4-FRONTEND.md` are planned follow-ups.

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
can serve it as static files in a later integration step.

## Stack

Vite + React 18 + TypeScript. No runtime UI framework — plain components
and the palette in `src/theme.css` (from the frontend design spec).
