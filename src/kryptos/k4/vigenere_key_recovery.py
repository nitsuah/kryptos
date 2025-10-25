"""Vigenère key recovery methods for K4 cryptanalysis.

Implements frequency-based key recovery for Vigenère ciphers using
the Kryptos keyed alphabet.
"""

from __future__ import annotations

from collections import Counter

KEYED_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"

# Expected frequencies for English (approximate, based on standard corpus)
# Adjusted for Kryptos context
ENGLISH_FREQ = {
    'E': 0.127,
    'T': 0.091,
    'A': 0.082,
    'O': 0.075,
    'I': 0.070,
    'N': 0.067,
    'S': 0.063,
    'H': 0.061,
    'R': 0.060,
    'D': 0.043,
    'L': 0.040,
    'C': 0.028,
    'U': 0.028,
    'M': 0.024,
    'W': 0.024,
    'F': 0.022,
    'G': 0.020,
    'Y': 0.020,
    'P': 0.019,
    'B': 0.015,
    'V': 0.010,
    'K': 0.008,
    'J': 0.002,
    'X': 0.002,
    'Q': 0.001,
    'Z': 0.001,
}


def recover_key_by_frequency(ciphertext: str, key_length: int, top_n: int = 3) -> list[str]:
    """Recover Vigenère key using frequency analysis.

    Args:
        ciphertext: Ciphertext to analyze
        key_length: Known or suspected key length
        top_n: Return top N candidate keys

    Returns:
        List of candidate keys (most likely first)
    """
    # Clean ciphertext
    ct = ''.join(c for c in ciphertext.upper() if c.isalpha())

    if len(ct) < key_length:
        return []

    # Split into columns by key position
    columns = [[] for _ in range(key_length)]
    for i, char in enumerate(ct):
        columns[i % key_length].append(char)

    # Recover each key character by frequency analysis
    key_chars = []
    for column in columns:
        if not column:
            key_chars.append(['A'])  # Default fallback
            continue

        # Try each possible key character and score
        scores = []
        for k_char in KEYED_ALPHABET:
            k_idx = KEYED_ALPHABET.index(k_char)

            # Decrypt this column with this key char
            decrypted = []
            for c in column:
                try:
                    c_idx = KEYED_ALPHABET.index(c)
                    p_idx = (c_idx - k_idx) % len(KEYED_ALPHABET)
                    decrypted.append(KEYED_ALPHABET[p_idx])
                except ValueError:
                    continue

            # Score against English frequencies
            if decrypted:
                score = _score_english_frequency(''.join(decrypted))
                scores.append((score, k_char))

        # Get top candidates for this position
        scores.sort(reverse=True)
        key_chars.append([k for _, k in scores[:top_n]])

    # Generate candidate keys from top choices per position
    candidates = _generate_key_combinations(key_chars, max_keys=top_n)

    return candidates


def _score_english_frequency(text: str) -> float:
    """Score text against expected English letter frequencies.

    Args:
        text: Plaintext to score

    Returns:
        Score (higher = more English-like)
    """
    if not text:
        return 0.0

    # Count frequencies
    counts = Counter(text)
    total = len(text)

    # Chi-squared test against English
    chi_squared = 0.0
    for char in KEYED_ALPHABET:
        observed = counts.get(char, 0) / total
        expected = ENGLISH_FREQ.get(char, 0.001)
        chi_squared += ((observed - expected) ** 2) / expected

    # Return negative chi-squared (lower chi-squared = better match)
    return -chi_squared


def _generate_key_combinations(key_chars: list[list[str]], max_keys: int = 10) -> list[str]:
    """Generate key combinations from candidate characters at each position.

    Args:
        key_chars: List of candidate characters for each key position
        max_keys: Maximum number of keys to generate

    Returns:
        List of candidate keys
    """
    if not key_chars:
        return []

    # Start with first position
    keys = [[c] for c in key_chars[0]]

    # Add each subsequent position
    for position in key_chars[1:]:
        new_keys = []
        for key in keys:
            for char in position:
                new_keys.append(key + [char])
                if len(new_keys) >= max_keys * 10:  # Limit explosion
                    break
            if len(new_keys) >= max_keys * 10:
                break
        keys = new_keys

    # Convert to strings and limit
    result = [''.join(k) for k in keys[:max_keys]]
    return result


def recover_key_with_crib(
    ciphertext: str,
    crib: str,
    key_length: int,
    position: int | None = None,
) -> list[str]:
    """Recover Vigenère key using known plaintext (crib).

    Args:
        ciphertext: Ciphertext to analyze
        crib: Known plaintext word
        key_length: Known or suspected key length
        position: Optional known position of crib (tries all if None)

    Returns:
        List of candidate keys
    """
    ct = ''.join(c for c in ciphertext.upper() if c.isalpha())
    crib = ''.join(c for c in crib.upper() if c.isalpha())

    if len(crib) < key_length:
        return []

    positions = [position] if position is not None else range(len(ct) - len(crib) + 1)
    candidates = []

    for pos in positions:
        # Extract key from crib
        key_chars = [''] * key_length
        valid = True

        for i, plain_char in enumerate(crib):
            cipher_char = ct[pos + i]
            key_pos = (pos + i) % key_length

            try:
                p_idx = KEYED_ALPHABET.index(plain_char)
                c_idx = KEYED_ALPHABET.index(cipher_char)
                k_idx = (c_idx - p_idx) % len(KEYED_ALPHABET)
                k_char = KEYED_ALPHABET[k_idx]

                # Check consistency
                if key_chars[key_pos] == '':
                    key_chars[key_pos] = k_char
                elif key_chars[key_pos] != k_char:
                    valid = False
                    break
            except ValueError:
                valid = False
                break

        if valid and all(key_chars):
            key = ''.join(key_chars)
            if key not in candidates:
                candidates.append(key)

    return candidates


def test_key_recovery():
    """Quick test of key recovery."""
    # Simple test
    from kryptos.ciphers import vigenere_decrypt

    # Create a test ciphertext
    plaintext = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
    key = "SECRET"

    # Encrypt it (reverse of decrypt)
    ciphertext = ""
    for i, p in enumerate(plaintext):
        k = key[i % len(key)]
        p_idx = KEYED_ALPHABET.index(p)
        k_idx = KEYED_ALPHABET.index(k)
        c_idx = (p_idx + k_idx) % len(KEYED_ALPHABET)
        ciphertext += KEYED_ALPHABET[c_idx]

    print(f"Plaintext:  {plaintext}")
    print(f"Key:        {key}")
    print(f"Ciphertext: {ciphertext}")

    # Try to recover key
    recovered = recover_key_by_frequency(ciphertext, len(key), top_n=5)
    print(f"\nRecovered keys: {recovered[:3]}")

    # Test decryption with recovered keys
    for test_key in recovered[:3]:
        try:
            result = vigenere_decrypt(ciphertext, test_key)
            print(f"Key '{test_key}': {result[:40]}...")
        except (ValueError, KeyError) as e:
            print(f"Key '{test_key}': Failed - {e}")


if __name__ == "__main__":
    test_key_recovery()
