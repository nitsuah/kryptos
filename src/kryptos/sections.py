"""Unified section access helpers.

This module provides a stable mapping from symbolic section names ("K1".."K4")
to their decrypt helpers. It allows higher-level orchestration / CLI code to
iterate sections without importing each package manually.

K4: For K4 we will expose richer pipeline search capabilities; for now we map
to the current best-effort composite decrypt (placeholder returning string or
raising NotImplementedError if advanced search not yet wired here).
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from . import k1, k2, k3

try:
    from .k4 import decrypt_best  # type: ignore
except ImportError:
    decrypt_best = None  # type: ignore


@runtime_checkable
class SectionCallable(Protocol):
    def __call__(self, *args, **kwargs) -> Any: ...  # noqa: D401,E701 (broad for heterogeneous returns)


SectionDecrypt = SectionCallable


def _k4_decrypt_placeholder(*_args, **_kwargs) -> str:
    raise NotImplementedError("K4 decrypt pipeline not yet exposed via sections API")


SECTIONS: dict[str, SectionDecrypt] = {
    "K1": k1.decrypt,
    "K2": k2.decrypt,
    "K3": k3.decrypt,
    "K4": decrypt_best if callable(decrypt_best) else _k4_decrypt_placeholder,
}

__all__ = ["SECTIONS"]
