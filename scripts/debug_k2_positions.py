"""Debug K2 per-position candidates."""

import sys

from kryptos.k4.vigenere_key_recovery import KEYED_ALPHABET, _score_english_frequency

sys.path.insert(0, 'tests')
from test_vigenere_key_recovery import K2_CIPHERTEXT, K2_KEY  # noqa: E402

# Clean and split into columns
ct = ''.join(c for c in K2_CIPHERTEXT.upper() if c.isalpha())
columns = [ct[i::8] for i in range(8)]

print(f"Target key: {K2_KEY}")
print(f"Ciphertext length: {len(ct)}\n")

for pos, (column, expected_char) in enumerate(zip(columns, K2_KEY)):
    print(f"Position {pos} (expected '{expected_char}'):")

    # Score all candidates
    scores = []
    for k_char in KEYED_ALPHABET:
        k_idx = KEYED_ALPHABET.index(k_char)
        decrypted = []
        for c in column:
            c_idx = KEYED_ALPHABET.index(c)
            p_idx = (c_idx - k_idx) % len(KEYED_ALPHABET)
            decrypted.append(KEYED_ALPHABET[p_idx])

        score = _score_english_frequency(''.join(decrypted))
        scores.append((score, k_char))

    scores.sort(reverse=True)

    # Show top 5
    for i, (score, char) in enumerate(scores[:5], 1):
        marker = ' <-- CORRECT' if char == expected_char else ''
        print(f"  {i}. {char}: {score:.2f}{marker}")

    # Find correct char position
    correct_rank = next((i for i, (_, c) in enumerate(scores) if c == expected_char), -1) + 1
    print(f"  Correct char '{expected_char}' is at rank #{correct_rank}\n")
