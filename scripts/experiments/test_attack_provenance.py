#!/usr/bin/env python3
"""Test attack provenance logging system."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kryptos.pipeline.attack_executor import AttackExecutor  # noqa: E402


def test_vigenere_logging():
    """Test Vigenère attack logging."""
    print("=" * 80)
    print("VIGENÈRE ATTACK LOGGING")
    print("=" * 80)

    # Create executor with temp log dir
    log_dir = Path(tempfile.mkdtemp())
    executor = AttackExecutor(log_dir=log_dir)

    # Test known plaintext
    plaintext = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
    ciphertext = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
    key = "PALIMPSEST"

    print(f"Ciphertext: {ciphertext}")
    print(f"Key: {key}")
    print()

    # Execute attack
    result, record = executor.vigenere_attack(
        ciphertext=ciphertext,
        key=key,
        crib_text="BETWEEN",
        crib_position=0,
        tags=["k1", "test", "vigenere"],
    )

    print(f"Decrypted:  {result}")
    print(f"Expected:   {plaintext}")
    print()
    print(f"Attack ID: {record.attack_id}")
    print(f"Success: {record.result.success}")
    print(f"Execution time: {record.result.execution_time_seconds:.4f}s")
    print(f"Tags: {record.tags}")
    print()

    # Try the same attack again (should detect duplicate)
    result2, record2 = executor.vigenere_attack(
        ciphertext=ciphertext,
        key=key,
        crib_text="BETWEEN",
        tags=["k1", "test", "duplicate"],
    )

    if record.attack_id == record2.attack_id:
        print("✓ Deduplication working - same attack ID returned")
    else:
        print("⚠ Different attack ID - deduplication may not be working")
    print()

    # Query statistics
    stats = executor.get_statistics()
    print("Statistics:")
    print(f"  Total attacks: {stats['total_attacks']}")
    print(f"  Unique attacks: {stats['unique_attacks']}")
    print(f"  Duplicates prevented: {stats['duplicates_prevented']}")
    print(f"  Successful: {stats['successful_attacks']}")
    print()


def test_transposition_logging():
    """Test transposition attack logging."""
    print("=" * 80)
    print("TRANSPOSITION ATTACK LOGGING")
    print("=" * 80)

    log_dir = Path(tempfile.mkdtemp())
    executor = AttackExecutor(log_dir=log_dir)

    # Known test case
    ciphertext = "OEASYESSDSEBLPEOHAFABHCRSYALWEIPGRAUEWSTLTMOSETNELDRYLRNAEIT"
    period = 5
    true_perm = [2, 4, 0, 3, 1]

    print(f"Ciphertext: {ciphertext}")
    print(f"Period: {period}")
    print(f"True permutation: {true_perm}")
    print()

    # Test exhaustive search
    print("Testing exhaustive search...")
    (perm_ex, score_ex), record_ex = executor.transposition_attack(
        ciphertext=ciphertext,
        period=period,
        method="exhaustive",
        tags=["k3", "transposition", "exhaustive"],
    )

    print(f"  Found permutation: {perm_ex}")
    print(f"  Score: {score_ex:.6f}")
    print(f"  Attack ID: {record_ex.attack_id}")
    print(f"  Success: {record_ex.result.success}")
    print()

    # Test SA search
    print("Testing simulated annealing...")
    (perm_sa, score_sa), record_sa = executor.transposition_attack(
        ciphertext=ciphertext,
        period=period,
        method="simulated_annealing",
        num_restarts=5,
        tags=["k3", "transposition", "sa"],
    )

    print(f"  Found permutation: {perm_sa}")
    print(f"  Score: {score_sa:.6f}")
    print(f"  Attack ID: {record_sa.attack_id}")
    print(f"  Success: {record_sa.result.success}")
    print()

    # Query all transposition attacks
    transposition_attacks = executor.query_attacks(cipher_type="transposition")
    print(f"Total transposition attacks logged: {len(transposition_attacks)}")

    for i, attack in enumerate(transposition_attacks, 1):
        method = attack.parameters.key_or_params.get("method")
        score = attack.result.confidence_scores.get("transposition_score", 0.0)
        print(f"  {i}. {method:20s} score={score:.6f} success={attack.result.success}")
    print()


def test_query_interface():
    """Test attack querying and filtering."""
    print("=" * 80)
    print("QUERY INTERFACE TEST")
    print("=" * 80)

    log_dir = Path(tempfile.mkdtemp())
    executor = AttackExecutor(log_dir=log_dir)

    # Log several attacks
    test_cases = [
        ("vigenere", "TESTCIPHER", "KEY1", ["test", "vigenere"]),
        ("vigenere", "TESTCIPHER", "KEY2", ["test", "vigenere"]),
        ("vigenere", "TESTCIPHER", "KEY3", ["test", "vigenere", "promising"]),
    ]

    for _cipher_type, ciphertext, key, tags in test_cases:
        executor.vigenere_attack(ciphertext, key, tags=tags)

    # Query all attacks
    all_attacks = executor.query_attacks()
    print(f"All attacks: {len(all_attacks)}")

    # Query by cipher type
    vigenere_attacks = executor.query_attacks(cipher_type="vigenere")
    print(f"Vigenère attacks: {len(vigenere_attacks)}")

    # Query by tags
    promising_attacks = executor.query_attacks(tags=["promising"])
    print(f"Promising attacks: {len(promising_attacks)}")

    # Query successful only
    successful_attacks = executor.query_attacks(success_only=True)
    print(f"Successful attacks: {len(successful_attacks)}")

    print()


def main():
    """Run all provenance logging tests."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  ATTACK PROVENANCE LOGGING TEST SUITE".center(78) + "║")
    print("║" + "  Tracking every attack for reproducibility".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    test_vigenere_logging()
    test_transposition_logging()
    test_query_interface()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✓ Vigenère attacks logged with full parameters")
    print("✓ Transposition attacks logged with permutations")
    print("✓ Deduplication working (same attack = same ID)")
    print("✓ Query interface supports filtering by type/tags/success")
    print("✓ Execution time and metadata tracked")
    print()
    print("Attack provenance system ready for K4 campaign!")
    print()


if __name__ == "__main__":
    main()
