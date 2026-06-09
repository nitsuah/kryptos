"""Tests for systematic Beaufort cipher sweep against K4 (Attack 5)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from kryptos.k4.beaufort_sweep import (
    BEAUFORT_KEY_CANDIDATES,
    K4,
    KEYED_ALPHABET,
    STANDARD_ALPHABET,
    beaufort_decrypt_alphabet,
    run_beaufort_sweep,
)
from kryptos.k4.eureka import EurekaSignal


class TestBeaufortDecryptAlphabet:
    def test_reciprocal_property(self):
        """Beaufort encryption == decryption (reciprocal cipher)."""
        key = "KRYPTOS"
        plain = "HELLOWORLD"
        ct = beaufort_decrypt_alphabet(plain, key, STANDARD_ALPHABET)
        recovered = beaufort_decrypt_alphabet(ct, key, STANDARD_ALPHABET)
        assert recovered == plain

    def test_zero_key_shift(self):
        # Key 'A' = index 0 → P[i] = (0 - C[i]) mod 26 = -C[i] mod 26
        result = beaufort_decrypt_alphabet("A", "A", STANDARD_ALPHABET)
        assert result == "A"  # (0 - 0) mod 26 = 0 → A

    def test_single_char_kryptos_key(self):
        result = beaufort_decrypt_alphabet("A", "B", STANDARD_ALPHABET)
        assert len(result) == 1

    def test_empty_ciphertext(self):
        result = beaufort_decrypt_alphabet("", "KRYPTOS", STANDARD_ALPHABET)
        assert result == ""

    def test_keyed_alphabet_roundtrip(self):
        key = "PALIMPSEST"
        plain = "BERLIN"
        ct = beaufort_decrypt_alphabet(plain, key, KEYED_ALPHABET)
        recovered = beaufort_decrypt_alphabet(ct, key, KEYED_ALPHABET)
        assert recovered == plain

    def test_drops_chars_not_in_alphabet(self):
        result = beaufort_decrypt_alphabet("A B", "K", STANDARD_ALPHABET)
        assert len(result) == 2  # space dropped

    def test_known_beaufort_roundtrip_kryptos_key(self):
        key = "KRYPTOS"
        msg = "OBKRUOXOGHULBSOLI"
        ct = beaufort_decrypt_alphabet(msg, key, KEYED_ALPHABET)
        recovered = beaufort_decrypt_alphabet(ct, key, KEYED_ALPHABET)
        assert recovered == msg


class TestBeaufortKeyCandidates:
    def test_canonical_keys_present(self):
        for key in ("KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK"):
            assert key in BEAUFORT_KEY_CANDIDATES

    def test_all_candidates_non_empty(self):
        for key in BEAUFORT_KEY_CANDIDATES:
            assert len(key) > 0


class TestRunBeaufortSweep:
    def _tiny_params(self, tmp_path):
        return dict(
            key_candidates=["KRYPTOS", "BERLIN"],
            alphabets={"standard": STANDARD_ALPHABET},
            null_artifact_path=tmp_path / "null_beaufort.json",
            eureka_snapshot_path=tmp_path / "snap_beaufort.md",
        )

    def test_returns_dict(self, tmp_path):
        result = run_beaufort_sweep(K4, **self._tiny_params(tmp_path))
        assert isinstance(result, dict)

    def test_status_null_result(self, tmp_path):
        result = run_beaufort_sweep(K4, **self._tiny_params(tmp_path))
        assert result["status"] == "null_result"

    def test_attack_field(self, tmp_path):
        result = run_beaufort_sweep(K4, **self._tiny_params(tmp_path))
        assert result["attack"] == "beaufort_sweep"

    def test_writes_artifact(self, tmp_path):
        params = self._tiny_params(tmp_path)
        run_beaufort_sweep(K4, **params)
        assert Path(params["null_artifact_path"]).exists()

    def test_artifact_valid_json(self, tmp_path):
        params = self._tiny_params(tmp_path)
        run_beaufort_sweep(K4, **params)
        data = json.loads(Path(params["null_artifact_path"]).read_text())
        assert "run_params" in data
        assert "best_candidates" in data
        assert "key_candidates" in data["run_params"]
        assert "total_tested" in data["run_params"]

    def test_total_tested_equals_keys_times_alphabets(self, tmp_path):
        params = self._tiny_params(tmp_path)
        result = run_beaufort_sweep(K4, **params)
        # 2 keys × 1 alphabet = 2 tests
        assert result["run_params"]["total_tested"] == 2

    def test_best_candidates_is_list(self, tmp_path):
        result = run_beaufort_sweep(K4, **self._tiny_params(tmp_path))
        assert isinstance(result["best_candidates"], list)

    def test_full_sweep_all_keys_both_alphabets(self, tmp_path):
        result = run_beaufort_sweep(
            K4,
            null_artifact_path=tmp_path / "null_full.json",
            eureka_snapshot_path=tmp_path / "snap_full.md",
        )
        expected_tested = len(BEAUFORT_KEY_CANDIDATES) * 2  # 2 alphabets
        assert result["run_params"]["total_tested"] == expected_tested

    def test_eureka_raised_on_all_keywords(self, tmp_path):
        """Build a ciphertext that decrypts with key KRYPTOS to all 4 keywords."""
        plaintext = ("EASTBERLINCLOCKBYNORTHEAST" + "X" * 72)[:97]
        key = "KRYPTOS"
        # Encrypt with Beaufort (reciprocal, so encrypt = decrypt)
        ct = beaufort_decrypt_alphabet(plaintext, key, STANDARD_ALPHABET)

        with pytest.raises(EurekaSignal):
            run_beaufort_sweep(
                ct,
                key_candidates=["KRYPTOS"],
                alphabets={"standard": STANDARD_ALPHABET},
                null_artifact_path=tmp_path / "null_eur.json",
                eureka_snapshot_path=tmp_path / "snap_eur.md",
                keyword_eureka_threshold=4,
            )

    def test_eureka_snapshot_written(self, tmp_path):
        plaintext = ("EASTBERLINCLOCKBYNORTHEAST" + "X" * 72)[:97]
        key = "KRYPTOS"
        ct = beaufort_decrypt_alphabet(plaintext, key, STANDARD_ALPHABET)
        snap_path = tmp_path / "snap_eur2.md"

        with pytest.raises(EurekaSignal) as exc_info:
            run_beaufort_sweep(
                ct,
                key_candidates=["KRYPTOS"],
                alphabets={"standard": STANDARD_ALPHABET},
                null_artifact_path=tmp_path / "null_eur2.json",
                eureka_snapshot_path=snap_path,
                keyword_eureka_threshold=4,
            )
        assert Path(exc_info.value.snapshot_path).exists()

    def test_keyed_alphabet_sweep(self, tmp_path):
        result = run_beaufort_sweep(
            K4,
            key_candidates=["KRYPTOS"],
            alphabets={"keyed": KEYED_ALPHABET},
            null_artifact_path=tmp_path / "null_keyed.json",
            eureka_snapshot_path=tmp_path / "snap_keyed.md",
        )
        assert result["run_params"]["total_tested"] == 1
