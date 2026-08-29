"""Tests for kryptos.k4.hypothesis_graph — canonical hypothesis graph."""

from __future__ import annotations

import json

import pytest

from kryptos.k4 import hypothesis_graph as hg


class TestNewGraph:
    def test_all_edges_present(self):
        graph = hg.new_graph()
        assert len(graph["edges"]) == len(hg.EDGES)
        for src, dst in hg.EDGES:
            assert f"{src}->{dst}" in graph["edges"]

    def test_seeded_statuses_valid(self):
        graph = hg.new_graph()
        for info in graph["edges"].values():
            assert info["status"] in hg.VALID_STATUSES

    def test_confirmed_seed(self):
        graph = hg.new_graph()
        assert graph["edges"]["K4_CIPHERTEXT->EASTNORTHEAST"]["status"] == "confirmed"


class TestRecordResult:
    def test_updates_status_and_evidence(self):
        graph = hg.new_graph()
        edge = ("EASTNORTHEAST", "DIRECTIONAL_TRAVERSAL")
        hg.record_result(graph, edge, "null", evidence="some_artifact.json")
        info = graph["edges"]["EASTNORTHEAST->DIRECTIONAL_TRAVERSAL"]
        assert info["status"] == "null"
        assert info["evidence"] == "some_artifact.json"
        assert "updated" in info

    def test_invalid_status_raises(self):
        graph = hg.new_graph()
        with pytest.raises(ValueError):
            hg.record_result(graph, hg.EDGES[0], "not_a_status")

    def test_unknown_edge_raises(self):
        graph = hg.new_graph()
        with pytest.raises(KeyError):
            hg.record_result(graph, ("NOPE", "ALSO_NOPE"), "null")


class TestPersistence:
    def test_save_and_load_round_trip(self, tmp_path):
        path = tmp_path / "graph.json"
        graph = hg.new_graph()
        hg.record_result(graph, hg.EDGES[0], "eureka", evidence="test")
        hg.save(graph, path)
        loaded = hg.load(path)
        assert loaded == graph

    def test_load_seeds_when_missing(self, tmp_path):
        path = tmp_path / "does_not_exist.json"
        loaded = hg.load(path)
        assert loaded == hg.new_graph()

    def test_save_writes_valid_json(self, tmp_path):
        path = tmp_path / "graph.json"
        hg.save(hg.new_graph(), path)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "edges" in data
        assert "nodes" in data


class TestRendering:
    def test_to_mermaid_contains_flowchart(self):
        text = hg.to_mermaid(hg.new_graph())
        assert text.startswith("flowchart TD")
        for src, dst in hg.EDGES:
            assert src in text
            assert dst in text

    def test_to_markdown_table_has_header_and_rows(self):
        text = hg.to_markdown_table(hg.new_graph())
        lines = text.splitlines()
        assert lines[0].startswith("| Edge")
        assert len(lines) == len(hg.EDGES) + 2  # header + separator + one row per edge
