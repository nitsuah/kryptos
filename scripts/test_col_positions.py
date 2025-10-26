import sys

from test_vigenere_key_recovery import K2_CIPHERTEXT

from kryptos.k4.vigenere_encrypt import KEYED_ALPHABET
from kryptos.k4.vigenere_key_recovery import _score_candidates_for_column

sys.path.insert(0, 'tests')

key_len = 8
target_key = "ABSCISSA"

for col_idx in [2, 5]:
    print(f'\nColumn {col_idx+1} (pos {col_idx}, expected {target_key[col_idx]}):')
    col_text = K2_CIPHERTEXT[col_idx::key_len]
    scored = _score_candidates_for_column(col_text, KEYED_ALPHABET)
    for i, (char, score) in enumerate(scored[:10], 1):
        mark = ' <<<' if char == target_key[col_idx] else ''
        print(f'  {i}. {char}: {score:.2f}{mark}')
