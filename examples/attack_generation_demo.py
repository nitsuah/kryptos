#!/usr/bin/env python3
"""
Attack Generation & Execution Demo

Demonstrates the Phase 5 workflow:
1. AttackGenerator → structured attack parameters from Q-Research hints
2. OPS Agent → parallel attack execution
3. AttackLogger → provenance tracking & deduplication

This shows how the autonomous system discovers and executes attacks
without manual intervention.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from kryptos.agents.ops import OpsAgent, OpsConfig


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def demo_basic_workflow():
    """Demo: Basic attack generation and execution workflow."""
    print_section("DEMO: Attack Generation → Execution → Logging")

    # K4 ciphertext (97 chars)
    k4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBN" "YPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

    print(f"\nCiphertext: {k4[:40]}...")
    print(f"Length: {len(k4)} characters")

    with TemporaryDirectory() as tmpdir:
        # Initialize OPS with attack generation enabled
        config = OpsConfig(
            enable_attack_generation=True,
            attack_log_dir=Path(tmpdir) / "attack_logs",
            log_level="INFO",
        )
        ops = OpsAgent(config=config)

        print("\n✓ OPS Agent initialized with attack generation enabled")

        # Step 1: Generate attacks from Q-Research hints
        print("\n[1] Generating attacks from Q-Research hints...")
        attacks = ops.generate_attack_queue_from_q_hints(
            ciphertext=k4,
            max_attacks=10,
        )

        print(f"    Generated {len(attacks)} attacks")
        print("    Top 3 attacks:")
        for i, attack in enumerate(attacks[:3], 1):
            params = attack.parameters
            key_info = str(list(params.key_or_params.keys())[:2])
            print(f"    {i}. {params.cipher_type} | priority={attack.priority:.2f} | keys={key_info}")

        # Step 2: Execute attacks
        print("\n[2] Executing attack queue...")
        summary = ops.execute_attack_queue(
            attack_queue=attacks,
            ciphertext=k4,
            batch_size=5,
        )

        print(f"    Executed: {summary['executed']}/{summary['total_attacks']}")
        print(f"    Successful: {summary['successful']}")

        # Step 3: Check deduplication
        print("\n[3] Testing deduplication...")
        attacks2 = ops.generate_attack_queue_from_q_hints(k4, max_attacks=5)

        if ops.attack_generator:
            gen_stats = ops.attack_generator.get_statistics()
            print(f"    Duplicates filtered by generator: {gen_stats['duplicates_filtered']}")

        ops.execute_attack_queue(attacks2, k4)
        if ops.attack_logger:
            logger_stats = ops.attack_logger.stats
            print(f"    Duplicates prevented by logger: {logger_stats['duplicates_prevented']}")
            print(f"    Total unique attacks: {logger_stats['unique_attacks']}")

        # Step 4: Comprehensive queue
        print("\n[4] Generating comprehensive attack queue...")
        comp_attacks = ops.generate_attack_queue_comprehensive(
            ciphertext=k4,
            cipher_types=["vigenere", "transposition"],
            max_attacks=20,
        )

        sources = {}
        for attack in comp_attacks:
            sources[attack.source] = sources.get(attack.source, 0) + 1

        print(f"    Generated {len(comp_attacks)} attacks from multiple sources:")
        for source, count in sources.items():
            print(f"    - {source}: {count} attacks")

        print("\n✅ Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("• Automatic attack generation from Q-Research hints")
        print("• Parallel execution with batching")
        print("• 100% deduplication (in-batch + cross-execution)")
        print("• Comprehensive queue from multiple sources")
        print("• Provenance tracking via AttackLogger")


def main():
    """Run demo."""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "ATTACK GENERATION DEMO" + " " * 36 + "║")
    print("║" + " " * 24 + "Phase 5 Workflow" + " " * 38 + "║")
    print("╚" + "═" * 78 + "╝")

    try:
        demo_basic_workflow()

        print("\n" + "=" * 80)
        print("Next Steps (Phase 5.3):")
        print("• Replace placeholder execution with real cipher implementations")
        print("• Integrate SPY agent for plaintext scoring")
        print("• Add validation pipeline: SPY → LINGUIST → Q → Human review")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    main()
