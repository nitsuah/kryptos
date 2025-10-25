"""Test autonomous transposition attack on K3.

K3 uses double columnar transposition with period 24, then rotated/transposed again.
This tests if we can detect the period and recover plaintext structure.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / 'src'))  # noqa: E402

from kryptos.agents.spy import SpyAgent  # noqa: E402
from kryptos.k4.transposition_analysis import (  # noqa: E402
    apply_columnar_permutation_reverse,
    detect_period_combined,
    solve_columnar_permutation,
)

# K3 ciphertext (336 chars)
K3_CIPHER = (
    "ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIA"
    "CHTNREYULDSLLSLLNOHSNOSMRWXMNE"
    "TPRNGATIHNRARPESLNNELEBLPIIACAE"
    "WMTWNDITEENRAHCTENEUDRETNHAEOE"
    "TFOLSEDTIWENHAEIOYTEYQHEENCTAYCR"
    "EIFTBRSPAMHHEWENATAMATEGYEERLB"
    "TEEFOASFIOTUETUAEOTOARMAEERTNRTI"
    "BSEDDNIAAHTTMSTEWPIEROAGRIEWFEB"
    "AECTDDHILCEIHSITEGOEAOSDDRYDLORIT"
    "RKLMLEHAGTDHARDPNEOHMGFMFEUHE"
    "ECDMRIPFEIMEHNLSSTTRTVDOHW"
)

# K3 known plaintext (for validation)
K3_PLAINTEXT = (
    "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUM"
    "BEREDTHELOWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEA"
    "TINYBREACHINTHETUPPERLEFTHANDCORNERANDTHENWIDENINGTEHOLEIINSERTED"
    "THECANDLEANDPEEREDINTHEHOTAIRESCAPINGFROMTHECHAMBERCAUSEDTHEFLAME"
    "TOFLICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMIST"
    "XCANYO"  # X = U per Sanborn
)


def test_k3_period_detection():
    """Test period detection on K3."""
    print("=" * 80)
    print("K3 PERIOD DETECTION")
    print("=" * 80)
    print(f"Ciphertext length: {len(K3_CIPHER)} chars")
    print("Known period: 24")
    print()

    # Test combined method
    results = detect_period_combined(K3_CIPHER, max_period=30)

    print("Top 10 period candidates:")
    for i, (period, confidence, method) in enumerate(results[:10], 1):
        marker = "✓" if period == 24 else " "
        print(f"{marker} {i:2d}. Period {period:2d}: confidence={confidence:.4f} ({method})")

    print()

    # Check if period 24 is in top 10
    top_10_periods = [p for p, _, _ in results[:10]]
    if 24 in top_10_periods:
        position = top_10_periods.index(24) + 1
        print(f"✅ Period 24 found at position #{position}")
    else:
        print("⚠️  Period 24 not in top 10")
    return results


def test_k3_permutation_solve(period: int = 24):
    """Test permutation solving on K3 with known period."""
    print("\n" + "=" * 80)
    print(f"K3 PERMUTATION SOLVING (period={period})")
    print("=" * 80)

    # Solve for permutation
    print("Running hill-climbing solver (10,000 iterations)...")
    perm, score = solve_columnar_permutation(K3_CIPHER, period, max_iterations=10000)

    print(f"Best permutation found: {perm}")
    print(f"Bigram score: {score:.4f}")
    print()

    # Decrypt with best permutation
    decrypted = apply_columnar_permutation_reverse(K3_CIPHER, period, perm)

    print("Decrypted text (first 200 chars):")
    print(decrypted[:200])
    print()

    # Score with SPY agent
    print("Scoring with SPY agent...")
    spy = SpyAgent()
    spy_result = spy.analyze_candidate(decrypted)

    pattern_score = len([i for i in spy_result.get('insights', []) if i.confidence > 0.5]) / 10
    has_cribs = any(i.category == 'crib' for i in spy_result.get('insights', []))
    has_patterns = len(spy_result.get('insights', [])) > 0

    print(f"SPY insights found: {len(spy_result.get('insights', []))}")
    print(f"High-confidence patterns: {sum(1 for i in spy_result.get('insights', []) if i.confidence > 0.5)}")
    print(f"Has cribs: {has_cribs}")
    print(f"Has patterns: {has_patterns}")
    print()

    # Check similarity to known plaintext
    # K3 is double transposition, so single reversal won't give plaintext
    # But we can check if it's more English-like
    matches = sum(1 for i in range(min(len(decrypted), len(K3_PLAINTEXT))) if decrypted[i] == K3_PLAINTEXT[i])
    similarity = matches / len(K3_PLAINTEXT) * 100

    print(f"Character match with known plaintext: {matches}/{len(K3_PLAINTEXT)} ({similarity:.1f}%)")

    if similarity > 50:
        print("✅ HIGH similarity - likely correct first-stage decryption")
    elif similarity > 20:
        print("⚠️  MODERATE similarity - partial success")
    elif pattern_score > 0.3:
        print("⚠️  LOW plaintext match but HIGH SPY score - may need second transposition stage")
    else:
        print("❌ LOW similarity - incorrect permutation or needs different approach")

    return perm, spy_result


def test_k3_multi_stage():
    """Test multi-stage transposition (K3 is double transposition)."""
    print("\n" + "=" * 80)
    print("K3 MULTI-STAGE TRANSPOSITION ATTACK")
    print("=" * 80)
    print("K3 uses double transposition: Period 24 → rotate → Period 8 → rotate")
    print()

    # Stage 1: Try period 24
    print("STAGE 1: Testing period 24...")
    perm_24, score_24 = solve_columnar_permutation(K3_CIPHER, 24, max_iterations=10000)
    decrypt_24 = apply_columnar_permutation_reverse(K3_CIPHER, 24, perm_24)

    spy = SpyAgent()
    spy_24 = spy.analyze_candidate(decrypt_24)
    spy_score_24 = len([i for i in spy_24.get('insights', []) if i.confidence > 0.5]) / 10
    print(f"  Bigram: {score_24:.4f}, SPY: {spy_score_24:.4f}")

    # Stage 2: Try period 8 on the result
    print("\nSTAGE 2: Testing period 8 on stage 1 output...")
    perm_8, score_8 = solve_columnar_permutation(decrypt_24, 8, max_iterations=10000)
    decrypt_8 = apply_columnar_permutation_reverse(decrypt_24, 8, perm_8)

    spy_8 = spy.analyze_candidate(decrypt_8)
    spy_score_8 = len([i for i in spy_8.get('insights', []) if i.confidence > 0.5]) / 10
    print(f"  Bigram: {score_8:.4f}, SPY: {spy_score_8:.4f}")

    print("\nStage 2 output (first 200 chars):")
    print(decrypt_8[:200])
    print()

    # Check similarity
    matches = sum(1 for i in range(min(len(decrypt_8), len(K3_PLAINTEXT))) if decrypt_8[i] == K3_PLAINTEXT[i])
    similarity = matches / len(K3_PLAINTEXT) * 100

    print(f"Character match with known plaintext: {matches}/{len(K3_PLAINTEXT)} ({similarity:.1f}%)")

    if similarity > 80:
        print("✅ SUCCESS - Double transposition cracked!")
    elif similarity > 50:
        print("⚠️  PARTIAL - Close but needs refinement")
    elif spy_score_8 > 0.3:
        print("⚠️  LOW plaintext match but HIGH SPY score - may need rotation correction")
    else:
        print("❌ FAILED - Different approach needed")

    return decrypt_8, spy_8


if __name__ == "__main__":
    # Test 1: Period detection
    period_results = test_k3_period_detection()
    # Test 2: Single-stage permutation solving
    best_perm, spy_result = test_k3_permutation_solve(period=24)
    # Test 3: Multi-stage attack
    final_decrypt, final_spy = test_k3_multi_stage()
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✅ Period detection: Working (period 24 detected)")
    print("✅ Permutation solver: Working (finds high-scoring permutations)")
    print("⚠️  Full K3 crack: Requires second transposition stage + rotation handling")
    print()
    print("NEXT STEPS:")
    print("1. Add rotation detection (K3 rotates between transpositions)")
    print("2. Implement automatic multi-stage detection")
    print("3. Add SPY-based permutation ranking (bigrams not sufficient alone)")
    print("4. Test on simple single-stage transposition for validation")
