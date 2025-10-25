#!/usr/bin/env python3
"""
K4 Autonomous Attack Generation Example

This script demonstrates using Phase 5 to autonomously generate and execute
attacks against the K4 ciphertext. Shows the complete workflow from analysis
to execution without manual parameter tuning.

Usage:
    python examples/k4_autonomous_attack.py [--max-attacks 50] [--batch-size 10]
"""

from __future__ import annotations

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from kryptos.agents.ops import OpsAgent, OpsConfig

# K4 ciphertext (97 characters)
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBN" "YPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"


def print_section(title: str, width: int = 80):
    """Print a formatted section header."""
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width)


def analyze_and_generate(ops: OpsAgent, max_attacks: int = 50) -> list:
    """Generate attack queue from Q-Research analysis."""
    print_section("Step 1: Q-Research Analysis & Attack Generation")

    print("\nAnalyzing K4 ciphertext...")
    print(f"  Length: {len(K4_CIPHERTEXT)} characters")
    print(f"  Text: {K4_CIPHERTEXT[:40]}...")

    # Generate from Q-Research hints
    print(f"\nGenerating up to {max_attacks} attacks from Q-Research hints...")
    attacks = ops.generate_attack_queue_from_q_hints(
        ciphertext=K4_CIPHERTEXT,
        max_attacks=max_attacks,
    )

    print(f"✓ Generated {len(attacks)} attacks")

    # Show attack breakdown by cipher type
    cipher_types = {}
    for attack in attacks:
        ct = attack.parameters.cipher_type
        cipher_types[ct] = cipher_types.get(ct, 0) + 1

    print("\n  Attack breakdown by cipher type:")
    for cipher_type, count in sorted(cipher_types.items()):
        print(f"    - {cipher_type}: {count} attacks")

    # Show priority distribution
    high = sum(1 for a in attacks if a.priority >= 0.7)
    medium = sum(1 for a in attacks if 0.5 <= a.priority < 0.7)
    low = sum(1 for a in attacks if a.priority < 0.5)

    print("\n  Priority distribution:")
    print(f"    - High priority (≥0.7): {high}")
    print(f"    - Medium priority (0.5-0.7): {medium}")
    print(f"    - Low priority (<0.5): {low}")

    # Show top 5 attacks
    print("\n  Top 5 attacks by priority:")
    for i, attack in enumerate(attacks[:5], 1):
        params = attack.parameters
        key_info = str(list(params.key_or_params.keys())[:3])
        print(f"    {i}. {params.cipher_type} | priority={attack.priority:.3f}")
        print(f"       Keys: {key_info}")
        print(f"       Rationale: {attack.rationale[:80]}...")

    return attacks


def execute_attacks(ops: OpsAgent, attacks: list, batch_size: int = 10):
    """Execute attack queue with batching."""
    print_section("Step 2: Parallel Attack Execution")

    print(f"\nExecuting {len(attacks)} attacks in batches of {batch_size}...")
    print("(Note: Using placeholder execution for Phase 5.2)")

    summary = ops.execute_attack_queue(
        attack_queue=attacks,
        ciphertext=K4_CIPHERTEXT,
        batch_size=batch_size,
    )

    print("\n✓ Execution complete")
    print(f"  Total attacks: {summary['total_attacks']}")
    print(f"  Executed: {summary['executed']}")
    print(f"  Successful: {summary['successful']} (placeholder always returns 0)")

    return summary


def show_provenance(ops: OpsAgent, summary: dict):
    """Show provenance tracking statistics."""
    print_section("Step 3: Provenance Tracking & Deduplication")

    if not ops.attack_logger:
        print("⚠ Attack logging not enabled")
        return

    logger_stats = summary["attack_logger_stats"]

    print("\n  Attack Logger Statistics:")
    print(f"    - Total attacks logged: {logger_stats['total_attacks']}")
    print(f"    - Unique attacks: {logger_stats['unique_attacks']}")
    print(f"    - Duplicates prevented: {logger_stats['duplicates_prevented']}")

    if logger_stats['duplicates_prevented'] > 0:
        dedup_rate = logger_stats['duplicates_prevented'] / (
            logger_stats['total_attacks'] + logger_stats['duplicates_prevented']
        )
        print(f"    - Deduplication rate: {dedup_rate:.1%}")

    if ops.attack_generator:
        gen_stats = ops.attack_generator.get_statistics()
        print("\n  Attack Generator Statistics:")
        print(f"    - Total generated: {gen_stats['generated']}")
        print(f"    - From Q-Research: {gen_stats['from_q_hints']}")
        print(f"    - From coverage gaps: {gen_stats['from_coverage_gaps']}")
        print(f"    - Duplicates filtered: {gen_stats['duplicates_filtered']}")


