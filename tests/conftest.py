"""Shared pytest fixtures."""

import pytest

from kryptos.api.security import RATE_LIMITER


@pytest.fixture(autouse=True)
def _local_dev_api_defaults(monkeypatch):
    """Run API tests as a local, non-production dev server with no rate limit.

    Tests that exercise auth set their own environment on top of this.
    """
    for var in ("KRYPTOS_API_TOKEN", "KRYPTOS_ENV", "APP_ENV", "ENVIRONMENT", "FLASK_ENV", "ENV", "RENDER"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("KRYPTOS_API_AUTH", "off")
    monkeypatch.setenv("KRYPTOS_RATE_LIMIT_PER_MIN", "0")
    RATE_LIMITER.reset()
    yield
    RATE_LIMITER.reset()
