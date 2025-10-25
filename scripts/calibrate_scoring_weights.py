"""Calibrate scoring weights using K1-K3 known plaintexts.

This script performs grid search to find optimal scoring component weights
that best distinguish correct plaintexts from incorrect ones.
"""

import json
from pathlib import Path

from kryptos.ciphers import k3_decrypt, vigenere_decrypt
from kryptos.k4.scoring import (
    bigram_score,
    chi_square_stat,
    crib_bonus,
    index_of_coincidence,
    quadgram_score,
    trigram_score,
)


def load_config():
    """Load Kryptos configuration."""
    config_path = Path(__file__).parent.parent / "config" / "config.json"
    with open(config_path) as f:
        return json.load(f)


def get_known_plaintexts():
    """Get K1-K3 plaintexts and some decoy texts."""
    config = load_config()

    # K1 plaintext (Vigenère with PALIMPSEST)
    k1_cipher = config["ciphertexts"]["K1"].replace(" ", "")
    k1_plain = vigenere_decrypt(k1_cipher, "PALIMPSEST", preserve_non_alpha=False)

    # K2 plaintext (Vigenère with ABSCISSA)
    k2_cipher = config["ciphertexts"]["K2"]
    k2_plain = vigenere_decrypt(k2_cipher, "ABSCISSA", preserve_non_alpha=True)
    k2_plain = "".join(c for c in k2_plain if c.isalpha())  # Remove non-alpha

    # K3 plaintext (Transposition)
    k3_cipher = config["ciphertexts"]["K3"]
    k3_plain = k3_decrypt(k3_cipher)
    k3_plain = "".join(c for c in k3_plain if c.isalpha())

    # Generate decoy texts (wrong keys applied to ciphertexts)
    decoys = []

    # Try K1 cipher with wrong Vigenère keys
    for wrong_key in ["ABSCISSA", "BERLIN", "CLOCK", "KRYPTOS", "WRONGKEY"]:
        try:
            decoy = vigenere_decrypt(k1_cipher, wrong_key, preserve_non_alpha=False)
            decoys.append(decoy)
        except Exception:
            pass

    # Try K2 cipher with wrong Vigenère keys
    for wrong_key in ["PALIMPSEST", "BERLIN", "CLOCK", "KRYPTOS", "WRONGKEY"]:
        try:
            decoy = vigenere_decrypt(k2_cipher, wrong_key, preserve_non_alpha=False)
            decoy = "".join(c for c in decoy if c.isalpha())
            decoys.append(decoy)
        except Exception:
            pass

    # K3 with wrong transposition patterns (use cipher as-is, partial decrypts)
    k3_chars = "".join(c for c in k3_cipher if c.isalpha())
    # Add some partial/wrong transposition attempts
    for shift in [1, 2, 3, 5, 7]:
        decoy = k3_chars[shift:] + k3_chars[:shift]  # Rotated
        decoys.append(decoy)

    return {
        "correct": [k1_plain, k2_plain, k3_plain],
        "decoys": decoys,
    }


def score_with_weights(text: str, weights: dict[str, float]) -> float:
    """Score text with custom component weights."""
    # Component scores (normalized)
    ioc = index_of_coincidence(text)
    chi2 = chi_square_stat(text)
    bg = bigram_score(text)
    tg = trigram_score(text)
    qg = quadgram_score(text)
    crib = crib_bonus(text)

    # Normalize chi-square (lower is better, so invert)
    chi2_normalized = -chi2 / 100.0  # Scale down

    # Combine with weights
    score = (
        weights.get("ioc", 0.0) * ioc
        + weights.get("chi2", 0.0) * chi2_normalized
        + weights.get("bigram", 0.0) * bg
        + weights.get("trigram", 0.0) * tg
        + weights.get("quadgram", 0.0) * qg
        + weights.get("crib", 0.0) * crib
    )
    return score


