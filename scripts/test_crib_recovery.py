#!/usr/bin/env python3
"""Test crib-based key recovery on K1."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kryptos.ciphers import vigenere_decrypt  # noqa: E402
from kryptos.k4.vigenere_key_recovery import recover_key_with_crib  # noqa: E402

# K1 data
K1_CIPHER = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
K1_KEY = "PALIMPSEST"  # Known solution
K1_PLAIN = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"

print("=" * 80)
print("CRIB-BASED KEY RECOVERY TEST: K1")
print("=" * 80)
print(f"Ciphertext: {K1_CIPHER}")
print(f"Length: {len(K1_CIPHER)}")
print(f"Known key: {K1_KEY} (length {len(K1_KEY)})")
print(f"Known plaintext: {K1_PLAIN}")
print()

# Test with different cribs
cribs = [
    "BETWEEN",  # Start of plaintext (7 chars)
    "SUBTLE",  # Word in middle (6 chars)
    "LIGHT",  # Word in middle (5 chars)
    "NUANCE",  # Near end (6 chars)
]

for crib in cribs:
    print(f"\n{'='*80}")
    print(f"Testing with crib: '{crib}' (length {len(crib)})")
    print(f"{'='*80}")

    # Try to recover key
    results = recover_key_with_crib(K1_CIPHER, crib, len(K1_KEY))

    if results:
        print(f"Found {len(results)} candidate keys:\n")
        for i, (key, pos, conf) in enumerate(results[:5], 1):
            # Test the key
            plaintext = vigenere_decrypt(K1_CIPHER, key)
            is_correct = key == K1_KEY
            marker = "✅ CORRECT!" if is_correct else ""

            print(f"{i}. Key: {key} | Position: {pos} | Confidence: {conf:.2f} {marker}")
            print(f"   Plaintext: {plaintext}")

            if is_correct:
                print(f"\n   🎉 SUCCESS! Recovered correct key using crib '{crib}'!")
                break
    else:
        print("❌ No keys recovered")

print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")
print("Crib-based recovery can crack K1 if:")
print("  1. We know a word from the plaintext (BETWEEN, SUBTLE, LIGHT, etc.)")
print("  2. The crib is at least 50-60% of the key length")
print("  3. The crib provides enough key positions to constrain the solution")
