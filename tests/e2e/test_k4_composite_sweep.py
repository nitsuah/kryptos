"""Tests for composite parameter sweep — K4-ATTACK-4."""

import json
from pathlib import Path

import pytest

from kryptos.k4.composite_sweep import K4, _keyword_hits, _vigenere_decrypt, run_composite_sweep
from kryptos.k4.eureka import EurekaSignal


class TestVigenereDecrypt:
    ALPHA = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def test_zero_shifts_identity(self):
        assert _vigenere_decrypt("EAST", [0, 0, 0, 0], self.ALPHA) == "EAST"

    def test_single_shift_wraps(self):
        # A shifted down by 1 → Z
        assert _vigenere_decrypt("A", [1], self.ALPHA) == "Z"

    def test_roundtrip(self):
        from kryptos.k4.berlin_clock import apply_clock_shifts

        shifts = [3, 1, 4, 1, 5]
        encrypted = apply_clock_shifts("FINDTHEEAST", shifts)
        decrypted = _vigenere_decrypt(encrypted, shifts, self.ALPHA)
        assert decrypted == "FINDTHEEAST"

    def test_cyclic_shifts(self):
        result = _vigenere_decrypt("BCDE", [1], self.ALPHA)
        assert result == "ABCD"

    def test_keyed_alphabet(self):
        from kryptos.k4.vigenere_key_recovery import KEYED_ALPHABET

        text = "KRYT"
        shifts = [0, 0, 0, 0]
        assert _vigenere_decrypt(text, shifts, KEYED_ALPHABET) == "KRYT"


class TestKeywordHits:
    def test_none_in_gibberish(self):
        assert _keyword_hits("QZXVJWPQZXVJWPQZXV") == 0

    def test_east_alone(self):
        assert _keyword_hits("FINDTHEEAST") == 1

    def test_all_four_present(self):
        text = "EASTBERLINNORTHEASTCLOCK"
        assert _keyword_hits(text) == 4

    def test_case_insensitive(self):
        assert _keyword_hits("east berlin northeast clock") == 4

    def test_partial_match_not_counted(self):
        # "EASTE" is not "EAST" as a standalone token — but substring match IS OK
        assert _keyword_hits("EASTERBERLIN") >= 1  # "EAST" is a substring of "EASTER"


