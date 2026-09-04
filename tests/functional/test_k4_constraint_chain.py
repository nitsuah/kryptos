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
        assert r["layers"]["reconstructed_plaintext_alignment"]["satisfied"] is True
        assert r["layers_satisfied"] >= 3

    def test_keyword_layer_excludes_confirmed_crib_words(self):
        # A candidate satisfying confirmed_cribs necessarily contains
        # NORTHEAST/BERLIN/CLOCK as substrings too -- if the keyword layer
        # counted those, it would trivially pass whenever the crib layer
        # does, defeating the point of "independent" evidence layers. The
        # reconstruction's only remaining independent P11 hint is COMPASS
        # (one hit, below the 3-hit threshold), so this layer must be False
        # here even though the crib layer is True.
        from kryptos.k4.constraint_chain import _keyword_layer

        recon = reconstructed_plaintext()
        r = evaluate_candidate(recon)
        assert r["layers"]["confirmed_cribs"]["satisfied"] is True
        assert r["layers"]["sanborn_hint_keywords"]["satisfied"] is False

        layer = _keyword_layer(recon)
        assert layer["satisfied"] is False
        assert "COMPASS" in layer["detail"]
        for confirmed_crib_word in ("EAST", "NORTHEAST", "BERLIN", "CLOCK"):
            assert confirmed_crib_word not in layer["detail"].rsplit(": ", 1)[1]

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

    def test_geometry_layer_preserves_a_zero_rotation_offset(self, monkeypatch):
        # rotation_offset=0 is a real, meaningful geometry sweep parameter
        # (see geometry_combined_sweep.py) -- `0 or key_info.get("bearing")`
        # would incorrectly treat it as falsy and fall through to the
        # unrelated "bearing" key instead. Only exercisable once a bearing
        # is actually sourced (Phase 8, still open), so this synthesizes
        # one via monkeypatch rather than waiting on that outreach.
        from kryptos.k4 import constraint_chain, physical_geometry

        synthetic = physical_geometry.KryptosPhysicalGeometry(
            compass_rose=physical_geometry.CompassRoseGeometry(
                true_bearing=physical_geometry.Measurement(value=0.0, unit="degrees", source="test fixture")
            )
        )
        monkeypatch.setattr(physical_geometry, "CURRENT", synthetic)

        layer = constraint_chain._geometry_layer({"rotation_offset": 0, "bearing": 999.0})
        assert layer["satisfied"] is True
        assert "candidate bearing 0" in layer["detail"]

    def test_layers_satisfied_matches_actual_count(self):
        r = evaluate_candidate(reconstructed_plaintext())
        actual = sum(1 for layer in r["layers"].values() if layer["satisfied"])
        assert r["layers_satisfied"] == actual
        assert r["layers_total"] == len(LAYER_NAMES)
