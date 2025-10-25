"""Test brute-force period detection on simple transposition."""

from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / 'src'))

from kryptos.k4.transposition_analysis import (  # noqa: E402
    detect_period_by_brute_force,
)

PLAINTEXT = (
    "CRYPTOGRAPHYISTHEPRACTICEANDSTUDY"
    "OFSECURECOMMUNICATIONINTHEPRESENCE"
    "OFTHIRDPARTIESMOREGENERALLYITISA"
    "BOUTCONSTRUCTINGANDANALYZINGPROTO"
    "COLSTHATPREVENTTHIRDPARTIESORTHE"
    "PUBLICFROMREADINGPRIVATEMESSAGES"
)


def encrypt_columnar(plaintext: str, period: int, permutation: list[int]) -> str:
    """Encrypt using columnar transposition."""
    text = ''.join(c for c in plaintext.upper() if c.isalpha())
    columns = ['' for _ in range(period)]
    for i, char in enumerate(text):
        columns[i % period] += char
    return ''.join(columns[p] for p in permutation)


print("=" * 80)
print("BRUTE-FORCE PERIOD DETECTION TEST")
print("=" * 80)

# Test case: period 7 with random permutation
period = 7
perm = [3, 0, 5, 1, 6, 4, 2]
ciphertext = encrypt_columnar(PLAINTEXT, period, perm)

print(f"True period: {period}")
print(f"Ciphertext length: {len(ciphertext)}")
print("Testing periods 2-15...")
print()

results = detect_period_by_brute_force(ciphertext, min_period=2, max_period=15, top_n=5)

print("Top 5 results:")
for i, (p, score, preview) in enumerate(results, 1):
    marker = "<<<" if p == period else ""
    print(f"{i}. Period {p:2d}: score={score:.4f} {marker}")
    print(f"   Preview: {preview}")

print()
if results[0][0] == period:
    print("SUCCESS: Correct period detected as #1!")
else:
    print(f"PARTIAL: Correct period at position #{[p for p, _, _ in results].index(period) + 1}")
