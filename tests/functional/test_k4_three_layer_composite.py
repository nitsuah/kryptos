"""Tests for the P1 three-layer composite attack."""

from __future__ import annotations

import json
from datetime import time
from pathlib import Path

import pytest

from kryptos.k4.three_layer_composite import (
    CIA_PRIORITY_TIMES,
    K4,
    _decrypt_three_layer,
    _mono_subst_decrypt,
    _vigenere_decrypt_std,
    run_three_layer_composite,
)
from kryptos.k4.eureka import EurekaSignal
from kryptos.k4.vigenere_key_recovery import KNOWN_KEYED_ALPHABETS

STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS_ALPHA = KNOWN_KEYED_ALPHABETS["KRYPTOS"]


# ---------------------------------------------------------------------------
# Unit: _mono_subst_decrypt
# ---------------------------------------------------------------------------
class TestMonoSubstDecrypt:
    def test_identity_with_standard_alphabet(self):
        assert _mono_subst_decrypt("HELLO", STANDARD) == "HELLO"

    def test_roundtrip_keyed_alphabet(self):
        # Encrypt: map each standard position to keyed alphabet position
        plain = "EAST"
        encrypted = "".join(KRYPTOS_ALPHA[STANDARD.index(c)] for c in plain)
        assert _mono_subst_decrypt(encrypted, KRYPTOS_ALPHA) == plain

    def test_non_alpha_passthrough(self):
        result = _mono_subst_decrypt("A B", STANDARD)
        assert " " in result

    def test_case_insensitive_input(self):
        lower = _mono_subst_decrypt("east", KRYPTOS_ALPHA)
        upper = _mono_subst_decrypt("EAST", KRYPTOS_ALPHA)
        assert lower == upper


# ---------------------------------------------------------------------------
# Unit: _vigenere_decrypt_std
# ---------------------------------------------------------------------------
class TestVigenereDecryptStd:
    def test_zero_shifts_identity(self):
        assert _vigenere_decrypt_std("EAST", [0, 0, 0, 0]) == "EAST"

    def test_single_shift(self):
        # B shifted down by 1 → A
        assert _vigenere_decrypt_std("B", [1]) == "A"

    def test_wrap_around(self):
        # A shifted down by 1 → Z
        assert _vigenere_decrypt_std("A", [1]) == "Z"

    def test_cyclic_shifts(self):
        result = _vigenere_decrypt_std("BCDE", [1])
        assert result == "ABCD"

    def test_roundtrip(self):
        from kryptos.k4.berlin_clock import apply_clock_shifts

        plain = "FINDTHEEAST"
        shifts = [3, 1, 4, 1, 5]
        encrypted = apply_clock_shifts(plain, shifts, decrypt=False)
        decrypted = _vigenere_decrypt_std(encrypted, shifts)
        assert decrypted == plain


# ---------------------------------------------------------------------------
# Unit: _decrypt_three_layer roundtrip
# ---------------------------------------------------------------------------
class TestDecryptThreeLayerRoundtrip:
    """Encrypt with known params, verify decrypt recovers the plaintext."""

    def _encrypt_three_layer(
        self, plain: str, n_cols: int, perm: list[int], clock_shifts: list[int], subst_alphabet: str
    ) -> str:
        from kryptos.k4.transposition_analysis import apply_columnar_permutation_encrypt

        # Layer 1: monoalphabetic substitution
        step1 = "".join(subst_alphabet[STANDARD.index(c)] if c in STANDARD else c for c in plain.upper())
        # Layer 2: clock-Vigenère
        step2 = "".join(
            STANDARD[(STANDARD.index(c) + clock_shifts[i % len(clock_shifts)]) % 26]
            if c.isalpha()
            else c
            for i, c in enumerate(step1)
        )
        # Layer 3: columnar transposition
        return apply_columnar_permutation_encrypt(step2, n_cols, perm)

    def test_identity_perm_zero_shifts_standard_alpha(self, tmp_path):
        plain = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:20]
        n_cols = 4
        perm = list(range(n_cols))
        shifts = [0] * 24
        ct = self._encrypt_three_layer(plain, n_cols, perm, shifts, STANDARD)
        recovered = _decrypt_three_layer(ct, n_cols, tuple(perm), shifts, STANDARD)
        assert recovered == plain

    def test_kryptos_alpha_nonzero_shifts(self, tmp_path):
        plain = "EASTBERLINNORTHEAST"
        n_cols = 5
        perm = [2, 0, 4, 1, 3]
        shifts = [7, 17, 3, 23]
        ct = self._encrypt_three_layer(plain, n_cols, perm, shifts, KRYPTOS_ALPHA)
        recovered = _decrypt_three_layer(ct, n_cols, tuple(perm), shifts, KRYPTOS_ALPHA)
        assert recovered == plain


