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


def test_latest_run_reads_suite_artifact(tmp_path):
    from kryptos.k4.crib_constraints import run_crib_constraint_suite
    from kryptos.k4.hypothesis_ledger import latest_run, ledger_summary

    assert latest_run(tmp_path / "missing.json") is None
    art = tmp_path / "run.json"
    run_crib_constraint_suite(widths=[2, 3], artifact_path=art)
    run = latest_run(art)
    assert run["timestamp"] and run["columnar_survivors_period_le_22"] == 0
    assert ledger_summary(art)["latest_run"] == run


def test_every_eliminated_entry_has_a_positive_control():
    """Repo rule: an exhaustive elimination must ship a planted-solution test next to it."""
    for e in (e for e in LEDGER if e["tier"] == "eliminated"):
        text = (REPO / e["test"]).read_text(encoding="utf-8").lower()
        assert "positive" in text and "control" in text, e["id"]


def test_attack_registry_matches_dispatcher():
    """Every runnable frontier vector has a dispatch branch, and vice versa."""
    import re

    from kryptos.api.k4_attack_routes import FRONTIER_VECTORS

    src = (REPO / "src/kryptos/api/k4_attack_dispatch.py").read_text(encoding="utf-8")
    dispatched = set(re.findall(r'attack_id == "([a-z0-9_]+)"', src))
    runnable = {v["id"] for v in FRONTIER_VECTORS if v["runnable"]}
    assert runnable == dispatched


def test_keyed_columnar_frontier_is_registered_as_sampled_null():
    """Keep the bounded long-key experiment traceable without overclaiming elimination."""
    entry = next(e for e in LEDGER if e["id"] == "keyed_columnar_frontier")
    assert entry["tier"] == "sampled_null"
    assert entry["test"] == "tests/functional/test_k4_keyed_columnar_frontier.py"
    assert "widths 15–26" in entry["scope"]
