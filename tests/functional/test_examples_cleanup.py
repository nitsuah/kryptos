from __future__ import annotations

import time
from pathlib import Path

from kryptos.examples import purge_demo_artifacts


def _touch_tree(base: Path, name: str, delay: float = 0.0) -> Path:
    p = base / name
    (p / "sub").mkdir(parents=True, exist_ok=True)
    f = p / "sub" / "file.txt"
    f.write_text("x", encoding="utf-8")
    if delay:
        time.sleep(delay)
    return p


def test_purge_demo_artifacts_age_and_count(monkeypatch, tmp_path):
    # Redirect artifacts root
    monkeypatch.setenv("KRYPTOS_FORCE_ARTIFACTS_ROOT", str(tmp_path)) if hasattr(monkeypatch, "setenv") else None
    from kryptos import paths as kp

    monkeypatch.setattr(kp, "get_artifacts_root", lambda: tmp_path)
    demo_root = tmp_path / "demo"
    demo_root.mkdir()
    # Create 3 demo dirs with slight time differences
    d1 = _touch_tree(demo_root, "run_old")
    time.sleep(0.02)
    _touch_tree(demo_root, "run_mid")
    time.sleep(0.02)
    _touch_tree(demo_root, "run_new")

    # Simulate old by adjusting mtime of d1
    old_ts = time.time() - 3600 * 25  # > 24h
    for target in [d1] + list(d1.rglob('*')):
        try:
            import os

            os.utime(target, (old_ts, old_ts))
        except OSError:
            pass

    res = purge_demo_artifacts(max_age_hours=24, max_keep=2)
    # d1 should be age-purged, and of d2/d3 both kept due to max_keep=2
    removed_names = {p.name for p in res.removed}
    kept_names = {p.name for p in res.kept}
    assert "run_old" in removed_names
    assert kept_names == {"run_mid", "run_new"}
    # Directories actually gone
    assert not d1.exists()


def test_purge_demo_artifacts_count_only(monkeypatch, tmp_path):
    from kryptos import paths as kp

    monkeypatch.setattr(kp, "get_artifacts_root", lambda: tmp_path)
    demo_root = tmp_path / "demo"
    demo_root.mkdir()
    d1 = _touch_tree(demo_root, "a")
    time.sleep(0.01)
    _touch_tree(demo_root, "b")
    time.sleep(0.01)
    _touch_tree(demo_root, "c")
    res = purge_demo_artifacts(max_age_hours=None, max_keep=2)
    # Should keep newest two (b, c) and remove a
    removed_names = {p.name for p in res.removed}
    kept_names = {p.name for p in res.kept}
    assert removed_names == {"a"}
    assert kept_names == {"b", "c"}
    assert not d1.exists()
