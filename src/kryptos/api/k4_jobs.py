"""In-memory job registry for K4 frontier attack background jobs.

Holds the status model for a background attack run (queued/running/complete/
error/eureka, progress, top candidates, summary) and the thread-safe store
backing it. Jobs live in memory; when ``DATABASE_URL`` is set, finished jobs
(complete / error / eureka) are also written to the ``k4_attack_jobs`` table so
their results survive a restart, and ``get_job`` / ``list_jobs`` fall back to it.
Persistence is best-effort: a database error is logged and never fails a job.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)
_TERMINAL = {"complete", "error", "eureka"}

_JOBS: dict[str, dict[str, Any]] = {}
_JOBS_LOCK = threading.Lock()


def new_job(attack_id: str) -> str:
    """Register a new job in `queued` status and return its id."""
    job_id = str(uuid.uuid4())
    with _JOBS_LOCK:
        _JOBS[job_id] = {
            "job_id": job_id,
            "attack_id": attack_id,
            "status": "queued",
            "progress_pct": 0,
            "clock_time": None,
            "total_candidates": 0,
            "top_candidates": [],
            "summary": None,
            "error": None,
            "created_at": _now(),
            "updated_at": _now(),
        }
    return job_id


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def update_job(job_id: str, **kwargs: Any) -> None:
    """Merge `kwargs` into the job's fields; a no-op if the job is unknown."""
    snapshot = None
    with _JOBS_LOCK:
        if job_id in _JOBS:
            _JOBS[job_id].update(kwargs, updated_at=_now())
            if kwargs.get("status") in _TERMINAL:
                snapshot = dict(_JOBS[job_id])
    if snapshot is not None:
        _persist(snapshot)


def get_job(job_id: str) -> dict[str, Any] | None:
    """Return a snapshot copy of the job's fields, or None if unknown."""
    with _JOBS_LOCK:
        if job_id in _JOBS:
            return dict(_JOBS[job_id])
    return _load(job_id)


def list_jobs(limit: int = 20) -> list[dict[str, Any]]:
    """Recent jobs, newest first: in-memory jobs plus persisted ones not already in memory."""
    with _JOBS_LOCK:
        jobs = {j["job_id"]: dict(j) for j in _JOBS.values()}
    for j in _load_recent(limit):
        jobs.setdefault(j["job_id"], j)
    return sorted(jobs.values(), key=lambda j: j.get("created_at") or "", reverse=True)[:limit]


# ── Persistence (Neon) ──────────────────────────────────────────────────────

_COLUMNS = ("job_id", "attack_id", "status", "progress_pct", "total_candidates", "summary", "error",
            "created_at", "updated_at")  # fmt: skip


def _db_enabled() -> bool:
    return bool(os.getenv("DATABASE_URL"))


def _persist(job: dict[str, Any]) -> None:
    if not _db_enabled():
        return
    try:
        from kryptos.db import get_conn

        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO k4_attack_jobs (job_id, attack_id, status, progress_pct, total_candidates,
                                            summary, error, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s)
                ON CONFLICT (job_id) DO UPDATE SET status = EXCLUDED.status,
                    progress_pct = EXCLUDED.progress_pct, total_candidates = EXCLUDED.total_candidates,
                    summary = EXCLUDED.summary, error = EXCLUDED.error, updated_at = EXCLUDED.updated_at
                """,
                (
                    job["job_id"], job["attack_id"], job["status"], job.get("progress_pct") or 0,
                    job.get("total_candidates") or 0, json.dumps(job.get("summary"), default=str),
                    job.get("error"), job.get("created_at"), job.get("updated_at"),
                ),
            )  # fmt: skip
    except Exception:  # noqa: BLE001 - persistence must never break a job
        logger.exception("could not persist K4 job %s", job.get("job_id"))


def _row_to_job(row: tuple) -> dict[str, Any]:
    job = dict(zip(_COLUMNS, row, strict=True))
    job["job_id"] = str(job["job_id"])
    for k in ("created_at", "updated_at"):
        if job.get(k) is not None and not isinstance(job[k], str):
            job[k] = job[k].isoformat()
    if isinstance(job.get("summary"), str):
        job["summary"] = json.loads(job["summary"])
    job.setdefault("clock_time", None)
    job["top_candidates"] = []
    return job


def _load(job_id: str) -> dict[str, Any] | None:
    if not _db_enabled():
        return None
    try:
        from kryptos.db import get_conn

        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(_COLUMNS)} FROM k4_attack_jobs WHERE job_id = %s", (job_id,))
            row = cur.fetchone()
        return _row_to_job(row) if row else None
    except Exception:  # noqa: BLE001
        logger.exception("could not load K4 job %s", job_id)
        return None


def _load_recent(limit: int) -> list[dict[str, Any]]:
    if not _db_enabled():
        return []
    try:
        from kryptos.db import get_conn

        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(f"SELECT {', '.join(_COLUMNS)} FROM k4_attack_jobs ORDER BY created_at DESC LIMIT %s", (limit,))
            return [_row_to_job(r) for r in cur.fetchall()]
    except Exception:  # noqa: BLE001
        logger.exception("could not list K4 jobs")
        return []