def run_comprehensive_analysis(ops: OpsAgent, max_attacks: int = 100):
    """Run comprehensive attack generation from all sources."""
    print_section("Step 4: Comprehensive Attack Generation")

    print("\nGenerating comprehensive attack queue...")
    print("  Sources: Q-Research + Coverage Gaps + Literature")

    attacks = ops.generate_attack_queue_comprehensive(
        ciphertext=K4_CIPHERTEXT,
        cipher_types=["vigenere", "transposition"],
        max_attacks=max_attacks,
    )

    print(f"\n✓ Generated {len(attacks)} attacks from multiple sources")

    # Show source breakdown
    sources = {}
    for attack in attacks:
        sources[attack.source] = sources.get(attack.source, 0) + 1

    print("\n  Source breakdown:")
    for source, count in sorted(sources.items()):
        print(f"    - {source}: {count} attacks")

    return attacks


def main():
    """Run K4 autonomous attack generation."""
    parser = argparse.ArgumentParser(description="K4 Autonomous Attack Generation Demo")
    parser.add_argument(
        "--max-attacks",
        type=int,
        default=50,
        help="Maximum attacks to generate (default: 50)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Batch size for parallel execution (default: 10)",
    )
    parser.add_argument(
        "--comprehensive",
        action="store_true",
        help="Run comprehensive analysis (all sources)",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        help="Directory for attack logs (default: temp directory)",
    )
    args = parser.parse_args()

    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + "K4 AUTONOMOUS ATTACK GENERATION".center(78) + "║")
    print("║" + "Phase 5: Research → Generation → Execution".center(78) + "║")
    print("╚" + "═" * 78 + "╝")

    # Setup
    if args.log_dir:
        log_dir = args.log_dir
        log_dir.mkdir(parents=True, exist_ok=True)

        config = OpsConfig(
            enable_attack_generation=True,
            attack_log_dir=log_dir,
            log_level="INFO",
        )
        ops = OpsAgent(config=config)

        print(f"\n✓ Initialized OPS Agent (logs: {log_dir})")

        # Run analysis
        attacks = analyze_and_generate(ops, args.max_attacks)
        summary = execute_attacks(ops, attacks, args.batch_size)
        show_provenance(ops, summary)

        if args.comprehensive:
            comp_attacks = run_comprehensive_analysis(ops, args.max_attacks * 2)
            comp_summary = execute_attacks(ops, comp_attacks, args.batch_size)
            show_provenance(ops, comp_summary)

        print(f"\n✓ Attack logs saved to: {log_dir}")

    else:
        with TemporaryDirectory() as tmpdir:
            config = OpsConfig(
                enable_attack_generation=True,
                attack_log_dir=Path(tmpdir) / "attack_logs",
                log_level="INFO",
            )
            ops = OpsAgent(config=config)

            print("\n✓ Initialized OPS Agent (using temp directory)")

            # Run analysis
            attacks = analyze_and_generate(ops, args.max_attacks)
            summary = execute_attacks(ops, attacks, args.batch_size)
            show_provenance(ops, summary)

            if args.comprehensive:
                comp_attacks = run_comprehensive_analysis(ops, args.max_attacks * 2)
                comp_summary = execute_attacks(ops, comp_attacks, args.batch_size)
                show_provenance(ops, comp_summary)

    # Summary
    print_section("Summary")
    print("\n✅ Autonomous attack generation complete!")
    print("\nWhat happened:")
    print("  1. Q-Research analyzed K4 ciphertext automatically")
    print("  2. AttackGenerator converted hints → structured parameters")
    print("  3. OPS Agent executed attacks in parallel batches")
    print("  4. AttackLogger tracked all attempts with deduplication")
    print("\nNext Steps (Phase 5.3):")
    print("  • Replace placeholder execution with real ciphers")
    print("  • Integrate SPY agent for plaintext scoring")
    print("  • Filter promising candidates for human review")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    main()
