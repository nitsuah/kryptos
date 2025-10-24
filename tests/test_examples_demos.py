from __future__ import annotations

from pathlib import Path

from kryptos.examples import run_composite_demo, run_sections_demo


def test_run_composite_demo_creates_artifacts(tmp_path, monkeypatch):
    # Redirect artifacts root to tmp to avoid polluting real repo artifacts
    from kryptos import paths as kp

    monkeypatch.setattr(kp, "get_artifacts_root", lambda: tmp_path)
    out = run_composite_demo(limit=5)
    p = Path(out)
    assert p.exists() and p.is_dir(), "Composite demo did not create output directory"
    # Expect attempt logs file
    logs = list(p.glob("attempts_*.json"))
    assert logs, "Expected attempts log JSON files in composite demo output"


def test_run_sections_demo_structure():
    info = run_sections_demo()
    names = {d["name"] for d in info}
    # K1-K3 present, K4 omitted by default
    assert {"K1", "K2", "K3"}.issubset(names)
    assert "K4" not in names
    # Each entry has callable
    for entry in info:
        assert callable(entry["callable"])
