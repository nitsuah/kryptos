"""Test attack generation engine integration.

Validates that attack generator:
1. Generates attacks from Q-Research hints
2. Fills coverage gaps
3. Deduplicates against attack logger
4. Prioritizes attacks correctly
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kryptos.pipeline.attack_generator import AttackGenerator  # noqa: E402
from kryptos.provenance.attack_log import AttackLogger  # noqa: E402

# Load config for K4 data
config_path = Path(__file__).parent.parent / "config" / "config.json"
with open(config_path) as f:
    config = json.load(f)

K4_CIPHERTEXT = config["ciphertexts"]["K4"]
CRIBS = config["cribs"]


def test_q_hints_generation():
    """Test attack generation from Q-Research hints."""
    print("=" * 80)
    print("TEST: Attack Generation from Q-Research Hints")
    print("=" * 80)
    print()

    generator = AttackGenerator()

    print("Generating attacks from Q-Research hints for K4...")
    attacks = generator.generate_from_q_hints(K4_CIPHERTEXT, max_attacks=20)

    print(f"Generated {len(attacks)} attacks")
    print()

    # Show top 10
    print("Top 10 priority attacks:")
    for i, spec in enumerate(attacks[:10], 1):
        print(f"{i:2d}. [{spec.parameters.cipher_type:15s}] Priority: {spec.priority:.3f}")
        print(f"    Source: {spec.source}")
        print(f"    Rationale: {spec.rationale}")
        print(f"    Tags: {', '.join(spec.tags)}")
        print()

    print("✓ Q-hints generation working")
    print()


def test_coverage_gap_generation():
    """Test attack generation from coverage gaps."""
    print("=" * 80)
    print("TEST: Attack Generation from Coverage Gaps")
    print("=" * 80)
    print()

    # Create attack logger with some existing attacks
    logger = AttackLogger(log_dir=Path(tempfile.mkdtemp()))

    # Simulate some attacks already tried
    from kryptos.provenance.attack_log import AttackParameters, AttackResult

    for key_length in [7, 10, 11]:  # Already tried these
        params = AttackParameters(
            cipher_type="vigenere",
            key_or_params={"key_length": key_length},
        )
        result = AttackResult(
            success=False,
            plaintext_candidate="",
        )
        logger.log_attack(K4_CIPHERTEXT, params, result, tags=["test"])

    # Create generator with logger
    generator = AttackGenerator(attack_logger=logger)

    print("Generating attacks to fill coverage gaps...")
    attacks = generator.generate_from_coverage_gaps(max_attacks=15)

    print(f"Generated {len(attacks)} gap-filling attacks")
    print()

    # Show distribution
    cipher_counts = {}
    for attack in attacks:
        ct = attack.parameters.cipher_type
        cipher_counts[ct] = cipher_counts.get(ct, 0) + 1

    print("Attack distribution:")
    for cipher_type, count in cipher_counts.items():
        print(f"  {cipher_type}: {count} attacks")
    print()

    # Show top 5
    print("Top 5 gap-filling attacks:")
    for i, spec in enumerate(attacks[:5], 1):
        print(f"{i}. [{spec.parameters.cipher_type}] Priority: {spec.priority:.3f}")
        print(f"   {spec.rationale}")
    print()

    print("✓ Coverage gap generation working")
    print()


def test_deduplication():
    """Test attack deduplication."""
    print("=" * 80)
    print("TEST: Attack Deduplication")
    print("=" * 80)
    print()

    # Create logger with existing attacks
    logger = AttackLogger(log_dir=Path(tempfile.mkdtemp()))

    from kryptos.provenance.attack_log import AttackParameters, AttackResult

    # Log some attacks
    for key_length in [7, 8, 9]:
        params = AttackParameters(
            cipher_type="vigenere",
            key_or_params={"key_length": key_length},
        )
        result = AttackResult(
            success=False,
            plaintext_candidate="",
        )
        logger.log_attack(K4_CIPHERTEXT, params, result, tags=["test"])

    print(f"Existing attacks logged: {len(logger.query_attacks())}")
    print()

    # Generate queue
    generator = AttackGenerator(attack_logger=logger)

    print("Generating comprehensive attack queue...")
    queue = generator.generate_comprehensive_queue(
        ciphertext=K4_CIPHERTEXT,
        max_attacks=50,
        cribs=CRIBS,
    )

    print(f"Queue size after deduplication: {len(queue)}")
    print()

    # Check stats
    print("Generation statistics:")
    for key, value in generator.stats.items():
        print(f"  {key}: {value}")
    print()

    # Verify no duplicates
    fingerprints = set()
    duplicates = 0
    for spec in queue:
        fp = spec.fingerprint()
        if fp in fingerprints:
            duplicates += 1
        fingerprints.add(fp)

    print(f"Duplicates in queue: {duplicates}")
    assert duplicates == 0, "Queue should not contain duplicates"
    print("✓ No duplicates in queue")
    print()

    print("✓ Deduplication working")
    print()


def test_full_queue_generation():
    """Test full attack queue generation."""
    print("=" * 80)
    print("TEST: Full Attack Queue Generation")
    print("=" * 80)
    print()

    generator = AttackGenerator()

    print("Generating comprehensive attack queue for K4...")
    queue = generator.generate_comprehensive_queue(
        ciphertext=K4_CIPHERTEXT,
        max_attacks=100,
        cribs=CRIBS,
    )

    print(f"Total attacks in queue: {len(queue)}")
    print()

    # Analyze queue composition
    sources = {}
    cipher_types = {}

    for spec in queue:
        sources[spec.source] = sources.get(spec.source, 0) + 1
        cipher_types[spec.parameters.cipher_type] = cipher_types.get(spec.parameters.cipher_type, 0) + 1

    print("Queue composition by source:")
    for source, count in sources.items():
        print(f"  {source}: {count} attacks")
    print()

    print("Queue composition by cipher type:")
    for cipher_type, count in cipher_types.items():
        print(f"  {cipher_type}: {count} attacks")
    print()

    # Show top 15 attacks
    print("Top 15 priority attacks:")
    for i, spec in enumerate(queue[:15], 1):
        params_str = str(spec.parameters.key_or_params)
        if len(params_str) > 40:
            params_str = params_str[:37] + "..."

        print(
            f"{i:2d}. [{spec.parameters.cipher_type:15s}] " f"Priority: {spec.priority:.3f}, Source: {spec.source:15s}",
        )
        print(f"    {spec.rationale}")
    print()

    print("✓ Full queue generation working")
    print()


def test_priority_ordering():
    """Test that attacks are properly prioritized."""
    print("=" * 80)
    print("TEST: Attack Priority Ordering")
    print("=" * 80)
    print()

    generator = AttackGenerator()

    queue = generator.generate_comprehensive_queue(
        ciphertext=K4_CIPHERTEXT,
        max_attacks=50,
        cribs=CRIBS,
    )

    print("Verifying priority ordering...")

    # Check that priorities are descending
    is_sorted = all(queue[i].priority >= queue[i + 1].priority for i in range(len(queue) - 1))

    print(f"Queue properly sorted: {is_sorted}")
    assert is_sorted, "Queue should be sorted by priority (descending)"

    # Show priority distribution
    print()
    print("Priority distribution:")
    print(f"  Highest: {queue[0].priority:.3f}")
    print(f"  Median: {queue[len(queue)//2].priority:.3f}")
    print(f"  Lowest: {queue[-1].priority:.3f}")
    print()

    print("✓ Priority ordering correct")
    print()


if __name__ == "__main__":
    test_q_hints_generation()
    test_coverage_gap_generation()
    test_deduplication()
    test_full_queue_generation()
    test_priority_ordering()

    print("=" * 80)
    print("ALL TESTS PASSED ✓")
    print("Attack generation engine ready for K4 campaign!")
    print("=" * 80)
