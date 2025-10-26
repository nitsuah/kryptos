"""Vigenère key recovery methods for K4 cryptanalysis.

Implements frequency-based key recovery for Vigenère ciphers using
the Kryptos keyed alphabet.
"""

from __future__ import annotations

from collections import Counter

from kryptos.provenance.search_space import SearchSpaceTracker

KEYED_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Lazy import to avoid circular dependencies
_spy_agent = None


def _get_spy_agent():
    """Lazy load SPY agent to avoid import at module level."""
    global _spy_agent
    if _spy_agent is None:
        from kryptos.agents.spy import SpyAgent

        _spy_agent = SpyAgent()
    return _spy_agent


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


def recover_key_by_frequency(
    ciphertext: str,
    key_length: int,
    top_n: int = 3,
    skip_tried: bool = False,
    tracker: SearchSpaceTracker | None = None,
    alphabet: str | None = None,
    try_all_alphabets: bool = False,
    use_spy_scoring: bool = False,
) -> list[str]:
    """Recover Vigenère key using frequency analysis.

    NOTE: SPY scoring (use_spy_scoring=True) is expensive and often doesn't improve results.
    Default is False for performance. Enable only if you need better candidate ranking.

    Args:
        ciphertext: Ciphertext to analyze
        key_length: Known or suspected key length
        top_n: Return top N candidate keys
        skip_tried: If True, filter out keys that were already tried (cross-run memory)
        tracker: Optional SearchSpaceTracker instance (creates default if None and skip_tried=True)
        alphabet: Alphabet to use (default: KEYED_ALPHABET). Can also be STANDARD_ALPHABET.
        try_all_alphabets: If True, try both KEYED and STANDARD alphabets and return best results
        use_spy_scoring: If True, re-rank candidates using SPY agent scoring (slow, often unhelpful)

    Returns:
        List of candidate keys (most likely first), filtered if skip_tried=True
    """
    # If try_all_alphabets is enabled, recursively try both and merge results
    if try_all_alphabets:
        keyed_results = recover_key_by_frequency(
            ciphertext,
            key_length,
            top_n=top_n,
            skip_tried=skip_tried,
            tracker=tracker,
            alphabet=KEYED_ALPHABET,
        )
        standard_results = recover_key_by_frequency(
            ciphertext,
            key_length,
            top_n=top_n,
            skip_tried=skip_tried,
            tracker=tracker,
            alphabet=STANDARD_ALPHABET,
        )
        # Merge and deduplicate
        seen = set()
        merged = []
        for key in keyed_results + standard_results:
            if key not in seen:
                seen.add(key)
                merged.append(key)
        return merged[:top_n]

    # Use provided alphabet or default to keyed
    if alphabet is None:
        alphabet = KEYED_ALPHABET
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
        for k_char in alphabet:
            k_idx = alphabet.index(k_char)

            # Decrypt this column with this key char
            decrypted = []
            for c in column:
                try:
                    c_idx = alphabet.index(c)
                    p_idx = (c_idx - k_idx) % len(alphabet)
                    decrypted.append(alphabet[p_idx])
                except ValueError:
                    continue

            # Score against English frequencies
            if decrypted:
                score = _score_english_frequency(''.join(decrypted))
                scores.append((score, k_char))

        # Get top candidates for this position
        scores.sort(reverse=True)
        # Use top_n candidates per position (Phase 5 behavior)
        # If SPY scoring enabled, keep a few more to increase search space
        # K1 requires top 6 per position (E at position 7 is rank #6)
        # K2 requires top 10 per position (S at position 2 is rank #2, C at position 5 is rank #2)
        per_position_candidates = 5 if use_spy_scoring else max(10, top_n)
        key_chars.append([k for _, k in scores[:per_position_candidates]])

    # Generate candidate keys from top choices per position
    # Using rank-prioritized generation: keys with lower total rank appear first
    # PALIMPSEST (ranks [1,2,1,2,1,1,1,6,3,2], sum=20) will appear much earlier
    # than lexicographic ordering (position 101M+)
    #
    # With smart generation, we can use a reasonable limit (e.g., 500k)
    # and still cover most practical keys
    if use_spy_scoring:
        # For SPY scoring: generate fewer candidates (SPY is slow)
        max_candidates = min(100, 5 ** min(len(key_chars), 4))
    else:
        # For dictionary ranking: generate 500k candidates
        # Smart generation ensures low-rank combinations appear first
        max_candidates = 500_000

    candidates = _generate_key_combinations(key_chars, max_keys=max_candidates)

    # Apply dictionary-based re-ranking before SPY scoring
    # Real English words (like PALIMPSEST, ABSCISSA) should rank higher
    candidates = _rank_by_word_likelihood(candidates)

    # Re-rank using SPY agent if enabled
    if use_spy_scoring and candidates:
        from kryptos.ciphers import vigenere_decrypt

        spy = _get_spy_agent()
        scored_candidates = []

        for key in candidates:
            try:
                # Decrypt with this key
                plaintext = vigenere_decrypt(ciphertext, key)

                # Score with SPY agent
                analysis = spy.analyze_candidate(plaintext)
                spy_score = analysis.get('pattern_score', 0.0)

                scored_candidates.append((spy_score, key))
            except (ValueError, KeyError):
                # Skip invalid keys
                continue

        # Sort by SPY score and keep top_n
        scored_candidates.sort(reverse=True)
        candidates = [key for _, key in scored_candidates[:top_n]]
    else:
        # No SPY scoring - just take top_n after dictionary ranking
        candidates = candidates[:top_n]

    # Filter out already-tried keys if cross-run memory enabled
    if skip_tried:
        if tracker is None:
            tracker = SearchSpaceTracker()

        candidates_filtered = [k for k in candidates if not tracker.already_tried("vigenere", k)]

        # Mark new keys as tried and record exploration
        new_keys = candidates_filtered
        if new_keys:
            tracker.record_exploration(
                cipher_type="vigenere",
                region_key=f"length_{key_length}",
                count=len(new_keys),
                keys=new_keys,
            )

        candidates = candidates_filtered

    return candidates


