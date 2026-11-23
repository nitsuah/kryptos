"""Boot-time schema auto-migrate (kryptos.api.app.auto_migrate)."""

from kryptos.api import app as app_module


def test_skipped_without_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    called = []
    monkeypatch.setattr("kryptos.db_schema.init_schema", lambda: called.append(1) or [])
    assert app_module.auto_migrate() is None
    assert called == []


def test_runs_init_schema_when_database_url_set(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid/db")
    monkeypatch.delenv("KRYPTOS_DB_AUTO_MIGRATE", raising=False)
    monkeypatch.setattr("kryptos.db_schema.init_schema", lambda: ["k4_constraint_runs"])
    assert app_module.auto_migrate() == ["k4_constraint_runs"]


def test_opt_out(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid/db")
    monkeypatch.setenv("KRYPTOS_DB_AUTO_MIGRATE", "0")
    called = []
    monkeypatch.setattr("kryptos.db_schema.init_schema", lambda: called.append(1) or [])
    assert app_module.auto_migrate() is None
    assert called == []


def test_failure_never_raises(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid/db")
    monkeypatch.delenv("KRYPTOS_DB_AUTO_MIGRATE", raising=False)

    def _boom():
        raise RuntimeError("db down")

    monkeypatch.setattr("kryptos.db_schema.init_schema", _boom)
    assert app_module.auto_migrate() is None


def test_skips_and_failures_are_logged_loudly(monkeypatch, caplog):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with caplog.at_level("WARNING", logger="kryptos.api.app"):
        app_module.auto_migrate()
    assert any(r.levelname == "WARNING" and "skipped" in r.getMessage() for r in caplog.records)

    caplog.clear()
    monkeypatch.setenv("DATABASE_URL", "postgresql://example.invalid/db")
    monkeypatch.setenv("KRYPTOS_DB_AUTO_MIGRATE", "0")
    with caplog.at_level("WARNING", logger="kryptos.api.app"):
        app_module.auto_migrate()
    assert any(r.levelname == "WARNING" and "skipped" in r.getMessage() for r in caplog.records)

    caplog.clear()
    monkeypatch.delenv("KRYPTOS_DB_AUTO_MIGRATE")

    def _boom():
        raise RuntimeError("db down")

    monkeypatch.setattr("kryptos.db_schema.init_schema", _boom)
    with caplog.at_level("WARNING", logger="kryptos.api.app"):
        assert app_module.auto_migrate() is None
    assert any(r.levelname == "ERROR" and "FAILED" in r.getMessage() for r in caplog.records)
