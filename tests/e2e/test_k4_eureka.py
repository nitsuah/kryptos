"""Tests for Eureka capture protocol (K4-ATTACK-6)."""

from pathlib import Path

import pytest

from kryptos.k4.eureka import EurekaSignal, check_eureka, eureka_check_and_capture, write_breakthrough_snapshot

K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"


class TestCheckEureka:
    def test_k4_passes_with_threshold_4(self):
        assert check_eureka(K4) is True

    def test_gibberish_fails(self):
        assert check_eureka("A" * 97) is False

    def test_threshold_1_easy_to_pass(self):
        # Any text that matches at least 1 crib
        assert check_eureka(K4, threshold=1) is True

    def test_threshold_above_4_never_passes(self):
        assert check_eureka(K4, threshold=5) is False


class TestWriteBreakthroughSnapshot:
    def test_creates_file(self, tmp_path):
        out = tmp_path / "snap.md"
        path = write_breakthrough_snapshot(K4, {"perm": [0, 1, 2]}, path=out)
        assert Path(path).exists()

    def test_file_contains_candidate_text(self, tmp_path):
        out = tmp_path / "snap.md"
        write_breakthrough_snapshot(K4, {}, path=out)
        content = Path(out).read_text()
        assert K4 in content

    def test_file_contains_crib_labels(self, tmp_path):
        out = tmp_path / "snap.md"
        write_breakthrough_snapshot(K4, {}, path=out)
        content = Path(out).read_text()
        for label in ["EAST", "NORTHEAST", "BERLIN", "CLOCK"]:
            assert label in content

    def test_key_info_serialised(self, tmp_path):
        out = tmp_path / "snap.md"
        key_info = {"perm": [3, 1, 0, 2], "n_cols": 10, "route": "ene_diagonal"}
        write_breakthrough_snapshot(K4, key_info, path=out)
        content = Path(out).read_text()
        assert "ene_diagonal" in content

    def test_extra_metadata_included(self, tmp_path):
        out = tmp_path / "snap.md"
        write_breakthrough_snapshot(K4, {}, extra={"sweep_run": "test123"}, path=out)
        content = Path(out).read_text()
        assert "test123" in content

    def test_returns_absolute_path_string(self, tmp_path):
        out = tmp_path / "snap.md"
        result = write_breakthrough_snapshot(K4, {}, path=out)
        assert isinstance(result, str)
        assert Path(result).is_absolute()


class TestEurekaCheckAndCapture:
    def test_miss_returns_none(self, tmp_path):
        out = tmp_path / "snap.md"
        result = eureka_check_and_capture("A" * 97, {}, snapshot_path=out, raise_signal=False)
        assert result is None
        assert not out.exists()

    def test_hit_writes_snapshot(self, tmp_path):
        out = tmp_path / "snap.md"
        result = eureka_check_and_capture(K4, {"test": True}, snapshot_path=out, raise_signal=False)
        assert result is not None
        assert out.exists()

    def test_hit_returns_result_dict(self, tmp_path):
        out = tmp_path / "snap.md"
        result = eureka_check_and_capture(K4, {}, snapshot_path=out, raise_signal=False)
        assert "candidate_text" in result
        assert "crib_summary" in result
        assert "snapshot_path" in result

    def test_raises_eureka_signal_by_default(self, tmp_path):
        out = tmp_path / "snap.md"
        with pytest.raises(EurekaSignal) as exc_info:
            eureka_check_and_capture(K4, {}, snapshot_path=out, raise_signal=True)
        assert exc_info.value.snapshot_path == str(out.resolve())

    def test_eureka_signal_carries_result(self, tmp_path):
        out = tmp_path / "snap.md"
        with pytest.raises(EurekaSignal) as exc_info:
            eureka_check_and_capture(K4, {"my_key": 42}, snapshot_path=out)
        assert exc_info.value.result["key_info"]["my_key"] == 42

    def test_partial_threshold(self, tmp_path):
        out = tmp_path / "snap.md"
        # threshold=1: K4 should trigger even with only 1 required
        result = eureka_check_and_capture(K4, {}, snapshot_path=out, threshold=1, raise_signal=False)
        assert result is not None