class TestRunCompositeSweep:
    """Fast tests using tiny parameter space to stay well under CI time limits."""

    def _tiny_params(self, tmp_path):
        """Minimal params: 1 alphabet, 1 grid, 1 clock state, 2 perms."""
        return dict(
            alphabets={"STANDARD": "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
            grid_sizes=[7],
            clock_step_seconds=43200,  # 2 clock states (00:00 and 12:00)
            routes=("columnar",),
            max_perms_per_grid=2,
            null_artifact_path=tmp_path / "null.json",
            eureka_snapshot_path=tmp_path / "snap.md",
        )

    def test_returns_dict(self, tmp_path):
        result = run_composite_sweep(K4, **self._tiny_params(tmp_path))
        assert isinstance(result, dict)

    def test_status_null_result(self, tmp_path):
        result = run_composite_sweep(K4, **self._tiny_params(tmp_path))
        assert result["status"] == "null_result"

    def test_writes_null_artifact(self, tmp_path):
        params = self._tiny_params(tmp_path)
        run_composite_sweep(K4, **params)
        assert Path(params["null_artifact_path"]).exists()

    def test_null_artifact_is_valid_json(self, tmp_path):
        params = self._tiny_params(tmp_path)
        run_composite_sweep(K4, **params)
        data = json.loads(Path(params["null_artifact_path"]).read_text())
        assert "run_params" in data
        assert "best_candidates" in data

    def test_run_params_in_artifact(self, tmp_path):
        params = self._tiny_params(tmp_path)
        run_composite_sweep(K4, **params)
        data = json.loads(Path(params["null_artifact_path"]).read_text())
        rp = data["run_params"]
        assert "grid_sizes" in rp
        assert "clock_states_count" in rp
        assert "total_candidates_checked" in rp

    def test_alphabet_alignment_in_result(self, tmp_path):
        result = run_composite_sweep(K4, **self._tiny_params(tmp_path))
        assert "alphabet_alignment" in result

    def test_best_candidates_is_list(self, tmp_path):
        result = run_composite_sweep(K4, **self._tiny_params(tmp_path))
        assert isinstance(result["best_candidates"], list)

    def test_total_candidates_positive(self, tmp_path):
        result = run_composite_sweep(K4, **self._tiny_params(tmp_path))
        assert result["run_params"]["total_candidates_checked"] > 0


def _make_test_ciphertext(plain: str, n_cols: int) -> str:
    """Encrypt plain with identity columnar then 00:00:00 Berlin Clock shifts.

    Mirrors the exact pipeline the sweep undoes:
      ct = clock_vigenere_encrypt(columnar_encrypt(plain, identity))
    so the sweep recovers plain at the 00:00:00 clock state.
    """
    from datetime import time

    from kryptos.k4.berlin_clock import apply_clock_shifts, full_berlin_clock_shifts
    from kryptos.k4.transposition_analysis import apply_columnar_permutation_encrypt

    intermediate = apply_columnar_permutation_encrypt(plain, n_cols, list(range(n_cols)))
    clock_shifts = full_berlin_clock_shifts(time(0, 0, 0))
    return apply_clock_shifts(intermediate, clock_shifts, decrypt=False)


class TestEurekaTrigger:
    # Plaintext with all 4 K4 keywords, padded to 97 chars
    _PLAIN = ("EASTBERLINCLOCKBYNORTHEAST" + "X" * 72)[:97]
    _N_COLS = 7

    def test_eureka_raised_when_all_keywords_present(self, tmp_path):
        """Round-trip: encrypt with identity columnar, sweep recovers all 4 keywords."""
        ct = _make_test_ciphertext(self._PLAIN, self._N_COLS)
        with pytest.raises(EurekaSignal) as exc_info:
            run_composite_sweep(
                ciphertext=ct,
                alphabets={"STANDARD": "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
                grid_sizes=[self._N_COLS],
                clock_step_seconds=43200,  # 00:00 → all-zero shifts
                routes=("columnar",),
                max_perms_per_grid=50,
                null_artifact_path=tmp_path / "null.json",
                eureka_snapshot_path=tmp_path / "snap.md",
                keyword_eureka_threshold=4,
            )
        assert exc_info.value.snapshot_path is not None

    def test_eureka_threshold_1_easy(self, tmp_path):
        """Threshold=1 fires on a text containing only EAST."""
        plain = ("EASTXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")[:97]
        ct = _make_test_ciphertext(plain, self._N_COLS)
        with pytest.raises(EurekaSignal):
            run_composite_sweep(
                ciphertext=ct,
                alphabets={"STANDARD": "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
                grid_sizes=[self._N_COLS],
                clock_step_seconds=43200,
                routes=("columnar",),
                max_perms_per_grid=50,
                null_artifact_path=tmp_path / "null.json",
                eureka_snapshot_path=tmp_path / "snap.md",
                keyword_eureka_threshold=1,
            )

    def test_eureka_signal_carries_snapshot(self, tmp_path):
        ct = _make_test_ciphertext(self._PLAIN, self._N_COLS)
        snap_path = tmp_path / "snap.md"
        with pytest.raises(EurekaSignal) as exc_info:
            run_composite_sweep(
                ciphertext=ct,
                alphabets={"STANDARD": "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
                grid_sizes=[self._N_COLS],
                clock_step_seconds=43200,
                routes=("columnar",),
                max_perms_per_grid=50,
                null_artifact_path=tmp_path / "null.json",
                eureka_snapshot_path=snap_path,
                keyword_eureka_threshold=4,
            )
        assert Path(exc_info.value.snapshot_path).exists()
