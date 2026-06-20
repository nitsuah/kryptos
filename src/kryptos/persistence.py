"""Best-effort persistence of campaign runs and candidates to Neon/Postgres.

The ``campaign_runs`` and ``candidates`` tables (see ``kryptos.db_schema``)
exist but, until now, nothing populated them — candidate output lived only in
the JSON/CSV artifacts under ``artifacts/``. This module mirrors that output
into Neon when ``DATABASE_URL`` is configured, so the API/dashboard layer has
queryable run history.

Every function here is best-effort: a missing ``DATABASE_URL``, an absent
``psycopg2``, or any database error is swallowed (logged at WARNING) and the
caller's file-based flow is unaffected. Persistence is never on the critical
path of a cryptanalysis run.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from collections.abc import Sequence
from typing import Any

logger = logging.getLogger(__name__)


def _key_hash(key: Sequence[Sequence[int]]) -> str:
    flat = ",".join(str(v) for row in key for v in row)
    return hashlib.sha1(flat.encode("utf-8")).hexdigest()[:16]


def db_enabled() -> bool:
    """True when a DATABASE_URL is configured (DB persistence is possible)."""
    return bool(os.getenv("DATABASE_URL"))


def persist_campaign_candidates(
    stage: str,
    cipher_label: str,
    ciphertext: str,
    candidates: list[dict[str, Any]],
    limit: int = 50,
    lineage: list[str] | None = None,
    status: str = "complete",
    metadata: dict[str, Any] | None = None,
) -> int | None:
    """Record a campaign run and its top candidates in Neon.

    Creates one ``campaign_runs`` row and inserts up to ``limit`` ranked
    ``candidates`` rows referencing it. Returns the new ``campaign_runs.id``,
    or ``None`` if persistence was skipped (no DATABASE_URL) or failed.

    Args mirror ``kryptos.k4.reporting.write_candidates_json`` so call sites
    can persist the same data they already write to disk.
    """
    if not db_enabled():
        return None

    try:
        from kryptos.db import get_conn
    except ImportError as exc:  # pragma: no cover - defensive
        logger.warning("DB persistence unavailable (%s); skipping", exc)
        return None

    ranked = sorted(candidates, key=lambda c: c.get("score", 0.0), reverse=True)[:limit]

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO campaign_runs (label, stage, cipher_label, ciphertext, status, metadata)"
                    " VALUES (%s, %s, %s, %s, %s, %s::jsonb) RETURNING id",
                    (
                        cipher_label,
                        stage,
                        cipher_label,
                        ciphertext[:500],
                        status,
                        json.dumps(metadata or {}),
                    ),
                )
                run_id = cur.fetchone()[0]

                for rank, cand in enumerate(ranked, start=1):
                    key = cand.get("key")
                    cur.execute(
                        "INSERT INTO candidates"
                        " (campaign_run_id, rank, score, source, key, key_hash, text, metrics, origin_stage, lineage)"
                        " VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s::jsonb, %s, %s::jsonb)",
                        (
                            run_id,
                            rank,
                            cand.get("score"),
                            cand.get("source"),
                            json.dumps(key) if key is not None else None,
                            _key_hash(key) if key else None,
                            cand.get("text", ""),
                            json.dumps(cand.get("metrics", {})),
                            stage,
                            json.dumps(cand.get("lineage") or lineage),
                        ),
                    )
        logger.info("Persisted campaign run %s with %d candidates to Neon", run_id, len(ranked))
        return int(run_id)
    except Exception as exc:  # noqa: BLE001 - persistence must never break a run
        logger.warning("Failed to persist campaign candidates to DB (%s); file artifacts unaffected", exc)
        return None


def fetch_recent_runs(limit: int = 20) -> list[dict[str, Any]]:
    """Return recent campaign runs (newest first). Empty list if DB disabled."""
    if not db_enabled():
        return []
    try:
        from kryptos.db import get_conn

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, label, stage, cipher_label, status, started_at, finished_at"
                    " FROM campaign_runs ORDER BY id DESC LIMIT %s",
                    (limit,),
                )
                rows = cur.fetchall()
        cols = ["id", "label", "stage", "cipher_label", "status", "started_at", "finished_at"]
        return [dict(zip(cols, row)) for row in rows]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to fetch campaign runs (%s)", exc)
        return []


def fetch_run_candidates(run_id: int, limit: int = 50) -> list[dict[str, Any]]:
    """Return a run's candidates ordered by rank. Empty list if DB disabled."""
    if not db_enabled():
        return []
    try:
        from kryptos.db import get_conn

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT rank, score, source, key, key_hash, text, metrics, origin_stage, lineage"
                    " FROM candidates WHERE campaign_run_id = %s ORDER BY rank LIMIT %s",
                    (run_id, limit),
                )
                rows = cur.fetchall()
        cols = ["rank", "score", "source", "key", "key_hash", "text", "metrics", "origin_stage", "lineage"]
        return [dict(zip(cols, row)) for row in rows]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to fetch candidates for run %s (%s)", run_id, exc)
        return []


