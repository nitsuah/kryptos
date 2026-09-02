"""Tests for kryptos.k4.three_layer_composite.run_three_layer_composite_geometric.

Item 13 — mono-subst(keyed) -> clock-Vigenere -> Phase-1 24-column geometric
permutation, swapping out the brute-force arbitrary columnar transposition
that run_three_layer_composite (P1) already tested null.
"""

from __future__ import annotations

import json

import pytest

from kryptos.k4.eureka import EurekaSignal
from kryptos.k4.geometry24 import apply_forward
from kryptos.k4.geometry_combined_sweep import composed_flat_indices
from kryptos.k4.three_layer_composite import (
    BERLIN_WALL_PRIORITY_TIMES,
    CIA_PRIORITY_TIMES,
    _build_clock_sequence,
    run_three_layer_composite_geometric,
)
from kryptos.k4.vigenere_key_recovery import KNOWN_KEYED_ALPHABETS

STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _mono_subst_encrypt(text: str, alphabet: str) -> str:
    return "".join(alphabet[STANDARD.index(c)] for c in text)


def _vigenere_encrypt_std(text: str, shifts: list[int]) -> str:
    n = len(shifts)
    return "".join(STANDARD[(STANDARD.index(c) + shifts[i % n]) % 26] for i, c in enumerate(text))


def _planted_ciphertext() -> tuple[str, dict]:
    plaintext_chars = list("A" * 97)
    plaintext_chars[21:25] = "EAST"
    plaintext_chars[25:34] = "NORTHEAST"
    plaintext_chars[63:69] = "BERLIN"
    plaintext_chars[69:74] = "CLOCK"
    plaintext = "".join(plaintext_chars)

    alphabet = KNOWN_KEYED_ALPHABETS["KRYPTOS"]
    step_a = _mono_subst_encrypt(plaintext, alphabet)

    clocks = _build_clock_sequence(CIA_PRIORITY_TIMES, 3600)
    clock_shifts = clocks[0]["shifts"]
    clock_time = clocks[0]["time"]
    step_b = _vigenere_encrypt_std(step_a, clock_shifts)

    flat_idx = composed_flat_indices("col_major", "flip_v", 6, "leading")
    planted_ct = apply_forward(step_b, flat_idx)
    return planted_ct, {"clock_time": clock_time, "alphabet": alphabet}


class TestBerlinWallPriorityTimes:
    def test_six_sourced_times(self):
        assert len(BERLIN_WALL_PRIORITY_TIMES) == 6
        assert "18:53:00" in BERLIN_WALL_PRIORITY_TIMES  # Schabowski's key statement
        assert "19:05:00" in BERLIN_WALL_PRIORITY_TIMES  # AP flash: border opening
        assert "20:00:00" in BERLIN_WALL_PRIORITY_TIMES  # ARD lead broadcast

    def test_includes_est_equivalents(self):
        # Each CET time has a -6h EST counterpart, mirroring how
        # CIA_PRIORITY_TIMES tests both timezone framings of one event.
        assert "12:53:00" in BERLIN_WALL_PRIORITY_TIMES
        assert "13:05:00" in BERLIN_WALL_PRIORITY_TIMES
        assert "14:00:00" in BERLIN_WALL_PRIORITY_TIMES

    def test_usable_as_priority_clock_times(self, tmp_path):
        summary = run_three_layer_composite_geometric(
            subst_alphabets={"KRYPTOS": KNOWN_KEYED_ALPHABETS["KRYPTOS"]},
            order_names=["row_major"],
            reflection_names=["identity"],
            rotation_offsets=[0],
            remainder_modes=["trailing"],
            priority_clock_times=BERLIN_WALL_PRIORITY_TIMES,
            null_artifact_path=tmp_path / "null.json",
            graph_path=tmp_path / "graph.json",
            eureka_snapshot_path=tmp_path / "snap.md",
        )
        assert summary["run_params"]["clock_states_tested"] == BERLIN_WALL_PRIORITY_TIMES


