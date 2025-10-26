"""Vigenère key recovery methods for K4 cryptanalysis.

Implements frequency-based key recovery for Vigenère ciphers using
the Kryptos keyed alphabet.
"""

from __future__ import annotations

from collections import Counter

from kryptos.provenance.search_space import SearchSpaceTracker

KEYED_ALPHABET = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
STANDARD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

_spy_agent = None


def _get_spy_agent():
    global _spy_agent
    if _spy_agent is None:
        from kryptos.agents.spy import SpyAgent

        _spy_agent = SpyAgent()
    return _spy_agent


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
        seen = set()
        merged = []
        for key in keyed_results + standard_results:
            if key not in seen:
                seen.add(key)
                merged.append(key)
        return merged[:top_n]

    if alphabet is None:
        alphabet = KEYED_ALPHABET
    ct = ''.join(c for c in ciphertext.upper() if c.isalpha())

    if len(ct) < key_length:
        return []

    columns = [[] for _ in range(key_length)]
    for i, char in enumerate(ct):
        columns[i % key_length].append(char)

    key_chars = []
    for column in columns:
        if not column:
            key_chars.append(['A'])
            continue

        scores = []
        for k_char in alphabet:
            k_idx = alphabet.index(k_char)

            decrypted = []
            for c in column:
                try:
                    c_idx = alphabet.index(c)
                    p_idx = (c_idx - k_idx) % len(alphabet)
                    decrypted.append(alphabet[p_idx])
                except ValueError:
                    continue

            if decrypted:
                score = _score_english_frequency(''.join(decrypted))
                scores.append((score, k_char))

        scores.sort(reverse=True)
        per_position_candidates = 5 if use_spy_scoring else max(10, top_n)
        key_chars.append([k for _, k in scores[:per_position_candidates]])

    if use_spy_scoring:
        max_candidates = min(100, 5 ** min(len(key_chars), 4))
    else:
        max_candidates = 500_000

    candidates = _generate_key_combinations(key_chars, max_keys=max_candidates)

    candidates = _rank_by_word_likelihood(candidates)

    if use_spy_scoring and candidates:
        from kryptos.ciphers import vigenere_decrypt

        spy = _get_spy_agent()
        scored_candidates = []

        for key in candidates:
            try:
                plaintext = vigenere_decrypt(ciphertext, key)

                analysis = spy.analyze_candidate(plaintext)
                spy_score = analysis.get('pattern_score', 0.0)

                scored_candidates.append((spy_score, key))
            except (ValueError, KeyError):
                continue

        scored_candidates.sort(reverse=True)
        candidates = [key for _, key in scored_candidates[:top_n]]
    else:
        candidates = candidates[:top_n]

    if skip_tried:
        if tracker is None:
            tracker = SearchSpaceTracker()

        candidates_filtered = [k for k in candidates if not tracker.already_tried("vigenere", k)]

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
    if not candidates:
        return candidates

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

        if key in known_cipher_keys:
            score += 1000.0

        vowels = sum(1 for c in key if c in 'AEIOU')
        vowel_ratio = vowels / len(key) if key else 0
        if 0.2 <= vowel_ratio <= 0.4:
            score += 10.0

        consonant_run = 0
        for c in key:
            if c in 'AEIOU':
                consonant_run = 0
            else:
                consonant_run += 1
                if consonant_run >= 4:
                    score -= 20.0
                    break

        alternations = 0
        for i in range(len(key) - 1):
            is_vowel = [c in 'AEIOU' for c in key[i : i + 2]]
            if is_vowel[0] != is_vowel[1]:
                alternations += 1
        score += alternations * 2.0

        for i in range(len(key) - 2):
            if key[i] == key[i + 1] == key[i + 2]:
                score -= 15.0
                break

        scored.append((score, key))

    scored.sort(reverse=True)
    return [key for _, key in scored]


