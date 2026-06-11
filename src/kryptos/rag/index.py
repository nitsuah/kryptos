"""Turbovec-backed vector index over `artifacts/` chunks."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from kryptos.paths import get_artifacts_root, get_turbovec_index_dir
from kryptos.rag.chunking import iter_artifact_chunks
from kryptos.rag.embeddings import embed_query, embed_texts

INDEX_NAME = "kryptos-artifacts"
EMBED_BATCH_SIZE = 64
BIT_WIDTH = 4


@dataclass(frozen=True)
class SearchResult:
    score: float
    path: str
    chunk_index: int
    text: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class ArtifactIndex:
    """Turbovec `IdMapIndex` over text chunks from `artifacts/`, with a JSON sidecar
    mapping vector ids back to their source file/chunk/text."""

    def __init__(self, index_dir: Path | None = None):
        self._index_dir = index_dir or get_turbovec_index_dir()
        self._index_path = self._index_dir / f"{INDEX_NAME}.tvim"
        self._meta_path = self._index_dir / f"{INDEX_NAME}.meta.json"
        self._index = None
        self._meta: dict | None = None

    @property
    def is_loaded(self) -> bool:
        return self._meta is not None

    def status(self) -> dict:
        meta = self._meta
        if meta is None and self._meta_path.exists():
            meta = json.loads(self._meta_path.read_text(encoding="utf-8"))
        if meta is None:
            return {"indexed": False}
        return {
            "indexed": True,
            "chunk_count": len(meta["chunks"]),
            "model": meta["model"],
            "built_at": meta["built_at"],
            "index_path": str(self._index_path),
        }

    def load(self) -> bool:
        """Load a previously-built index + sidecar from disk, if present."""
        if not self._meta_path.exists():
            return False
        meta = json.loads(self._meta_path.read_text(encoding="utf-8"))
        if meta["chunks"] and self._index_path.exists():
            from turbovec import IdMapIndex

            self._index = IdMapIndex.load(str(self._index_path))
        else:
            self._index = None
        self._meta = meta
        return True

    def build(self, artifacts_root: Path | None = None) -> dict:
        """Rebuild the index from scratch over *artifacts_root* (default `artifacts/`)."""
        artifacts_root = artifacts_root or get_artifacts_root()
        chunks = list(iter_artifact_chunks(artifacts_root))

        meta: dict = {"model": "", "dim": 0, "built_at": _now(), "chunks": {}}
        index = None

        if chunks:
            from turbovec import IdMapIndex

            from kryptos.rag.embeddings import DEFAULT_MODEL_NAME

            vector_batches = []
            for start in range(0, len(chunks), EMBED_BATCH_SIZE):
                end = start + EMBED_BATCH_SIZE
                vector_batches.append(embed_texts([c.text for c in chunks[start:end]]))
            vectors = np.vstack(vector_batches)

            index = IdMapIndex(dim=vectors.shape[1], bit_width=BIT_WIDTH)
            ids = np.arange(len(chunks), dtype=np.uint64)
            index.add_with_ids(vectors, ids)

            meta["model"] = DEFAULT_MODEL_NAME
            meta["dim"] = int(vectors.shape[1])
            meta["chunks"] = {str(i): asdict(c) for i, c in enumerate(chunks)}

        self._index_dir.mkdir(parents=True, exist_ok=True)
        if index is not None:
            index.write(str(self._index_path))
        elif self._index_path.exists():
            self._index_path.unlink()
        self._meta_path.write_text(json.dumps(meta), encoding="utf-8")

        self._index = index
        self._meta = meta
        return self.status()

    def search(self, query: str, k: int = 10) -> list[SearchResult]:
        if self._meta is None:
            raise RuntimeError("Index not built/loaded. Call build() or load() first.")
        if self._index is None or not self._meta["chunks"]:
            return []

        query_vec = embed_query(query, self._meta["model"]).reshape(1, -1)
        scores, ids = self._index.search(query_vec, k=min(k, len(self._meta["chunks"])))

        results = []
        for score, chunk_id in zip(scores[0], ids[0], strict=True):
            chunk_meta = self._meta["chunks"][str(int(chunk_id))]
            results.append(
                SearchResult(
                    score=float(score),
                    path=chunk_meta["path"],
                    chunk_index=chunk_meta["chunk_index"],
                    text=chunk_meta["text"],
                ),
            )
        return results
