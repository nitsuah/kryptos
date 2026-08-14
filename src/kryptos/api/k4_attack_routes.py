"""API routes for K4 frontier attack execution.

POST /api/k4/attacks/run         — start a background attack job
GET  /api/k4/attacks/jobs/{id}   — poll job status + top candidates
GET  /api/k4/attacks/frontier    — list P1-P7 frontier vectors
"""

from __future__ import annotations

import logging
import threading
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory job registry (survives for the lifetime of the server process)
# ---------------------------------------------------------------------------
_JOBS: dict[str, dict[str, Any]] = {}
_JOBS_LOCK = threading.Lock()


def _new_job(attack_id: str) -> str:
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


def _update_job(job_id: str, **kwargs: Any) -> None:
    with _JOBS_LOCK:
        if job_id in _JOBS:
            _JOBS[job_id].update(kwargs)


def _get_job(job_id: str) -> dict[str, Any] | None:
    with _JOBS_LOCK:
        return dict(_JOBS[job_id]) if job_id in _JOBS else None


# ---------------------------------------------------------------------------
# P1-P7 frontier vector metadata
# ---------------------------------------------------------------------------
FRONTIER_VECTORS = [
    {
        "id": "p1_three_layer",
        "priority": 1,
        "name": "P1 — 3-Layer Composite",
        "status": "Active",
        "description": (
            "keyed-alphabet substitution → clock-Vigenère → columnar transposition. "
            "CIA timestamp states (13:00 EST, 19:00 Berlin) tested first, then full 24-state sweep. "
            "~51,840 combos at 6-col grid across 3 alphabets."
        ),
        "layer_count": 3,
        "combo_estimate": 51840,
        "runnable": True,
    },
    {
        "id": "p2_shadow_masking",
        "priority": 2,
        "name": "P2 — Shadow / Null Masking",
        "status": "Active",
        "description": (
            "12 null-character masking variants applied as Layer 0 before the P1 chain. "
            "Removes or repositions placeholder characters before Vigenère/transposition."
        ),
        "layer_count": 4,
        "combo_estimate": 622080,
        "runnable": False,
    },
    {
        "id": "p3_k2_coord_clock",
        "priority": 3,
        "name": "P3 — K2 Coordinate Clock Timestamps",
        "status": "Active",
        "description": (
            "K2 plaintext contains WGS-84 coordinates (38°57'6.5\"N, 77°8'44\"W). "
            "Digit sequences [38, 57, 6, 5, 77, 8, 44] treated as clock times: "
            "5-8 candidate states seconds vs minutes."
        ),
        "layer_count": 2,
        "combo_estimate": 8,
        "runnable": False,
    },
    {
        "id": "p4_timezone_offset",
        "priority": 4,
        "name": "P4 — ±6-Hour Berlin/CIA Timezone Offset",
        "status": "Active",
        "description": (
            "Berlin is UTC+1 (CET), CIA Langley is UTC-5 (EST) — a 6-hour gap. "
            "Modifier doubles any sweep by testing both the local and 6-hour-shifted clock state."
        ),
        "layer_count": 2,
        "combo_estimate": 103680,
        "runnable": False,
    },
    {
        "id": "p5_two_crib_filter",
        "priority": 5,
        "name": "P5 — BERLIN+CLOCK 2-Crib Soft Filter",
        "status": "Active",
        "description": (
            "Surface near-misses: candidates with BERLIN (pos 63-68) and CLOCK (pos 69-73) "
            "both present. Relaxes threshold from 4 to 2 to catch partial hits."
        ),
        "layer_count": 2,
        "combo_estimate": 51840,
        "runnable": False,
    },
    {
        "id": "p6_k3_running_key",
        "priority": 6,
        "name": "P6 — K3 Running Key",
        "status": "Active",
        "description": (
            "Use first 97 characters of K3 plaintext (SLOWLY DESPARATLY SLOWLY...) "
            "as a running key for K4 decryption. 2-4 variant combinations."
        ),
        "layer_count": 2,
        "combo_estimate": 4,
        "runnable": False,
    },
    {
        "id": "p7_gronsfeld",
        "priority": 7,
        "name": "P7 — Gronsfeld Cipher",
        "status": "Active",
        "description": (
            "Gronsfeld uses decimal digit strings as key. K2 coordinate digits "
            "(389065770844) as candidate keys. Requires kryptos.k4.gronsfeld implementation."
        ),
        "layer_count": 1,
        "combo_estimate": 4,
        "runnable": False,
    },
    {
        "id": "p8_myszkowski",
        "priority": 8,
        "name": "P8 — Myszkowski Transposition",
        "status": "Deferred",
        "description": (
            "Repeated-letter keywords (ABSCISSA, PALIMPSEST) produce non-standard columnar "
            "groupings. KRYPTOS has no repeated letters so cannot be used here."
        ),
        "layer_count": 1,
        "combo_estimate": None,
        "runnable": False,
    },
    {
        "id": "p9_trifid",
        "priority": 9,
        "name": "P9 — Trifid Cipher",
        "status": "Deferred",
        "description": "27-letter cube fractionation cipher. Requires kryptos.k4.trifid implementation.",
        "layer_count": 1,
        "combo_estimate": None,
        "runnable": False,
    },
    {
        "id": "p10_straddle",
        "priority": 10,
        "name": "P10 — Straddle Checkerboard",
        "status": "Deferred",
        "description": "Variable-length encoding expansion cipher. Requires implementation.",
        "layer_count": 1,
        "combo_estimate": None,
        "runnable": False,
    },
]


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class RunAttackRequest(BaseModel):
    attack_id: str = Field("p1_three_layer", description="Which attack to run")
    priority_only: bool = Field(False, description="Only test CIA priority clock times")
    grid_sizes: list[int] | None = Field(None, description="Column counts to sweep")
    max_perms_per_grid: int | None = Field(720, ge=1, le=40320)


