import importlib.util
from pathlib import Path

import pytest


def test_create_pr_requires_token():
    mod_path = Path(__file__).resolve().parents[1] / 'scripts' / 'dev' / 'create_pr.py'
    spec = importlib.util.spec_from_file_location('create_pr', str(mod_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore

    with pytest.raises(ValueError):
        mod.create_pr('owner', 'repo', head='feature/no-token', token=None)
