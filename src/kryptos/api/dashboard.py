"""Dashboard API router: campaign run history, candidates, and decrypt.

Read endpoints query the Neon tables through ``kryptos.persistence`` and
degrade gracefully when ``DATABASE_URL`` is unset (they return empty results
and ``db_enabled: false`` rather than erroring). ``POST /api/decrypt`` reuses
the section decrypt helpers (``kryptos.sections``) and needs no database.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from kryptos import persistence
from kryptos.sections import SECTIONS


class StatusResponse(BaseModel):
    db_enabled: bool
    table_counts: dict[str, int] = Field(default_factory=dict)
    latest_run: dict[str, Any] | None = None


class RunsResponse(BaseModel):
    db_enabled: bool
    count: int
    runs: list[dict[str, Any]] = Field(default_factory=list)


class CandidatesResponse(BaseModel):
    db_enabled: bool
    count: int
    candidates: list[dict[str, Any]] = Field(default_factory=list)


class DecryptRequest(BaseModel):
    section: str = Field(..., description="Section to decrypt: K1, K2, K3, or K4")
    ciphertext: str = Field(..., min_length=1)
    key: str | None = Field(None, description="Vigenère key (required for K1/K2)")


class DecryptResponse(BaseModel):
    section: str
    plaintext: str


class AttackVector(BaseModel):
    name: str
    status: str
    artifact: str | None = None
    description: str | None = None


class AttackVectorsResponse(BaseModel):
    vectors: list[AttackVector]


def create_dashboard_router() -> APIRouter:
    router = APIRouter(prefix="/api", tags=["dashboard"])

    @router.get("/status", response_model=StatusResponse)
    def status() -> StatusResponse:
        enabled = persistence.db_enabled()
        runs = persistence.fetch_recent_runs(limit=1) if enabled else []
        return StatusResponse(
            db_enabled=enabled,
            table_counts=persistence.table_counts(),
            latest_run=runs[0] if runs else None,
        )

    @router.get("/runs", response_model=RunsResponse)
    def runs(limit: int = Query(20, ge=1, le=200)) -> RunsResponse:
        rows = persistence.fetch_recent_runs(limit=limit)
        return RunsResponse(db_enabled=persistence.db_enabled(), count=len(rows), runs=rows)

    @router.get("/runs/{run_id}/candidates", response_model=CandidatesResponse)
    def run_candidates(run_id: int, limit: int = Query(50, ge=1, le=500)) -> CandidatesResponse:
        rows = persistence.fetch_run_candidates(run_id, limit=limit)
        return CandidatesResponse(db_enabled=persistence.db_enabled(), count=len(rows), candidates=rows)

    @router.get("/candidates", response_model=CandidatesResponse)
    def candidates(limit: int = Query(20, ge=1, le=200)) -> CandidatesResponse:
        rows = persistence.fetch_top_candidates(limit=limit)
        return CandidatesResponse(db_enabled=persistence.db_enabled(), count=len(rows), candidates=rows)

    @router.post("/decrypt", response_model=DecryptResponse)
    def decrypt(req: DecryptRequest) -> DecryptResponse:
        section = req.section.upper()
        if section not in SECTIONS:
            raise HTTPException(status_code=422, detail=f"Unknown section: {section}")
        decrypt_fn = SECTIONS[section]
        try:
            if section in ("K1", "K2"):
                if not req.key:
                    raise HTTPException(status_code=422, detail=f"{section} requires a key")
                plaintext = decrypt_fn(req.ciphertext, req.key)
            elif section == "K3":
                plaintext = decrypt_fn(req.ciphertext)
            else:  # K4 — best-effort pipeline, no key
                result = decrypt_fn(req.ciphertext)
                plaintext = getattr(result, "plaintext", result)
        except HTTPException:
            raise
        except NotImplementedError as exc:
            raise HTTPException(status_code=501, detail=str(exc) or "Section decrypt not implemented") from exc
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=f"Decrypt failed: {exc}") from exc
        return DecryptResponse(section=section, plaintext=str(plaintext))

    @router.get("/attack-vectors", response_model=AttackVectorsResponse)
    def attack_vectors() -> AttackVectorsResponse:
        # For now, this is static. Could be moved to DB or a config file later.
        vectors = [
            AttackVector(
                name="Clock → Hill 2×2 Invertibility",
                status="Ruled Out",
                artifact="K4_CLOCK_HILL_NULL.json",
                description="Tests using the Berlin Clock state to seed a 2x2 Hill cipher matrix.",
            ),
            AttackVector(
                name="4-char Clock Key → Vigenère",
                status="Ruled Out",
                artifact="K4_CLOCK_VIG_NULL.json",
                description="Derives a 4-character key from clock state for Vigenère decryption.",
            ),
            AttackVector(
                name="Non-standard Berlin Clock Sub-row",
                status="Ruled Out",
                artifact="K4_CLOCK_SUBROW_NULL.json",
                description="Uses non-standard groupings of clock lamps as keystream generators.",
            ),
            AttackVector(
                name="Berlin Clock → Columnar Transposition",
                status="Ruled Out",
                artifact="K4_CLOCK_TRANS_NULL.json",
                description="Uses lamp counts as column widths for transposition ciphers.",
            ),
            AttackVector(
                name="Beaufort Cipher Sweep",
                status="Ruled Out",
                artifact="K4_BEAUFORT_NULL.json",
                description="Sweeps common keywords using the Beaufort cipher variant.",
            ),
            AttackVector(
                name="Quagmire I-IV Sweep",
                status="Ruled Out",
                artifact="K4_QUAGMIRE_NULL.json",
                description="Exhaustive sweep of all four Quagmire variants with common keywords.",
            ),
            AttackVector(
                name="Physical-Grid Tableau-Walk",
                status="Ruled Out",
                artifact="K4_PHYSICAL_GRID_NULL.json",
                description="Simulates walking paths on a physical grid to generate keystreams.",
            ),
            AttackVector(
                name="Composite (Clock/Grid/Alphabet)",
                status="Ruled Out",
                artifact="K4_COMPOSITE_SWEEP_NULL.json",
                description="Tests combinations of other known K4 elements.",
            ),
            AttackVector(
                name="Vigenère Statistical Attack",
                status="In Progress",
                description="Ongoing statistical analysis to find Vigenère key candidates.",
            ),
            AttackVector(
                name="Machine Learning Analysis",
                status="Planned",
                description="Use ML models to detect patterns in K4 ciphertext.",
            ),
        ]
        return AttackVectorsResponse(vectors=vectors)

    return router


__all__ = ["create_dashboard_router"]
