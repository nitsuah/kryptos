"""FastAPI app: health check + turbovec RAG search + dashboard SPA."""

from __future__ import annotations

import json
import logging
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from kryptos.api.dashboard import create_dashboard_router
from kryptos.api.k4_attack_routes import create_k4_attack_router
from kryptos.api.ledger_routes import create_ledger_router
from kryptos.api.log_stream import (
    install_log_streaming,
    log_event_stream,
    log_token,
    public_log_mode,
    token_matches,
)
from kryptos.api.security import rate_limit, require_api_token
from kryptos.api.vault_routes import create_vault_router
from kryptos.k4.world_clock_hypothesis import analyze_world_clock_hypothesis
from kryptos.rag.index import ArtifactIndex

logger = logging.getLogger(__name__)


def _resolve_frontend_dist() -> Path | None:
    """Locate the built frontend bundle, or None if it isn't present.

    Order: KRYPTOS_FRONTEND_DIST env override, then <repo_root>/frontend/dist,
    then <cwd>/frontend/dist. A dist counts only if it contains index.html.
    """
    candidates: list[Path] = []
    override = os.environ.get("KRYPTOS_FRONTEND_DIST")
    if override:
        candidates.append(Path(override))
    try:
        from kryptos.paths import get_repo_root

        candidates.append(get_repo_root() / "frontend" / "dist")
    except Exception:  # noqa: BLE001 - repo-root discovery is best-effort
        pass
    candidates.append(Path.cwd() / "frontend" / "dist")

    for c in candidates:
        if c.is_dir() and (c / "index.html").is_file():
            return c
    return None


_STDERR_MARKER = "_kryptos_stderr_handler"


def _ensure_stderr_logging() -> None:
    """Send kryptos records (with tracebacks) to stderr so they land in the host's logs.

    Under uvicorn the root logger has no handler, so without this the only copy of a
    kryptos traceback would be the in-memory SSE buffer. Idempotent.
    """
    logger = logging.getLogger("kryptos")
    if any(getattr(h, _STDERR_MARKER, False) for h in logger.handlers):
        return
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    handler.setLevel(logging.INFO)
    setattr(handler, _STDERR_MARKER, True)
    logger.addHandler(handler)


def auto_migrate() -> list[str] | None:
    """Apply the idempotent Neon/Postgres schema at boot.

    Runs when ``DATABASE_URL`` is set unless ``KRYPTOS_DB_AUTO_MIGRATE=0``. Every
    statement is ``CREATE ... IF NOT EXISTS``, so this only ever adds missing tables
    and indexes. Failures are logged and never stop the server (the API degrades the
    same way it does with no database).
    """
    if not os.getenv("DATABASE_URL"):
        return None
    if (os.getenv("KRYPTOS_DB_AUTO_MIGRATE") or "1").strip().lower() in {"0", "false", "no", "off"}:
        logger.info("DB auto-migrate disabled (KRYPTOS_DB_AUTO_MIGRATE=0)")
        return None
    try:
        from kryptos.db_schema import init_schema

        tables = init_schema()
    except Exception:  # noqa: BLE001 - boot must survive an unreachable DB
        logger.exception("DB auto-migrate failed; continuing without schema changes")
        return None
    logger.info("DB auto-migrate ensured %d tables: %s", len(tables), ", ".join(tables))
    return tables


@asynccontextmanager
async def _lifespan(_app: FastAPI) -> AsyncIterator[None]:
    _ensure_stderr_logging()
    auto_migrate()
    yield


def _presented_log_token(request: Request, token: str | None) -> str | None:
    header = request.headers.get("x-kryptos-log-token")
    if header:
        return header.strip()
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return token.strip() if token else None


