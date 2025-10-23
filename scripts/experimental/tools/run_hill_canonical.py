#!/usr/bin/env python3
"""DEPRECATED: thin wrapper around `k4.hill_constraints.decrypt_and_score`.

Replacement usage:
    from k4 import hill_constraints as hc  # type: ignore
    results = hc.decrypt_and_score(ciphertext, prune_3x3=True, partial_len=60, partial_min=-800.0)

Scheduled for removal after tests switch to adapter.
"""

import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
# ensure src is importable
if str(repo / 'src') not in sys.path:
    sys.path.insert(0, str(repo / 'src'))

try:
    from k4 import hill_constraints as hc  # type: ignore
except ImportError as e:
    print('Failed to import k4.hill_constraints (deprecated script):', e)
    raise

cfg = repo / 'config' / 'config.json'
cipher = None
if cfg.exists():
    try:
        data = json.loads(cfg.read_text(encoding='utf-8'))
        if isinstance(data, dict):
            cipher = data.get('K4') or data.get('K4_CIPHER')
    except Exception:
        cipher = None
if not cipher:
    cipher = 'OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR'

print('Running decrypt_and_score (prune_3x3=True) on ciphertext length', len(cipher))
results = hc.decrypt_and_score(cipher, prune_3x3=True, partial_len=60, partial_min=-800.0)
print('Found', len(results), 'candidate decryptions')

for i, r in enumerate(results[:10], start=1):
    score = r.get('score')
    source = r.get('source')
    text = (r.get('text') or '').replace('\n', ' ')
    snippet = text[:200]
    print(f"{i}. score={score:.6f} source={source} snippet={snippet}")
