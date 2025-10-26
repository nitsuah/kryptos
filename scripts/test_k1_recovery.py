"""Test K1 recovery with PALIMPSEST."""

import sys

from kryptos.k4.vigenere_key_recovery import recover_key_by_frequency

sys.path.insert(0, 'tests')
from test_vigenere_key_recovery import K1_CIPHERTEXT, K1_KEY  # noqa: E402

print("Recovering K1 key with dictionary ranking...")
keys = recover_key_by_frequency(K1_CIPHERTEXT, len(K1_KEY), top_n=10, use_spy_scoring=False)
print('Top 10 keys:')
for i, k in enumerate(keys, 1):
    marker = ' <-- CORRECT' if k == K1_KEY else ''
    print(f'{i}. {k}{marker}')

if K1_KEY in keys:
    pos = keys.index(K1_KEY) + 1
    print(f'\n✓ PALIMPSEST FOUND at position #{pos}')
else:
    print('\n✗ PALIMPSEST NOT FOUND')
