#!/usr/bin/env python3
"""Quick test of expanded Vigenère hypothesis."""

from kryptos.k4.constants import K4_CIPHERTEXT
from kryptos.k4.hypotheses import VigenereHypothesis

h = VigenereHypothesis(
    min_key_length=1,
    max_key_length=5,
    keys_per_length=2,
    explicit_keywords=['BERLIN', 'CLOCK', 'KRYPTOS'],
)

cands = h.generate_candidates(K4_CIPHERTEXT, limit=15)

print(f'Generated {len(cands)} candidates\n')
print('Top 5:')
for i, c in enumerate(cands[:5], 1):
    print(f'{i}. Score: {c.score:7.2f} | Key: {c.key_info["key"]:15s} | Explicit: {c.key_info.get("explicit", False)}')
    print(f'   {c.plaintext[:40]}...')
