"""Tests for kryptos.k4.overnight_runner -- Phase 7 scheduled sweep runner."""

from __future__ import annotations

from kryptos.k4.eureka import EurekaSignal
from kryptos.k4.overnight_runner import PENDING_SWEEPS, run_all_pending_sweeps


def _stub_null(name: str):
    def _fn():
        return {"status": "null_result", "attack": name}

    return _fn


def _stub_eureka(name: str):
    def _fn():
        raise EurekaSignal(snapshot_path=f"/tmp/{name}.md", result={"candidate_text": "X" * 97})

    return _fn


class TestPendingSweepsRegistry:
    def test_registry_is_nonempty_and_callable(self):
        assert len(PENDING_SWEEPS) > 0
        for name, fn in PENDING_SWEEPS.items():
            assert callable(fn), name

    def test_consensus_scoring_runs_last(self):
        # cross_vector_consensus scans artifacts every other sweep writes --
        # it must not run before them.
        assert list(PENDING_SWEEPS.keys())[-1] == "cross_vector_consensus"


class TestRunAllPendingSweeps:
    def test_all_null_runs_every_sweep(self):
        sweeps = {"a": _stub_null("a"), "b": _stub_null("b"), "c": _stub_null("c")}
        result = run_all_pending_sweeps(sweeps=sweeps)
        assert result["status"] == "all_null"
        assert result["sweeps_run"] == ["a", "b", "c"]
        assert all(r["status"] == "null_result" for r in result["results"].values())

    def test_eureka_halts_remaining_sweeps(self):
        sweeps = {"a": _stub_null("a"), "b": _stub_eureka("b"), "c": _stub_null("c")}
        result = run_all_pending_sweeps(sweeps=sweeps)
        assert result["status"] == "breakthrough"
        assert result["breakthrough_sweep"] == "b"
        assert result["sweeps_run"] == ["a", "b"]
        assert "c" not in result["results"]

    def test_progress_callback_fires_per_sweep(self):
        calls: list[tuple[str, str]] = []
        sweeps = {"a": _stub_null("a")}
        run_all_pending_sweeps(sweeps=sweeps, progress_cb=lambda n, s: calls.append((n, s)))
        assert ("a", "starting") in calls
        assert ("a", "null_result") in calls
