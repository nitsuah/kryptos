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
            "8 null-character masking variants (stride-2/3/4, block-8, clock-shadow, arc-fraction) "
            "applied as Layer 0 before the P1 chain. Recalculates crib positions in each residue."
        ),
        "layer_count": 4,
        "combo_estimate": 8,
        "runnable": True,
    },
    {
        "id": "p3_k2_coord_clock",
        "priority": 3,
        "name": "P3 — K2 Coordinate Clock Timestamps",
        "status": "Active",
        "description": (
            "K2 plaintext WGS-84 coordinates read as HH:MM clock times: "
            "14:57, 06:05, 17:08, 08:44, 13:57. Each tested as Berlin Clock state for P1."
        ),
        "layer_count": 2,
        "combo_estimate": 5,
        "runnable": True,
    },
    {
        "id": "p4_timezone_offset",
        "priority": 4,
        "name": "P4 — ±6-Hour Berlin/CIA Timezone Offset",
        "status": "Active",
        "description": (
            "Berlin (CET=UTC+1) vs CIA Langley (EST=UTC−5) is a 6-hour gap. "
            "Doubles any clock sweep by testing ±6h shifted state alongside base state."
        ),
        "layer_count": 2,
        "combo_estimate": 10,
        "runnable": True,
    },
    {
        "id": "p5_two_crib_filter",
        "priority": 5,
        "name": "P5 — BERLIN+CLOCK 2-Crib Soft Filter",
        "status": "Active",
        "description": (
            "Relaxes Eureka threshold from 4 to 2 (BERLIN+CLOCK at positions 63-73). "
            "Surfaces near-misses where the transposition is right but substitution key wrong."
        ),
        "layer_count": 2,
        "combo_estimate": 51840,
        "runnable": True,
    },
    {
        "id": "p6_k3_running_key",
        "priority": 6,
        "name": "P6 — K3 Running Key",
        "status": "Active",
        "description": (
            "First 97 chars of K3 plaintext (SLOWLYDESPARATLYSLOWLY...) as Vigenère running key. "
            "4 variants: standard/KRYPTOS alphabet × direct/reversed key."
        ),
        "layer_count": 2,
        "combo_estimate": 4,
        "runnable": True,
    },
    {
        "id": "p7_gronsfeld",
        "priority": 7,
        "name": "P7 — Gronsfeld Cipher",
        "status": "Active",
        "description": (
            "Vigenère with decimal digit key (0-9 shifts). K2 coordinate digit keys: "
            "385765, 770844, 385706577, 3857. Implemented in kryptos.k4.gronsfeld."
        ),
        "layer_count": 1,
        "combo_estimate": 20,
        "runnable": True,
    },
    {
        "id": "p13_magnetic_declination",
        "priority": 13,
        "name": "P13 — Magnetic Declination Clock Offset",
        "status": "Active",
        "description": (
            "At CIA HQ (38.957°N, 77.145°W) on Nov 3 1990, IGRF magnetic declination ≈ −9.9° west. "
            "Applied to a 12-hour clock face: 9.9° ÷ 360° × 720 min ≈ 20-minute offset. "
            "Tests CIA+K2 base times shifted ±20 min (14 states total)."
        ),
        "layer_count": 2,
        "combo_estimate": 14,
        "runnable": True,
    },
    {
        "id": "p12_misspelling",
        "priority": 12,
        "name": "P12 — Misspelling-Derived Alphabets",
        "status": "Active",
        "description": (
            "K1 IQLUSION (I≡L) and K3 DESPARATLY (A≡E) may define partial K4 alphabet constraints. "
            "Tests 9 alphabets: KRYPTOS/PALIMPSEST/ABSCISSA × {I↔L swap, A↔E swap, both swaps}."
        ),
        "layer_count": 3,
        "combo_estimate": 9 * 720 * 2,
        "runnable": True,
    },
    {
        "id": "p11_alt_keywords",
        "priority": 11,
        "name": "P11 — Alternative Keyed-Alphabet Keywords",
        "status": "Active",
        "description": (
            "Tests 11 sculptor/location/crib-derived keywords (SANBORN, LANGLEY, SCHEIDT, WENDELL, "
            "NORTHEAST, BERLIN, CLOCK, SHADOW, BETWEEN, COMPASS, DIGETAL) as keyed-alphabet seeds "
            "in the 3-layer composite sweep. CIA timestamps tested first."
        ),
        "layer_count": 3,
        "combo_estimate": 11 * 720 * 2,
        "runnable": True,
    },
    {
        "id": "p18_key_csp",
        "priority": 18,
        "name": "P18 — Repeating-Key CSP",
        "status": "Active",
        "description": (
            "Constraint satisfaction over 22 known (position, shift) pairs from all 4 crib windows. "
            "For key lengths 2–20, checks if any period is consistent with EAST/NORTHEAST/BERLIN/CLOCK shifts. "
            "Consistent lengths have their partial key completed via exhaustive enumeration."
        ),
        "layer_count": 1,
        "combo_estimate": 19,
        "runnable": True,
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
# Attack worker dispatcher
# ---------------------------------------------------------------------------
def _run_attack_worker(job_id: str, req: "RunAttackRequest") -> None:
    """Dispatch the correct attack module and update job state on completion."""
    attack_id = req.attack_id

    if attack_id == "p1_three_layer":
        from kryptos.k4.three_layer_composite import CIA_PRIORITY_TIMES, run_three_layer_composite

        clock_step = 86400 if req.priority_only else 3600

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
            grid_sizes=req.grid_sizes,
            clock_step_seconds=clock_step,
            priority_clock_times=CIA_PRIORITY_TIMES,
            max_perms_per_grid=req.max_perms_per_grid,
            progress_cb=_progress,
        )

    elif attack_id == "p2_shadow_masking":
        from kryptos.k4.masking_v2 import all_masking_variants
        from kryptos.k4.composite_sweep import run_composite_sweep
        from kryptos.k4.vigenere_key_recovery import KNOWN_KEYED_ALPHABETS

        variants = all_masking_variants()
        best: list[dict[str, Any]] = []
        for i, (residue, meta) in enumerate(variants):
            pct = ((i + 1) / len(variants)) * 100
            _update_job(job_id, progress_pct=round(pct, 1), clock_time=meta["mode"], total_candidates=i + 1)
            try:
                result = run_composite_sweep(
                    ciphertext=residue,
                    alphabets=KNOWN_KEYED_ALPHABETS,
                    grid_sizes=[7, 8],
                    clock_step_seconds=43200,
                    max_perms_per_grid=24,
                    null_artifact_path=f"K4_MASK_{meta['mode'].replace(':', '-')}_NULL.json",
                )
                for c in result.get("best_candidates", []):
                    c["mask_mode"] = meta["mode"]
                    best.extend(result.get("best_candidates", []))
            except Exception:  # noqa: BLE001
                pass
        best.sort(key=lambda r: (-r.get("keyword_hits", 0), -r.get("instructional_score", 0)))
        summary = {"status": "null_result", "attack": "P2_shadow_masking", "variants_tested": len(variants), "best_candidates": best[:10]}

    elif attack_id == "p3_k2_coord_clock":
        from kryptos.k4.k2_clock_states import get_k2_clock_states
        from kryptos.k4.composite_sweep import run_composite_sweep, K4
        from kryptos.k4.vigenere_key_recovery import KNOWN_KEYED_ALPHABETS

        states = get_k2_clock_states(include_tz_offset=False)
        all_best: list[dict[str, Any]] = []
        for i, state in enumerate(states):
            pct = ((i + 1) / len(states)) * 100
            _update_job(job_id, progress_pct=round(pct, 1), clock_time=state["time"], total_candidates=i + 1)
            # Use the specific shift sequence only
            single_alpha = {"KRYPTOS": KNOWN_KEYED_ALPHABETS["KRYPTOS"]}
            try:
                from kryptos.k4.composite_sweep import _vigenere_decrypt, _keyword_hits
                from kryptos.k4.transposition_analysis import apply_columnar_permutation_reverse
                from itertools import permutations as _perms
                ct = "".join(c for c in K4.upper() if c.isalpha())
                for alpha_name, alphabet in KNOWN_KEYED_ALPHABETS.items():
                    stripped = _vigenere_decrypt(ct, state["shifts"], alphabet)
                    for n_cols in [7, 8, 10]:
                        for perm in list(_perms(range(n_cols)))[:120]:
                            candidate = apply_columnar_permutation_reverse(stripped, n_cols, list(perm))
                            hits = _keyword_hits(candidate)
                            if hits > 0:
                                all_best.append({"candidate_text": candidate, "keyword_hits": hits, "clock_time": state["time"], "alpha": alpha_name, "source": state.get("source", "")})
            except Exception:  # noqa: BLE001
                pass
        all_best.sort(key=lambda r: -r["keyword_hits"])
        summary = {"status": "null_result", "attack": "P3_k2_coord_clock", "states_tested": len(states), "best_candidates": all_best[:10]}

    elif attack_id == "p4_timezone_offset":
        from kryptos.k4.k2_clock_states import get_k2_clock_states, get_tz_offset_states, CIA_TIMESTAMP_TIMES, clock_state_for_time
        from kryptos.k4.composite_sweep import _vigenere_decrypt, _keyword_hits, K4
        from kryptos.k4.transposition_analysis import apply_columnar_permutation_reverse
        from kryptos.k4.vigenere_key_recovery import KNOWN_KEYED_ALPHABETS
        from itertools import permutations as _perms

        base = [clock_state_for_time(t) for t, _ in CIA_TIMESTAMP_TIMES]
        states = get_tz_offset_states(base)
        ct = "".join(c for c in K4.upper() if c.isalpha())
        all_best: list[dict[str, Any]] = []
        for i, state in enumerate(states):
            pct = ((i + 1) / len(states)) * 100
            _update_job(job_id, progress_pct=round(pct, 1), clock_time=state["time"], total_candidates=i + 1)
            for alpha_name, alphabet in KNOWN_KEYED_ALPHABETS.items():
                stripped = _vigenere_decrypt(ct, state["shifts"], alphabet)
                for n_cols in [7, 8, 10]:
                    for perm in list(_perms(range(n_cols)))[:120]:
                        candidate = apply_columnar_permutation_reverse(stripped, n_cols, list(perm))
                        hits = _keyword_hits(candidate)
                        if hits > 0:
                            all_best.append({"candidate_text": candidate, "keyword_hits": hits, "clock_time": state["time"], "alpha": alpha_name, "is_offset": state.get("is_offset", False)})
        all_best.sort(key=lambda r: -r["keyword_hits"])
        summary = {"status": "null_result", "attack": "P4_timezone_offset", "states_tested": len(states), "best_candidates": all_best[:10]}

    elif attack_id == "p5_two_crib_filter":
        from kryptos.k4.three_layer_composite import run_three_layer_composite, CIA_PRIORITY_TIMES

        def _progress(info: dict[str, Any]) -> None:
            pct = (info["clock_idx"] / info["total_clock"]) * 100
            _update_job(job_id, progress_pct=round(pct, 1), clock_time=info["clock_time"], total_candidates=info["total_candidates"], top_candidates=info["top_candidates"])

        summary = run_three_layer_composite(
            keyword_eureka_threshold=2,  # relaxed to 2 cribs
            max_perms_per_grid=req.max_perms_per_grid or 120,
            progress_cb=_progress,
            null_artifact_path="K4_P5_2CRIB_NULL.json",
            eureka_snapshot_path="K4_P5_2CRIB_EUREKA.md",
        )
        summary["attack"] = "P5_two_crib_soft_filter"

    elif attack_id == "p6_k3_running_key":
        from kryptos.k4.running_key import run_k3_running_key_attack
        _update_job(job_id, progress_pct=50.0, clock_time="running-key")
        summary = run_k3_running_key_attack()

    elif attack_id == "p7_gronsfeld":
        from kryptos.k4.gronsfeld import run_gronsfeld_sweep
        _update_job(job_id, progress_pct=50.0, clock_time="gronsfeld")
        summary = run_gronsfeld_sweep()

    elif attack_id == "p13_magnetic_declination":
        from kryptos.k4.k2_clock_states import get_magnetic_declination_states
        from kryptos.k4.composite_sweep import _vigenere_decrypt, _keyword_hits, K4
        from kryptos.k4.transposition_analysis import apply_columnar_permutation_reverse
        from kryptos.k4.vigenere_key_recovery import KNOWN_KEYED_ALPHABETS
        from itertools import permutations as _perms

        states = get_magnetic_declination_states()
        ct = "".join(c for c in K4.upper() if c.isalpha())
        all_best: list[dict[str, Any]] = []
        for i, state in enumerate(states):
            pct = ((i + 1) / len(states)) * 100
            _update_job(job_id, progress_pct=round(pct, 1), clock_time=state["time"], total_candidates=i + 1)
            for alpha_name, alphabet in KNOWN_KEYED_ALPHABETS.items():
                stripped = _vigenere_decrypt(ct, state["shifts"], alphabet)
                for n_cols in [7, 8, 10]:
                    for perm in list(_perms(range(n_cols)))[:120]:
                        candidate = apply_columnar_permutation_reverse(stripped, n_cols, list(perm))
                        hits = _keyword_hits(candidate)
                        if hits > 0:
                            all_best.append({"candidate_text": candidate, "keyword_hits": hits,
                                             "clock_time": state["time"], "alpha": alpha_name,
                                             "source": state.get("source", "")})
        all_best.sort(key=lambda r: -r["keyword_hits"])
        summary = {"status": "null_result", "attack": "P13_magnetic_declination",
                   "states_tested": len(states), "best_candidates": all_best[:10]}

    elif attack_id == "p12_misspelling":
        from kryptos.k4.misspelling_alphabets import run_misspelling_sweep

        def _progress_p12(info: dict[str, Any]) -> None:
            pct = (info["clock_idx"] / info["total_clock"]) * 100
            _update_job(
                job_id,
                progress_pct=round(pct, 1),
                clock_time=info["clock_time"],
                total_candidates=info["total_candidates"],
                top_candidates=info["top_candidates"],
            )

        summary = run_misspelling_sweep(
            grid_sizes=req.grid_sizes,
            priority_only=req.priority_only,
            max_perms_per_grid=req.max_perms_per_grid or 120,
            progress_cb=_progress_p12,
        )

    elif attack_id == "p11_alt_keywords":
        from kryptos.k4.alt_keywords import run_alt_keyword_sweep

        def _progress_p11(info: dict[str, Any]) -> None:
            pct = (info["clock_idx"] / info["total_clock"]) * 100
            _update_job(
                job_id,
                progress_pct=round(pct, 1),
                clock_time=info["clock_time"],
                total_candidates=info["total_candidates"],
                top_candidates=info["top_candidates"],
            )

        summary = run_alt_keyword_sweep(
            grid_sizes=req.grid_sizes,
            priority_only=req.priority_only,
            max_perms_per_grid=req.max_perms_per_grid or 120,
            progress_cb=_progress_p11,
        )

    elif attack_id == "p18_key_csp":
        from kryptos.k4.key_csp import run_key_csp_attack
        _update_job(job_id, progress_pct=25.0, clock_time="csp-solving")
        summary = run_key_csp_attack()
        _update_job(job_id, progress_pct=100.0)

    else:
        summary = {"status": "error", "error": f"Unknown attack: {attack_id}"}

    _update_job(
        job_id,
        status="complete",
        progress_pct=100.0,
        summary=summary,
        total_candidates=summary.get("total_candidates", summary.get("states_tested", summary.get("variants_tested", 0))),
        top_candidates=summary.get("best_candidates", [])[:5],
    )


