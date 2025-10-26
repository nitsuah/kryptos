"""Test full K2 recovery with detailed output."""

import sys

from kryptos.k4.vigenere_key_recovery import (
    KEYED_ALPHABET,
    _generate_key_combinations,
    _rank_by_word_likelihood,
    _score_english_frequency,
)

sys.path.insert(0, 'tests')
from test_vigenere_key_recovery import K2_CIPHERTEXT, K2_KEY  # noqa: E402

# Clean and split into columns
ct = ''.join(c for c in K2_CIPHERTEXT.upper() if c.isalpha())
columns = [ct[i::8] for i in range(8)]

# Get top 5 candidates per position
key_chars = []
for column in columns:
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
    key_chars.append([k for _, k in scores[:5]])

# Generate 5000 combinations
raw_candidates = _generate_key_combinations(key_chars, max_keys=5000)
print(f"Generated {len(raw_candidates)} raw candidates")
print(f"ABSCISSA at position #{raw_candidates.index(K2_KEY) + 1} before ranking")

# Apply dictionary ranking
ranked_candidates = _rank_by_word_likelihood(raw_candidates)
print("\nAfter dictionary ranking:")
if K2_KEY in ranked_candidates:
    pos = ranked_candidates.index(K2_KEY) + 1
    print(f"ABSCISSA at position #{pos}")
    print("\nTop 20 after ranking:")
    for i, k in enumerate(ranked_candidates[:20], 1):
        marker = ' <-- CORRECT' if k == K2_KEY else ''
        print(f"  {i}. {k}{marker}")
else:
    print("ABSCISSA NOT FOUND (shouldn't happen!)")
