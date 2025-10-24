"""Central logging setup helper.

Usage:
    from kryptos.logging import setup_logging
    log = setup_logging(logger_name="kryptos")

Provides idempotent logger configuration without touching root handlers.
"""

from __future__ import annotations

import logging

_HANDLER_MARKER = "_kryptos_handler"
_DEFAULT_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def setup_logging(
    level: int | str = "INFO",
    logger_name: str = "kryptos",
    fmt: str = _DEFAULT_FORMAT,
    propagate: bool = False,
    force: bool = False,
) -> logging.Logger:
    """Configure and return a named logger idempotently.

    If force=True existing kryptos handler is replaced.
    """
    logger = logging.getLogger(logger_name)
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    existing = [h for h in logger.handlers if getattr(h, _HANDLER_MARKER, False)]
    if existing and force:
        for h in existing:
            logger.removeHandler(h)
        existing = []
    if not existing:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt))
        setattr(handler, _HANDLER_MARKER, True)
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = propagate
    return logger


__all__ = ["setup_logging"]
