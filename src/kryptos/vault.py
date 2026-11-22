"""Kryptos Vault — seal a secret with a keyed-alphabet cipher, store it in Neon
with a TTL and a server-enforced read limit, and hand back an opaque token.

Unlike :mod:`kryptos.persistence` (best-effort, never on the critical path), the
vault *requires* a database: without ``DATABASE_URL`` the operations raise
:class:`VaultUnavailable` so callers can surface a clear error.

Security model (thematic, not a hardened secrets manager):

- The payload is encrypted with the KRYPTOS keyed-alphabet Vigenère
  (:func:`kryptos.ciphers.vigenere_encrypt`). The **key is never stored** — only
  the ciphertext, so DB access alone does not reveal the plaintext.
- A salted ``verifier`` (scrypt of the plaintext) is stored so a wrong key can be
  rejected *without* consuming a read. Offline guessing by anyone with DB access
  is slowed by the scrypt cost but not prevented; this remains a puzzle feature.
  Verifiers written by earlier versions (a bare sha256 prefix) are still accepted
  and are upgraded to scrypt on the next successful unseal.
- Wrong-key attempts are counted per payload and the payload locks after
  :data:`MAX_FAILED_ATTEMPTS`; the lock clears by itself after
  ``KRYPTOS_VAULT_LOCK_HOURS`` (default 1) without further attempts.
- The opaque ``token`` (UUIDv4) is the capability. A row self-destructs once
  ``reads_used`` reaches ``max_reads`` or ``expires_at`` passes.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from kryptos.ciphers import vigenere_decrypt, vigenere_encrypt

logger = logging.getLogger(__name__)

CIPHER_LABEL = "vigenere-keyed"
MAX_TTL_SECONDS = 30 * 24 * 3600  # 30 days
MAX_READS_CAP = 1000
MAX_PLAINTEXT_CHARS = 10_000
MAX_KEY_CHARS = 256
MAX_FAILED_ATTEMPTS = 5
DEFAULT_LOCK_HOURS = 1.0
_SCRYPT_PREFIX = "scrypt$"
_SCRYPT_N, _SCRYPT_R, _SCRYPT_P = 2**14, 8, 1


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


def lock_cooldown() -> timedelta:
    """How long a locked payload stays locked (``KRYPTOS_VAULT_LOCK_HOURS``, default 1)."""
    try:
        hours = float(os.getenv("KRYPTOS_VAULT_LOCK_HOURS") or DEFAULT_LOCK_HOURS)
    except ValueError:
        hours = DEFAULT_LOCK_HOURS
    return timedelta(hours=max(0.0, hours))


def _validate_key(key: str) -> None:
    """Raise ValueError for a key the cipher cannot use, before any attempt is counted."""
    if not key or len(key) > MAX_KEY_CHARS:
        raise ValueError(f"key must be 1 to {MAX_KEY_CHARS} characters")
    vigenere_decrypt("A" * len(key), key, preserve_non_alpha=True)


def _scrypt(plaintext: str, salt: bytes) -> bytes:
    return hashlib.scrypt(
        plaintext.encode("utf-8"), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P, maxmem=64 * 1024 * 1024, dklen=32
    )


def _verifier(plaintext: str) -> str:
    """Salted, slow verifier: ``scrypt$<salt hex>$<hash hex>``."""
    salt = os.urandom(16)
    return f"{_SCRYPT_PREFIX}{salt.hex()}${_scrypt(plaintext, salt).hex()}"


def _is_legacy_verifier(stored: str) -> bool:
    return not stored.startswith(_SCRYPT_PREFIX)


def _verifier_matches(plaintext: str, stored: str) -> bool:
    if _is_legacy_verifier(stored):
        legacy = hashlib.sha256(plaintext.encode("utf-8")).hexdigest()[:16]
        return hmac.compare_digest(legacy.encode(), stored.encode())
    try:
        _prefix, salt_hex, hash_hex = stored.split("$")
        expected = bytes.fromhex(hash_hex)
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    return hmac.compare_digest(_scrypt(plaintext, salt), expected)


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
    if len(plaintext) > MAX_PLAINTEXT_CHARS:
        raise ValueError(f"plaintext must be at most {MAX_PLAINTEXT_CHARS} characters")
    if len(key) > MAX_KEY_CHARS:
        raise ValueError(f"key must be at most {MAX_KEY_CHARS} characters")
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
                "SELECT cipher, max_reads, reads_used, sealed_at, expires_at, failed_attempts, last_failed_at"
                " FROM vault_payloads WHERE token = %s",
                (token,),
            )
            row = cur.fetchone()
    if row is None:
        raise VaultNotFound(f"No vault payload for token {token}")
    cipher, max_reads, reads_used, sealed_at, expires_at, failed_attempts, last_failed_at = row
    return {
        "token": token,
        "cipher": cipher,
        "status": _status(reads_used, max_reads, expires_at, failed_attempts, last_failed_at),
        "max_reads": max_reads,
        "reads_used": reads_used,
        "reads_remaining": max(0, max_reads - reads_used),
        "sealed_at": sealed_at.isoformat() if sealed_at else None,
        "expires_at": expires_at.isoformat() if expires_at else None,
    }


def unseal(token: str, key: str) -> dict[str, Any]:
    """Decrypt a payload with ``key`` and consume one read.

    A wrong key raises :class:`VaultWrongKey` *without* burning a read, but counts
    toward :data:`MAX_FAILED_ATTEMPTS`; once reached the payload is locked and
    raises :class:`VaultGone`. Expired or
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

            # A malformed key is rejected before an attempt is reserved.
            _validate_key(key)

            # Reserve a guess before checking the key so parallel attempts cannot
            # exceed the cap; a correct key resets the counter below. A lock older
            # than the cooldown starts a fresh count.
            now = datetime.now(timezone.utc)
            cur.execute(
                "UPDATE vault_payloads SET"
                " failed_attempts = CASE WHEN failed_attempts >= %s THEN 1 ELSE failed_attempts + 1 END,"
                " last_failed_at = %s"
                " WHERE token = %s AND (failed_attempts < %s OR last_failed_at IS NULL OR last_failed_at <= %s)"
                " RETURNING failed_attempts",
                (MAX_FAILED_ATTEMPTS, now, token, MAX_FAILED_ATTEMPTS, now - lock_cooldown()),
            )
            attempt = cur.fetchone()
            if attempt is None:
                raise VaultGone("Vault payload is locked after too many failed attempts; try again later")

            plaintext = vigenere_decrypt(ciphertext, key, preserve_non_alpha=True)
            if verifier is not None and not _verifier_matches(plaintext, verifier):
                left = MAX_FAILED_ATTEMPTS - attempt[0]
                raise VaultWrongKey(f"Key did not decrypt the payload ({left} attempts left)")
            if verifier is not None and _is_legacy_verifier(verifier):
                cur.execute("UPDATE vault_payloads SET verifier = %s WHERE token = %s", (_verifier(plaintext), token))

            # Atomically claim a read; if another caller raced us to the last
            # read, RETURNING yields nothing and we report the payload as gone.
            cur.execute(
                "UPDATE vault_payloads SET reads_used = reads_used + 1, failed_attempts = 0, last_failed_at = NULL"
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


def _status(
    reads_used: int,
    max_reads: int,
    expires_at: datetime | None,
    failed_attempts: int = 0,
    last_failed_at: datetime | None = None,
) -> str:
    if _is_expired(expires_at):
        return "expired"
    if failed_attempts >= MAX_FAILED_ATTEMPTS and (
        last_failed_at is None or last_failed_at > datetime.now(timezone.utc) - lock_cooldown()
    ):
        return "locked"
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
    "MAX_FAILED_ATTEMPTS",
    "MAX_PLAINTEXT_CHARS",
]
