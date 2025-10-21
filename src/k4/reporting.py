"""Candidate reporting utilities for K4 analysis.

Writes ranked candidate decryptions to JSON (full detail) and optional CSV (summary).
"""
from __future__ import annotations

from collections.abc import Sequence
import os
import json
import csv
import hashlib
from datetime import datetime
from .scoring import baseline_stats

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def _key_hash(key: Sequence[Sequence[int]]) -> str:
    flat = ','.join(str(v) for row in key for v in row)
    return hashlib.sha1(flat.encode('utf-8')).hexdigest()[:16]

def write_candidates_json(
    stage: str,
    cipher_label: str,
    ciphertext: str,
    candidates: list[dict],
    output_path: str = 'reports/k4_candidates.json',
    limit: int = 50,
    lineage: list[str] | None = None,
) -> str:
    """Write detailed candidate list (limited) to JSON. Returns path."""
    _ensure_dir(os.path.dirname(output_path) or '.')
    ranked = sorted(candidates, key=lambda c: c.get('score', 0.0), reverse=True)[:limit]
    enriched = []
    for rank, cand in enumerate(ranked, start=1):
        text = cand.get('text', '')
        metrics = baseline_stats(text)
        key = cand.get('key')
        enriched.append({
            'rank': rank,
            'score': cand.get('score'),
            'source': cand.get('source'),
            'key': key,
            'key_hash': _key_hash(key) if key else None,
            'text': text,
            'metrics': metrics,
            'origin_stage': stage,
            'candidate_lineage': cand.get('lineage') or lineage,
            'trace': cand.get('trace'),
        })
    payload = {
        'cipher': cipher_label,
        'stage': stage,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'ciphertext_prefix': ciphertext[:50],
        'candidate_count': len(enriched),
        'lineage': lineage,
        'candidates': enriched,
    }
    with open(output_path, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2)
    return output_path

def write_candidates_csv(
    candidates: list[dict],
    output_path: str = 'reports/k4_candidates.csv',
    limit: int = 50,
) -> str:
    """Write summary CSV: rank, score, source, key_hash, text_prefix. Returns path."""
    _ensure_dir(os.path.dirname(output_path) or '.')
    ranked = sorted(candidates, key=lambda c: c.get('score', 0.0), reverse=True)[:limit]
    with open(output_path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['rank', 'score', 'source', 'key_hash', 'text_prefix'])
        for rank, cand in enumerate(ranked, start=1):
            key = cand.get('key')
            w.writerow([
                rank,
                cand.get('score'),
                cand.get('source'),
                _key_hash(key) if key else '',
                (cand.get('text', '')[:60]),
            ])
    return output_path

def generate_candidate_artifacts(
    stage: str,
    cipher_label: str,
    ciphertext: str,
    candidates: list[dict],
    out_dir: str = 'reports',
    limit: int = 50,
    write_csv: bool = True,
    lineage: list[str] | None = None,
) -> dict[str, str]:
    """Generate JSON (and optionally CSV) artifacts; return dict of paths."""
    _ensure_dir(out_dir)
    json_path = os.path.join(out_dir, 'k4_candidates.json')
    paths = {
        'json': write_candidates_json(stage, cipher_label, ciphertext, candidates, json_path, limit, lineage=lineage),
    }
    if write_csv:
        csv_path = os.path.join(out_dir, 'k4_candidates.csv')
        paths['csv'] = write_candidates_csv(candidates, csv_path, limit)
    return paths

__all__ = ['write_candidates_json', 'write_candidates_csv', 'generate_candidate_artifacts']