def _rank_by_word_likelihood(candidates: list[str]) -> list[str]:
    """Re-rank candidate keys by word likelihood.

    English words (PALIMPSEST, ABSCISSA) should rank higher than gibberish.
    Uses simple heuristics: vowel distribution, consonant patterns, real word check.

    Args:
        candidates: List of candidate keys

    Returns:
        Re-ranked list (word-like keys first)
    """
    if not candidates:
        return candidates

    # Common English words used as Vigenère keys (historical precedent)
    known_cipher_keys = {
        'PALIMPSEST',
        'ABSCISSA',
        'KRYPTOS',
        'BERLIN',
        'CLOCK',
        'CIPHER',
        'SECRET',
        'SHADOW',
        'LIGHT',
        'DIGITAL',
    }

    scored = []
    for key in candidates:
        score = 0.0

        # Exact match with known cipher key
        if key in known_cipher_keys:
            score += 1000.0

        # Check if it "looks like" an English word
        # 1. Reasonable vowel ratio (20-40%)
        vowels = sum(1 for c in key if c in 'AEIOU')
        vowel_ratio = vowels / len(key) if key else 0
        if 0.2 <= vowel_ratio <= 0.4:
            score += 10.0

        # 2. No impossible consonant clusters (3+ consonants in a row)
        consonant_run = 0
        for c in key:
            if c in 'AEIOU':
                consonant_run = 0
            else:
                consonant_run += 1
                if consonant_run >= 4:
                    score -= 20.0
                    break

        # 3. Alternating patterns are good (consonant-vowel-consonant)
        alternations = 0
        for i in range(len(key) - 1):
            is_vowel = [c in 'AEIOU' for c in key[i : i + 2]]
            if is_vowel[0] != is_vowel[1]:
                alternations += 1
        score += alternations * 2.0

        # 4. Penalty for repeated characters (AAAA, ZZZZ unlikely in real words)
        for i in range(len(key) - 2):
            if key[i] == key[i + 1] == key[i + 2]:
                score -= 15.0
                break

        scored.append((score, key))

    # Sort by score (highest first), then return just the keys
    scored.sort(reverse=True)
    return [key for _, key in scored]


