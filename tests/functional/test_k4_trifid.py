"""Tests for kryptos.k4.trifid — P9 Trifid cube fractionation."""

from __future__ import annotations

import json

import pytest

from kryptos.k4.eureka import EurekaSignal
from kryptos.k4.trifid import FILLER, build_cube_order, run_trifid_attack, trifid_decrypt, trifid_encrypt


class TestPrimitives:
    def test_cube_order_is_27_unique_symbols(self):
        cube = build_cube_order("KRYPTOS")
        assert len(cube) == 27
        assert len(set(cube)) == 27
        assert cube.startswith("KRYPTOS")
        assert cube.endswith(FILLER)

    @pytest.mark.parametrize(
        "plaintext,keyword,period",
        [
            ("THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG", "KRYPTOS", 5),
            ("ATTACKATDAWNXX", "PALIMPSEST", 7),
            ("A", "ABSCISSA", 5),
            ("AB", "ABSCISSA", 5),
            (
                "THISISALONGERTESTMESSAGEFORROUNDTRIPPINGWITHVARIOUSLENGTHS",
                "KRYPTOSABSCISSA",
                13,
            ),
            ("X" * 97, "KRYPTOS", 97),
        ],
    )
    def test_encrypt_decrypt_roundtrip(self, plaintext, keyword, period):
        ct = trifid_encrypt(plaintext, keyword, period)
        assert trifid_decrypt(ct, keyword, period) == plaintext

    def test_roundtrip_survives_filler_symbol_in_ciphertext(self):
        # Regression: a naive isalpha()-only clean step would silently strip
        # FILLER out of a ciphertext block that legitimately contains it,
        # corrupting block boundaries on decrypt.
        plaintext = "X" * 11
        cube = build_cube_order("KRYPTOS")
        ct = trifid_encrypt(plaintext, "KRYPTOS", 11)
        assert FILLER in ct  # sanity: this specific case does produce a filler char
        assert trifid_decrypt(ct, "KRYPTOS", 11) == plaintext
        del cube  # only needed to assert the module-level constant is consistent


class TestNullResultArtifact:
    def test_null_result_artifact(self, tmp_path):
        artifact = tmp_path / "null.json"
        summary = run_trifid_attack(
            candidate_keywords=["KRYPTOS"],
            candidate_periods=[5, 7],
            null_artifact_path=artifact,
        )
        assert summary["status"] == "null_result"
        assert summary["attack"] == "P9_trifid"
        assert summary["run_params"]["total_tested"] == 2  # 1 keyword x 2 periods
        data = json.loads(artifact.read_text(encoding="utf-8"))
        assert data["attack"] == "P9_trifid"


class TestEurekaOnPlantedSolution:
    def test_eureka_on_planted_solution(self, tmp_path):
        plaintext_chars = list("A" * 97)
        plaintext_chars[21:25] = "EAST"
        plaintext_chars[25:34] = "NORTHEAST"
        plaintext_chars[63:69] = "BERLIN"
        plaintext_chars[69:74] = "CLOCK"
        plaintext = "".join(plaintext_chars)

        planted_ct = trifid_encrypt(plaintext, "KRYPTOS", 13)

        with pytest.raises(EurekaSignal) as excinfo:
            run_trifid_attack(
                ciphertext=planted_ct,
                candidate_keywords=["KRYPTOS"],
                candidate_periods=[13],
                null_artifact_path=tmp_path / "null.json",
                eureka_snapshot_path=tmp_path / "snap.md",
            )

        result = excinfo.value.result
        assert result["positional_crib_hits"] == 4
        assert result["key_info"]["keyword"] == "KRYPTOS"
        assert result["key_info"]["period"] == 13
        assert result["validation"]["promote"] is True
        assert result["validation"]["reproduced"] is True
