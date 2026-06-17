"""Tests for kryptos.db_schema — Neon/Postgres table definitions."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

import pytest

from kryptos.db_schema import SCHEMA_STATEMENTS, init_schema

EXPECTED_TABLES = {
    "strategy_kb",
    "ops_decisions",
    "discovered_cribs",
    "campaign_runs",
    "candidates",
    "vault_payloads",
}

# Marker so live tests never collide with (or delete) real rows
_TEST_TAG = "__kryptos_test__"


class TestSchemaStatements:
    def test_expected_tables_defined(self):
        assert set(SCHEMA_STATEMENTS) == EXPECTED_TABLES

    def test_all_ddl_idempotent(self):
        for name, ddl in SCHEMA_STATEMENTS.items():
            assert "CREATE TABLE IF NOT EXISTS" in ddl, name
            # Idempotent indexes too, if any
            assert "CREATE INDEX " not in ddl.replace("CREATE INDEX IF NOT EXISTS", ""), name

    def test_campaign_runs_defined_before_candidates(self):
        """candidates has an FK to campaign_runs, so definition order matters."""
        names = list(SCHEMA_STATEMENTS)
        assert names.index("campaign_runs") < names.index("candidates")

    def test_init_schema_returns_tables_without_executing(self):
        """With an explicit conn, init_schema must not import kryptos.db."""

        class FakeCursor:
            executed: list[str] = []

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def execute(self, sql):
                FakeCursor.executed.append(sql)

        class FakeConn:
            def cursor(self):
                return FakeCursor()

        FakeCursor.executed = []
        tables = init_schema(conn=FakeConn())
        assert tables == sorted(EXPECTED_TABLES)
        assert len(FakeCursor.executed) == len(EXPECTED_TABLES)


@pytest.mark.skipif(not os.environ.get("DATABASE_URL"), reason="DATABASE_URL not set")
class TestSchemaLive:
    """Round-trip tests against a live database, using the exact SQL shapes
    that ops_director.py and spy_web_intel.py issue."""

    @pytest.fixture(autouse=True)
    def _schema(self):
        init_schema()
        yield
        # Remove any rows this test class created
        from kryptos.db import get_conn

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM strategy_kb WHERE description LIKE %s", (f"{_TEST_TAG}%",))
                cur.execute("DELETE FROM ops_decisions WHERE reasoning LIKE %s", (f"{_TEST_TAG}%",))
                cur.execute("DELETE FROM discovered_cribs WHERE text LIKE %s", (f"{_TEST_TAG}%",))
                cur.execute("DELETE FROM candidates WHERE text LIKE %s", (f"{_TEST_TAG}%",))
                cur.execute("DELETE FROM campaign_runs WHERE label LIKE %s", (f"{_TEST_TAG}%",))

    def test_init_schema_idempotent(self):
        assert init_schema() == sorted(EXPECTED_TABLES)
        assert init_schema() == sorted(EXPECTED_TABLES)

    def test_strategy_kb_roundtrip(self):
        from kryptos.db import get_conn

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO strategy_kb (category, description, attack_type, confidence, metadata)"
                    " VALUES (%s, %s, %s, %s, %s::jsonb)",
                    ("lesson", f"{_TEST_TAG} hill climbing stalls", "hill", 0.7, json.dumps({"k": 1})),
                )
                # Exact read shape from OpsStrategicDirector._load_strategy_kb
                cur.execute(
                    "SELECT category, description, attack_type, confidence, metadata FROM strategy_kb ORDER BY id"
                )
                rows = [r for r in cur.fetchall() if r[1].startswith(_TEST_TAG)]
        assert rows == [("lesson", f"{_TEST_TAG} hill climbing stalls", "hill", 0.7, {"k": 1})]

    def test_strategy_kb_rejects_unknown_category(self):
        from kryptos.db import get_conn

        with get_conn() as conn:
            with conn.cursor() as cur:
                with pytest.raises(Exception, match="strategy_kb_category_check"):
                    cur.execute(
                        "INSERT INTO strategy_kb (category, description) VALUES (%s, %s)",
                        ("bogus", f"{_TEST_TAG} nope"),
                    )

    def test_ops_decisions_insert(self):
        from kryptos.db import get_conn

        # Exact insert shape from OpsStrategicDirector._save_decision
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO ops_decisions
                       (timestamp, action, reasoning, affected_attacks, resource_changes,
                        success_criteria, review_in_hours, confidence)
                       VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s)""",
                    (
                        datetime.now(timezone.utc),
                        "reallocate",
                        f"{_TEST_TAG} test decision",
                        ["hill", "vigenere"],
                        json.dumps({"hill": 0.5}),
                        "improvement",
                        2.0,
                        0.8,
                    ),
                )
                cur.execute(
                    "SELECT action, affected_attacks, resource_changes FROM ops_decisions WHERE reasoning LIKE %s",
                    (f"{_TEST_TAG}%",),
                )
                row = cur.fetchone()
        assert row == ("reallocate", ["hill", "vigenere"], {"hill": 0.5})

    def test_discovered_cribs_upsert(self):
        from kryptos.db import get_conn

        crib = f"{_TEST_TAG}LANGLEY"
        # Exact upsert shape from SpyWebIntel._save_cache, run twice to hit ON CONFLICT
        upsert = """INSERT INTO discovered_cribs (text, source, confidence, category, context)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (text) DO UPDATE
                        SET confidence = EXCLUDED.confidence,
                            source     = EXCLUDED.source,
                            category   = EXCLUDED.category,
                            context    = EXCLUDED.context"""
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(upsert, (crib, "test", 0.5, "location", "first"))
                cur.execute(upsert, (crib, "test2", 0.9, "location", "second"))
                # Exact read shape from SpyWebIntel._load_cache
                cur.execute(
                    "SELECT text, confidence, source, context, created_at, category FROM discovered_cribs"
                    " WHERE text = %s",
                    (crib,),
                )
                rows = cur.fetchall()
        assert len(rows) == 1
        text, confidence, source, context, created_at, category = rows[0]
        assert (text, confidence, source, context, category) == (crib, 0.9, "test2", "second", "location")
        assert created_at is not None

    def test_candidates_fk_to_campaign_runs(self):
        from kryptos.db import get_conn

        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO campaign_runs (label, stage, cipher_label, status) VALUES (%s, %s, %s, %s)"
                    " RETURNING id",
                    (f"{_TEST_TAG}run", "stage1", "K4", "complete"),
                )
                run_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO candidates (campaign_run_id, rank, score, text, key, metrics)"
                    " VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb)",
                    (run_id, 1, -12.5, f"{_TEST_TAG}EASTNORTHEAST", json.dumps([[1, 2], [3, 4]]), json.dumps({})),
                )
                cur.execute("SELECT rank, score, key FROM candidates WHERE campaign_run_id = %s", (run_id,))
                row = cur.fetchone()
        assert row == (1, -12.5, [[1, 2], [3, 4]])
