"""CLI entry package for kryptos.

Provides a minimal command-line interface; see `python -m kryptos.cli --help`.
"""

from __future__ import annotations

__all__ = ["main"]

from .main import main  # noqa: E402,F401
