"""Tests for the reconstructed-plaintext-keyword sweep in kryptos.k4.plaintext_evidence."""

from __future__ import annotations

import json

from kryptos.k4 import plaintext_evidence as pe


class TestReconstructedPlaintextKeyedAlphabets:
    def test_covers_every_keyword(self):
        alphabets = pe.reconstructed_plaintext_keyed_alphabets()
        assert set(alphabets.keys()) == set(pe.RECONSTRUCTED_PLAINTEXT_KEYWORDS)

    def test_all_alphabets_are_valid_permutations(self):
        for kw, alphabet in pe.reconstructed_plaintext_keyed_alphabets().items():
            assert sorted(alphabet) == list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), kw

    def test_excludes_already_tested_p11_keywords(self):
        # EAST/NORTHEAST/BERLIN/CLOCK/COMPASS already have dedicated
        # coverage elsewhere (P11's alt_keywords.py) -- this list must not
        # silently re-test them under a different name.
        already_tested = {"EAST", "NORTHEAST", "BERLIN", "CLOCK", "COMPASS"}
        assert already_tested.isdisjoint(pe.RECONSTRUCTED_PLAINTEXT_KEYWORDS)


class TestRunReconstructedPlaintextKeywordSweep:
    def test_null_result_artifact(self, tmp_path):
        artifact = tmp_path / "null.json"
        summary = pe.run_reconstructed_plaintext_keyword_sweep(
            grid_sizes=[7], max_perms_per_grid=5, null_artifact_path=str(artifact)
        )
        assert summary["status"] == "null_result"
        data = json.loads(artifact.read_text(encoding="utf-8"))
        assert data["run_params"]["attack"] == "P1_three_layer_composite"

    def test_uses_the_reconstructed_keyword_alphabets(self, tmp_path):
        artifact = tmp_path / "null.json"
        summary = pe.run_reconstructed_plaintext_keyword_sweep(
            grid_sizes=[7], max_perms_per_grid=5, null_artifact_path=str(artifact)
        )
        assert set(summary["run_params"]["subst_alphabets"]) == set(pe.RECONSTRUCTED_PLAINTEXT_KEYWORDS)