def evaluate_weights(weights: dict[str, float], data: dict) -> dict:
    """Evaluate how well weights distinguish correct from decoy texts."""
    correct_scores = [score_with_weights(text, weights) for text in data["correct"]]
    decoy_scores = [score_with_weights(text, weights) for text in data["decoys"]]

    avg_correct = sum(correct_scores) / len(correct_scores)
    avg_decoy = sum(decoy_scores) / len(decoy_scores)

    # Separation metric: how much better correct scores than decoys
    separation = avg_correct - avg_decoy

    # Classification accuracy: how many correct > all decoys
    correct_wins = sum(1 for c in correct_scores if c > max(decoy_scores))

    return {
        "separation": separation,
        "avg_correct": avg_correct,
        "avg_decoy": avg_decoy,
        "correct_wins": correct_wins,
        "total_correct": len(correct_scores),
        "accuracy": correct_wins / len(correct_scores),
    }


def grid_search():
    """Perform grid search over weight combinations."""
    print("Loading K1-K3 plaintexts and generating decoys...")
    data = get_known_plaintexts()

    print(f"Correct plaintexts: {len(data['correct'])}")
    print(f"Decoy texts: {len(data['decoys'])}")
    print()

    # Current weights from combined_plaintext_score
    baseline = {
        "ioc": 0.0,  # Not in current formula
        "chi2": 0.1,  # Part of chi_square_stat
        "bigram": 0.1,
        "trigram": 0.2,
        "quadgram": 0.4,
        "crib": 0.2,
    }

    print("Baseline weights (from current combined_plaintext_score):")
    print(f"  {baseline}")
    baseline_results = evaluate_weights(baseline, data)
    print(f"  Separation: {baseline_results['separation']:.2f}")
    print(f"  Avg correct: {baseline_results['avg_correct']:.2f}")
    print(f"  Avg decoy: {baseline_results['avg_decoy']:.2f}")
    print(f"  Accuracy: {baseline_results['accuracy']:.1%}")
    print()

    # Grid search parameters
    print("Performing grid search...")
    best_weights = baseline
    best_separation = baseline_results["separation"]

    # Test various weight combinations
    weight_options = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]

    total_tests = 0
    for ioc_w in weight_options:
        for chi2_w in weight_options:
            for bg_w in weight_options:
                for tg_w in weight_options:
                    for qg_w in weight_options:
                        for crib_w in weight_options:
                            weights = {
                                "ioc": ioc_w,
                                "chi2": chi2_w,
                                "bigram": bg_w,
                                "trigram": tg_w,
                                "quadgram": qg_w,
                                "crib": crib_w,
                            }
                            results = evaluate_weights(weights, data)
                            total_tests += 1

                            if results["separation"] > best_separation:
                                best_separation = results["separation"]
                                best_weights = weights
                                print(f"  New best! Separation: {best_separation:.2f}")
                                print(f"    Weights: {best_weights}")
                                print(f"    Accuracy: {results['accuracy']:.1%}")

    print()
    print("=" * 80)
    print("GRID SEARCH COMPLETE")
    print("=" * 80)
    print(f"Total combinations tested: {total_tests}")
    print()
    print("Best weights:")
    for component, weight in best_weights.items():
        print(f"  {component:10s}: {weight:.2f}")
    print()

    best_results = evaluate_weights(best_weights, data)
    print("Best results:")
    print(f"  Separation: {best_results['separation']:.2f}")
    print(f"  Avg correct: {best_results['avg_correct']:.2f}")
    print(f"  Avg decoy: {best_results['avg_decoy']:.2f}")
    print(f"  Accuracy: {best_results['accuracy']:.1%}")
    print()

    # Compare to baseline
    improvement = (best_separation - baseline_results["separation"]) / abs(baseline_results["separation"])
    print(f"Improvement over baseline: {improvement:+.1%}")


if __name__ == "__main__":
    import random

    random.seed(42)  # Reproducible decoys
    grid_search()