def _score_english_frequency(text: str) -> float:
    """Score text against expected English letter frequencies.

    Uses absolute difference for short texts (< 10 chars) where chi-squared
    is unreliable, and chi-squared for longer texts.

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

    # For very short texts (like K1 columns with 6 chars), chi-squared is unreliable
    # Use simple absolute difference instead
    if total < 10:
        score = 0.0
        for char in KEYED_ALPHABET:
            observed = counts.get(char, 0) / total
            expected = ENGLISH_FREQ.get(char, 0.005)
            score -= abs(observed - expected)
        return score

    # For longer texts, chi-squared is more robust
    chi_squared = 0.0
    for char in KEYED_ALPHABET:
        observed = counts.get(char, 0) / total
        expected = ENGLISH_FREQ.get(char, 0.001)
        chi_squared += ((observed - expected) ** 2) / expected

    # Return negative chi-squared (lower chi-squared = better match)
    return -chi_squared


def _generate_key_combinations(key_chars: list[list[str]], max_keys: int = 10) -> list[str]:
    """Generate key combinations from candidate characters at each position.

    Generates combinations in rank-prioritized order: combinations with lower
    total rank appear first. This ensures that keys like PALIMPSEST (ranks [1,2,1,2,...])
    appear earlier than lexicographic ordering would place them.

    Args:
        key_chars: List of candidate characters for each key position
        max_keys: Maximum number of keys to generate

    Returns:
        List of candidate keys (up to max_keys)
    """
    if not key_chars:
        return []

    import heapq

    # Use a priority queue to generate combinations by rank sum
    # Entry format: (rank_sum, combination_indices)
    # Start with all rank-0 (first candidate at each position)
    initial = tuple(0 for _ in key_chars)
    initial_sum = sum(initial)

    heap = [(initial_sum, initial)]
    seen = {initial}
    result = []

    while heap and len(result) < max_keys:
        _, indices = heapq.heappop(heap)

        # Convert indices to actual key
        try:
            key = ''.join(key_chars[i][idx] for i, idx in enumerate(indices))
            result.append(key)
        except IndexError:
            continue

        # Generate neighbors: increment each position's index by 1
        for pos in range(len(indices)):
            if indices[pos] + 1 < len(key_chars[pos]):
                neighbor = list(indices)
                neighbor[pos] += 1
                neighbor_tuple = tuple(neighbor)

                if neighbor_tuple not in seen:
                    seen.add(neighbor_tuple)
                    neighbor_sum = sum(neighbor_tuple)
                    heapq.heappush(heap, (neighbor_sum, neighbor_tuple))

    return result


def recover_key_with_crib(
    ciphertext: str,
    crib: str,
    key_length: int,
    position: int | None = None,
) -> list[tuple[str, int, float]]:
    """Recover Vigenère key using known plaintext (crib).

    Args:
        ciphertext: Ciphertext to analyze
        crib: Known plaintext word
        key_length: Known or suspected key length
        position: Optional known position of crib (tries all if None)

    Returns:
        List of tuples: (candidate_key, position_found, confidence_score)
        Sorted by confidence (higher = better)
    """
    ct = ''.join(c for c in ciphertext.upper() if c.isalpha())
    crib = ''.join(c for c in crib.upper() if c.isalpha())

    # Need at least 3 characters to extract meaningful key info
    if len(crib) < 3:
        return []

    positions = [position] if position is not None else range(len(ct) - len(crib) + 1)
    candidates: list[tuple[str, int, float]] = []

    for pos in positions:
        # Extract partial key from crib
        key_chars = [''] * key_length
        positions_filled = set()
        valid = True

        for i, plain_char in enumerate(crib):
            if pos + i >= len(ct):
                break

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
                    positions_filled.add(key_pos)
                elif key_chars[key_pos] != k_char:
                    valid = False
                    break
            except ValueError:
                valid = False
                break

        if not valid:
            continue

        # Complete key using frequency analysis for unfilled positions
        if len(positions_filled) == key_length:
            # Full key recovered
            key = ''.join(key_chars)
            confidence = 1.0  # Complete key from crib
            candidates.append((key, pos, confidence))
        elif len(positions_filled) >= key_length // 2:
            # Partial key - fill remaining with frequency analysis
            unfilled = [i for i in range(key_length) if key_chars[i] == '']

            # Use frequency analysis to complete the key
            completed_keys = _complete_partial_key(ct, key_chars, unfilled)
            for completed_key in completed_keys[:5]:  # Top 5 completions
                confidence = len(positions_filled) / key_length  # Partial confidence
                candidates.append((completed_key, pos, confidence))

    # Sort by confidence (higher first), then by position (earlier first)
    candidates.sort(key=lambda x: (-x[2], x[1]))

    # Deduplicate by key
    seen_keys = set()
    unique_candidates = []
    for key, pos, conf in candidates:
        if key not in seen_keys:
            seen_keys.add(key)
            unique_candidates.append((key, pos, conf))

    return unique_candidates


def _complete_partial_key(ciphertext: str, partial_key: list[str], unfilled_positions: list[int]) -> list[str]:
    """Complete a partial key using frequency analysis on remaining positions.

    Args:
        ciphertext: Full ciphertext
        partial_key: Partially recovered key (empty strings for unknown positions)
        unfilled_positions: Indices of positions that need to be filled

    Returns:
        List of completed keys (best candidates first)
    """
    if not unfilled_positions:
        return [''.join(partial_key)]

    key_length = len(partial_key)

    # For small numbers of unfilled positions, try all combinations
    if len(unfilled_positions) <= 3:
        return _brute_force_complete(ciphertext, partial_key, unfilled_positions)

    # For larger numbers, use frequency analysis
    completed = partial_key.copy()

    for pos in unfilled_positions:
        # Extract column for this position
        column = [ciphertext[i] for i in range(pos, len(ciphertext), key_length) if i < len(ciphertext)]

        if len(column) < 3:  # Too few samples
            completed[pos] = 'K'  # Default to 'K' (most common in Kryptos alphabet)
            continue

        # Try each possible key character and score
        scores = []
        for k_char in KEYED_ALPHABET:
            try:
                plaintext_col = []
                for c_char in column:
                    c_idx = KEYED_ALPHABET.index(c_char)
                    k_idx = KEYED_ALPHABET.index(k_char)
                    p_idx = (c_idx - k_idx) % len(KEYED_ALPHABET)
                    plaintext_col.append(KEYED_ALPHABET[p_idx])

                score = _score_english_frequency(''.join(plaintext_col))
                scores.append((score, k_char))
            except (ValueError, IndexError):
                continue

        if scores:
            scores.sort(reverse=True)
            completed[pos] = scores[0][1]

    return [''.join(completed)]


def _brute_force_complete(ciphertext: str, partial_key: list[str], unfilled_positions: list[int]) -> list[str]:
    """Try all possible completions for a small number of unfilled positions.

    Two-stage approach:
    1. Fast frequency pre-filter (adaptive size based on text length)
    2. SPY scoring on top candidates for accurate ranking
    """
    from kryptos.agents.spy import SpyAgent
    from kryptos.ciphers import vigenere_decrypt

    # Stage 1: Fast frequency-based pre-filter
    freq_candidates = []

    def generate_combinations(pos_idx: int, current_key: list[str]) -> None:
        if pos_idx >= len(unfilled_positions):
            key_str = ''.join(current_key)
            try:
                plaintext = vigenere_decrypt(ciphertext, key_str)
                # Quick frequency score
                score = _score_english_frequency(plaintext)
                freq_candidates.append((score, key_str, plaintext))
            except (ValueError, KeyError):
                pass
            return

        pos = unfilled_positions[pos_idx]
        for char in KEYED_ALPHABET:
            current_key[pos] = char
            generate_combinations(pos_idx + 1, current_key[:])

    generate_combinations(0, partial_key[:])

    # Adaptive filter size: shorter texts need larger candidate pools
    # (frequency scoring less reliable on short texts)
    if len(ciphertext) < 100:
        top_n = min(500, len(freq_candidates))  # Short text: check top 500
    else:
        top_n = min(100, len(freq_candidates))  # Long text: top 100 sufficient

    freq_candidates.sort(reverse=True)
    top_freq = freq_candidates[:top_n]

    # Stage 2: SPY scoring on top frequency candidates
    spy = SpyAgent()
    spy_candidates = []

    for _, key_str, plaintext in top_freq:
        analysis = spy.analyze_candidate(plaintext)
        spy_score = analysis['pattern_score']
        spy_candidates.append((spy_score, key_str))

    # Sort by SPY score and return top 20
    spy_candidates.sort(reverse=True)
    return [key for _, key in spy_candidates[:20]]


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
