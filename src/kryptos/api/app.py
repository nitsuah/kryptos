"""FastAPI app: health check + turbovec RAG search over `artifacts/`."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, HTTPException, Query

from kryptos.rag.index import ArtifactIndex


def create_app(index: ArtifactIndex | None = None) -> FastAPI:
    index = index if index is not None else ArtifactIndex()
    index.load()

    app = FastAPI(title="Kryptos API", version="0.1.0")

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

    return app


app = create_app()
