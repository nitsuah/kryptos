"""K4 hypothesis ledger API: what has been ruled out, how, and how firmly.

``GET /api/k4/ledger`` returns every family with its tier (``eliminated``,
``sampled_null``, ``open``), scope, evidence, and the module and test behind it.
``?tier=`` filters to one tier. Data lives in :mod:`kryptos.k4.hypothesis_ledger`.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from kryptos.k4.hypothesis_ledger import TIERS, ledger, ledger_summary


def create_ledger_router() -> APIRouter:
    router = APIRouter(prefix="/api/k4/ledger", tags=["k4-ledger"])

    @router.get("")
    def get_ledger(tier: str | None = Query(None, description="eliminated | sampled_null | open")) -> dict[str, Any]:
        if tier is None:
            return ledger_summary()
        if tier not in TIERS:
            raise HTTPException(status_code=422, detail=f"Unknown tier '{tier}'. Use one of {list(TIERS)}")
        return {"tier": tier, "entries": ledger(tier)}

    return router
