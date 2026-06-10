"""Turbovec-backed RAG over `artifacts/` (cipher/hypothesis search).

See AI_STACK_STRATEGY "Now" item #1: an embedded, in-process vector index
over the locally-generated `artifacts/` tree (search results, decisions,
hypotheses, logs) — no server/daemon, no migrations.
"""

from kryptos.rag.index import ArtifactIndex, SearchResult

__all__ = ["ArtifactIndex", "SearchResult"]
