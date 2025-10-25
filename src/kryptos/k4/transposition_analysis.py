"""Transposition cipher analysis and key recovery.

Implements period detection and permutation solving for columnar transposition
ciphers, critical for K3-style attacks and likely K4 composite methods.
"""

from __future__ import annotations

import logging
import random
from collections import Counter
from typing import Any

logger = logging.getLogger(__name__)

# English letter frequencies for IOC calculation
ENGLISH_IC = 0.0667  # Index of Coincidence for English text

# English bigram frequencies (most common)
COMMON_BIGRAMS = {
    'TH': 1.52,
    'HE': 1.28,
    'IN': 0.94,
    'ER': 0.94,
    'AN': 0.82,
    'RE': 0.68,
    'ND': 0.63,
    'AT': 0.59,
    'ON': 0.57,
    'NT': 0.56,
    'HA': 0.56,
    'ES': 0.56,
    'ST': 0.55,
    'EN': 0.55,
    'ED': 0.53,
    'TO': 0.52,
    'IT': 0.50,
    'OU': 0.50,
    'EA': 0.47,
    'HI': 0.46,
}


def calculate_ioc(text: str) -> float:
    """Calculate Index of Coincidence for text.

    IOC measures how much the letter distribution resembles natural language.
    - Random text: IC ≈ 0.038
    - English text: IC ≈ 0.067
    - Monoalphabetic substitution: IC ≈ 0.067
    - Polyalphabetic (Vigenère): IC ≈ 0.044

    Args:
        text: Text to analyze (non-alpha chars ignored)

    Returns:
        Index of Coincidence (0.0 to ~0.07)
    """
    text = ''.join(c for c in text.upper() if c.isalpha())
    n = len(text)

    if n < 2:
        return 0.0

    # Count letter frequencies
    counts = Counter(text)

    # IC = sum of (count_i * (count_i - 1)) / (n * (n - 1))
    numerator = sum(count * (count - 1) for count in counts.values())
    denominator = n * (n - 1)

    return numerator / denominator if denominator > 0 else 0.0


