"""Attempt log persistence utilities for K4 analysis.

Aggregates in-memory attempt logs from Hill, Berlin Clock, and transposition searches
and writes them to timestamped JSON artifact for post-run auditing.
"""
from __future__ import annotations
import os
import json
from datetime import datetime
from typing import Any
from .pipeline import get_hill_attempt_log, get_clock_attempt_log
from .transposition import get_transposition_attempt_log

DEF_LIMIT = 5000  # safety cap per category

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def persist_attempt_logs(
    out_dir: str = 'reports',
    label: str = 'K4',
    clear: bool = True,
    limit: int = DEF_LIMIT,
) -> str:
    """Persist collected attempt logs to JSON file. Returns file path.
    limit: maximum entries per category to write (older entries beyond limit are dropped).
    clear: if True, clears in-memory buffers after writing.
    """
    hill = get_hill_attempt_log(clear=False)
    clock = get_clock_attempt_log(clear=False)
    trans = get_transposition_attempt_log(clear=False)
    payload: dict[str, Any] = {
        'label': label,
        'generated_at': datetime.utcnow().isoformat() + 'Z',
        'counts': {
            'hill': len(hill),
            'clock': len(clock),
            'transposition': len(trans),
        },
        'hill_attempts': hill[:limit],
        'clock_attempts': clock[:limit],
        'transposition_attempts': trans[:limit],
    }
    _ensure_dir(out_dir)
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    path = os.path.join(out_dir, f'attempts_{label.lower()}_{ts}.json')
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2)
    if clear:
        # Clear only after successful write
        get_hill_attempt_log(clear=True)
        get_clock_attempt_log(clear=True)
        get_transposition_attempt_log(clear=True)
    return path

__all__ = ['persist_attempt_logs']
