"""Hypothesis ledger data and its API route."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from kryptos.api.app import create_app
from kryptos.k4.hypothesis_ledger import LEDGER, TIERS

REPO = Path(__file__).resolve().parents[2]


def test_entries_well_formed():
    ids = [e["id"] for e in LEDGER]
    assert len(ids) == len(set(ids))
    for e in LEDGER:
        assert e["tier"] in TIERS
        assert e["family"]


def _resolve(dotted: str) -> object:
    """Import the longest importable module prefix, then getattr the rest."""
    parts = dotted.split(".")
    for cut in range(len(parts), 0, -1):
        try:
            obj = importlib.import_module(".".join(parts[:cut]))
        except ImportError:
            continue
        for attr in parts[cut:]:
            obj = getattr(obj, attr)
        return obj
    raise ImportError(dotted)


def test_eliminated_entries_point_at_real_code_and_tests():
    for e in (e for e in LEDGER if e["tier"] == "eliminated"):
        first, *rest = [part.strip() for part in e["module"].split("/")]
        _resolve(first)
        base = first.rsplit(".", 1)[0]
        for name in rest:
            _resolve(f"{base}.{name}")
        assert (REPO / e["test"]).exists(), e["test"]


@pytest.fixture()
def client():
    return TestClient(create_app())


def test_ledger_route(client):
    data = client.get("/api/k4/ledger").json()
    assert set(data["counts"]) == set(TIERS)
    assert sum(data["counts"].values()) == len(LEDGER)


def test_ledger_route_filter(client):
    data = client.get("/api/k4/ledger", params={"tier": "open"}).json()
    assert data["tier"] == "open" and all(e["tier"] == "open" for e in data["entries"])
    assert client.get("/api/k4/ledger", params={"tier": "bogus"}).status_code == 422
