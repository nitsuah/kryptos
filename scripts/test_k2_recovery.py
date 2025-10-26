"""Quick test of K2 key recovery."""

import sys

from kryptos.k4.vigenere_key_recovery import recover_key_by_frequency

sys.path.insert(0, 'tests')
from test_vigenere_key_recovery import K2_CIPHERTEXT, K2_KEY  # noqa: E402

print("Recovering with dictionary ranking...")
keys = recover_key_by_frequency(K2_CIPHERTEXT, 8, top_n=10, use_spy_scoring=False)
print('Top 10 keys:')
for i, k in enumerate(keys, 1):
    marker = ' <-- CORRECT' if k == K2_KEY else ''
    print(f'{i}. {k}{marker}')

if K2_KEY in keys:
    pos = keys.index(K2_KEY) + 1
    print(f'\n✓ ABSCISSA FOUND at position #{pos}')
else:
    print('\n✗ ABSCISSA NOT FOUND')
