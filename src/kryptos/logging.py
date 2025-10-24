"""Central logging setup helper.

Usage:
    from kryptos.logging import setup_logging
    setup_logging()

Ensures idempotent configuration; avoids duplicate handlers.
"""

from __future__ import annotations

import logging

_DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def setup_logging(level: int = logging.INFO, fmt: str = _DEFAULT_FORMAT, force: bool = False) -> None:
    """Configure root logging once.

    force=True will remove existing handlers. Otherwise existing configuration is preserved.
    """
    root = logging.getLogger()
    if root.handlers and not force:
        return
    if force:
        for h in list(root.handlers):
            root.removeHandler(h)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt))
    root.addHandler(handler)
    root.setLevel(level)


__all__ = ["setup_logging"]