class JobStatusResponse(BaseModel):
    job_id: str
    attack_id: str
    status: str
    progress_pct: float
    clock_time: str | None
    total_candidates: int
    top_candidates: list[dict[str, Any]]
    summary: dict[str, Any] | None
    error: str | None


class FrontierVectorsResponse(BaseModel):
    vectors: list[dict[str, Any]]


# ---------------------------------------------------------------------------
# Router factory
# ---------------------------------------------------------------------------
def create_k4_attack_router() -> APIRouter:
    router = APIRouter(prefix="/api/k4/attacks", tags=["k4-attacks"])

    @router.get("/frontier", response_model=FrontierVectorsResponse)
    def frontier() -> FrontierVectorsResponse:
        return FrontierVectorsResponse(vectors=FRONTIER_VECTORS)

    @router.post("/run", response_model=JobStatusResponse)
    def run_attack(req: RunAttackRequest) -> JobStatusResponse:
        if req.attack_id != "p1_three_layer":
            raise HTTPException(
                status_code=422,
                detail=f"Attack '{req.attack_id}' is not yet runnable. Only p1_three_layer is implemented.",
            )

        job_id = _new_job(req.attack_id)
        _update_job(job_id, status="running")

        def _worker() -> None:
            try:
                from kryptos.k4.three_layer_composite import CIA_PRIORITY_TIMES, run_three_layer_composite
                from kryptos.k4.eureka import EurekaSignal

                grid_sizes = req.grid_sizes
                clock_step = 86400 if req.priority_only else 3600
                priority_times = CIA_PRIORITY_TIMES if req.priority_only else CIA_PRIORITY_TIMES

                def _progress(info: dict[str, Any]) -> None:
                    pct = (info["clock_idx"] / info["total_clock"]) * 100
                    _update_job(
                        job_id,
                        progress_pct=round(pct, 1),
                        clock_time=info["clock_time"],
                        total_candidates=info["total_candidates"],
                        top_candidates=info["top_candidates"],
                    )

                summary = run_three_layer_composite(
                    grid_sizes=grid_sizes,
                    clock_step_seconds=clock_step,
                    priority_clock_times=priority_times,
                    max_perms_per_grid=req.max_perms_per_grid,
                    progress_cb=_progress,
                )
                _update_job(
                    job_id,
                    status="complete",
                    progress_pct=100.0,
                    summary=summary,
                    top_candidates=summary.get("best_candidates", [])[:5],
                )
            except EurekaSignal as e:
                logger.critical("EUREKA SIGNAL in P1 attack! %s", e)
                _update_job(
                    job_id,
                    status="eureka",
                    progress_pct=100.0,
                    summary={"snapshot_path": e.snapshot_path, "result": e.result},
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception("P1 attack job %s failed", job_id)
                _update_job(job_id, status="error", error=str(exc))

        t = threading.Thread(target=_worker, daemon=True, name=f"k4-p1-{job_id[:8]}")
        t.start()

        return JobStatusResponse(**_get_job(job_id))  # type: ignore[arg-type]

    @router.get("/jobs/{job_id}", response_model=JobStatusResponse)
    def job_status(job_id: str) -> JobStatusResponse:
        job = _get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        return JobStatusResponse(**job)

    return router


__all__ = ["create_k4_attack_router", "FRONTIER_VECTORS"]
