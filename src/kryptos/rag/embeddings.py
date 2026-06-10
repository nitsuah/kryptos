"""Sentence-transformer embeddings for the turbovec RAG index."""

from __future__ import annotations

from functools import lru_cache

import numpy as np

DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _load_model(model_name: str):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def embed_texts(texts: list[str], model_name: str = DEFAULT_MODEL_NAME) -> np.ndarray:
    model = _load_model(model_name)
    vectors = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return np.asarray(vectors, dtype=np.float32)


def embed_query(text: str, model_name: str = DEFAULT_MODEL_NAME) -> np.ndarray:
    return embed_texts([text], model_name)[0]
