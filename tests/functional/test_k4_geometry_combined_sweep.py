"""Tests for kryptos.k4.geometry_combined_sweep — combined geometric-permutation attack."""

from __future__ import annotations

import json

import pytest

from kryptos.k4 import geometry24
from kryptos.k4 import geometry_combined_sweep as gcs
from kryptos.k4.eureka import EurekaSignal
from kryptos.k4.physical_grid import build_tableau
from kryptos.k4.quagmire import quagmire3_encrypt


def _planted_ciphertext(*, all_four_cribs: bool = True) -> tuple[str, list[int]]:
    plaintext_chars = list("A" * 97)
    plaintext_chars[22:26] = "EAST"
    plaintext_chars[26:35] = "NORTHEAST"
    plaintext_chars[63:69] = "BERLIN"
    if all_four_cribs:
        plaintext_chars[69:74] = "CLOCK"  # leave as filler "AAAAA" otherwise -> 3/4 cribs
    plaintext = "".join(plaintext_chars)

    keystream = "".join(build_tableau("KRYPTOS")[5])  # route row_05
    presubst_ct = quagmire3_encrypt(plaintext, keystream, "KRYPTOS")

    flat_idx = gcs.composed_flat_indices("col_major", "flip_v", 6, "leading")
    planted_ct = geometry24.apply_forward(presubst_ct, flat_idx)
    return planted_ct, flat_idx


class TestComposedFlatIndices:
    def test_row_major_identity_zero_trailing_is_identity(self):
        flat = gcs.composed_flat_indices("row_major", "identity", 0, "trailing")
        assert flat == list(range(97))

    def test_is_a_valid_permutation(self):
        flat = gcs.composed_flat_indices("col_major", "flip_v", 6, "leading")
        assert sorted(flat) == list(range(97))

    def test_drop_mode_length(self):
        flat = gcs.composed_flat_indices("boustrophedon", "rotate_180", -6, "drop")
        assert sorted(flat) == list(range(geometry24.CORE_LEN))


class TestNullResultArtifact:
    def test_null_result_artifact(self, tmp_path):
        artifact = tmp_path / "null.json"
        summary = gcs.run_geometry_combined_sweep(
            order_names=["row_major"],
            reflection_names=["identity"],
            rotation_offsets=[0],
            remainder_modes=["trailing"],
            null_artifact_path=artifact,
            graph_path=tmp_path / "graph.json",
            eureka_snapshot_path=tmp_path / "snap.md",
        )
        assert summary["status"] == "null_result"
        assert summary["run_params"]["total_tested"] == 108 * 2
        data = json.loads(artifact.read_text(encoding="utf-8"))
        assert data["attack"] == "geometry_combined_sweep"

    def test_null_result_updates_hypothesis_graph(self, tmp_path):
        graph_path = tmp_path / "graph.json"
        gcs.run_geometry_combined_sweep(
            order_names=["row_major"],
            reflection_names=["identity"],
            rotation_offsets=[0],
            remainder_modes=["trailing"],
            null_artifact_path=tmp_path / "null.json",
            graph_path=graph_path,
            eureka_snapshot_path=tmp_path / "snap.md",
        )
        data = json.loads(graph_path.read_text(encoding="utf-8"))
        edge = data["edges"]["GEOMETRIC_POSITIONAL_TRANSFORM->SUBSTITUTION_LAYER"]
        assert edge["status"] == "null"


class TestEurekaOnPlantedSolution:
    def test_eureka_on_planted_solution(self, tmp_path):
        planted_ct, _ = _planted_ciphertext()

        with pytest.raises(EurekaSignal) as excinfo:
            gcs.run_geometry_combined_sweep(
                ciphertext=planted_ct,
                order_names=["col_major"],
                reflection_names=["flip_v"],
                rotation_offsets=[6],
                remainder_modes=["leading"],
                null_artifact_path=tmp_path / "null.json",
                graph_path=tmp_path / "graph.json",
                eureka_snapshot_path=tmp_path / "snap.md",
            )

        result = excinfo.value.result
        assert result["positional_crib_hits"] == 4
        assert result["key_info"]["order"] == "col_major"
        assert result["key_info"]["reflection"] == "flip_v"
        assert result["key_info"]["rotation_offset"] == 6
        assert result["key_info"]["remainder_mode"] == "leading"
        assert result["key_info"]["tableau_route"] == "row_05"
        assert result["validation"]["promote"] is True
        assert result["validation"]["reproduced"] is True

    def test_eureka_updates_hypothesis_graph(self, tmp_path):
        planted_ct, _ = _planted_ciphertext()
        graph_path = tmp_path / "graph.json"

        with pytest.raises(EurekaSignal):
            gcs.run_geometry_combined_sweep(
                ciphertext=planted_ct,
                order_names=["col_major"],
                reflection_names=["flip_v"],
                rotation_offsets=[6],
                remainder_modes=["leading"],
                null_artifact_path=tmp_path / "null.json",
                graph_path=graph_path,
                eureka_snapshot_path=tmp_path / "snap.md",
            )

        data = json.loads(graph_path.read_text(encoding="utf-8"))
        edge = data["edges"]["GEOMETRIC_POSITIONAL_TRANSFORM->SUBSTITUTION_LAYER"]
        assert edge["status"] == "eureka"


class TestPartialMatchDoesNotHalt:
    def test_threshold_crossing_without_full_match_does_not_raise(self, tmp_path):
        # 3/4 cribs (no CLOCK) crosses positional_eureka_threshold=3 but must
        # not be treated as a validated breakthrough: promote requires all 4.
        planted_ct, _ = _planted_ciphertext(all_four_cribs=False)
        graph_path = tmp_path / "graph.json"

        summary = gcs.run_geometry_combined_sweep(
            ciphertext=planted_ct,
            order_names=["col_major"],
            reflection_names=["flip_v"],
            rotation_offsets=[6],
            remainder_modes=["leading"],
            null_artifact_path=tmp_path / "null.json",
            graph_path=graph_path,
            eureka_snapshot_path=tmp_path / "snap.md",
        )

        assert summary["status"] == "null_result"
        assert any(c["positional_crib_hits"] == 3 for c in summary["best_candidates"])
        assert not (tmp_path / "snap.md").exists()

        data = json.loads(graph_path.read_text(encoding="utf-8"))
        edge = data["edges"]["GEOMETRIC_POSITIONAL_TRANSFORM->SUBSTITUTION_LAYER"]
        # partial_null (recorded when the threshold-crossing candidate failed
        # promotion) must not be downgraded by the final "null" summary write.
        assert edge["status"] == "partial_null"
