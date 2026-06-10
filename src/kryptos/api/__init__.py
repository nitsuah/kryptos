"""Minimal FastAPI app exposing turbovec RAG search over `artifacts/`.

Run with: `kryptos serve` (see `kryptos.cli.main.cmd_serve`).
"""

from kryptos.api.app import create_app

__all__ = ["create_app"]