def create_app(index: ArtifactIndex | None = None) -> FastAPI:
    index = index if index is not None else ArtifactIndex()
    index.load()

    # Capture kryptos log records into the ring buffer the SSE tail streams.
    install_log_streaming()

    app = FastAPI(title="Kryptos API", version="0.1.0", lifespan=_lifespan)

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        # Full details go to the server log only; clients get a generic message.
        logger.error("Unhandled error on %s %s", request.method, request.url.path, exc_info=exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    # CORS: allow the Cloudflare Pages–hosted SPA to call this backend cross-origin.
    # Configure via KRYPTOS_CORS_ORIGINS (comma-separated); defaults to the
    # production custom domain, Pages preview host, and legacy Netlify origin.
    # "*" disables origin checks (dev only).
    cors_origins = os.environ.get(
        "KRYPTOS_CORS_ORIGINS",
        "https://kryptos.nitsuah.io,https://kryptos-k4.pages.dev,https://kryptos-k4.netlify.app",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in cors_origins.split(",") if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Read-only demo data (status, runs, candidates, ledger, frontier list, world-clock
    # diagnostic) stays public but rate limited; token-protected routes add their own checks.
    public_limit = [Depends(rate_limit)]
    app.include_router(create_dashboard_router(), dependencies=public_limit)
    app.include_router(create_vault_router())
    app.include_router(create_k4_attack_router(), dependencies=public_limit)
    app.include_router(create_ledger_router(), dependencies=public_limit)

    @app.get("/api/k4/world-clock/hypothesis", dependencies=public_limit)
    def world_clock_hypothesis() -> dict:
        """Return the deterministic six-segment World Clock diagnostic."""
        return analyze_world_clock_hypothesis()

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/api/rag/status")
    def rag_status() -> dict:
        return index.status()

    @app.post("/api/rag/reindex", dependencies=[Depends(require_api_token)])
    def rag_reindex() -> dict:
        return index.build()

    @app.get("/api/rag/search", dependencies=[Depends(rate_limit)])
    def rag_search(q: str = Query(..., min_length=1), k: int = Query(10, ge=1, le=50)) -> dict:
        if not index.is_loaded:
            raise HTTPException(
                status_code=409,
                detail="Index not built yet. POST /api/rag/reindex first.",
            )
        results = index.search(q, k=k)
        return {"query": q, "results": [asdict(r) for r in results]}

    @app.get("/api/stream/logs")
    async def stream_logs(
        request: Request,
        backlog: int = Query(200, ge=0, le=1000),
        follow: bool = Query(True),
        token: str | None = Query(None, description="Admin log token (EventSource cannot send headers)"),
    ) -> StreamingResponse:
        # Anonymous visitors get the redacted public view (one line per record, no
        # tracebacks, credentials masked). KRYPTOS_LOG_TOKEN unlocks the full view.
        presented = _presented_log_token(request, token)
        if presented is not None and log_token() is not None and not token_matches(presented):
            raise HTTPException(status_code=401, detail="Invalid log token")
        full = token_matches(presented)
        if not full and public_log_mode() == "off":
            raise HTTPException(status_code=401, detail="Log stream requires a token")
        view = "full" if full else "public"

        async def _frames() -> AsyncIterator[str]:
            # Named event: plain onmessage listeners ignore it; the dashboard uses it
            # to label the view.
            yield f"event: meta\ndata: {json.dumps({'view': view})}\n\n"
            async for frame in log_event_stream(
                request.is_disconnected, backlog=backlog, follow=follow, public=not full
            ):
                yield frame

        # X-Accel-Buffering disables proxy buffering so events flush immediately.
        headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "X-Kryptos-Log-View": view}
        return StreamingResponse(_frames(), media_type="text/event-stream", headers=headers)

    # Mount the built SPA LAST so API routes (/api/*, /health) always win.
    # html=True serves index.html for unknown paths (client-side routing).
    dist = _resolve_frontend_dist()
    if dist is not None:
        app.mount("/", StaticFiles(directory=str(dist), html=True), name="spa")
        logger.info("Serving frontend SPA from %s", dist)
    else:
        logger.info("No frontend dist found; serving API only")

    return app


app = create_app()
