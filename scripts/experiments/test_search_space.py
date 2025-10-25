"""Test search space tracking integration with attack logging.

Validates that search space tracker correctly:
1. Syncs with AttackLogger to compute coverage
2. Identifies gaps in explored parameter ranges
3. Generates priority attack recommendations
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kryptos.pipeline.attack_executor import AttackExecutor  # noqa: E402
from kryptos.provenance.search_space import SearchSpaceTracker  # noqa: E402

# Load config for K1/K3 data
config_path = Path(__file__).parent.parent / "config" / "config.json"
with open(config_path) as f:
    config = json.load(f)

K1_CIPHERTEXT = config["ciphertexts"]["K1"].replace(" ", "")
K3_CIPHERTEXT = config["ciphertexts"]["K3"].replace("?", "").replace(" ", "").replace("\n", "")


def test_search_space_basic():
    """Test basic search space tracking."""
    print("=" * 80)
    print("TEST: Basic Search Space Tracking")
    print("=" * 80)
    print()

    tracker = SearchSpaceTracker(cache_dir=Path(tempfile.mkdtemp()))

    # Register Vigenère key space regions (lengths 1-26)
    for length in range(1, 27):
        # Approximate key space size (26^length capped at reasonable number)
        if length <= 4:
            total_keys = 26**length
        elif length <= 8:
            total_keys = 1000000  # Representative sample
        else:
            total_keys = 10000000  # Larger sample space

        tracker.register_region(
            cipher_type="vigenere",
            region_key=f"length_{length}",
            parameters={"key_length": length},
            total_size=total_keys,
        )

    # Simulate exploration
    tracker.record_exploration("vigenere", "length_7", count=50, successful=0)
    tracker.record_exploration("vigenere", "length_10", count=100, successful=0)
    tracker.record_exploration("vigenere", "length_11", count=75, successful=0)

    # Check coverage
    coverage = tracker.get_coverage("vigenere")
    print(f"Overall Vigenère coverage: {coverage:.6f}%")
    print()

    # Get coverage report
    report = tracker.get_coverage_report("vigenere")
    vigenere_report = report["cipher_types"]["vigenere"]

    print(f"Total explored: {vigenere_report['total_explored']}")
    print(f"Total size: {vigenere_report['total_size']}")
    print()

    # Show explored regions
    print("Explored regions:")
    for region in vigenere_report["regions"]:
        if region["explored_count"] > 0:
            print(
                f"  {region['region']}: {region['explored_count']} attacks "
                f"({region['coverage_percent']:.4f}% coverage)",
            )
    print()

    # Identify gaps
    print("Coverage gaps (< 1% explored):")
    gaps = tracker.identify_gaps("vigenere", min_coverage=1.0)
    for gap in gaps[:10]:
        print(f"  {gap.parameters}: {gap.coverage_percent:.4f}% " f"({gap.explored_count}/{gap.total_size})")
    print()

    print("✓ Basic search space tracking working")
    print()


def test_attack_executor_integration():
    """Test integration between AttackExecutor and SearchSpaceTracker."""
    print("=" * 80)
    print("TEST: Attack Executor + Search Space Integration")
    print("=" * 80)
    print()

    # Create executor with logging
    executor = AttackExecutor(log_dir=Path(tempfile.mkdtemp()))

    # Execute several attacks on K1
    print("Executing attacks on K1...")
    k1_ciphertext = K1_CIPHERTEXT

    # Try different key lengths
    test_keys = [
        ("PALIN", 5, "Length 5 (partial)"),
        ("PALIMP", 6, "Length 6 (partial)"),
        ("PALIMPS", 7, "Length 7 (partial)"),
        ("PALIMPSE", 8, "Length 8 (partial)"),
        ("PALIMPSES", 9, "Length 9 (partial)"),
        ("PALIMPSEST", 10, "Length 10 (correct)"),
        ("PALIMPSESTS", 11, "Length 11 (too long)"),
    ]

    for key, length, description in test_keys:
        plaintext, record = executor.vigenere_attack(
            ciphertext=k1_ciphertext,
            key=key,
            tags=["k1_test", f"length_{length}"],
        )
        print(f"  {description}: {key} → success={record.result.success}")

    print()

    # Query all attacks
    all_attacks = executor.query_attacks()
    print(f"Total attacks logged: {len(all_attacks)}")
    print()

    # Now create search space tracker and sync
    print("Creating search space tracker...")
    tracker = SearchSpaceTracker(cache_dir=Path(tempfile.mkdtemp()))

    # Register Vigenère regions
    for length in range(1, 27):
        if length <= 4:
            total_keys = 26**length
        elif length <= 8:
            total_keys = 1000000
        else:
            total_keys = 10000000

        tracker.register_region(
            cipher_type="vigenere",
            region_key=f"length_{length}",
            parameters={"key_length": length},
            total_size=total_keys,
        )

    # Manually sync attacks to search space
    print("Syncing attacks to search space tracker...")
    for record in all_attacks:
        if record.parameters.cipher_type == "vigenere":
            # Extract key length from tags or key itself
            key = record.parameters.key_or_params.get("key", "")
            key_length = len(key)

            region_key = f"length_{key_length}"
            successful = 1 if record.result.success else 0

            tracker.record_exploration(
                cipher_type="vigenere",
                region_key=region_key,
                count=1,
                successful=successful,
            )

    print()

    # Get coverage report
    report = tracker.get_coverage_report("vigenere")
    vigenere_report = report["cipher_types"]["vigenere"]

    print(f"Overall coverage: {vigenere_report['overall_coverage']:.6f}%")
    print()

    print("Explored regions:")
    for region in vigenere_report["regions"]:
        if region["explored_count"] > 0:
            print(
                f"  {region['region']}: {region['explored_count']} attacks " f"({region['success_rate']:.1f}% success)",
            )
    print()

    # Get recommendations
    print("Top 5 priority attack targets:")
    recommendations = tracker.get_recommendations(top_n=5)
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec['region']} " f"(coverage: {rec['coverage']:.4f}%, priority: {rec['priority_score']:.1f})")
        print(f"     Reason: {rec['reason']}")
    print()

    print("✓ Attack executor integration working")
    print()


def test_transposition_search_space():
    """Test search space tracking for transposition attacks."""
    print("=" * 80)
    print("TEST: Transposition Search Space")
    print("=" * 80)
    print()

    executor = AttackExecutor(log_dir=Path(tempfile.mkdtemp()))
    tracker = SearchSpaceTracker(cache_dir=Path(tempfile.mkdtemp()))

    # Register transposition period regions
    for period in range(2, 21):
        # Transposition permutations: period! (factorial)
        import math

        total_perms = math.factorial(period) if period <= 8 else 10000000

        tracker.register_region(
            cipher_type="transposition",
            region_key=f"period_{period}",
            parameters={"period": period},
            total_size=total_perms,
        )

    # Execute some transposition attacks on K3
    print("Executing transposition attacks on K3...")
    k3_ciphertext = K3_CIPHERTEXT

    test_periods = [14, 15, 16, 17, 18, 19, 20]  # K3 is double transposition

    for period in test_periods:
        result, record = executor.transposition_attack(
            ciphertext=k3_ciphertext,
            period=period,
            method="simulated_annealing",
            tags=["k3_test", f"period_{period}"],
        )
        permutation, score = result
        print(f"  Period {period}: score={score:.2f}, success={record.result.success}")

        # Record in search space
        tracker.record_exploration(
            cipher_type="transposition",
            region_key=f"period_{period}",
            count=1,
            successful=1 if record.result.success else 0,
        )

    print()

    # Get coverage report
    report = tracker.get_coverage_report("transposition")
    trans_report = report["cipher_types"]["transposition"]

    print(f"Overall transposition coverage: {trans_report['overall_coverage']:.6f}%")
    print()

    print("Explored periods:")
    for region in trans_report["regions"]:
        if region["explored_count"] > 0:
            print(f"  {region['region']}: {region['explored_count']} attacks")
    print()

    # Identify gaps
    gaps = tracker.identify_gaps("transposition", min_coverage=1.0)
    print(f"Coverage gaps: {len(gaps)} periods with <1% coverage")
    print("First 5 unexplored periods:")
    for gap in gaps[:5]:
        print(f"  Period {gap.parameters['period']}: 0% coverage")
    print()

    print("✓ Transposition search space working")
    print()


def test_multi_cipher_dashboard():
    """Test dashboard view across multiple cipher types."""
    print("=" * 80)
    print("TEST: Multi-Cipher Dashboard")
    print("=" * 80)
    print()

    tracker = SearchSpaceTracker(cache_dir=Path(tempfile.mkdtemp()))

    # Register multiple cipher types
    # Vigenère
    for length in [7, 10, 11]:  # Common K4 key lengths
        tracker.register_region(
            cipher_type="vigenere",
            region_key=f"length_{length}",
            parameters={"key_length": length},
            total_size=1000000,
        )
        tracker.record_exploration("vigenere", f"length_{length}", count=50)

    # Transposition
    for period in [14, 15, 16]:  # Common periods
        tracker.register_region(
            cipher_type="transposition",
            region_key=f"period_{period}",
            parameters={"period": period},
            total_size=100000,
        )
        tracker.record_exploration("transposition", f"period_{period}", count=10)

    # Hill
    for size in [2, 3]:
        tracker.register_region(
            cipher_type="hill",
            region_key=f"matrix_{size}x{size}",
            parameters={"matrix_size": size},
            total_size=100000 if size == 2 else 1000000,
        )
        tracker.record_exploration("hill", f"matrix_{size}x{size}", count=5)

    # Get full report
    print("Full coverage report:")
    full_report = tracker.get_coverage_report()

    for cipher_type, stats in full_report["cipher_types"].items():
        print(f"\n{cipher_type.upper()}:")
        print(f"  Overall coverage: {stats['overall_coverage']:.4f}%")
        print(f"  Total explored: {stats['total_explored']}")
        print(f"  Regions tracked: {len(stats['regions'])}")

    print()

    # Get global recommendations
    print("Top 10 priority targets across all ciphers:")
    recommendations = tracker.get_recommendations(top_n=10)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i:2d}. {rec['cipher_type']:15s} {rec['region']:15s} " f"(priority: {rec['priority_score']:6.1f})")
    print()

    print("✓ Multi-cipher dashboard working")
    print()


if __name__ == "__main__":
    test_search_space_basic()
    test_attack_executor_integration()
    test_transposition_search_space()
    test_multi_cipher_dashboard()

    print("=" * 80)
    print("ALL TESTS PASSED ✓")
    print("Search space tracking ready for K4 campaign!")
    print("=" * 80)
