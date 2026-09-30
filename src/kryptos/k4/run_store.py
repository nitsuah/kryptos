"""Best-effort Neon storage for crib-constraint suite runs.

The suite always writes ``K4_CRIB_CONSTRAINTS_NULL.json`` to the working directory. On a
host with an ephemeral disk (Render) that file disappears on redeploy, so when
``DATABASE_URL`` is set the summary is also stored in ``k4_constraint_runs`` and
``hypothesis_ledger.latest_run`` falls back to the newest row. Database errors are logged
and never fail a run.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def _enabled() -> bool:
    return bool(os.getenv("DATABASE_URL"))


def save_run(summary: dict[str, Any]) -> bool:
    """Store a suite summary; returns True if a row was written."""
    if not _enabled():
        return False
    try:
        from kryptos.db import get_conn

        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO k4_constraint_runs (summary) VALUES (%s::jsonb)", (json.dumps(summary, default=str),)
            )
        return True
    except Exception:  # noqa: BLE001 - storage must never break a run
        logger.exception("could not store crib-constraint run")
        return False


def load_latest() -> dict[str, Any] | None:
    """Newest stored suite summary, or None."""
    if not _enabled():
        return None
    try:
        from kryptos.db import get_conn

        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT summary FROM k4_constraint_runs ORDER BY created_at DESC LIMIT 1")
            row = cur.fetchone()
        if not row:
            return None
        return row[0] if isinstance(row[0], dict) else json.loads(row[0])
    except Exception:  # noqa: BLE001
        logger.exception("could not load latest crib-constraint run")
        return None


__all__ = ["load_latest", "save_run"]
