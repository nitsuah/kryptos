"""In-memory job registry for K4 frontier attack background jobs.

Holds the status model for a background attack run (queued/running/complete/
error/eureka, progress, top candidates, summary) and the thread-safe store
backing it. Survives for the lifetime of the server process only.
"""

from __future__ import annotations

import threading
import uuid
from typing import Any

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
        }
    return job_id


def update_job(job_id: str, **kwargs: Any) -> None:
    """Merge `kwargs` into the job's fields; a no-op if the job is unknown."""
    with _JOBS_LOCK:
        if job_id in _JOBS:
            _JOBS[job_id].update(kwargs)


def get_job(job_id: str) -> dict[str, Any] | None:
    """Return a snapshot copy of the job's fields, or None if unknown."""
    with _JOBS_LOCK:
        return dict(_JOBS[job_id]) if job_id in _JOBS else None
