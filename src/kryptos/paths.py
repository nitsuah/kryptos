"""Central path helpers ensuring all artifact/log writes remain inside the repo.

Primary helpers (cached):
    get_repo_root() -> Path
    get_artifacts_root() -> Path
    get_logs_dir() -> Path
    get_decisions_dir() -> Path
    get_tuning_runs_root() -> Path
    ensure_reports_dir() -> Path
    provenance_hash(text: str, meta: dict) -> str
    get_provenance_info() -> dict

Env override: KRYPTOS_REPO_ROOT can force a root for tests.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from functools import lru_cache
from pathlib import Path

ENV_ROOT = "KRYPTOS_REPO_ROOT"


@lru_cache(maxsize=1)
def get_repo_root() -> Path:
    override = os.environ.get(ENV_ROOT)
    if override:
        p = Path(override).resolve()
        if p.exists():
            return p
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[1]


def get_artifacts_root() -> Path:
    root = get_repo_root()
    art = root / "artifacts"
    art.mkdir(parents=True, exist_ok=True)
    return art


def get_logs_dir() -> Path:
    logs = get_artifacts_root() / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    return logs


def get_decisions_dir() -> Path:
    dec = get_artifacts_root() / "decisions"
    dec.mkdir(parents=True, exist_ok=True)
    return dec


def get_tuning_runs_root() -> Path:
    runs = get_artifacts_root() / "tuning_runs"
    runs.mkdir(parents=True, exist_ok=True)
    return runs


def ensure_reports_dir(ts: str | None = None) -> Path:
    root = get_artifacts_root()
    date_seg = datetime.utcnow().strftime("%Y%m%d")
    base = root / "reports" / date_seg
    base.mkdir(parents=True, exist_ok=True)
    if ts is None:
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    final = base / ts
    final.mkdir(parents=True, exist_ok=True)
    return final


def provenance_hash(text: str, meta: dict) -> str:
    hasher = hashlib.sha1()
    hasher.update(text.encode("utf-8"))
    try:
        meta_bytes = json.dumps(meta, sort_keys=True, separators=(",", ":")).encode("utf-8")
    except TypeError:
        meta_bytes = repr(meta).encode("utf-8")
    hasher.update(meta_bytes)
    return hasher.hexdigest()[:16]


def get_provenance_info(include_params: dict | None = None) -> dict:
    info = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "python_version": sys.version,
        "python_version_info": {
            "major": sys.version_info.major,
            "minor": sys.version_info.minor,
            "micro": sys.version_info.micro,
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "repo_root": str(get_repo_root()),
    }

    try:
        repo_root = get_repo_root()

        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            info["git_commit"] = result.stdout.strip()
        else:
            info["git_commit"] = None

        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            info["git_branch"] = result.stdout.strip()
        else:
            info["git_branch"] = None

        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            info["git_dirty"] = bool(result.stdout.strip())
        else:
            info["git_dirty"] = None

    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        info["git_commit"] = None
        info["git_branch"] = None
        info["git_dirty"] = None

    if include_params:
        info["params"] = include_params

    return info


__all__ = [
    "get_repo_root",
    "get_artifacts_root",
    "get_logs_dir",
    "get_decisions_dir",
    "get_tuning_runs_root",
    "ensure_reports_dir",
    "provenance_hash",
    "get_provenance_info",
]
