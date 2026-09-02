"""Tests for kryptos.k4.physical_grid — tableau-walk keystream attack."""

from __future__ import annotations

import json

import pytest

from kryptos.k4.eureka import EurekaSignal
from kryptos.k4.physical_grid import SIZE, build_tableau, candidate_keystreams, run_physical_grid_attack
from kryptos.k4.quagmire import keyword_alphabet, quagmire3_encrypt


class TestBuildTableau:
    def test_dimensions(self):
        grid = build_tableau("KRYPTOS")
        assert len(grid) == SIZE
        assert all(len(row) == SIZE for row in grid)

    def test_first_row_is_keyed_alphabet(self):
        grid = build_tableau("KRYPTOS")
        assert "".join(grid[0]) == keyword_alphabet("KRYPTOS")

    def test_each_row_is_left_rotation_of_previous(self):
        grid = build_tableau("KRYPTOS")
        for i in range(1, SIZE):
            prev = "".join(grid[i - 1])
            assert "".join(grid[i]) == prev[1:] + prev[0]

    def test_every_row_is_a_permutation(self):
        grid = build_tableau("KRYPTOS")
        keyed = set(keyword_alphabet("KRYPTOS"))
        for row in grid:
            assert set(row) == keyed

    def test_every_column_is_a_permutation(self):
        grid = build_tableau("KRYPTOS")
        keyed = set(keyword_alphabet("KRYPTOS"))
        for c in range(SIZE):
            assert {grid[r][c] for r in range(SIZE)} == keyed


class TestCandidateKeystreams:
    def test_route_count_and_lengths(self):
        streams = candidate_keystreams("KRYPTOS")
        # 26 rows + 26 cols + 26 main diags + 26 anti diags + 4 serpentine
        assert len(streams) == 26 * 4 + 4
        for name, ks in streams.items():
            if name.startswith("serpentine"):
                assert len(ks) == SIZE * SIZE
            else:
                assert len(ks) == SIZE

    def test_diagonal_degeneracy(self):
        # On a cyclic Vigenere tableau grid[i][j] = keyed[(i+j) % 26]:
        #   anti-diagonal (i + j = const)  -> a single constant letter
        #   main diagonal (j - i = const)  -> keyed[(2i + d) % 26], 13 letters
        streams = candidate_keystreams("KRYPTOS")
        for name, ks in streams.items():
            if name.startswith("antidiag"):
                assert len(set(ks)) == 1, name
            elif name.startswith("maindiag"):
                assert len(set(ks)) == 13, name

    def test_routes_are_distinct(self):
        streams = candidate_keystreams("KRYPTOS")
        # Rows/cols/diags should not all collapse to the same string
        single = {v for k, v in streams.items() if not k.startswith("serpentine")}
        assert len(single) > 26


class TestPhysicalGridAttack:
    def test_null_result_artifact(self, tmp_path):
        artifact = tmp_path / "null.json"
        summary = run_physical_grid_attack(
            null_artifact_path=artifact,
            eureka_snapshot_path=tmp_path / "snap.md",
        )
        assert summary["status"] == "null_result"
        assert summary["run_params"]["total_tested"] == (26 * 4 + 4) * 2
        data = json.loads(artifact.read_text(encoding="utf-8"))
        assert data["attack"] == "physical_grid"

    def test_eureka_on_planted_solution(self, tmp_path):
        # Plant a solution encrypted with a known tableau row as the keystream
        keystream = "".join(build_tableau("KRYPTOS")[5])  # route row_05
        plaintext = list("A" * 97)
        plaintext[21:25] = "EAST"
        plaintext[25:34] = "NORTHEAST"
        plaintext[63:69] = "BERLIN"
        plaintext[69:74] = "CLOCK"
        planted_ct = quagmire3_encrypt("".join(plaintext), keystream, "KRYPTOS")

        with pytest.raises(EurekaSignal) as excinfo:
            run_physical_grid_attack(
                ciphertext=planted_ct,
                null_artifact_path=tmp_path / "null.json",
                eureka_snapshot_path=tmp_path / "snap.md",
            )
        assert excinfo.value.result["positional_crib_hits"] == 4
        assert excinfo.value.result["key_info"]["route"] == "row_05"
