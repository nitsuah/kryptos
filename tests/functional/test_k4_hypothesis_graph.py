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


class TestRecordResultPreservingStrongest:
    def test_upgrade_applies(self):
        graph = hg.new_graph()
        edge = hg.EDGES[0]
        hg.record_result(graph, edge, "null", evidence="first")
        hg.record_result_preserving_strongest(graph, edge, "eureka", evidence="second")
        info = graph["edges"][f"{edge[0]}->{edge[1]}"]
        assert info["status"] == "eureka"
        assert info["evidence"] == "second"

    def test_downgrade_is_ignored(self):
        graph = hg.new_graph()
        edge = hg.EDGES[0]
        hg.record_result(graph, edge, "eureka", evidence="found it")
        hg.record_result_preserving_strongest(graph, edge, "null", evidence="a later narrower run")
        info = graph["edges"][f"{edge[0]}->{edge[1]}"]
        assert info["status"] == "eureka"
        assert info["evidence"] == "found it"

    def test_same_status_still_updates_evidence(self):
        graph = hg.new_graph()
        edge = hg.EDGES[0]
        hg.record_result(graph, edge, "null", evidence="first null")
        hg.record_result_preserving_strongest(graph, edge, "null", evidence="second null")
        info = graph["edges"][f"{edge[0]}->{edge[1]}"]
        assert info["evidence"] == "second null"

    def test_invalid_status_raises(self):
        graph = hg.new_graph()
        with pytest.raises(ValueError):
            hg.record_result_preserving_strongest(graph, hg.EDGES[0], "not_a_status")

    def test_unknown_edge_raises(self):
        graph = hg.new_graph()
        with pytest.raises(KeyError):
            hg.record_result_preserving_strongest(graph, ("NOPE", "ALSO_NOPE"), "null")


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

    def test_load_migrates_stale_graph_missing_new_edges(self, tmp_path):
        # Simulate a graph persisted before an edge existed in EDGES (e.g. a
        # Phase 1 file, saved before Phase 2 added CLOCK_VIGENERE_LAYER).
        path = tmp_path / "stale.json"
        stale_edges = {
            k: v for k, v in hg.new_graph()["edges"].items() if "CLOCK_VIGENERE" not in k and "THREE_LAYER" not in k
        }
        stale = {"nodes": hg.NODES[:12], "edges": stale_edges}
        path.write_text(json.dumps(stale), encoding="utf-8")

        loaded = hg.load(path)
        assert "SUBSTITUTION_LAYER->CLOCK_VIGENERE_LAYER" in loaded["edges"]
        assert "CLOCK_VIGENERE_LAYER->THREE_LAYER_GEOMETRIC_COMPOSITE" in loaded["edges"]
        # Recording on a newly-migrated edge must not raise KeyError.
        hg.record_result(loaded, ("SUBSTITUTION_LAYER", "CLOCK_VIGENERE_LAYER"), "null")

    def test_load_migration_preserves_existing_edge_data(self, tmp_path):
        path = tmp_path / "stale.json"
        graph = hg.new_graph()
        hg.record_result(graph, hg.EDGES[0], "eureka", evidence="pre-existing finding")
        del graph["edges"]["SUBSTITUTION_LAYER->CLOCK_VIGENERE_LAYER"]
        path.write_text(json.dumps(graph), encoding="utf-8")

        loaded = hg.load(path)
        key = f"{hg.EDGES[0][0]}->{hg.EDGES[0][1]}"
        assert loaded["edges"][key]["status"] == "eureka"
        assert loaded["edges"][key]["evidence"] == "pre-existing finding"

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
