"""Shared API protection: token auth and a small in-memory rate limiter.

Mutating and compute-heavy routes depend on :func:`require_api_token`. The
expected token comes from ``KRYPTOS_API_TOKEN`` and is presented as
``Authorization: Bearer <token>`` or ``X-Kryptos-Token``.

Without a configured token the routes are closed (HTTP 503). The only exception
is an explicit local-development opt-out, ``KRYPTOS_API_AUTH=off``, which is
honoured only when the deployment is not marked as production and the request
comes straight from a loopback address (no proxy forwarding headers).
"""

from __future__ import annotations

import hmac
import ipaddress
import os
import threading
import time
from collections import deque

from fastapi import HTTPException, Request

_FALSY = {"0", "false", "no", "off", "disabled", ""}
_PROD_VALUES = {"production", "prod", "live"}
# Starlette's TestClient reports this peer name instead of an address.
_LOOPBACK_NAMES = {"localhost", "testclient"}


def api_token() -> str | None:
    token = (os.getenv("KRYPTOS_API_TOKEN") or "").strip()
    return token or None


def is_production() -> bool:
    """True when the environment is marked as production (including Render)."""
    for var in ("KRYPTOS_ENV", "APP_ENV", "ENVIRONMENT", "FLASK_ENV", "ENV"):
        if (os.getenv(var) or "").strip().lower() in _PROD_VALUES:
            return True
    return (os.getenv("RENDER") or "").strip().lower() not in _FALSY


def dev_auth_opt_out() -> bool:
    """Local-development opt-out: ``KRYPTOS_API_AUTH=off`` outside production."""
    value = (os.getenv("KRYPTOS_API_AUTH") or "").strip().lower()
    return value in {"off", "disabled", "none"} and not is_production()


def is_loopback_host(host: str | None) -> bool:
    if not host:
        return False
    if host in _LOOPBACK_NAMES:
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _peer(request: Request) -> str | None:
    return request.client.host if request.client else None


def _trusted_hops() -> int:
    try:
        return max(1, int(os.getenv("KRYPTOS_TRUSTED_PROXY_HOPS") or "1"))
    except ValueError:
        return 1


def client_key(request: Request) -> str:
    """Identify the caller for rate limiting (proxy-aware only when opted in).

    With ``KRYPTOS_TRUST_PROXY`` set, the client is read from ``X-Forwarded-For``
    counting from the right: each trusted proxy appends the address it received
    the request from, so entries added by a client sit to the left of the trusted
    ones and cannot be forged. ``KRYPTOS_TRUSTED_PROXY_HOPS`` (default 1) is the
    number of trusted proxies in front of the app; the entry appended by the
    outermost one is used. On Render a single proxy layer appends the connecting
    address, so the right-most entry is the real client.
    """
    if (os.getenv("KRYPTOS_TRUST_PROXY") or "").strip().lower() not in _FALSY:
        parts = [p.strip() for p in request.headers.get("x-forwarded-for", "").split(",") if p.strip()]
        hops = _trusted_hops()
        if parts:
            return parts[-hops] if len(parts) >= hops else parts[0]
    return _peer(request) or "unknown"


def _presented_token(request: Request) -> str | None:
    header = request.headers.get("x-kryptos-token")
    if header:
        return header.strip()
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return None


def token_ok(presented: str | None) -> bool:
    expected = api_token()
    if not expected or not presented:
        return False
    return hmac.compare_digest(presented.encode(), expected.encode())


def _local_dev_request(request: Request) -> bool:
    forwarded = any(h in request.headers for h in ("x-forwarded-for", "forwarded", "x-real-ip"))
    return not forwarded and is_loopback_host(_peer(request))


class RateLimiter:
    """Sliding-window limiter keyed by caller; thread-safe and memory-bounded."""

    def __init__(self, max_keys: int = 10_000) -> None:
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()
        self._max_keys = max_keys

    def allow(self, key: str, limit: int, window: float = 60.0) -> bool:
        if limit <= 0:
            return True
        now = time.monotonic()
        with self._lock:
            if len(self._hits) >= self._max_keys and key not in self._hits:
                self._prune(now, window)
            hits = self._hits.setdefault(key, deque())
            while hits and now - hits[0] >= window:
                hits.popleft()
            if len(hits) >= limit:
                return False
            hits.append(now)
            return True

    def _prune(self, now: float, window: float) -> None:
        for k in [k for k, h in self._hits.items() if not h or now - h[-1] >= window]:
            del self._hits[k]
        if len(self._hits) >= self._max_keys:
            self._hits.clear()

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


RATE_LIMITER = RateLimiter()


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name) or default)
    except ValueError:
        return default


def rate_limit_per_minute() -> int:
    """Per-minute cap for anonymous callers of public routes (0 disables)."""
    return _env_int("KRYPTOS_RATE_LIMIT_PER_MIN", 60)


def auth_rate_limit_per_minute() -> int:
    """Per-minute cap for callers that presented a valid token (0 disables)."""
    return _env_int("KRYPTOS_AUTH_RATE_LIMIT_PER_MIN", 300)


def failed_auth_limit_per_minute() -> int:
    """Per-minute cap on failed token checks per client (0 disables)."""
    return _env_int("KRYPTOS_FAILED_AUTH_LIMIT_PER_MIN", 10)


def _too_many() -> HTTPException:
    return HTTPException(status_code=429, detail="Too many requests", headers={"Retry-After": "60"})


def rate_limit(request: Request) -> None:
    """Dependency for public routes: anonymous callers share a per-client bucket.

    A request carrying a valid token is not counted here; token-protected routes
    apply the separate authenticated bucket, so anonymous traffic can never use
    up an operator's allowance.
    """
    if token_ok(_presented_token(request)):
        return
    if not RATE_LIMITER.allow(f"anon:{client_key(request)}", rate_limit_per_minute()):
        raise _too_many()


def require_api_token(request: Request) -> None:
    """Dependency for mutating and expensive routes.

    The token is checked first. Failures count against a tight per-client limit
    (and are answered 429 once it is spent); a valid token is then limited by its
    own, separate bucket.
    """
    key = client_key(request)
    if api_token() is not None:
        if not token_ok(_presented_token(request)):
            if not RATE_LIMITER.allow(f"fail:{key}", failed_auth_limit_per_minute()):
                raise _too_many()
            raise HTTPException(status_code=401, detail="Invalid or missing API token")
    elif not (dev_auth_opt_out() and _local_dev_request(request)):
        raise HTTPException(status_code=503, detail="API token is not configured")
    if not RATE_LIMITER.allow(f"auth:{key}", auth_rate_limit_per_minute()):
        raise _too_many()


def max_attack_jobs() -> int:
    try:
        return max(1, int(os.getenv("KRYPTOS_MAX_ATTACK_JOBS") or "3"))
    except ValueError:
        return 3


__all__ = [
    "RATE_LIMITER",
    "RateLimiter",
    "auth_rate_limit_per_minute",
    "failed_auth_limit_per_minute",
    "api_token",
    "client_key",
    "dev_auth_opt_out",
    "is_loopback_host",
    "is_production",
    "max_attack_jobs",
    "rate_limit",
    "rate_limit_per_minute",
    "require_api_token",
    "token_ok",
]