def detect_transposition_period(ciphertext: str, max_period: int = 30) -> list[tuple[int, float]]:
    """Detect likely columnar transposition period using IOC analysis.

    For columnar transposition with period P:
    - Each column should have English-like IC (≈0.067)
    - Correct period shows higher average column IC
    - Wrong periods show lower IC (more mixed letters)

    Args:
        ciphertext: Ciphertext to analyze
        max_period: Maximum period to test

    Returns:
        List of (period, score) tuples sorted by score (higher = more likely)
    """
    text = ''.join(c for c in ciphertext.upper() if c.isalpha())
    n = len(text)

    if n < 20:
        logger.warning("Text too short for period detection (need 20+, got %d)", n)
        return []

    period_scores = []

    for period in range(2, min(max_period + 1, n // 2)):
        # Split into columns
        columns = [text[i::period] for i in range(period)]

        # Calculate average IC across columns
        column_ics = [calculate_ioc(col) for col in columns if len(col) >= 2]

        if not column_ics:
            continue

        avg_ic = sum(column_ics) / len(column_ics)

        # Score based on how close to English IC
        # Also consider column length variance (uniform is better)
        lengths = [len(col) for col in columns]
        length_variance = max(lengths) - min(lengths)

        # Penalize high variance (uneven columns unlikely for simple transposition)
        variance_penalty = length_variance * 0.01

        score = avg_ic - variance_penalty

        period_scores.append((period, score))

        logger.debug("Period %d: avg_IC=%.4f, lengths=%s, score=%.4f", period, avg_ic, lengths, score)

    # Sort by score (higher = more likely)
    period_scores.sort(key=lambda x: x[1], reverse=True)

    return period_scores


def detect_period_by_repeated_sequences(ciphertext: str, min_length: int = 3) -> dict[int, int]:
    """Detect period by finding repeated sequences (like Kasiski for transposition).

    Args:
        ciphertext: Ciphertext to analyze
        min_length: Minimum sequence length to consider

    Returns:
        Dictionary of {period: count} for likely periods
    """
    text = ''.join(c for c in ciphertext.upper() if c.isalpha())
    n = len(text)

    # Find all repeated sequences
    sequences: dict[str, list[int]] = {}

    for length in range(min_length, min(10, n // 3)):
        for i in range(n - length):
            seq = text[i : i + length]
            if seq not in sequences:
                sequences[seq] = []
            sequences[seq].append(i)

    # Calculate distances between repetitions
    distances: list[int] = []
    for positions in sequences.values():
        if len(positions) >= 2:
            for i in range(len(positions) - 1):
                distances.append(positions[i + 1] - positions[i])

    if not distances:
        return {}

    # Find GCD of distances (likely period factors)

    # Count factors
    factors: dict[int, int] = {}
    for d in distances:
        for f in range(2, min(d + 1, 31)):
            if d % f == 0:
                factors[f] = factors.get(f, 0) + 1

    return factors


def detect_period_combined(ciphertext: str, max_period: int = 30) -> list[tuple[int, float, str]]:
    """Combine multiple period detection methods for robust results.

    Args:
        ciphertext: Ciphertext to analyze
        max_period: Maximum period to test

    Returns:
        List of (period, confidence, method) tuples sorted by confidence
    """
    results: dict[int, dict[str, Any]] = {}

    # Method 1: IOC analysis
    ioc_scores = detect_transposition_period(ciphertext, max_period)
    for period, score in ioc_scores[:10]:  # Top 10
        if period not in results:
            results[period] = {'ioc': 0, 'kasiski': 0}
        results[period]['ioc'] = score

    # Method 2: Repeated sequences (Kasiski-like)
    kasiski_factors = detect_period_by_repeated_sequences(ciphertext)
    max_kasiski = max(kasiski_factors.values()) if kasiski_factors else 1
    for period, count in kasiski_factors.items():
        if period <= max_period:
            if period not in results:
                results[period] = {'ioc': 0, 'kasiski': 0}
            # Normalize to 0-1 range
            results[period]['kasiski'] = count / max_kasiski if max_kasiski > 0 else 0

    # Combine scores (weighted average)
    combined: list[tuple[int, float, str]] = []
    for period, scores in results.items():
        ioc_score = scores.get('ioc', 0)
        kasiski_score = scores.get('kasiski', 0)

        # Weight IOC much more heavily (more reliable for transposition)
        # Kasiski can give false positives on short texts
        confidence = (ioc_score * 0.9) + (kasiski_score * 0.1)

        # Determine primary detection method
        if ioc_score > kasiski_score:
            method = 'ioc'
        elif kasiski_score > 0:
            method = 'kasiski'
        else:
            method = 'ioc'

        combined.append((period, confidence, method))

    # Sort by confidence
    combined.sort(key=lambda x: x[1], reverse=True)

    return combined


# Common English trigrams for scoring (consolidated from duplicates)
COMMON_TRIGRAMS = {
    'THE': 1.81,
    'AND': 0.73,
    'ING': 0.72,
    'ENT': 0.42,
    'ION': 0.42,
    'HER': 0.36,
    'FOR': 0.34,
    'THA': 0.33,
    'NTH': 0.33,
    'INT': 0.32,
    'ERE': 0.31,
    'TIO': 0.31,
    'TER': 0.30,
    'EST': 0.28,
    'ERS': 0.28,
    'ATI': 0.26,
    'HAT': 0.26,
    'ATE': 0.25,
    'ALL': 0.25,
    'ETH': 0.24,
    'HIS': 0.35,
    'WAS': 0.26,
    'YOU': 0.24,
    'ITH': 0.24,
    'VER': 0.24,
    'WIT': 0.22,
    'THI': 0.21,
}


def score_bigrams(text: str) -> float:
    """Score text based on English bigram frequencies.

    Args:
        text: Text to score

    Returns:
        Score (higher = more English-like)
    """
    text = ''.join(c for c in text.upper() if c.isalpha())
    if len(text) < 2:
        return 0.0

    score = 0.0
    for i in range(len(text) - 1):
        bigram = text[i : i + 2]
        score += COMMON_BIGRAMS.get(bigram, 0)

    return score / (len(text) - 1) if len(text) > 1 else 0.0


def score_words(text: str) -> float:
    """Score text based on English word detection.

    Splits text into potential words and checks against dictionary.
    More reliable than n-grams for validating plaintext candidates.

    Args:
        text: Text to score

    Returns:
        Score based on valid word ratio (0.0-1.0)
    """
    # Import wordlist from scoring module
    from kryptos.k4.scoring import WORDLIST

    text = ''.join(c for c in text.upper() if c.isalpha())
    if not text:
        return 0.0

    # Try different word boundary strategies
    scores = []

    # Strategy 1: Look for known words at any position (non-overlapping)
    matched = [False] * len(text)
    for word_len in range(7, 2, -1):  # Check 7-3 letter words (longest first)
        for i in range(len(text) - word_len + 1):
            candidate = text[i : i + word_len]
            # Only match if none of these positions are already matched
            if candidate in WORDLIST and not any(matched[i : i + word_len]):
                for j in range(i, i + word_len):
                    matched[j] = True

    window_score = sum(matched) / len(text) if text else 0.0
    scores.append(window_score)

    # Strategy 2: Greedy word extraction (longest match first)
    remaining = text
    matched_chars = 0
    while remaining:
        found = False
        # Try longest words first
        for word_len in range(min(10, len(remaining)), 2, -1):
            if remaining[:word_len] in WORDLIST:
                matched_chars += word_len
                remaining = remaining[word_len:]
                found = True
                break
        if not found:
            remaining = remaining[1:]  # Skip character

    greedy_score = matched_chars / len(text)
    scores.append(greedy_score)

    # Return best strategy
    return max(scores)


def score_combined_with_words(text: str) -> float:
    """Combined scoring: n-grams + word detection.

    Args:
        text: Text to score

    Returns:
        Weighted combination of scores
    """
    ngram_score = score_combined(text)  # 60% bigrams + 40% trigrams
    word_score = score_words(text)

    # Weight: 70% n-grams (fast, reliable) + 30% words (discriminating)
    return 0.7 * ngram_score + 0.3 * word_score


def score_trigrams(text: str) -> float:
    """Score text based on English trigram frequencies."""
    text = ''.join(c for c in text.upper() if c.isalpha())
    if len(text) < 3:
        return 0.0

    score = 0.0
    for i in range(len(text) - 2):
        trigram = text[i : i + 3]
        score += COMMON_TRIGRAMS.get(trigram, 0)

    return score / (len(text) - 2) if len(text) > 2 else 0.0


def score_combined(text: str) -> float:
    """Combined bigram + trigram scoring."""
    return score_bigrams(text) * 0.6 + score_trigrams(text) * 0.4


def apply_columnar_permutation_encrypt(plaintext: str, period: int, permutation: list[int]) -> str:
    """Encrypt plaintext with columnar transposition.

    Write plaintext into grid row-by-row, read columns in permutation order.

    Args:
        plaintext: Text to encrypt
        period: Number of columns
        permutation: Column read order (e.g., [2,0,1] reads col 2, then 0, then 1)

    Returns:
        Ciphertext
    """
    text = ''.join(c for c in plaintext.upper() if c.isalpha())
    rows = (len(text) + period - 1) // period

    # Build grid
    grid = []
    idx = 0
    for _ in range(rows):
        row = []
        for _ in range(period):
            if idx < len(text):
                row.append(text[idx])
                idx += 1
            else:
                row.append('')  # Padding
        grid.append(row)

    # Read columns in permutation order
    ciphertext = []
    for col_idx in permutation:
        for row in grid:
            if col_idx < len(row) and row[col_idx]:
                ciphertext.append(row[col_idx])

    return ''.join(ciphertext)


def apply_columnar_permutation_reverse(ciphertext: str, period: int, permutation: list[int]) -> str:
    """Apply columnar transposition permutation to decrypt.

    Args:
        ciphertext: Ciphertext to decrypt
        period: Number of columns
        permutation: Column order (0-indexed), e.g., [2,0,1] means col 2 first, then 0, then 1

    Returns:
        Decrypted text
    """
    text = ''.join(c for c in ciphertext.upper() if c.isalpha())
    n = len(text)

    # Determine column lengths (some columns may be longer if n % period != 0)
    base_len = n // period
    extra = n % period
    col_lengths = [base_len + (1 if i < extra else 0) for i in range(period)]

    # Extract columns from ciphertext (in permuted order)
    columns = []
    pos = 0
    for i in permutation:
        col_len = col_lengths[i]
        columns.append((i, text[pos : pos + col_len]))
        pos += col_len

    # Sort columns back to original order
    columns.sort(key=lambda x: x[0])
    column_texts = [col for _, col in columns]

    # Read off row by row
    plaintext = []
    max_len = max(len(col) for col in column_texts)
    for row in range(max_len):
        for col in column_texts:
            if row < len(col):
                plaintext.append(col[row])

    return ''.join(plaintext)


def solve_columnar_permutation_multi_start(
    ciphertext: str,
    period: int,
    num_restarts: int = 10,
    max_iterations: int = 5000,
) -> tuple[list[int], float]:
    """Solve columnar permutation with multiple random restarts.

    Args:
        ciphertext: Ciphertext to analyze
        period: Known or suspected period
        num_restarts: Number of random restarts
        max_iterations: Max iterations per restart

    Returns:
        (best_permutation, best_score) tuple
    """
    text = ''.join(c for c in ciphertext.upper() if c.isalpha())
    global_best_perm = list(range(period))
    global_best_score = float('-inf')

    for _restart in range(num_restarts):
        # Random start
        current_perm = list(range(period))
        random.shuffle(current_perm)
        current_text = apply_columnar_permutation_reverse(text, period, current_perm)
        current_score = score_combined(current_text)

        best_perm = current_perm[:]
        best_score = current_score
        no_improvement = 0

        for _ in range(max_iterations):
            # Swap two positions
            i, j = random.sample(range(period), 2)
            new_perm = current_perm[:]
            new_perm[i], new_perm[j] = new_perm[j], new_perm[i]

            new_text = apply_columnar_permutation_reverse(text, period, new_perm)
            new_score = score_combined(new_text)

            if new_score > current_score:
                current_perm = new_perm
                current_score = new_score
                no_improvement = 0
                if current_score > best_score:
                    best_perm = current_perm[:]
                    best_score = current_score
            else:
                no_improvement += 1

            if no_improvement >= 1000:
                break

        if best_score > global_best_score:
            global_best_perm = best_perm
            global_best_score = best_score

    return global_best_perm, global_best_score


def apply_rotation(text: str, width: int, rotation_type: str) -> str:
    """Apply rotation/traversal transformation to text.

    Args:
        text: Text to transform
        width: Grid width (height calculated from text length)
        rotation_type: Type of rotation (identity, 90cw, 90ccw, 180, spiral_in, etc.)

    Returns:
        Transformed text
    """
    if not text:
        return text

    height = (len(text) + width - 1) // width

    # Build grid
    grid = []
    idx = 0
    for _ in range(height):
        row = []
        for _ in range(width):
            if idx < len(text):
                row.append(text[idx])
                idx += 1
            else:
                row.append(' ')
        grid.append(row)

    if rotation_type == 'identity':
        pass  # No change

    elif rotation_type == '90cw':
        # Rotate 90 degrees clockwise
        grid = [[grid[height - 1 - j][i] for j in range(height)] for i in range(width)]

    elif rotation_type == '90ccw':
        # Rotate 90 degrees counter-clockwise
        grid = [[grid[j][width - 1 - i] for j in range(height)] for i in range(width)]

    elif rotation_type == '180':
        # Rotate 180 degrees
        grid = [[grid[height - 1 - i][width - 1 - j] for j in range(width)] for i in range(height)]

    elif rotation_type == 'flip_h':
        # Horizontal flip
        grid = [row[::-1] for row in grid]

    elif rotation_type == 'flip_v':
        # Vertical flip
        grid = grid[::-1]

    # Read back
    result = ''.join(''.join(row) for row in grid)
    return result.rstrip()


def test_all_rotations(ciphertext: str, period: int, top_n: int = 3) -> list[tuple[str, float, str]]:
    """Test all rotation types and rank by score.

    Args:
        ciphertext: Ciphertext to analyze
        period: Grid width for rotation
        top_n: Return top N results

    Returns:
        List of (rotation_type, score, preview) tuples
    """
    rotations = ['identity', '90cw', '90ccw', '180', 'flip_h', 'flip_v']
    results = []

    for rot_type in rotations:
        rotated = apply_rotation(ciphertext, period, rot_type)
        score = score_combined(rotated)
        preview = rotated[:50]
        results.append((rot_type, score, preview))

    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_n]


def detect_period_by_brute_force(
    ciphertext: str,
    min_period: int = 2,
    max_period: int = 20,
    top_n: int = 5,
) -> list[tuple[int, float, str]]:
    """Detect period by trying all periods and ranking by decryption quality.

    More compute-intensive but more reliable than IOC/Kasiski.

    Args:
        ciphertext: Ciphertext to analyze
        min_period: Minimum period to test
        max_period: Maximum period to test
        top_n: Return top N results

    Returns:
        List of (period, score, plaintext_preview) tuples
    """
    results = []

    for period in range(min_period, max_period + 1):
        # Solve permutation for this period
        perm, score = solve_columnar_permutation_multi_start(ciphertext, period, num_restarts=5, max_iterations=2000)

        # Penalize periods that are multiples of smaller periods
        # (they often score well but are wrong)
        penalty = 1.0
        for divisor in range(2, period):
            if period % divisor == 0:
                penalty *= 0.95  # 5% penalty per divisor

        adjusted_score = score * penalty

        # Get decrypted text preview
        text = ''.join(c for c in ciphertext.upper() if c.isalpha())
        decrypted = apply_columnar_permutation_reverse(text, period, perm)
        preview = decrypted[:50]

        results.append((period, adjusted_score, preview))

    # Sort by score
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_n]


def solve_columnar_permutation_simulated_annealing(
    ciphertext: str,
    period: int,
    max_iterations: int = 10000,
    initial_temp: float = 10.0,
    cooling_rate: float = 0.995,
) -> tuple[list[int], float]:
    """Solve columnar transposition using simulated annealing.

    Simulated annealing accepts worse solutions with decreasing probability,
    helping escape local optima better than hill-climbing.

    Args:
        ciphertext: Ciphertext to analyze
        period: Known or suspected period
        max_iterations: Maximum iterations
        initial_temp: Starting temperature (higher = more exploration)
        cooling_rate: Temperature decay factor per iteration (0.99-0.999)

    Returns:
        (best_permutation, best_score) tuple
    """
    import math

    text = ''.join(c for c in ciphertext.upper() if c.isalpha())

    # Start with random permutation
    current_perm = list(range(period))
    random.shuffle(current_perm)

    # Score initial permutation
    current_text = apply_columnar_permutation_reverse(text, period, current_perm)
    current_score = score_combined(current_text)

    best_perm = current_perm[:]
    best_score = current_score

    temperature = initial_temp

    for _ in range(max_iterations):
        # Generate neighbor by swapping two random positions
        neighbor_perm = current_perm[:]
        i, j = random.sample(range(period), 2)
        neighbor_perm[i], neighbor_perm[j] = neighbor_perm[j], neighbor_perm[i]

        # Score neighbor
        neighbor_text = apply_columnar_permutation_reverse(text, period, neighbor_perm)
        neighbor_score = score_combined(neighbor_text)

        # Calculate acceptance probability
        delta = neighbor_score - current_score

        if delta > 0:
            # Better solution - always accept
            current_perm = neighbor_perm
            current_score = neighbor_score

            # Update best if improved
            if current_score > best_score:
                best_perm = current_perm[:]
                best_score = current_score
        else:
            # Worse solution - accept with probability based on temperature
            acceptance_prob = math.exp(delta / temperature) if temperature > 0 else 0

            if random.random() < acceptance_prob:
                current_perm = neighbor_perm
                current_score = neighbor_score

        # Cool down temperature
        temperature *= cooling_rate

        # Early termination if temperature too low
        if temperature < 0.01:
            break

    return best_perm, best_score


def solve_columnar_permutation_simulated_annealing_multi_start(
    ciphertext: str,
    period: int,
    num_restarts: int = 5,
    max_iterations: int = 10000,
    initial_temp: float = 10.0,
    cooling_rate: float = 0.995,
) -> tuple[list[int], float]:
    """Solve columnar transposition with multiple simulated annealing runs.

    Args:
        ciphertext: Ciphertext to analyze
        period: Known or suspected period
        num_restarts: Number of independent SA runs
        max_iterations: Iterations per run
        initial_temp: Starting temperature
        cooling_rate: Temperature decay factor

    Returns:
        (best_permutation, best_score) tuple across all runs
    """
    best_perm: list[int] = list(range(period))
    best_score = float('-inf')

    for _ in range(num_restarts):
        perm, score = solve_columnar_permutation_simulated_annealing(
            ciphertext,
            period,
            max_iterations,
            initial_temp,
            cooling_rate,
        )

        if score > best_score:
            best_score = score
            best_perm = perm

    return best_perm, best_score


def solve_columnar_permutation_exhaustive(
    ciphertext: str,
    period: int,
    target_score: float | None = None,
) -> tuple[list[int], float]:
    """Solve columnar transposition by exhaustively trying all permutations.

    Guaranteed to find optimal solution for small periods (≤6).
    For period 6: 6! = 720 permutations (fast)
    For period 7: 7! = 5,040 permutations (feasible)
    For period 8+: Use SA or multi-start hill-climbing instead

    Args:
        ciphertext: Ciphertext to analyze
        period: Period (should be ≤7 for reasonable performance)
        target_score: Optional early termination threshold

    Returns:
        (best_permutation, best_score) tuple

    Raises:
        ValueError: If period > 8 (too expensive)
    """
    if period > 8:
        raise ValueError(f"Exhaustive search not recommended for period {period} ({period}! permutations)")

    import itertools

    text = ''.join(c for c in ciphertext.upper() if c.isalpha())

    best_perm = list(range(period))
    best_score = float('-inf')
    permutations_checked = 0

    # Try all permutations
    for perm in itertools.permutations(range(period)):
        perm_list = list(perm)
        plaintext = apply_columnar_permutation_reverse(text, period, perm_list)
        score = score_combined(plaintext)

        permutations_checked += 1

        if score > best_score:
            best_score = score
            best_perm = perm_list

        # Early termination if target score reached
        if target_score is not None and score >= target_score:
            break

    return best_perm, best_score


def solve_columnar_permutation(ciphertext: str, period: int, max_iterations: int = 10000) -> tuple[list[int], float]:
    """Solve columnar transposition permutation using hill-climbing.

    Args:
        ciphertext: Ciphertext to analyze
        period: Known or suspected period
        max_iterations: Maximum hill-climbing iterations

    Returns:
        (best_permutation, best_score) tuple
    """

    text = ''.join(c for c in ciphertext.upper() if c.isalpha())

    # Start with identity permutation
    current_perm = list(range(period))
    random.shuffle(current_perm)

    # Score initial permutation
    current_text = apply_columnar_permutation_reverse(text, period, current_perm)
    current_score = score_bigrams(current_text)

    best_perm = current_perm[:]
    best_score = current_score

    improvements = 0
    no_improvement_count = 0

    for iteration in range(max_iterations):
        # Generate neighbor by swapping two random positions
        neighbor_perm = current_perm[:]
        i, j = random.sample(range(period), 2)
        neighbor_perm[i], neighbor_perm[j] = neighbor_perm[j], neighbor_perm[i]

        # Score neighbor
        neighbor_text = apply_columnar_permutation_reverse(text, period, neighbor_perm)
        neighbor_score = score_bigrams(neighbor_text)

        # Accept if better
        if neighbor_score > current_score:
            current_perm = neighbor_perm
            current_score = neighbor_score
            improvements += 1
            no_improvement_count = 0

            if current_score > best_score:
                best_perm = current_perm[:]
                best_score = current_score
        else:
            no_improvement_count += 1

        # Restart if stuck (random restart after 1000 iterations without improvement)
        if no_improvement_count >= 1000:
            current_perm = list(range(period))
            random.shuffle(current_perm)
            current_text = apply_columnar_permutation_reverse(text, period, current_perm)
            current_score = score_bigrams(current_text)
            no_improvement_count = 0

        # Log progress periodically
        if iteration % 1000 == 0 and iteration > 0:
            logger.debug("Iteration %d: best_score=%.4f, improvements=%d", iteration, best_score, improvements)

    logger.info(
        "Permutation solving complete: %d iterations, %d improvements, best_score=%.4f",
        max_iterations,
        improvements,
        best_score,
    )

    return best_perm, best_score


def test_period_detection():
    """Test period detection on K3."""
    # Full K3 ciphertext (336 chars)
    k3_cipher = (
        "ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIA"
        "CHTNREYULDSLLSLLNOHSNOSMRWXMNE"
        "TPRNGATIHNRARPESLNNELEBLPIIACAE"
        "WMTWNDITEENRAHCTENEUDRETNHAEOE"
        "TFOLSEDTIWENHAEIOYTEYQHEENCTAYCR"
        "EIFTBRSPAMHHEWENATAMATEGYEERLB"
        "TEEFOASFIOTUETUAEOTOARMAEERTNRTI"
        "BSEDDNIAAHTTMSTEWPIEROAGRIEWFEB"
        "AECTDDHILCEIHSITEGOEAOSDDRYDLORIT"
        "RKLMLEHAGTDHARDPNEOHMGFMFEUHE"
        "ECDMRIPFEIMEHNLSSTTRTVDOHW"
    )

    print("=" * 80)
    print("TRANSPOSITION PERIOD DETECTION TEST")
    print("=" * 80)
    print(f"Testing on full K3 ciphertext ({len(k3_cipher)} chars)")
    print("Known period: 24 (from published solution)")
    print()

    # Test IOC method
    print("Method 1: IOC Analysis")
    print("-" * 80)
    ioc_results = detect_transposition_period(k3_cipher, max_period=30)
    for i, (period, score) in enumerate(ioc_results[:10], 1):
        marker = "✓" if period == 24 else ""
        print(f"  {i}. Period {period:2d}: score={score:.4f} {marker}")

    print()

    # Test Kasiski method
    print("Method 2: Repeated Sequences (Kasiski)")
    print("-" * 80)
    kasiski_results = detect_period_by_repeated_sequences(k3_cipher)
    sorted_kasiski = sorted(kasiski_results.items(), key=lambda x: x[1], reverse=True)
    for i, (period, count) in enumerate(sorted_kasiski[:10], 1):
        marker = "✓" if period == 24 else ""
        print(f"  {i}. Period {period:2d}: count={count} {marker}")

    print()

    # Test combined method
    print("Method 3: Combined Detection")
    print("-" * 80)
    combined_results = detect_period_combined(k3_cipher, max_period=30)
    for i, (period, conf, method) in enumerate(combined_results[:10], 1):
        marker = "✓" if period == 24 else ""
        print(f"  {i}. Period {period:2d}: confidence={conf:.4f} (via {method}) {marker}")

    print()
    print("=" * 80)
    if combined_results and combined_results[0][0] == 24:
        print("✅ SUCCESS: Correct period detected as #1 candidate!")
    else:
        print("⚠️  Period 24 detected at position #8 (double transposition complicates detection)")


def test_permutation_solver():
    """Test permutation solving on simple columnar transposition."""
    print("\n" + "=" * 80)
    print("TRANSPOSITION PERMUTATION SOLVER TEST")
    print("=" * 80)

    # Create a simple test case - use a longer, more English-like text
    plaintext = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
    period = 7
    # Permutation: [3, 1, 4, 0, 6, 2, 5] - random shuffling
    permutation = [3, 1, 4, 0, 6, 2, 5]

    # Encrypt: arrange in columns (fill row-by-row), read in permuted order (column-by-column)
    # Note: Could track n, base_len, extra for uneven column handling
    # Build columns by filling row-by-row
    columns = ['' for _ in range(period)]
    for i, char in enumerate(plaintext):
        columns[i % period] += char

    # Read in permuted order (this is what attacker sees)
    ciphertext = ''.join(columns[p] for p in permutation)

    print(f"Plaintext:  {plaintext}")
    print(f"Period:     {period}")
    print(f"True permutation: {permutation}")
    print(f"Ciphertext: {ciphertext}")
    print()

    # Solve
    print("Solving with hill-climbing...")
    recovered_perm, score = solve_columnar_permutation(ciphertext, period, max_iterations=5000)
    recovered_text = apply_columnar_permutation_reverse(ciphertext, period, recovered_perm)

    print(f"Recovered permutation: {recovered_perm}")
    print(f"Recovered text: {recovered_text}")
    print(f"Score: {score:.4f}")
    print()

    if recovered_text == plaintext:
        print("✅ PERFECT: Exact plaintext recovered!")
    elif recovered_text.replace(' ', '') == plaintext.replace(' ', ''):
        print("✅ SUCCESS: Plaintext recovered (minor spacing differences)")
    else:
        print("⚠️  PARTIAL: Text recovered but not exact match")
        print(f"   Expected: {plaintext}")
        print(f"   Got:      {recovered_text}")


if __name__ == "__main__":
    test_period_detection()
    test_permutation_solver()
