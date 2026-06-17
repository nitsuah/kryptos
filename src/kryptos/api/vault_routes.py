"""Vault API router: seal a secret, unseal it with a key, peek at its status.

Backed by :mod:`kryptos.vault` and the ``vault_payloads`` Neon table. The vault
requires ``DATABASE_URL``; without it these endpoints return 503. Vault errors
map to HTTP status: not found -> 404, expired/exhausted -> 410, wrong key -> 403.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field

from kryptos import vault


class SealRequest(BaseModel):
    plaintext: str = Field(..., min_length=1, description="Secret to seal")
    key: str = Field(..., min_length=1, description="Keyed-alphabet Vigenère key")
    ttl_seconds: int = Field(86400, ge=0, le=vault.MAX_TTL_SECONDS, description="Lifetime in seconds; 0 = no expiry")
    max_reads: int = Field(1, ge=1, le=vault.MAX_READS_CAP, description="Server-enforced read limit")


class SealResponse(BaseModel):
    token: str
    cipher: str
    max_reads: int
    expires_at: str | None = None


class UnsealRequest(BaseModel):
    token: str = Field(..., min_length=1)
    key: str = Field(..., min_length=1)


class UnsealResponse(BaseModel):
    token: str
    plaintext: str
    reads_remaining: int
    expires_at: str | None = None


class PeekResponse(BaseModel):
    token: str
    cipher: str
    status: str
    max_reads: int
    reads_used: int
    reads_remaining: int
    sealed_at: str | None = None
    expires_at: str | None = None


def create_vault_router() -> APIRouter:
    router = APIRouter(prefix="/api/vault", tags=["vault"])

    @router.post("/seal", response_model=SealResponse)
    def seal(req: SealRequest) -> SealResponse:
        try:
            result = vault.seal(req.plaintext, req.key, ttl_seconds=req.ttl_seconds, max_reads=req.max_reads)
        except vault.VaultUnavailable as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return SealResponse(**result)

    @router.post("/unseal", response_model=UnsealResponse)
    def unseal(req: UnsealRequest) -> UnsealResponse:
        try:
            result = vault.unseal(req.token, req.key)
        except vault.VaultUnavailable as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except vault.VaultNotFound as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except vault.VaultGone as exc:
            raise HTTPException(status_code=410, detail=str(exc)) from exc
        except vault.VaultWrongKey as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return UnsealResponse(**result)

    @router.get("/{token}", response_model=PeekResponse)
    def peek(token: str = Path(..., min_length=1)) -> PeekResponse:
        try:
            result = vault.peek(token)
        except vault.VaultUnavailable as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except vault.VaultNotFound as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return PeekResponse(**result)

    return router


__all__ = ["create_vault_router"]
