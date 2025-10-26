"""Test if ABSCISSA is generated before dictionary ranking."""

import sys

from kryptos.k4.vigenere_key_recovery import KEYED_ALPHABET, _generate_key_combinations, _score_english_frequency

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

print("Top 5 per position:")
for i, chars in enumerate(key_chars):
    print(f"  Pos {i}: {chars}")

# Generate combinations
print("\nGenerating 5000 combinations...")
raw_candidates = _generate_key_combinations(key_chars, max_keys=5000)

print(f"Generated {len(raw_candidates)} keys")
if K2_KEY in raw_candidates:
    pos = raw_candidates.index(K2_KEY) + 1
    print(f"✓ ABSCISSA FOUND at position #{pos} (BEFORE dictionary ranking)")
else:
    print("✗ ABSCISSA NOT in raw candidates")
    print(f"First with 'ABS': {[k for k in raw_candidates if k.startswith('ABS')][:5]}")
