"""Test Beaufort cipher implementation."""

from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / 'src'))

from kryptos.k4.beaufort import beaufort_decrypt, beaufort_encrypt  # noqa: E402


def test_beaufort_reciprocal():
    """Test that Beaufort encryption/decryption is reciprocal."""
    print("=" * 80)
    print("TEST 1: Beaufort Reciprocal Property")
    print("=" * 80)

    plaintext = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
    key = "SECRET"

    print(f"Plaintext:  {plaintext}")
    print(f"Key:        {key}")
    print()

    # Encrypt
    ciphertext = beaufort_encrypt(plaintext, key)
    print(f"Encrypted:  {ciphertext}")

    # Decrypt (should get back plaintext)
    decrypted = beaufort_decrypt(ciphertext, key)
    print(f"Decrypted:  {decrypted}")
    print()

    if decrypted == plaintext:
        print("SUCCESS: Decryption recovered plaintext")
    else:
        print(f"FAILED: Expected {plaintext}, got {decrypted}")

    # Test reciprocal property: encrypt(encrypt(P, K), K) = P
    double_encrypt = beaufort_encrypt(ciphertext, key)
    print(f"\nDouble encrypt: {double_encrypt}")

    if double_encrypt == plaintext:
        print("SUCCESS: Beaufort is reciprocal (encrypt = decrypt)")
    else:
        print(f"FAILED: Expected {plaintext}, got {double_encrypt}")

    return decrypted == plaintext


def test_beaufort_vs_vigenere():
    """Compare Beaufort vs Vigenère cipher."""
    print("\n" + "=" * 80)
    print("TEST 2: Beaufort vs Vigenère Comparison")
    print("=" * 80)

    from kryptos.ciphers import vigenere_decrypt

    plaintext = "ATTACKATDAWN"
    key = "LEMON"

    # Vigenère encryption (manual)
    from kryptos.ciphers import KEYED_ALPHABET

    vigenere_ct = ""
    for i, p in enumerate(plaintext):
        p_idx = KEYED_ALPHABET.index(p)
        k_idx = KEYED_ALPHABET.index(key[i % len(key)])
        c_idx = (p_idx + k_idx) % len(KEYED_ALPHABET)
        vigenere_ct += KEYED_ALPHABET[c_idx]

    # Beaufort encryption
    beaufort_ct = beaufort_encrypt(plaintext, key)

    print(f"Plaintext:       {plaintext}")
    print(f"Key:             {key}")
    print(f"Vigenère CT:     {vigenere_ct}")
    print(f"Beaufort CT:     {beaufort_ct}")
    print()

    # Verify they're different
    if vigenere_ct != beaufort_ct:
        print("SUCCESS: Beaufort and Vigenère produce different ciphertexts")
    else:
        print("FAILED: Ciphertexts should differ")

    # Decrypt Vigenère
    vig_pt = vigenere_decrypt(vigenere_ct, key)
    print(f"Vigenère decrypt: {vig_pt}")

    # Decrypt Beaufort
    bea_pt = beaufort_decrypt(beaufort_ct, key)
    print(f"Beaufort decrypt: {bea_pt}")

    success = vig_pt == plaintext and bea_pt == plaintext
    if success:
        print("\nSUCCESS: Both ciphers decrypt correctly")
    else:
        print("\nFAILED: Decryption mismatch")

    return success


def test_beaufort_edge_cases():
    """Test edge cases."""
    print("\n" + "=" * 80)
    print("TEST 3: Edge Cases")
    print("=" * 80)

    # Test 1: Empty key
    try:
        beaufort_encrypt("TEST", "")
        print("FAILED: Should raise ValueError for empty key")
        return False
    except ValueError:
        print("SUCCESS: Empty key raises ValueError")

    # Test 2: Non-alpha preservation
    plaintext = "HELLO WORLD!"
    key = "KEY"
    encrypted = beaufort_encrypt(plaintext, key, preserve_non_alpha=True)
    decrypted = beaufort_decrypt(encrypted, key, preserve_non_alpha=True)

    print(f"\nPlaintext:  {plaintext}")
    print(f"Encrypted:  {encrypted}")
    print(f"Decrypted:  {decrypted}")

    if " " in encrypted and "!" in encrypted and decrypted == plaintext:
        print("SUCCESS: Non-alpha characters preserved")
        return True
    else:
        print("FAILED: Non-alpha preservation issue")
        return False


def test_beaufort_known_example():
    """Test with a known Beaufort example."""
    print("\n" + "=" * 80)
    print("TEST 4: Known Example")
    print("=" * 80)

    # Using standard alphabet for reference
    # Plaintext: HELLO
    # Key: KEY
    # Standard Beaufort: C[i] = (K[i] - P[i]) mod 26
    # H=7, E=4, L=11, L=11, O=14
    # K=10, E=4, Y=24
    # C[0] = (10-7) = 3 = D
    # C[1] = (4-4) = 0 = A
    # C[2] = (24-11) = 13 = N
    # C[3] = (10-11) = -1 = 25 = Z
    # C[4] = (4-14) = -10 = 16 = Q

    # But we use KEYED alphabet, so results will differ
    plaintext = "HELLO"
    key = "KEY"

    encrypted = beaufort_encrypt(plaintext, key)
    decrypted = beaufort_decrypt(encrypted, key)

    print(f"Plaintext:  {plaintext}")
    print(f"Key:        {key}")
    print(f"Encrypted:  {encrypted}")
    print(f"Decrypted:  {decrypted}")
    print()

    if decrypted == plaintext:
        print("SUCCESS: Known example works correctly")
        return True
    else:
        print(f"FAILED: Expected {plaintext}, got {decrypted}")
        return False


if __name__ == "__main__":
    results = []

    results.append(test_beaufort_reciprocal())
    results.append(test_beaufort_vs_vigenere())
    results.append(test_beaufort_edge_cases())
    results.append(test_beaufort_known_example())

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\nALL TESTS PASSED")
    else:
        print(f"\n{total - passed} TEST(S) FAILED")
