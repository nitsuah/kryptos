"""Candidate reporting utilities for K4 analysis.

Writes ranked candidate decryptions to JSON (full detail) and optional CSV (summary).
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from collections.abc import Sequence
from datetime import datetime, timezone

from ..paths import ensure_reports_dir
from .scoring import baseline_stats


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _key_hash(key: Sequence[Sequence[int]]) -> str:
    flat = ",".join(str(v) for row in key for v in row)
    return hashlib.sha1(flat.encode("utf-8")).hexdigest()[:16]


def write_candidates_json(
    stage: str,
    cipher_label: str,
    ciphertext: str,
    candidates: list[dict],
    output_path: str | None = None,
    limit: int = 50,
    lineage: list[str] | None = None,
) -> str:
    """Write detailed candidate list (limited) to JSON. Returns path."""
    if output_path is None:
        base = ensure_reports_dir()
        output_path = str(base / "k4_candidates.json")
    _ensure_dir(os.path.dirname(output_path) or ".")
    ranked = sorted(candidates, key=lambda c: c.get("score", 0.0), reverse=True)[:limit]
    enriched = []
    for rank, cand in enumerate(ranked, start=1):
        text = cand.get("text", "")
        metrics = baseline_stats(text)
        key = cand.get("key")
        enriched.append(
            {
                "rank": rank,
                "score": cand.get("score"),
                "source": cand.get("source"),
                "key": key,
                "key_hash": _key_hash(key) if key else None,
                "text": text,
                "metrics": metrics,
                "origin_stage": stage,
                "candidate_lineage": cand.get("lineage") or lineage,
                "trace": cand.get("trace"),
            },
        )
    payload = {
        "cipher": cipher_label,
        "stage": stage,
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "ciphertext_prefix": ciphertext[:50],
        "candidate_count": len(enriched),
        "lineage": lineage,
        "candidates": enriched,
    }
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    return output_path


def write_candidates_csv(
    candidates: list[dict],
    output_path: str | None = None,
    limit: int = 50,
) -> str:
    """Write summary CSV: rank, score, source, key_hash, text_prefix. Returns path."""
    if output_path is None:
        base = ensure_reports_dir()
        output_path = str(base / "k4_candidates.csv")
    _ensure_dir(os.path.dirname(output_path) or ".")
    ranked = sorted(candidates, key=lambda c: c.get("score", 0.0), reverse=True)[:limit]
    with open(output_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["rank", "score", "source", "key_hash", "text_prefix"])
        for rank, cand in enumerate(ranked, start=1):
            key = cand.get("key")
            w.writerow(
                [
                    rank,
                    cand.get("score"),
                    cand.get("source"),
                    _key_hash(key) if key else "",
                    (cand.get("text", "")[:60]),
                ],
            )
    return output_path


def generate_candidate_artifacts(
    stage: str,
    cipher_label: str,
    ciphertext: str,
    candidates: list[dict],
    out_dir: str | None = None,
    limit: int = 50,
    write_csv: bool = True,
    lineage: list[str] | None = None,
    persist_db: bool | None = None,
) -> dict[str, str]:
    """Generate JSON (and optionally CSV) artifacts; return dict of paths.

    When ``persist_db`` is ``None`` (the default) the candidates are also
    mirrored to Neon if ``DATABASE_URL`` is configured; pass ``True``/``False``
    to force or skip that. DB persistence is best-effort and never affects the
    file artifacts. If a run is persisted, its id is returned under the
    ``'db_run_id'`` key.
    """
    if out_dir is None:
        out_dir = str(ensure_reports_dir())
    _ensure_dir(out_dir)
    json_path = os.path.join(out_dir, "k4_candidates.json")
    paths = {
        "json": write_candidates_json(stage, cipher_label, ciphertext, candidates, json_path, limit, lineage=lineage),
    }
    if write_csv:
        csv_path = os.path.join(out_dir, "k4_candidates.csv")
        paths["csv"] = write_candidates_csv(candidates, csv_path, limit)

    from ..persistence import db_enabled, persist_campaign_candidates

    if persist_db or (persist_db is None and db_enabled()):
        run_id = persist_campaign_candidates(stage, cipher_label, ciphertext, candidates, limit, lineage=lineage)
        if run_id is not None:
            paths["db_run_id"] = str(run_id)
    return paths


__all__ = ["write_candidates_json", "write_candidates_csv", "generate_candidate_artifacts"]
