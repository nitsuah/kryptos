"""Debug script to check column scoring for K2."""

import sys

from kryptos.k4.vigenere_key_recovery import KEYED_ALPHABET, _score_english_frequency

sys.path.insert(0, 'tests')
from test_vigenere_key_recovery import K2_CIPHERTEXT, K2_KEY  # noqa: E402

# Clean ciphertext
ct = ''.join(c for c in K2_CIPHERTEXT.upper() if c.isalpha())

# Split into columns
columns = [[] for _ in range(8)]
for i, char in enumerate(ct):
    columns[i % 8].append(char)

print(f"K2 Key: {K2_KEY}")
print(f"Ciphertext length: {len(ct)}\n")

# Check columns 3 and 6 (0-indexed: 2 and 5)
for col_idx, expected_key in [(2, 'S'), (5, 'C')]:
    print("=" * 60)
    print(f"Column {col_idx + 1} (Expected key: '{expected_key}')")
    print("=" * 60)

    column = columns[col_idx]
    print(f"Column content (first 30): {''.join(column[:30])}")
    print(f"Column length: {len(column)}\n")

    # Try all keys and score
    scores = []
    for k_char in KEYED_ALPHABET:
        k_idx = KEYED_ALPHABET.index(k_char)

        # Decrypt column
        decrypted = []
        for c in column:
            c_idx = KEYED_ALPHABET.index(c)
            p_idx = (c_idx - k_idx) % len(KEYED_ALPHABET)
            decrypted.append(KEYED_ALPHABET[p_idx])

        score = _score_english_frequency(''.join(decrypted))
        scores.append((score, k_char, ''.join(decrypted[:20])))

    scores.sort(reverse=True)

    print("Top 15 candidates:")
    for i, (score, k_char, preview) in enumerate(scores[:15], 1):
        marker = " <-- CORRECT" if k_char == expected_key else ""
        print(f"{i:2}. {k_char} score={score:8.4f} preview={preview}{marker}")

    # Find correct key position
    correct_pos = next((i for i, (_, k, _) in enumerate(scores) if k == expected_key), -1)
    if correct_pos >= 0:
        print(f"\n'{expected_key}' is at position {correct_pos + 1}")
    else:
        print(f"\n'{expected_key}' not in top 25!")
    print()
