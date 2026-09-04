"""Tests for kryptos.k4.geometry_substitution_search — P15 (optional).

SA substitution-key search behind a Phase-1 geometric permutation front-end.
"""

from __future__ import annotations

import json
import random

import pytest

from kryptos.k4 import geometry24
from kryptos.k4.eureka import EurekaSignal
from kryptos.k4.geometry_substitution_search import (
    STANDARD,
    run_geometry_substitution_sa_sweep,
    simulated_annealing_substitution_search,
)


def _mono_subst_encrypt(text: str, alphabet: str) -> str:
    return "".join(alphabet[STANDARD.index(c)] for c in text)


class TestSimulatedAnnealingSubstitutionSearch:
    def test_seed_alphabet_with_zero_iterations_returns_seed_unchanged(self):
        rng = random.Random(3)
        alpha_list = list(STANDARD)
        rng.shuffle(alpha_list)
        alphabet = "".join(alpha_list)

        best_alphabet, _score = simulated_annealing_substitution_search(
            "SOME ARBITRARY TEXT",
            max_iterations=0,
            seed_alphabet=alphabet,
        )
        assert best_alphabet == alphabet

    def test_seed_alphabet_must_be_a_permutation(self):
        with pytest.raises(ValueError):
            simulated_annealing_substitution_search("TEXT", max_iterations=0, seed_alphabet="NOTAPERMUTATION")


class TestNullResultArtifact:
    def test_null_result_artifact(self, tmp_path):
        artifact = tmp_path / "null.json"
        summary = run_geometry_substitution_sa_sweep(
            order_names=["row_major"],
            num_restarts=1,
            max_iterations=20,
            null_artifact_path=artifact,
        )
        assert summary["status"] == "null_result"
        assert summary["attack"] == "P15_geometry_substitution_sa"
        assert summary["run_params"]["total_tested"] == 1  # 1 order x 1 restart
        data = json.loads(artifact.read_text(encoding="utf-8"))
        assert data["attack"] == "P15_geometry_substitution_sa"


class TestEurekaOnPlantedSolution:
    def test_eureka_on_planted_solution(self, tmp_path):
        plaintext_chars = list("A" * 97)
        plaintext_chars[21:25] = "EAST"
        plaintext_chars[25:34] = "NORTHEAST"
        plaintext_chars[63:69] = "BERLIN"
        plaintext_chars[69:74] = "CLOCK"
        plaintext = "".join(plaintext_chars)

        rng = random.Random(7)
        alpha_list = list(STANDARD)
        rng.shuffle(alpha_list)
        alphabet = "".join(alpha_list)

        step1 = _mono_subst_encrypt(plaintext, alphabet)
        flat_idx = geometry24.flat_indices_for_order("row_major", "trailing")
        planted_ct = geometry24.apply_forward(step1, flat_idx)

        with pytest.raises(EurekaSignal) as excinfo:
            run_geometry_substitution_sa_sweep(
                ciphertext=planted_ct,
                order_names=["row_major"],
                num_restarts=1,
                max_iterations=0,
                seed_alphabet=alphabet,
                null_artifact_path=tmp_path / "null.json",
                eureka_snapshot_path=tmp_path / "snap.md",
            )

        result = excinfo.value.result
        assert result["positional_crib_hits"] == 4
        assert result["key_info"]["order"] == "row_major"
        assert result["key_info"]["alphabet"] == alphabet
        assert result["validation"]["promote"] is True
        assert result["validation"]["reproduced"] is True