def _score_english_frequency(text: str) -> float:
    if not text:
        return 0.0

    counts = Counter(text)
    total = len(text)

    if total < 10:
        score = 0.0
        for char in KEYED_ALPHABET:
            observed = counts.get(char, 0) / total
            expected = ENGLISH_FREQ.get(char, 0.005)
            score -= abs(observed - expected)
        return score

    chi_squared = 0.0
    for char in KEYED_ALPHABET:
        observed = counts.get(char, 0) / total
        expected = ENGLISH_FREQ.get(char, 0.001)
        chi_squared += ((observed - expected) ** 2) / expected

    return -chi_squared


def _generate_key_combinations(key_chars: list[list[str]], max_keys: int = 10) -> list[str]:
    if not key_chars:
        return []

    import heapq

    initial = tuple(0 for _ in key_chars)
    initial_sum = sum(initial)

    heap = [(initial_sum, initial)]
    seen = {initial}
    result = []

    while heap and len(result) < max_keys:
        _, indices = heapq.heappop(heap)

        try:
            key = ''.join(key_chars[i][idx] for i, idx in enumerate(indices))
            result.append(key)
        except IndexError:
            continue

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

    if len(crib) < 3:
        return []

    positions = [position] if position is not None else range(len(ct) - len(crib) + 1)
    candidates: list[tuple[str, int, float]] = []

    for pos in positions:
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

        if len(positions_filled) == key_length:
            key = ''.join(key_chars)
            confidence = 1.0
            candidates.append((key, pos, confidence))
        elif len(positions_filled) >= key_length // 2:
            unfilled = [i for i in range(key_length) if key_chars[i] == '']

            completed_keys = _complete_partial_key(ct, key_chars, unfilled)
            for completed_key in completed_keys[:5]:
                confidence = len(positions_filled) / key_length
                candidates.append((completed_key, pos, confidence))

    candidates.sort(key=lambda x: (-x[2], x[1]))

    seen_keys = set()
    unique_candidates = []
    for key, pos, conf in candidates:
        if key not in seen_keys:
            seen_keys.add(key)
            unique_candidates.append((key, pos, conf))

    return unique_candidates


def _complete_partial_key(ciphertext: str, partial_key: list[str], unfilled_positions: list[int]) -> list[str]:
    if not unfilled_positions:
        return [''.join(partial_key)]

    key_length = len(partial_key)

    if len(unfilled_positions) <= 3:
        return _brute_force_complete(ciphertext, partial_key, unfilled_positions)

    completed = partial_key.copy()

    for pos in unfilled_positions:
        column = [ciphertext[i] for i in range(pos, len(ciphertext), key_length) if i < len(ciphertext)]

        if len(column) < 3:
            completed[pos] = 'K'
            continue

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
    from kryptos.agents.spy import SpyAgent
    from kryptos.ciphers import vigenere_decrypt

    freq_candidates = []

    def generate_combinations(pos_idx: int, current_key: list[str]) -> None:
        if pos_idx >= len(unfilled_positions):
            key_str = ''.join(current_key)
            try:
                plaintext = vigenere_decrypt(ciphertext, key_str)
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

    if len(ciphertext) < 100:
        top_n = min(500, len(freq_candidates))
    else:
        top_n = min(100, len(freq_candidates))

    freq_candidates.sort(reverse=True)
    top_freq = freq_candidates[:top_n]

    spy = SpyAgent()
    spy_candidates = []

    for _, key_str, plaintext in top_freq:
        analysis = spy.analyze_candidate(plaintext)
        spy_score = analysis['pattern_score']
        spy_candidates.append((spy_score, key_str))

    spy_candidates.sort(reverse=True)
    return [key for _, key in spy_candidates[:20]]


def test_key_recovery():
    from kryptos.ciphers import vigenere_decrypt

    plaintext = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
    key = "SECRET"

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

    recovered = recover_key_by_frequency(ciphertext, len(key), top_n=5)
    print(f"\nRecovered keys: {recovered[:3]}")

    for test_key in recovered[:3]:
        try:
            result = vigenere_decrypt(ciphertext, test_key)
            print(f"Key '{test_key}': {result[:40]}...")
        except (ValueError, KeyError) as e:
            print(f"Key '{test_key}': Failed - {e}")


if __name__ == "__main__":
    test_key_recovery()
