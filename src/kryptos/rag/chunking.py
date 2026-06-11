"""Walk `artifacts/` and split JSON/Markdown files into text chunks for embedding."""

from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

INDEXABLE_SUFFIXES = {".json", ".md"}
MAX_FILE_BYTES = 256_000
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100


@dataclass(frozen=True)
class ArtifactChunk:
    path: str
    chunk_index: int
    text: str


def _file_text(path: Path) -> str | None:
    if path.suffix == ".md":
        return path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
        return json.dumps(data, indent=2, ensure_ascii=False)
    return None


def _split_chunks(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> Iterator[str]:
    text = text.strip()
    if not text:
        return
    step = size - overlap
    for start in range(0, len(text), step):
        end = start + size
        chunk = text[start:end].strip()
        if chunk:
            yield chunk
        if end >= len(text):
            break


def iter_artifact_chunks(artifacts_root: Path) -> Iterator[ArtifactChunk]:
    """Yield text chunks for every indexable file under *artifacts_root*."""
    if not artifacts_root.is_dir():
        return
    for path in sorted(artifacts_root.rglob("*")):
        if not path.is_file() or path.suffix not in INDEXABLE_SUFFIXES:
            continue
        if path.stat().st_size > MAX_FILE_BYTES:
            continue
        text = _file_text(path)
        if not text:
            continue
        rel = path.relative_to(artifacts_root).as_posix()
        for chunk_index, chunk in enumerate(_split_chunks(text)):
            yield ArtifactChunk(path=rel, chunk_index=chunk_index, text=chunk)
