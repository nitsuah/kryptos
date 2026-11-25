"""API contract tests for the keyed K4 hypothesis endpoint."""

from fastapi.testclient import TestClient

from kryptos.api.app import create_app
from kryptos.rag.index import ArtifactIndex


def make_client(tmp_path):
    return TestClient(create_app(index=ArtifactIndex(index_dir=tmp_path / "index")))


def test_vigenere_kryptos_returns_the_97_character_plaintext(tmp_path):
    response = make_client(tmp_path).post(
        "/api/k4/hypothesis", json={"family": "vigenere", "key": "KRYPTOS"}
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["plaintext"]) == 97
    assert payload["family"] == "vigenere"
    assert payload["key"] == "KRYPTOS"
    assert payload["all_cribs_match"] is False


def test_beaufort_normalizes_mixed_case_family_and_key(tmp_path):
    response = make_client(tmp_path).post(
        "/api/k4/hypothesis", json={"family": "BeAuFoRt", "key": "kRyPtOs"}
    )

    assert response.status_code == 200
    assert response.json()["family"] == "beaufort"
    assert response.json()["key"] == "KRYPTOS"


def test_invalid_family_empty_key_and_nonalphabetic_key_return_422(tmp_path):
    client = make_client(tmp_path)

    assert client.post("/api/k4/hypothesis", json={"family": "rot13", "key": "KRYPTOS"}).status_code == 422
    assert client.post("/api/k4/hypothesis", json={"family": "vigenere", "key": ""}).status_code == 422
    assert client.post("/api/k4/hypothesis", json={"family": "vigenere", "key": "1234"}).status_code == 422
