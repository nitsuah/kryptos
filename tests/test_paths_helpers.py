import re

from kryptos import paths


def test_env_override_repo_root(tmp_path, monkeypatch):
    # clear cache then override
    paths.get_repo_root.cache_clear()  # type: ignore[attr-defined]
    monkeypatch.setenv(paths.ENV_ROOT, str(tmp_path))
    root = paths.get_repo_root()
    assert root == tmp_path
    art = paths.get_artifacts_root()
    assert art.parent == root


def test_reports_dir_structure():
    reports_dir = paths.ensure_reports_dir()
    # pattern artifacts/reports/YYYYMMDD/YYYYMMDDTHHMMSSZ
    rel = reports_dir.relative_to(paths.get_artifacts_root())
    parts = rel.parts
    assert len(parts) == 3  # reports / date / timestamp
    date_seg = parts[1]
    ts_seg = parts[2]
    assert re.match(r"^\d{8}$", date_seg)
    assert re.match(r"^\d{8}T\d{6}Z$", ts_seg)


def test_provenance_hash_stable():
    h1 = paths.provenance_hash("alpha", {"b": 2, "a": 1})
    h2 = paths.provenance_hash("alpha", {"a": 1, "b": 2})
    assert h1 == h2
    h3 = paths.provenance_hash("alpha", {"a": 1, "b": 3})
    assert h3 != h1


def test_cwd_repo_root_preferred_for_installed_package(tmp_path, monkeypatch):
    repo_root = tmp_path / 'repo'
    repo_root.mkdir()
    (repo_root / 'pyproject.toml').write_text('[project]\nname = "kryptos-test"\nversion = "0.0.0"\n', encoding='utf-8')

    fake_site_packages = tmp_path / 'site-packages' / 'kryptos'
    fake_site_packages.mkdir(parents=True)
    fake_module = fake_site_packages / 'paths.py'
    fake_module.write_text('# placeholder', encoding='utf-8')

    paths.get_repo_root.cache_clear()  # type: ignore[attr-defined]
    monkeypatch.delenv(paths.ENV_ROOT, raising=False)
    monkeypatch.chdir(repo_root)
    monkeypatch.setattr(paths, '__file__', str(fake_module))

    assert paths.get_repo_root() == repo_root
    assert paths.get_artifacts_root() == repo_root / 'artifacts'


def test_containment_and_no_root_level_artifacts(tmp_path):
    # Ensure helper-created artifacts live directly under repo root
    repo_root = paths.get_repo_root()
    artifacts_root = paths.get_artifacts_root()
    assert artifacts_root.parent == repo_root
    # No writes should appear outside repo (simulate an operation)
    _ = paths.get_logs_dir()
    _ = paths.get_decisions_dir()
    outside = repo_root.parent / 'artifacts'
    # If outside exists (legacy), ensure we did not modify it this test
    if outside.exists() and outside != artifacts_root:
        before = {p.name for p in outside.iterdir()}
        # write a file inside proper artifacts
        (artifacts_root / 'containment_test.txt').write_text('ok', encoding='utf-8')
        after = {p.name for p in outside.iterdir()}
        assert before == after
    else:
        assert not outside.exists() or outside == artifacts_root
