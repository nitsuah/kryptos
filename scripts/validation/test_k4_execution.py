#!/usr/bin/env python3
"""Test K4 execution with real key recovery and SPY scoring."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kryptos.agents.ops import OpsAgent, OpsConfig  # noqa: E402

# K4 ciphertext
K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Create OPS agent
cfg = OpsConfig(enable_attack_generation=True, attack_log_dir=Path(tempfile.mkdtemp()))
ops = OpsAgent(cfg)

# Generate attacks from Q hints
print("Generating attacks...")
attack_queue = ops.generate_attack_queue_from_q_hints(K4, max_attacks=5)

# Execute
print(f"Executing {len(attack_queue)} attacks with key recovery...\n")
summary = ops.execute_attack_queue(attack_queue, K4)

# Show execution summary
print("\n=== EXECUTION SUMMARY ===")
print(f"Total attacks: {summary['total_attacks']}")
print(f"Executed: {summary['executed']}")
print(f"Successful: {summary['successful']}")
if summary['best_score'] is not None:
    print(f"Best score: {summary['best_score']:.4f}")
    print(f"Best attack: {summary['best_attack_rationale']}")
print()

# Query attack records from logger
print("=== ATTACK DETAILS ===")
if ops.attack_logger is None:
    print("Error: Attack logger not available")
    sys.exit(1)

attack_records = ops.attack_logger.query_attacks()
print(f"Retrieved {len(attack_records)} attack records\n")

for i, record in enumerate(attack_records, 1):
    key_len = (
        record.parameters.key_or_params.get('key_length', 'N/A')
        if isinstance(record.parameters.key_or_params, dict)
        else 'N/A'
    )
    print(f"{i}. {record.parameters.cipher_type} | key_length={key_len}")
    print(f"   Success: {record.result.success}")

    # Get best confidence score
    if record.result.confidence_scores:
        best_conf = max(record.result.confidence_scores.values())
        print(f"   Confidence: {best_conf:.4f}")

    if record.result.plaintext_candidate:
        print(f"   Plaintext: {record.result.plaintext_candidate[:60]}...")

    if record.result.error_message:
        print(f"   Error: {record.result.error_message}")
    print()

# Summary
successful_records = [r for r in attack_records if r.result.success]
print(f"Summary: {len(successful_records)}/{len(attack_records)} successful attacks")
if successful_records:
    print("\n✅ SUCCESSFUL ATTACKS:")
    for record in successful_records:
        best_conf = max(record.result.confidence_scores.values()) if record.result.confidence_scores else 0.0
        print(f"  - {record.parameters.cipher_type} | confidence={best_conf:.4f}")
        if record.result.plaintext_candidate:
            print(f"    {record.result.plaintext_candidate[:80]}...")