# ---------------------------------------------------------------------------
# Router factory
# ---------------------------------------------------------------------------
def create_k4_attack_router() -> APIRouter:
    router = APIRouter(prefix="/api/k4/attacks", tags=["k4-attacks"])

    @router.get("/frontier", response_model=FrontierVectorsResponse)
    def frontier() -> FrontierVectorsResponse:
        return FrontierVectorsResponse(vectors=FRONTIER_VECTORS)

    _RUNNABLE = {v["id"] for v in FRONTIER_VECTORS if v["runnable"]}

    @router.post("/run", response_model=JobStatusResponse)
    def run_attack(req: RunAttackRequest) -> JobStatusResponse:
        if req.attack_id not in _RUNNABLE:
            raise HTTPException(
                status_code=422,
                detail=f"Attack '{req.attack_id}' is not runnable. Runnable: {sorted(_RUNNABLE)}",
            )

        job_id = _new_job(req.attack_id)
        _update_job(job_id, status="running")

        def _worker() -> None:
            try:
                from kryptos.k4.eureka import EurekaSignal
                _run_attack_worker(job_id, req)
            except EurekaSignal as e:
                logger.critical("EUREKA SIGNAL in %s attack! %s", req.attack_id, e)
                _update_job(
                    job_id,
                    status="eureka",
                    progress_pct=100.0,
                    summary={"snapshot_path": e.snapshot_path, "result": e.result},
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception("%s attack job %s failed", req.attack_id, job_id)
                _update_job(job_id, status="error", error=str(exc))

        t = threading.Thread(target=_worker, daemon=True, name=f"k4-{req.attack_id[:6]}-{job_id[:8]}")
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