def fetch_top_candidates(limit: int = 20) -> list[dict[str, Any]]:
    """Return the highest-scoring candidates across all runs. Empty if DB off."""
    if not db_enabled():
        return []
    try:
        from kryptos.db import get_conn

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT campaign_run_id, rank, score, source, key_hash, text, origin_stage"
                    " FROM candidates WHERE score IS NOT NULL ORDER BY score DESC LIMIT %s",
                    (limit,),
                )
                rows = cur.fetchall()
        cols = ["campaign_run_id", "rank", "score", "source", "key_hash", "text", "origin_stage"]
        return [dict(zip(cols, row)) for row in rows]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to fetch top candidates (%s)", exc)
        return []


_STRATEGY_CATEGORIES = ("successful", "failed", "lesson")


def persist_strategy(
    category: str,
    description: str,
    attack_type: str | None = None,
    confidence: float | None = None,
    metadata: dict[str, Any] | None = None,
) -> int | None:
    """Record one accumulated-strategy entry in the ``strategy_kb`` table.

    ``category`` must be one of ``successful``, ``failed``, or ``lesson`` (the
    table's CHECK constraint). Returns the new ``strategy_kb.id``, or ``None``
    if persistence was skipped (no DATABASE_URL) or failed — callers keep their
    own JSONL/in-memory fallback, so a missing DB never loses the learning.
    """
    if category not in _STRATEGY_CATEGORIES:
        raise ValueError(f"category must be one of {_STRATEGY_CATEGORIES}, got {category!r}")
    if not db_enabled():
        return None
    try:
        from kryptos.db import get_conn
    except ImportError as exc:  # pragma: no cover - defensive
        logger.warning("DB persistence unavailable (%s); skipping", exc)
        return None

    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO strategy_kb (category, description, attack_type, confidence, metadata)"
                    " VALUES (%s, %s, %s, %s, %s::jsonb) RETURNING id",
                    (category, description, attack_type, confidence, json.dumps(metadata or {})),
                )
                strategy_id = cur.fetchone()[0]
        logger.info("Persisted %s strategy %s to strategy_kb", category, strategy_id)
        return int(strategy_id)
    except Exception as exc:  # noqa: BLE001 - persistence must never break a run
        logger.warning("Failed to persist strategy to DB (%s); caller fallback unaffected", exc)
        return None


def fetch_strategy_kb(limit: int = 200) -> list[dict[str, Any]]:
    """Return accumulated ``strategy_kb`` entries (newest first). Empty if DB off."""
    if not db_enabled():
        return []
    try:
        from kryptos.db import get_conn

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, category, description, attack_type, confidence, metadata, created_at"
                    " FROM strategy_kb ORDER BY id DESC LIMIT %s",
                    (limit,),
                )
                rows = cur.fetchall()
        cols = ["id", "category", "description", "attack_type", "confidence", "metadata", "created_at"]
        return [dict(zip(cols, row)) for row in rows]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to fetch strategy_kb (%s)", exc)
        return []


def table_counts() -> dict[str, int]:
    """Return row counts for the kryptos tables. Empty dict if DB disabled."""
    if not db_enabled():
        return {}
    tables = ["campaign_runs", "candidates", "strategy_kb", "ops_decisions", "discovered_cribs"]
    try:
        from kryptos.db import get_conn

        counts: dict[str, int] = {}
        with get_conn() as conn:
            with conn.cursor() as cur:
                for table in tables:
                    # Table names are a fixed internal allowlist, not user input.
                    cur.execute(f"SELECT count(*) FROM {table}")  # noqa: S608
                    counts[table] = int(cur.fetchone()[0])
        return counts
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to fetch table counts (%s)", exc)
        return {}


__all__ = [
    "db_enabled",
    "persist_campaign_candidates",
    "persist_strategy",
    "fetch_recent_runs",
    "fetch_run_candidates",
    "fetch_top_candidates",
    "fetch_strategy_kb",
    "table_counts",
]
