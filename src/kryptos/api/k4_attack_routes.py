"""API routes for K4 frontier attack execution.

POST /api/k4/attacks/run         — start a background attack job
GET  /api/k4/attacks/jobs/{id}   — poll job status + top candidates
GET  /api/k4/attacks/frontier    — list P1-P7 frontier vectors
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from kryptos.api.k4_attack_dispatch import run_attack_worker
from kryptos.api.k4_jobs import get_job, list_jobs, new_job, update_job

logger = logging.getLogger(__name__)

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
        "id": "p14_bearing",
        "priority": 14,
        "name": "P14 — CIA→Berlin Bearing",
        "status": "Active",
        "description": (
            "Great-circle bearing from CIA HQ to Berlin ≈ 50.7°. Tests: "
            "(1) Caesar shift 50 mod 26 = 24 (Y); "
            "(2) bearing as clock-minute offset on CIA timestamps; "
            "(3) Vigenère key cycle shifted by bearing positions."
        ),
        "layer_count": 1,
        "combo_estimate": 50,
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
            "Constraint satisfaction over the 24 known (position, shift) pairs from all 4 crib windows. "
            "For key lengths 2–20, checks if any period is consistent with EAST/NORTHEAST/BERLIN/CLOCK shifts. "
            "Consistent lengths have their partial key completed via exhaustive enumeration."
        ),
        "layer_count": 1,
        "combo_estimate": 19,
        "runnable": True,
    },
    {
        "id": "p21_crib_constraints",
        "priority": 21,
        "name": "P21 — Crib-Constraint Engine",
        "status": "Active",
        "description": (
            "Tests whole cipher families against the 24 crib letters instead of sampling keys: "
            "ciphertext/plaintext autokey (every lag), linear keys, Gronsfeld digit keys, running keys over "
            "the sculpture corpus, and periodic keys composed with every columnar transposition (widths 2-9) "
            "and the phase 6-7 geometric permutations, in both layer orders."
        ),
        "layer_count": 2,
        "combo_estimate": 46_232,
        "runnable": True,
    },
    {
        "id": "p15_straddling_checkerboard",
        "priority": 15,
        "name": "P15 — K2 Coordinate Straddling Checkerboard",
        "status": "Active",
        "description": (
            "K2 coordinate digits 3,8,5,7,6,5 (N) and 7,7,8,4,4 (W) as row-header indices "
            "in a straddling checkerboard. Tests 6 row-header pairs × 3 letter orderings × 2 "
            "digit-stream converters. Checks encoding distribution and decoding for crib matches."
        ),
        "layer_count": 1,
        "combo_estimate": 36,
        "runnable": True,
    },
    {
        "id": "p16_corpus_miner",
        "priority": 16,
        "name": "P16 — Candidate Corpus Fragment Mining",
        "status": "Active",
        "description": (
            "Loads all K4_*_NULL.json artifacts, extracts candidate_text from each, "
            "and runs a sliding-window n-gram frequency analysis over positions 0-21 "
            "(before EAST crib). Flags English fragments recurring in >3% of candidates "
            "as partial-plaintext anchors."
        ),
        "layer_count": 0,
        "combo_estimate": 1,
        "runnable": True,
    },
    {
        "id": "p19_advisory_keywords",
        "priority": 19,
        "name": "P19 — Sanborn Advisory Names as Keywords",
        "status": "Active",
        "description": (
            "Tests 9 name-derived keyed alphabets: SCHEIDT (most important — designed cipher "
            "with Sanborn), WEBSTER, STUDEMAN, KERR, SANBORN, LANGLEY, ELONKA, OSHEA, KRYPTOS. "
            "Same 3-layer composite sweep as P11, CIA timestamps first."
        ),
        "layer_count": 3,
        "combo_estimate": 9 * 2,
        "runnable": True,
    },
    {
        "id": "p20_cyrillic_projector",
        "priority": 20,
        "name": "P20 — Cyrillic Projector KGB Keywords",
        "status": "Active",
        "description": (
            "Sanborn's UNC Cyrillic Projector (1997) encodes a KGB recruitment manual. "
            "16 transliterated KGB keywords (AGENT, REZIDENT, RAZVEDKA, SLUZHBA, ...) "
            "tested as keyed-alphabet seeds in the 3-layer composite sweep."
        ),
        "layer_count": 3,
        "combo_estimate": 16 * 2,
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


class BearingInfo(BaseModel):
    forward_azimuth_deg: float
    back_azimuth_deg: float | None = None
    distance_m: float
    distance_ft: float
    source: str
    note: str | None = None


class PivotStatusResponse(BaseModel):
    """Physical/Geometric Pivot progress summary — v2 dashboard panel."""

    hypothesis_graph: dict[str, Any]
    hypothesis_graph_mermaid: str
    total_candidates_tested: int
    bearings: dict[str, BearingInfo]


# ---------------------------------------------------------------------------
# Router factory
# ---------------------------------------------------------------------------
def create_k4_attack_router() -> APIRouter:
    router = APIRouter(prefix="/api/k4/attacks", tags=["k4-attacks"])

    @router.get("/frontier", response_model=FrontierVectorsResponse)
    def frontier() -> FrontierVectorsResponse:
        return FrontierVectorsResponse(vectors=FRONTIER_VECTORS)

    @router.get("/pivot-status", response_model=PivotStatusResponse)
    def pivot_status() -> PivotStatusResponse:
        from kryptos.k4 import geodesy, hypothesis_graph
        from kryptos.k4.bearing_attack import CIA_BERLIN_BEARING_DEG, CIA_BERLIN_BEARING_INT

        graph = hypothesis_graph.load()
        geodesic = geodesy.cia_berlin_geodesic()

        return PivotStatusResponse(
            hypothesis_graph=graph,
            hypothesis_graph_mermaid=hypothesis_graph.to_mermaid(graph),
            # Grand total across the Physical/Geometric Pivot's real-K4 runs
            # (Phase 1: 482,112 + Phase 2: 74,880) — see
            # docs/analysis/K4_ACTIVE_RESEARCH.md's Physical/Geometric Pivot
            # section for the per-run breakdown. Updated by hand when a new
            # pivot sweep is run against real K4, not computed live.
            total_candidates_tested=556_992,
            bearings={
                "cia_berlin_spherical": BearingInfo(
                    forward_azimuth_deg=CIA_BERLIN_BEARING_DEG,
                    distance_m=0,
                    distance_ft=0,
                    source="bearing_attack.great_circle_bearing (spherical approximation)",
                    note=f"rounded to {CIA_BERLIN_BEARING_INT} deg for the Caesar-shift/clock-offset attacks",
                ),
                "cia_berlin_geodesic": BearingInfo(
                    forward_azimuth_deg=geodesic["forward_azimuth_deg"],
                    back_azimuth_deg=geodesic["back_azimuth_deg"],
                    distance_m=geodesic["distance_m"],
                    distance_ft=geodesic["distance_ft"],
                    source="kryptos.k4.geodesy (WGS84 geodesic, geographiclib)",
                ),
                "kryptos_lodestone_deflection": BearingInfo(
                    forward_azimuth_deg=0,
                    distance_m=0,
                    distance_ft=0,
                    source="community reporting (unverified)",
                    note=(
                        "Explicitly unmeasured per elonka.com's own Kryptos measurement "
                        "wish list as of this research pass — do not treat as a precise figure."
                    ),
                ),
            },
        )

    _RUNNABLE = {v["id"] for v in FRONTIER_VECTORS if v["runnable"]}

    @router.post("/run", response_model=JobStatusResponse)
    def run_attack(req: RunAttackRequest) -> JobStatusResponse:
        if req.attack_id not in _RUNNABLE:
            raise HTTPException(
                status_code=422,
                detail=f"Attack '{req.attack_id}' is not runnable. Runnable: {sorted(str(x) for x in _RUNNABLE)}",
            )

        job_id = new_job(req.attack_id)
        update_job(job_id, status="running")

        def _worker() -> None:
            try:
                from kryptos.k4.eureka import EurekaSignal

                run_attack_worker(job_id, req)
            except EurekaSignal as e:
                logger.critical("EUREKA SIGNAL in %s attack! %s", req.attack_id, e)
                update_job(
                    job_id,
                    status="eureka",
                    progress_pct=100.0,
                    summary={"snapshot_path": e.snapshot_path, "result": e.result},
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception("%s attack job %s failed", req.attack_id, job_id)
                update_job(job_id, status="error", error=str(exc))

        t = threading.Thread(target=_worker, daemon=True, name=f"k4-{req.attack_id[:6]}-{job_id[:8]}")
        t.start()

        return JobStatusResponse(**get_job(job_id))  # type: ignore[arg-type]

    @router.get("/jobs")
    def recent_jobs(limit: int = 20) -> dict[str, Any]:
        """Recent attack jobs, newest first (in-memory plus persisted when DATABASE_URL is set)."""
        return {"jobs": list_jobs(max(1, min(limit, 200)))}

    @router.get("/jobs/{job_id}", response_model=JobStatusResponse)
    def job_status(job_id: str) -> JobStatusResponse:
        job = get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        return JobStatusResponse(**job)

    return router


__all__ = ["create_k4_attack_router", "FRONTIER_VECTORS"]
