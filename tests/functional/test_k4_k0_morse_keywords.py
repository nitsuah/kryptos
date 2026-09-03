"""Tests for the K0 Morse-slab keyword sweep in kryptos.k4.k0_morse_keywords."""

from __future__ import annotations

import json

from kryptos.k4 import k0_morse_keywords as k0


class TestK0MorseKeyedAlphabets:
    def test_covers_every_keyword(self):
        alphabets = k0.k0_morse_keyed_alphabets()
        assert set(alphabets.keys()) == set(k0.K0_MORSE_KEYWORDS)

    def test_all_alphabets_are_valid_permutations(self):
        for kw, alphabet in k0.k0_morse_keyed_alphabets().items():
            assert sorted(alphabet) == list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), kw

    def test_excludes_already_tested_keywords(self):
        # SHADOW/BETWEEN/DIGETAL are in alt_keywords.P11_KEYWORDS; POSITION is
        # in plaintext_evidence.RECONSTRUCTED_PLAINTEXT_KEYWORDS. This list
        # must not silently re-test them under a different name.
        already_tested = {"SHADOW", "BETWEEN", "DIGETAL", "POSITION"}
        assert already_tested.isdisjoint(k0.K0_MORSE_KEYWORDS)

    def test_excludes_function_words_and_too_short_fragments(self):
        excluded = {"WHAT", "IS", "YOUR", "SOS", "RQ", "YR"}
        assert excluded.isdisjoint(k0.K0_MORSE_KEYWORDS)


class TestRunK0MorseKeywordSweep:
    def test_null_result_artifact(self, tmp_path):
        artifact = tmp_path / "null.json"
        summary = k0.run_k0_morse_keyword_sweep(grid_sizes=[7], max_perms_per_grid=5, null_artifact_path=str(artifact))
        assert summary["status"] == "null_result"
        data = json.loads(artifact.read_text(encoding="utf-8"))
        assert data["run_params"]["attack"] == "P1_three_layer_composite"

    def test_uses_the_k0_morse_keyword_alphabets(self, tmp_path):
        artifact = tmp_path / "null.json"
        summary = k0.run_k0_morse_keyword_sweep(grid_sizes=[7], max_perms_per_grid=5, null_artifact_path=str(artifact))
        assert set(summary["run_params"]["subst_alphabets"]) == set(k0.K0_MORSE_KEYWORDS)
