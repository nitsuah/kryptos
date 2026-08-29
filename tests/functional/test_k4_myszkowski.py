"""Tests for kryptos.k4.myszkowski — P8 Myszkowski transposition."""

from __future__ import annotations

import json

import pytest

from kryptos.k4.eureka import EurekaSignal
from kryptos.k4.myszkowski import (
    keyword_to_myszkowski_groups,
    myszkowski_decrypt,
    myszkowski_encrypt,
    run_myszkowski_attack,
)


class TestPrimitives:
    def test_groups_reflect_repeated_letters(self):
        # ABSCISSA: distinct sorted letters A,B,C,I,S -> ranks 1,2,3,4,5
        assert keyword_to_myszkowski_groups("ABSCISSA") == [1, 2, 5, 3, 4, 5, 5, 1]

    def test_no_repeats_behaves_like_plain_columnar_group_of_singletons(self):
        # KRYPTOS has no repeated letters -> every group is a singleton.
        groups = keyword_to_myszkowski_groups("KRYPTOS")
        assert sorted(set(groups)) == list(range(1, 8))
        assert len(groups) == len(set(groups))

    @pytest.mark.parametrize(
        "plaintext,keyword",
        [
            ("THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG", "ABSCISSA"),
            ("ATTACKATDAWNXX", "PALIMPSEST"),
            ("A", "ABSCISSA"),
            ("AB", "ABSCISSA"),
            (
                "THISISALONGERTESTMESSAGEFORROUNDTRIPPINGWITHVARIOUSLENGTHS",
                "PALIMPSEST",
            ),
        ],
    )
    def test_encrypt_decrypt_roundtrip(self, plaintext, keyword):
        ct = myszkowski_encrypt(plaintext, keyword)
        assert myszkowski_decrypt(ct, keyword) == plaintext


class TestNullResultArtifact:
    def test_null_result_artifact(self, tmp_path):
        artifact = tmp_path / "null.json"
        summary = run_myszkowski_attack(null_artifact_path=artifact)
        assert summary["status"] == "null_result"
        assert summary["attack"] == "P8_myszkowski"
        assert summary["run_params"]["total_tested"] == 4  # 2 keywords x 2 directions
        data = json.loads(artifact.read_text(encoding="utf-8"))
        assert data["attack"] == "P8_myszkowski"


class TestEurekaOnPlantedSolution:
    def _planted_ciphertext(self, keyword: str) -> str:
        plaintext_chars = list("A" * 97)
        plaintext_chars[22:26] = "EAST"
        plaintext_chars[26:35] = "NORTHEAST"
        plaintext_chars[63:69] = "BERLIN"
        plaintext_chars[69:74] = "CLOCK"
        plaintext = "".join(plaintext_chars)
        return myszkowski_encrypt(plaintext, keyword)

    def test_eureka_on_planted_solution(self, tmp_path):
        planted_ct = self._planted_ciphertext("ABSCISSA")

        with pytest.raises(EurekaSignal) as excinfo:
            run_myszkowski_attack(
                ciphertext=planted_ct,
                candidate_keywords=["ABSCISSA"],
                null_artifact_path=tmp_path / "null.json",
                eureka_snapshot_path=tmp_path / "snap.md",
            )

        result = excinfo.value.result
        assert result["positional_crib_hits"] == 4
        assert result["key_info"]["keyword"] == "ABSCISSA"
        assert result["key_info"]["direction"] == "decrypt"
        assert result["validation"]["promote"] is True
        assert result["validation"]["reproduced"] is True

    def test_eureka_on_planted_solution_palimpsest(self, tmp_path):
        planted_ct = self._planted_ciphertext("PALIMPSEST")

        with pytest.raises(EurekaSignal) as excinfo:
            run_myszkowski_attack(
                ciphertext=planted_ct,
                candidate_keywords=["PALIMPSEST"],
                null_artifact_path=tmp_path / "null.json",
                eureka_snapshot_path=tmp_path / "snap.md",
            )

        result = excinfo.value.result
        assert result["key_info"]["keyword"] == "PALIMPSEST"
        assert result["validation"]["promote"] is True
