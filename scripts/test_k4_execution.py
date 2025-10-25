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
results = ops.execute_attack_queue(attack_queue, K4)

# Show results
print(f"\nExecuted {len(results)} attacks\n")
for i, r in enumerate(results, 1):
    key_len = r.attack_params.parameters.get('key_length', 'N/A')
    print(f"{i}. {r.attack_params.cipher_type} | key_length={key_len}")
    print(f"   Success: {r.success} | Confidence: {r.confidence:.4f}")
    if r.plaintext:
        print(f"   Plaintext: {r.plaintext[:60]}...")
    if r.metadata.get('error'):
        print(f"   Error: {r.metadata['error']}")
    print()

# Summary
successful = [r for r in results if r.success]
print(f"Summary: {len(successful)}/{len(results)} successful attacks")
if successful:
    print("\n✅ SUCCESSFUL ATTACKS:")
    for r in successful:
        print(f"  - {r.attack_params.cipher_type} | confidence={r.confidence:.4f}")
        print(f"    {r.plaintext[:80]}...")
