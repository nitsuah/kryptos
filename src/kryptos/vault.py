"""Kryptos Vault — seal a secret with a keyed-alphabet cipher, store it in Neon
with a TTL and a server-enforced read limit, and hand back an opaque token.

Unlike :mod:`kryptos.persistence` (best-effort, never on the critical path), the
vault *requires* a database: without ``DATABASE_URL`` the operations raise
:class:`VaultUnavailable` so callers can surface a clear error.

Security model (thematic, not a hardened secrets manager):

- The payload is encrypted with the KRYPTOS keyed-alphabet Vigenère
  (:func:`kryptos.ciphers.vigenere_encrypt`). The **key is never stored** — only
  the ciphertext, so DB access alone does not reveal the plaintext.
- A short ``verifier`` (sha256 prefix of the plaintext) is stored so a wrong key
  can be rejected *without* consuming a read. This is a deliberate trade-off: it
  enables offline guessing by anyone with DB access, acceptable for this feature.
- The opaque ``token`` (UUIDv4) is the capability. A row self-destructs once
  ``reads_used`` reaches ``max_reads`` or ``expires_at`` passes.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from kryptos.ciphers import vigenere_decrypt, vigenere_encrypt

logger = logging.getLogger(__name__)

CIPHER_LABEL = "vigenere-keyed"
MAX_TTL_SECONDS = 30 * 24 * 3600  # 30 days
MAX_READS_CAP = 1000


class VaultError(Exception):
    """Base class for vault failures."""


class VaultUnavailable(VaultError):
    """Raised when no database is configured."""


class VaultNotFound(VaultError):
    """Raised when a token does not exist."""


class VaultGone(VaultError):
    """Raised when a payload is expired or its reads are exhausted."""


class VaultWrongKey(VaultError):
    """Raised when the supplied key does not decrypt the payload."""


def vault_enabled() -> bool:
    """True when a DATABASE_URL is configured (the vault needs storage)."""
    from kryptos import persistence

    return persistence.db_enabled()


def _verifier(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()[:16]


def _require_db():
    if not vault_enabled():
        raise VaultUnavailable("DATABASE_URL is not configured; the vault is unavailable")
    from kryptos.db import get_conn

    return get_conn


def seal(
    plaintext: str,
    key: str,
    ttl_seconds: int = 86400,
    max_reads: int = 1,
) -> dict[str, Any]:
    """Encrypt ``plaintext`` under ``key`` and store it; return the access token.

    Returns ``{token, expires_at, max_reads, cipher}``. ``expires_at`` is None
    when ``ttl_seconds`` is 0 (no expiry). Raises :class:`VaultUnavailable` if no
    database is configured, or ``ValueError`` for invalid arguments.
    """
    if not plaintext:
        raise ValueError("plaintext must not be empty")
    if max_reads < 1:
        raise ValueError("max_reads must be >= 1")
    max_reads = min(max_reads, MAX_READS_CAP)
    if ttl_seconds < 0:
        raise ValueError("ttl_seconds must be >= 0")
    ttl_seconds = min(ttl_seconds, MAX_TTL_SECONDS)

    get_conn = _require_db()
    # vigenere_encrypt validates the key has usable alphabetic characters.
    ciphertext = vigenere_encrypt(plaintext, key, preserve_non_alpha=True)
    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO vault_payloads"
                " (token, cipher, ciphertext, verifier, max_reads, reads_used, expires_at)"
                " VALUES (%s, %s, %s, %s, %s, 0, %s)",
                (token, CIPHER_LABEL, ciphertext, _verifier(plaintext), max_reads, expires_at),
            )
    logger.info("Sealed vault payload %s (max_reads=%s, ttl=%ss)", token, max_reads, ttl_seconds)
    return {
        "token": token,
        "cipher": CIPHER_LABEL,
        "max_reads": max_reads,
        "expires_at": expires_at.isoformat() if expires_at else None,
    }


def peek(token: str) -> dict[str, Any]:
    """Return metadata for a token without decrypting or consuming a read.

    Raises :class:`VaultNotFound` if the token is unknown. An expired/exhausted
    payload is still reported (``status`` reflects it) so the UI can explain why.
    """
    get_conn = _require_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT cipher, max_reads, reads_used, sealed_at, expires_at" " FROM vault_payloads WHERE token = %s",
                (token,),
            )
            row = cur.fetchone()
    if row is None:
        raise VaultNotFound(f"No vault payload for token {token}")
    cipher, max_reads, reads_used, sealed_at, expires_at = row
    return {
        "token": token,
        "cipher": cipher,
        "status": _status(reads_used, max_reads, expires_at),
        "max_reads": max_reads,
        "reads_used": reads_used,
        "reads_remaining": max(0, max_reads - reads_used),
        "sealed_at": sealed_at.isoformat() if sealed_at else None,
        "expires_at": expires_at.isoformat() if expires_at else None,
    }


def unseal(token: str, key: str) -> dict[str, Any]:
    """Decrypt a payload with ``key`` and consume one read.

    A wrong key raises :class:`VaultWrongKey` *without* burning a read. Expired or
    exhausted payloads raise :class:`VaultGone`; unknown tokens raise
    :class:`VaultNotFound`. Returns ``{plaintext, reads_remaining, expires_at}``.
    """
    get_conn = _require_db()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT ciphertext, verifier, max_reads, reads_used, expires_at"
                " FROM vault_payloads WHERE token = %s",
                (token,),
            )
            row = cur.fetchone()
            if row is None:
                raise VaultNotFound(f"No vault payload for token {token}")
            ciphertext, verifier, max_reads, reads_used, expires_at = row

            if _is_expired(expires_at):
                raise VaultGone("Vault payload has expired")
            if reads_used >= max_reads:
                raise VaultGone("Vault payload has no reads remaining")

            plaintext = vigenere_decrypt(ciphertext, key, preserve_non_alpha=True)
            if verifier is not None and _verifier(plaintext) != verifier:
                raise VaultWrongKey("Key did not decrypt the payload")

            # Atomically claim a read; if another caller raced us to the last
            # read, RETURNING yields nothing and we report the payload as gone.
            cur.execute(
                "UPDATE vault_payloads SET reads_used = reads_used + 1"
                " WHERE token = %s AND reads_used < max_reads RETURNING reads_used",
                (token,),
            )
            updated = cur.fetchone()
            if updated is None:
                raise VaultGone("Vault payload has no reads remaining")
            new_reads_used = updated[0]

    logger.info("Unsealed vault payload %s (read %s/%s)", token, new_reads_used, max_reads)
    return {
        "token": token,
        "plaintext": plaintext,
        "reads_remaining": max(0, max_reads - new_reads_used),
        "expires_at": expires_at.isoformat() if expires_at else None,
    }


def _is_expired(expires_at: datetime | None) -> bool:
    return expires_at is not None and expires_at <= datetime.now(timezone.utc)


def _status(reads_used: int, max_reads: int, expires_at: datetime | None) -> str:
    if _is_expired(expires_at):
        return "expired"
    if reads_used >= max_reads:
        return "exhausted"
    return "sealed"


__all__ = [
    "seal",
    "unseal",
    "peek",
    "vault_enabled",
    "VaultError",
    "VaultUnavailable",
    "VaultNotFound",
    "VaultGone",
    "VaultWrongKey",
    "CIPHER_LABEL",
]
