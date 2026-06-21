"""Thin database connection helper — reads DATABASE_URL from the environment."""

from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import contextmanager

_URL_ENV = "DATABASE_URL"


def get_db_url() -> str:
    url = os.getenv(_URL_ENV)
    if not url:
        raise RuntimeError(f"{_URL_ENV} is not set — add it to your .env file")
    # Strip inline comments that may be present in .env files
    return url.split("#")[0].strip()


@contextmanager
def get_conn() -> Generator:
    """Context manager that yields an autocommit psycopg2 connection."""
    try:
        import psycopg2
    except ImportError as exc:
        raise ImportError("psycopg2-binary is required: pip install psycopg2-binary") from exc

    conn = psycopg2.connect(get_db_url())
    conn.autocommit = True
    try:
        yield conn
    finally:
        conn.close()