# ---------------------------------------------------------------------------
# Integration: run_three_layer_composite (fast tiny params)
# ---------------------------------------------------------------------------
class TestRunThreeLayerComposite:
    def _tiny_params(self, tmp_path: Path) -> dict:
        return dict(
            subst_alphabets={"STANDARD": STANDARD},
            grid_sizes=[5],
            clock_step_seconds=43200,  # 2 clock states
            priority_clock_times=[],   # skip priority for speed
            max_perms_per_grid=6,
            null_artifact_path=tmp_path / "null.json",
            eureka_snapshot_path=tmp_path / "snap.md",
        )

    def test_returns_dict(self, tmp_path):
        result = run_three_layer_composite(K4, **self._tiny_params(tmp_path))
        assert isinstance(result, dict)

    def test_status_null_result(self, tmp_path):
        result = run_three_layer_composite(K4, **self._tiny_params(tmp_path))
        assert result["status"] == "null_result"

    def test_writes_null_artifact(self, tmp_path):
        params = self._tiny_params(tmp_path)
        run_three_layer_composite(K4, **params)
        assert Path(params["null_artifact_path"]).exists()

    def test_null_artifact_valid_json(self, tmp_path):
        params = self._tiny_params(tmp_path)
        run_three_layer_composite(K4, **params)
        data = json.loads(Path(params["null_artifact_path"]).read_text())
        assert "run_params" in data
        assert "best_candidates" in data
        assert data["run_params"]["attack"] == "P1_three_layer_composite"

    def test_total_candidates_positive(self, tmp_path):
        result = run_three_layer_composite(K4, **self._tiny_params(tmp_path))
        assert result["run_params"]["total_candidates_checked"] > 0

    def test_progress_callback_called(self, tmp_path):
        calls: list[dict] = []
        params = self._tiny_params(tmp_path)
        run_three_layer_composite(K4, **params, progress_cb=calls.append)
        assert len(calls) > 0
        assert "clock_time" in calls[0]
        assert "total_candidates" in calls[0]

    def test_priority_clock_times_listed_in_params(self, tmp_path):
        result = run_three_layer_composite(
            K4,
            subst_alphabets={"STANDARD": STANDARD},
            grid_sizes=[4],
            clock_step_seconds=43200,
            priority_clock_times=["13:00:00"],
            max_perms_per_grid=2,
            null_artifact_path=tmp_path / "null.json",
            eureka_snapshot_path=tmp_path / "snap.md",
        )
        assert "13:00:00" in result["run_params"]["priority_clock_times"]


# ---------------------------------------------------------------------------
# Eureka trigger (synthetic ciphertext)
# ---------------------------------------------------------------------------
class TestEurekaTrigger:
    """Encrypt plaintext with all three layers, then verify the sweep recovers it."""

    _PLAIN = ("EASTBERLINCLOCKBYNORTHEAST" + "X" * 72)[:97]
    _N_COLS = 5
    _CLOCK_TIME = "00:00:00"

    @staticmethod
    def _encrypt_three_layer(plain: str, n_cols: int, perm: list[int], clock_shifts: list[int]) -> str:
        from kryptos.k4.transposition_analysis import apply_columnar_permutation_encrypt

        # Layer 1: standard → standard mono-subst (identity for STANDARD alphabet)
        step1 = plain.upper()
        # Layer 2: clock-Vigenère encrypt (add shifts)
        step2 = "".join(
            STANDARD[(STANDARD.index(c) + clock_shifts[i % len(clock_shifts)]) % 26]
            if c.isalpha() else c
            for i, c in enumerate(step1)
        )
        # Layer 3: columnar transposition
        return apply_columnar_permutation_encrypt(step2, n_cols, perm)

    def _make_ct(self) -> str:
        from datetime import time
        from kryptos.k4.berlin_clock import full_berlin_clock_shifts

        shifts = full_berlin_clock_shifts(time(0, 0, 0))
        return self._encrypt_three_layer(self._PLAIN, self._N_COLS, list(range(self._N_COLS)), shifts)

    def test_eureka_raised_on_4_keyword_hit(self, tmp_path):
        ct = self._make_ct()
        with pytest.raises(EurekaSignal):
            run_three_layer_composite(
                ciphertext=ct,
                subst_alphabets={"STANDARD": STANDARD},
                grid_sizes=[self._N_COLS],
                clock_step_seconds=43200,  # covers 00:00:00 → all-zero-except-seconds shifts
                priority_clock_times=[],
                max_perms_per_grid=self._N_COLS,
                keyword_eureka_threshold=4,
                null_artifact_path=tmp_path / "null.json",
                eureka_snapshot_path=tmp_path / "snap.md",
            )

    def test_eureka_signal_carries_snapshot_path(self, tmp_path):
        ct = self._make_ct()
        snap = tmp_path / "snap.md"
        with pytest.raises(EurekaSignal) as exc_info:
            run_three_layer_composite(
                ciphertext=ct,
                subst_alphabets={"STANDARD": STANDARD},
                grid_sizes=[self._N_COLS],
                clock_step_seconds=43200,
                priority_clock_times=[],
                max_perms_per_grid=self._N_COLS,
                keyword_eureka_threshold=4,
                null_artifact_path=tmp_path / "null.json",
                eureka_snapshot_path=snap,
            )
        assert exc_info.value.snapshot_path is not None
        assert Path(exc_info.value.snapshot_path).exists()


# ---------------------------------------------------------------------------
# CIA priority timestamp coverage
# ---------------------------------------------------------------------------
class TestCIATimestamps:
    def test_default_priority_times_include_both_candidates(self):
        assert "13:00:00" in CIA_PRIORITY_TIMES
        assert "19:00:00" in CIA_PRIORITY_TIMES

    def test_priority_times_come_first_in_sequence(self, tmp_path):
        """Progress callback should see priority states before 00:00 hourly sweep."""
        calls: list[dict] = []
        run_three_layer_composite(
            K4,
            subst_alphabets={"STANDARD": STANDARD},
            grid_sizes=[4],
            clock_step_seconds=3600,
            max_perms_per_grid=1,
            null_artifact_path=tmp_path / "null.json",
            eureka_snapshot_path=tmp_path / "snap.md",
            progress_cb=calls.append,
        )
        # First two callbacks should be priority states
        assert calls[0]["is_priority"] is True
        assert calls[1]["is_priority"] is True
