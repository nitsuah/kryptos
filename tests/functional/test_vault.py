"""Vault tests: cipher round-trip, seal/unseal/peek flow, and HTTP error mapping.

A small in-memory fake stands in for the Neon ``vault_payloads`` table so the
real seal -> unseal -> peek logic (including expiry, exhaustion, wrong-key, and
the atomic read-decrement) is exercised without Postgres.
"""

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from kryptos import vault
from kryptos.api.app import create_app
from kryptos.ciphers import vigenere_decrypt, vigenere_encrypt
from kryptos.rag.index import ArtifactIndex

pytestmark = pytest.mark.slow


# --- Cipher round-trip --------------------------------------------------------


def test_vigenere_encrypt_decrypt_roundtrip():
    plain = "MEET AT THE BERLIN CLOCK"
    ct = vigenere_encrypt(plain, "PALIMPSEST", preserve_non_alpha=True)
    assert ct != plain
    assert vigenere_decrypt(ct, "PALIMPSEST", preserve_non_alpha=True) == plain


# --- Fake DB ------------------------------------------------------------------


class _FakeCursor:
    def __init__(self, store):
        self._store = store
        self._result = None

    def execute(self, sql, params=()):
        s = " ".join(sql.split())
        if s.startswith("INSERT INTO vault_payloads"):
            token, cipher, ciphertext, verifier, max_reads, expires_at = params
            self._store[token] = {
                "cipher": cipher,
                "ciphertext": ciphertext,
                "verifier": verifier,
                "max_reads": max_reads,
                "reads_used": 0,
                "sealed_at": datetime.now(timezone.utc),
                "expires_at": expires_at,
            }
            self._result = None
        elif s.startswith("SELECT cipher, max_reads, reads_used"):  # peek
            row = self._store.get(params[0])
            self._result = (
                (row["cipher"], row["max_reads"], row["reads_used"], row["sealed_at"], row["expires_at"])
                if row
                else None
            )
        elif s.startswith("SELECT ciphertext, verifier"):  # unseal load
            row = self._store.get(params[0])
            self._result = (
                (row["ciphertext"], row["verifier"], row["max_reads"], row["reads_used"], row["expires_at"])
                if row
                else None
            )
        elif s.startswith("UPDATE vault_payloads SET reads_used"):
            row = self._store.get(params[0])
            if row and row["reads_used"] < row["max_reads"]:
                row["reads_used"] += 1
                self._result = (row["reads_used"],)
            else:
                self._result = None
        else:  # pragma: no cover - unexpected SQL
            raise AssertionError(f"Unexpected SQL: {s}")

    def fetchone(self):
        return self._result

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _FakeConn:
    def __init__(self, store):
        self._store = store

    def cursor(self):
        return _FakeCursor(self._store)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def fake_vault(monkeypatch):
    store: dict = {}

    @contextmanager
    def _get_conn():
        yield _FakeConn(store)

    monkeypatch.setattr(vault, "_require_db", lambda: _get_conn)
    return store


# --- Module-level flow --------------------------------------------------------


def test_seal_then_unseal_roundtrip(fake_vault):
    sealed = vault.seal("ATTACK AT DAWN", "KRYPTOS", ttl_seconds=3600, max_reads=2)
    token = sealed["token"]
    assert sealed["cipher"] == vault.CIPHER_LABEL
    assert sealed["max_reads"] == 2

    opened = vault.unseal(token, "KRYPTOS")
    assert opened["plaintext"] == "ATTACK AT DAWN"
    assert opened["reads_remaining"] == 1


def test_wrong_key_does_not_consume_read(fake_vault):
    token = vault.seal("SECRET", "RIGHTKEY", max_reads=1)["token"]
    with pytest.raises(vault.VaultWrongKey):
        vault.unseal(token, "WRONGKEY")
    # Read was not burned: the correct key still works.
    assert vault.unseal(token, "RIGHTKEY")["plaintext"] == "SECRET"


def test_exhausted_after_max_reads(fake_vault):
    token = vault.seal("ONESHOT", "KEY", max_reads=1)["token"]
    assert vault.unseal(token, "KEY")["reads_remaining"] == 0
    with pytest.raises(vault.VaultGone):
        vault.unseal(token, "KEY")


def test_expired_payload_is_gone(fake_vault):
    token = vault.seal("OLD", "KEY", ttl_seconds=3600)["token"]
    fake_vault[token]["expires_at"] = datetime.now(timezone.utc) - timedelta(seconds=1)
    with pytest.raises(vault.VaultGone):
        vault.unseal(token, "KEY")


def test_peek_reports_status(fake_vault):
    token = vault.seal("HELLO", "KEY", max_reads=1)["token"]
    meta = vault.peek(token)
    assert meta["status"] == "sealed"
    assert meta["reads_remaining"] == 1
    vault.unseal(token, "KEY")
    assert vault.peek(token)["status"] == "exhausted"


def test_unknown_token_not_found(fake_vault):
    with pytest.raises(vault.VaultNotFound):
        vault.peek("00000000-0000-0000-0000-000000000000")


def test_seal_requires_database(monkeypatch):
    monkeypatch.setattr(vault, "vault_enabled", lambda: False)
    with pytest.raises(vault.VaultUnavailable):
        vault.seal("X", "KEY")


# --- HTTP layer ---------------------------------------------------------------


def _client(tmp_path):
    return TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))


def test_http_seal_unseal_peek(fake_vault, tmp_path):
    client = _client(tmp_path)

    resp = client.post(
        "/api/vault/seal",
        json={"plaintext": "BERLIN CLOCK", "key": "ABSCISSA", "ttl_seconds": 600, "max_reads": 1},
    )
    assert resp.status_code == 200
    token = resp.json()["token"]

    meta = client.get(f"/api/vault/{token}")
    assert meta.status_code == 200
    assert meta.json()["status"] == "sealed"

    opened = client.post("/api/vault/unseal", json={"token": token, "key": "ABSCISSA"})
    assert opened.status_code == 200
    assert opened.json()["plaintext"] == "BERLIN CLOCK"

    # Second unseal -> 410 Gone (max_reads exhausted).
    again = client.post("/api/vault/unseal", json={"token": token, "key": "ABSCISSA"})
    assert again.status_code == 410


def test_http_wrong_key_403(fake_vault, tmp_path):
    client = _client(tmp_path)
    token = client.post("/api/vault/seal", json={"plaintext": "X", "key": "RIGHT"}).json()["token"]
    resp = client.post("/api/vault/unseal", json={"token": token, "key": "WRONG"})
    assert resp.status_code == 403


def test_http_unknown_token_404(fake_vault, tmp_path):
    client = _client(tmp_path)
    resp = client.get("/api/vault/11111111-1111-1111-1111-111111111111")
    assert resp.status_code == 404


def test_http_unavailable_503(monkeypatch, tmp_path):
    monkeypatch.setattr(vault, "vault_enabled", lambda: False)
    client = _client(tmp_path)
    resp = client.post("/api/vault/seal", json={"plaintext": "X", "key": "K"})
    assert resp.status_code == 503
