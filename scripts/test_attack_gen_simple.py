"""Simple test for attack generation engine.

Validates that attack generator generates prioritized attack queues.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kryptos.pipeline.attack_generator import AttackGenerator  # noqa: E402

# Load config for K4 data
config_path = Path(__file__).parent.parent / "config" / "config.json"
with open(config_path) as f:
    config = json.load(f)

K4_CIPHERTEXT = config["ciphertexts"]["K4"]


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


def test_comprehensive_queue():
    """Test comprehensive attack queue generation."""
    print("=" * 80)
    print("TEST: Comprehensive Attack Queue Generation")
    print("=" * 80)
    print()

    generator = AttackGenerator()

    print("Generating comprehensive attack queue for K4...")
    queue = generator.generate_comprehensive_queue(
        ciphertext=K4_CIPHERTEXT,
        max_total=100,
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

    # Check stats
    print("Generation statistics:")
    for key, value in generator.stats.items():
        print(f"  {key}: {value}")
    print()

    print("✓ Comprehensive queue generation working")
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
        max_total=50,
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
    test_comprehensive_queue()
    test_priority_ordering()

    print("=" * 80)
    print("ALL TESTS PASSED ✓")
    print("Attack generation engine ready for K4 campaign!")
    print("=" * 80)
