"""FastAPI app: health check + turbovec RAG search + dashboard SPA."""

from __future__ import annotations

import logging
import os
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from kryptos.api.dashboard import create_dashboard_router
from kryptos.api.k4_attack_routes import create_k4_attack_router
from kryptos.api.log_stream import install_log_streaming, log_event_stream
from kryptos.api.vault_routes import create_vault_router
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


def create_app(index: ArtifactIndex | None = None) -> FastAPI:
    index = index if index is not None else ArtifactIndex()
    index.load()

    # Capture kryptos log records into the ring buffer the SSE tail streams.
    install_log_streaming()

    app = FastAPI(title="Kryptos API", version="0.1.0")
    app.include_router(create_dashboard_router())
    app.include_router(create_vault_router())
    app.include_router(create_k4_attack_router())

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/api/rag/status")
    def rag_status() -> dict:
        return index.status()

    @app.post("/api/rag/reindex")
    def rag_reindex() -> dict:
        return index.build()

    @app.get("/api/rag/search")
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
    ) -> StreamingResponse:
        stream = log_event_stream(request.is_disconnected, backlog=backlog, follow=follow)
        # X-Accel-Buffering disables proxy buffering so events flush immediately.
        headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
        return StreamingResponse(stream, media_type="text/event-stream", headers=headers)

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
