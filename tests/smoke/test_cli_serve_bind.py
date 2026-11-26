"""`kryptos serve` bind-address defaults and the token requirement for non-loopback binds."""

from __future__ import annotations

import sys
import types

import pytest

from kryptos.cli.main import _is_loopback_bind, build_parser, main


@pytest.fixture()
def fake_uvicorn(monkeypatch):
    calls: list[dict] = []
    mod = types.ModuleType("uvicorn")
    mod.run = lambda app, **kw: calls.append({"app": app, **kw})  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "uvicorn", mod)
    return calls


def test_default_host_is_loopback():
    assert build_parser().parse_args(["serve"]).host == "127.0.0.1"


@pytest.mark.parametrize("host", ["127.0.0.1", "::1", "[::1]", "localhost"])
def test_loopback_hosts(host):
    assert _is_loopback_bind(host)


@pytest.mark.parametrize("host", ["0.0.0.0", "::", "192.168.1.10", "example.com"])
def test_non_loopback_hosts(host):
    assert not _is_loopback_bind(host)


def test_serve_default_binds_loopback(monkeypatch, fake_uvicorn):
    monkeypatch.delenv("KRYPTOS_API_TOKEN", raising=False)
    assert main(["serve"]) == 0
    assert fake_uvicorn[0]["host"] == "127.0.0.1"


def test_non_loopback_without_token_is_refused(monkeypatch, fake_uvicorn, capsys):
    monkeypatch.delenv("KRYPTOS_API_TOKEN", raising=False)
    assert main(["serve", "--host", "0.0.0.0"]) == 2
    assert fake_uvicorn == []
    assert "KRYPTOS_API_TOKEN" in capsys.readouterr().err


def test_non_loopback_with_token_is_allowed(monkeypatch, fake_uvicorn):
    monkeypatch.setenv("KRYPTOS_API_TOKEN", "unit-test-token")
    assert main(["serve", "--host", "0.0.0.0"]) == 0
    assert fake_uvicorn[0]["host"] == "0.0.0.0"


def test_port_from_env_is_an_int(monkeypatch, fake_uvicorn):
    # Render sets PORT; uvicorn logs it with %d, so a str port raises a logging error on boot.
    monkeypatch.setenv("PORT", "10000")
    monkeypatch.delenv("KRYPTOS_API_TOKEN", raising=False)
    assert main(["serve"]) == 0
    assert fake_uvicorn[0]["port"] == 10000
