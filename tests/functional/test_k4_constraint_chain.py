"""Tests for kryptos.k4.constraint_chain."""

from __future__ import annotations

from kryptos.k4.constraint_chain import LAYER_NAMES, evaluate_candidate
from kryptos.k4.physical_grid import K4
from kryptos.k4.plaintext_evidence import reconstructed_plaintext


class TestEvaluateCandidate:
    def test_returns_every_layer(self):
        r = evaluate_candidate(K4)
        assert set(r["layers"].keys()) == set(LAYER_NAMES)

    def test_raw_ciphertext_satisfies_nothing(self):
        r = evaluate_candidate(K4)
        assert r["layers_satisfied"] == 0
        assert not r["layers"]["confirmed_cribs"]["satisfied"]

    def test_reconstructed_plaintext_satisfies_multiple_layers(self):
        recon = reconstructed_plaintext()
        r = evaluate_candidate(recon)
        assert r["layers"]["confirmed_cribs"]["satisfied"] is True
        assert r["layers"]["sanborn_hint_keywords"]["satisfied"] is True
        assert r["layers"]["reconstructed_plaintext_alignment"]["satisfied"] is True
        assert r["layers_satisfied"] >= 3

    def test_reconstructed_plaintext_scores_better_than_ciphertext_language_layer(self):
        recon = reconstructed_plaintext()
        r_recon = evaluate_candidate(recon)
        r_cipher = evaluate_candidate(K4)
        assert r_recon["layers"]["language_score"]["satisfied"]
        assert not r_cipher["layers"]["language_score"]["satisfied"]

    def test_geometry_layer_inapplicable_without_a_measured_bearing(self):
        # Phase 8 is still open -- this must stay honestly "not applicable"
        # rather than silently satisfied or silently failed.
        r = evaluate_candidate(K4)
        assert not r["layers"]["physical_geometry"]["satisfied"]
        assert "not yet applicable" in r["layers"]["physical_geometry"]["detail"]

    def test_layers_satisfied_matches_actual_count(self):
        r = evaluate_candidate(reconstructed_plaintext())
        actual = sum(1 for layer in r["layers"].values() if layer["satisfied"])
        assert r["layers_satisfied"] == actual
        assert r["layers_total"] == len(LAYER_NAMES)