class TestNullResultArtifact:
    def test_null_result_artifact(self, tmp_path):
        artifact = tmp_path / "null.json"
        summary = run_three_layer_composite_geometric(
            subst_alphabets={"KRYPTOS": KNOWN_KEYED_ALPHABETS["KRYPTOS"]},
            order_names=["row_major"],
            reflection_names=["identity"],
            rotation_offsets=[0],
            remainder_modes=["trailing"],
            null_artifact_path=artifact,
            graph_path=tmp_path / "graph.json",
            eureka_snapshot_path=tmp_path / "snap.md",
        )
        assert summary["status"] == "null_result"
        assert summary["run_params"]["total_tested"] == 2  # 2 priority clock states x 1 permutation combo
        data = json.loads(artifact.read_text(encoding="utf-8"))
        assert data["attack"] == "three_layer_composite_geometric"

    def test_full_clock_sweep_tests_more_states(self, tmp_path):
        summary = run_three_layer_composite_geometric(
            subst_alphabets={"KRYPTOS": KNOWN_KEYED_ALPHABETS["KRYPTOS"]},
            order_names=["row_major"],
            reflection_names=["identity"],
            rotation_offsets=[0],
            remainder_modes=["trailing"],
            full_clock_sweep=True,
            null_artifact_path=tmp_path / "null.json",
            graph_path=tmp_path / "graph.json",
            eureka_snapshot_path=tmp_path / "snap.md",
        )
        assert len(summary["run_params"]["clock_states_tested"]) > len(CIA_PRIORITY_TIMES)

    def test_null_result_updates_hypothesis_graph(self, tmp_path):
        graph_path = tmp_path / "graph.json"
        run_three_layer_composite_geometric(
            subst_alphabets={"KRYPTOS": KNOWN_KEYED_ALPHABETS["KRYPTOS"]},
            order_names=["row_major"],
            reflection_names=["identity"],
            rotation_offsets=[0],
            remainder_modes=["trailing"],
            null_artifact_path=tmp_path / "null.json",
            graph_path=graph_path,
            eureka_snapshot_path=tmp_path / "snap.md",
        )
        data = json.loads(graph_path.read_text(encoding="utf-8"))
        assert data["edges"]["SUBSTITUTION_LAYER->CLOCK_VIGENERE_LAYER"]["status"] == "null"
        assert data["edges"]["CLOCK_VIGENERE_LAYER->THREE_LAYER_GEOMETRIC_COMPOSITE"]["status"] == "null"


class TestEurekaOnPlantedSolution:
    def test_eureka_on_planted_solution(self, tmp_path):
        planted_ct, meta = _planted_ciphertext()

        with pytest.raises(EurekaSignal) as excinfo:
            run_three_layer_composite_geometric(
                ciphertext=planted_ct,
                subst_alphabets={"KRYPTOS": meta["alphabet"]},
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
        assert result["key_info"]["alpha_name"] == "KRYPTOS"
        assert result["key_info"]["order"] == "col_major"
        assert result["key_info"]["reflection"] == "flip_v"
        assert result["key_info"]["rotation_offset"] == 6
        assert result["key_info"]["remainder_mode"] == "leading"
        assert result["key_info"]["clock_time"] == meta["clock_time"]
        assert result["validation"]["promote"] is True
        assert result["validation"]["reproduced"] is True

    def test_eureka_updates_hypothesis_graph(self, tmp_path):
        planted_ct, meta = _planted_ciphertext()
        graph_path = tmp_path / "graph.json"

        with pytest.raises(EurekaSignal):
            run_three_layer_composite_geometric(
                ciphertext=planted_ct,
                subst_alphabets={"KRYPTOS": meta["alphabet"]},
                order_names=["col_major"],
                reflection_names=["flip_v"],
                rotation_offsets=[6],
                remainder_modes=["leading"],
                null_artifact_path=tmp_path / "null.json",
                graph_path=graph_path,
                eureka_snapshot_path=tmp_path / "snap.md",
            )

        data = json.loads(graph_path.read_text(encoding="utf-8"))
        assert data["edges"]["SUBSTITUTION_LAYER->CLOCK_VIGENERE_LAYER"]["status"] == "eureka"
        assert data["edges"]["CLOCK_VIGENERE_LAYER->THREE_LAYER_GEOMETRIC_COMPOSITE"]["status"] == "eureka"

    def test_reproduces_from_non_normalized_ciphertext(self, tmp_path):
        # _reproduce's default must use the normalized `ct`, not the raw
        # `ciphertext` parameter -- otherwise a ciphertext containing any
        # non-alpha character reproduces against a different (wrong) length
        # than what the sweep actually decrypted, and apply_inverse raises.
        planted_ct, meta = _planted_ciphertext()
        dirty_ct = planted_ct[:50] + "-" + planted_ct[50:]

        with pytest.raises(EurekaSignal) as excinfo:
            run_three_layer_composite_geometric(
                ciphertext=dirty_ct,
                subst_alphabets={"KRYPTOS": meta["alphabet"]},
                order_names=["col_major"],
                reflection_names=["flip_v"],
                rotation_offsets=[6],
                remainder_modes=["leading"],
                null_artifact_path=tmp_path / "null.json",
                graph_path=tmp_path / "graph.json",
                eureka_snapshot_path=tmp_path / "snap.md",
            )

        assert excinfo.value.result["validation"]["reproduced"] is True
        assert excinfo.value.result["validation"]["promote"] is True
