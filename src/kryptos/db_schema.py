"""Neon/Postgres schema for kryptos persistent storage.

Defines the tables that agent and pipeline code already target (or will):

- ``strategy_kb`` — read by ``OpsStrategicDirector._load_strategy_kb``
- ``ops_decisions`` — written by ``OpsStrategicDirector._save_decision``
- ``discovered_cribs`` — read/written by ``SpyWebIntel._load_cache``/``_save_cache``
- ``campaign_runs`` / ``candidates`` — Phase 3 candidate & run storage
  (currently file-based under ``artifacts/``; shapes mirror ``k4.reporting``)

All DDL is idempotent (``CREATE TABLE IF NOT EXISTS``), so ``init_schema()``
can run safely on every deploy. Apply with ``kryptos db-init`` or::

    from kryptos.db_schema import init_schema
    init_schema()
"""

from __future__ import annotations

# Mapping of table name -> idempotent DDL (table + its indexes).
SCHEMA_STATEMENTS: dict[str, str] = {
    "strategy_kb": """
        CREATE TABLE IF NOT EXISTS strategy_kb (
            id          BIGSERIAL PRIMARY KEY,
            category    TEXT NOT NULL CHECK (category IN ('successful', 'failed', 'lesson')),
            description TEXT NOT NULL,
            attack_type TEXT,
            confidence  DOUBLE PRECISION,
            metadata    JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """,
    "ops_decisions": """
        CREATE TABLE IF NOT EXISTS ops_decisions (
            id               BIGSERIAL PRIMARY KEY,
            timestamp        TIMESTAMPTZ NOT NULL,
            action           TEXT NOT NULL,
            reasoning        TEXT,
            affected_attacks TEXT[] NOT NULL DEFAULT '{}',
            resource_changes JSONB NOT NULL DEFAULT '{}'::jsonb,
            success_criteria TEXT,
            review_in_hours  DOUBLE PRECISION,
            confidence       DOUBLE PRECISION
        );
    """,
    "discovered_cribs": """
        CREATE TABLE IF NOT EXISTS discovered_cribs (
            id         BIGSERIAL PRIMARY KEY,
            text       TEXT NOT NULL UNIQUE,
            source     TEXT NOT NULL,
            confidence DOUBLE PRECISION NOT NULL,
            category   TEXT,
            context    TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """,
    "campaign_runs": """
        CREATE TABLE IF NOT EXISTS campaign_runs (
            id           BIGSERIAL PRIMARY KEY,
            label        TEXT,
            stage        TEXT,
            cipher_label TEXT,
            ciphertext   TEXT,
            status       TEXT NOT NULL DEFAULT 'running',
            started_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
            finished_at  TIMESTAMPTZ,
            metadata     JSONB NOT NULL DEFAULT '{}'::jsonb
        );
    """,
    "candidates": """
        CREATE TABLE IF NOT EXISTS candidates (
            id              BIGSERIAL PRIMARY KEY,
            campaign_run_id BIGINT REFERENCES campaign_runs(id) ON DELETE SET NULL,
            rank            INTEGER,
            score           DOUBLE PRECISION,
            source          TEXT,
            key             JSONB,
            key_hash        TEXT,
            text            TEXT NOT NULL,
            metrics         JSONB NOT NULL DEFAULT '{}'::jsonb,
            origin_stage    TEXT,
            lineage         JSONB,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS idx_candidates_score ON candidates (score DESC);
        CREATE INDEX IF NOT EXISTS idx_candidates_run ON candidates (campaign_run_id);
    """,
    "vault_payloads": """
        CREATE TABLE IF NOT EXISTS vault_payloads (
            token       UUID PRIMARY KEY,
            cipher      TEXT NOT NULL DEFAULT 'vigenere-keyed',
            ciphertext  TEXT NOT NULL,
            verifier    TEXT,
            max_reads   INTEGER NOT NULL DEFAULT 1 CHECK (max_reads >= 1),
            reads_used  INTEGER NOT NULL DEFAULT 0,
            sealed_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
            expires_at  TIMESTAMPTZ
        );
        CREATE INDEX IF NOT EXISTS idx_vault_expires ON vault_payloads (expires_at);
    """,
}


def init_schema(conn=None) -> list[str]:
    """Create all kryptos tables if they do not exist.

    Args:
        conn: Optional open psycopg2 connection. When omitted, a connection
            is opened via :func:`kryptos.db.get_conn` (requires DATABASE_URL).

    Returns:
        Sorted list of table names ensured.
    """
    if conn is not None:
        _apply(conn)
    else:
        from kryptos.db import get_conn

        with get_conn() as owned_conn:
            _apply(owned_conn)
    return sorted(SCHEMA_STATEMENTS)


def _apply(conn) -> None:
    with conn.cursor() as cur:
        # campaign_runs must exist before candidates (FK), so apply in
        # definition order rather than sorted order.
        for ddl in SCHEMA_STATEMENTS.values():
            cur.execute(ddl)


__all__ = ["SCHEMA_STATEMENTS", "init_schema"]
