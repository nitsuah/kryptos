"""Test Beaufort key recovery."""

from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / 'src'))

from kryptos.k4.beaufort import beaufort_decrypt, beaufort_encrypt, recover_beaufort_key  # noqa: E402


def test_key_recovery():
    """Test Beaufort key recovery with frequency analysis."""
    print("=" * 80)
    print("BEAUFORT KEY RECOVERY TEST")
    print("=" * 80)

    # Use longer plaintext for better statistics
    plaintext = (
        "THECRYPTOGRAPHYOFTHEKRYPTOSWASSUPPOSEDTOBEANEASYONEBUTITHASPROVEDTOBEONEOFTHE"
        "MOSTDIFFICULTPUZZLESINTHEWORLDTHEREAREMANYPEOPLEWHOHAVETRIED"
        "TOSOLVETHEFOURTHMESSAGEBUTNONEHAVESUCCEEDEDYET"
    )
    key = "BERLIN"

    print(f"Original plaintext ({len(plaintext)} chars):")
    print(f"{plaintext[:80]}...")
    print(f"\nKey: {key}")
    print()

    # Encrypt
    ciphertext = beaufort_encrypt(plaintext, key)
    print(f"Ciphertext: {ciphertext[:80]}...")
    print()

    # Try to recover key
    print("Attempting key recovery...")
    recovered_keys = recover_beaufort_key(ciphertext, len(key), top_n=1)

    if recovered_keys:
        recovered_key = recovered_keys[0]
        print(f"Recovered key: {recovered_key}")
        print(f"Actual key:    {key}")
        print()

        # Test decryption with recovered key
        decrypted = beaufort_decrypt(ciphertext, recovered_key)
        print(f"Decrypted: {decrypted[:80]}...")
        print()

        # Check accuracy
        matches = sum(1 for i in range(len(plaintext)) if decrypted[i] == plaintext[i])
        accuracy = matches / len(plaintext) * 100

        print(f"Accuracy: {accuracy:.1f}% ({matches}/{len(plaintext)} chars)")

        if recovered_key == key:
            print("\nSUCCESS: Exact key recovered!")
            return True
        elif accuracy > 80:
            print("\nPARTIAL: Key close enough for high accuracy")
            return True
        else:
            print("\nFAILED: Key recovery unsuccessful")
            return False
    else:
        print("FAILED: No keys recovered")
        return False


if __name__ == "__main__":
    success = test_key_recovery()
    print("\n" + "=" * 80)
    if success:
        print("KEY RECOVERY: WORKING")
    else:
        print("KEY RECOVERY: NEEDS IMPROVEMENT")
