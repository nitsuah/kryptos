#!/usr/bin/env python3
"""
Validate Phase 5.3 implementation with K1/K2/K3 known plaintexts.
Tests real cipher execution on solved Kryptos sections.
"""

import sys
from pathlib import Path

# Add project root to path (so 'src' is discoverable)
sys.path.insert(0, str(Path(__file__).parent.parent))

from kryptos.agents.spy import SpyAgent  # noqa: E402
from kryptos.ciphers import vigenere_decrypt  # noqa: E402
from kryptos.k4.vigenere_key_recovery import recover_key_by_frequency  # noqa: E402


def test_k1():
    """Test K1 (transposition cipher - not Vigenère)."""
    print("\n" + "=" * 80)
    print("K1: Columnar Transposition")
    print("=" * 80)

    # K1 ciphertext
    k1_cipher = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJ" "YQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"

    # K1 known plaintext
    k1_plain = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"

    print(f"Ciphertext: {k1_cipher}")
    print(f"Known plaintext: {k1_plain}")
    print("\nNote: K1 is columnar transposition, not Vigenère")
    print("Phase 5.3 currently supports Vigenère key recovery only")
    print("Status: SKIP (cipher type not supported yet)")

    return None


def test_k2():
    """Test K2 (Vigenère with keyword ABSCISSA)."""
    print("\n" + "=" * 80)
    print("K2: Vigenère Cipher")
    print("=" * 80)

    # K2 ciphertext
    k2_cipher = (
        "VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKK"
        "DQMCPFQZDQMMIAGPFXHQRLGTIMVMZJANQLVKQEDAGDVFRPJUNGEUNAQZGZLE"
        "CGYUXUEENJTBJLBQCRTBJDFHRRYIZETKZEMVDUFKSJHKFWHKUWQLSZFTIHHDDDUVH"
        "DWKBFUFPWNTDFIYCUQZEREEVLDKFEZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTEZ"
        "FKZBSFDQVGOGIPUFXHHDRKFFHQNTGPUAECNUVPDJMQCLQUMUNEDFQELZZVRR"
        "GKFFVOEEXBDMVPNFQXEZLGREDNQFMPNZGLFLPMRJQYALMGNUVPDXVKPDQUMEB"
        "EDMHDAFMJGZNUPLGEWJLLAETG"
    )

    # K2 key
    k2_key = "ABSCISSA"

    # K2 known plaintext
    k2_plain = (
        "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDTHE"
        "XDATACAMEFROMASATELLITESPECTROSCOPYITHEHOWSOCRYSTALLIZETHEYLAYEREDMAN"
        "TICROCKSYLAMAGNESIUMFERROUSHOWDOWEMOLYTHEYTILTEDTHECRYSTALLINESTRUCTURENO"
        "TCARBROHYDRATESMOLBDENMECARBONCARATNALUMINYMOLIDBDENUM"
    )

    print(f"Ciphertext length: {len(k2_cipher)}")
    print(f"Known key: {k2_key} (length {len(k2_key)})")
    print(f"Known plaintext: {k2_plain[:60]}...")

    # Test 1: Direct decryption with known key
    print("\n--- Test 1: Direct decryption with known key ---")
    decrypted = vigenere_decrypt(k2_cipher, k2_key)
    matches = decrypted == k2_plain
    print(f"Decrypted: {decrypted[:60]}...")
    print(f"Expected:  {k2_plain[:60]}...")
    print(f"Match: {'✅ PASS' if matches else '❌ FAIL'}")

    # Test 2: Key recovery attempt
    print("\n--- Test 2: Key recovery from ciphertext ---")
    recovered_keys = recover_key_by_frequency(k2_cipher, len(k2_key), top_n=10)

    if recovered_keys:
        print(f"Top {len(recovered_keys)} candidate keys:")
        spy = SpyAgent()
        for i, key in enumerate(recovered_keys, 1):
            test_decrypt = vigenere_decrypt(k2_cipher, key)
            is_correct = key == k2_key
            marker = "✅ CORRECT" if is_correct else ""

            # Test with SPY agent
            analysis = spy.analyze_candidate(test_decrypt)
            pattern_score = analysis['pattern_score']

            print(f"  {i}. {key} | SPY: {pattern_score:.3f} {marker}")
            print(f"     Decrypted: {test_decrypt[:60]}...")

            if is_correct:
                print(f"\n✅ CORRECT KEY RECOVERED: {key}")
                return True

        print("\n❌ FAIL: Correct key not in top 10 candidates")
        return False
    else:
        print("❌ FAIL: No keys recovered")
        return False


def test_k3():
    """Test K3 (transposition cipher - not Vigenère)."""
    print("\n" + "=" * 80)
    print("K3: Columnar Transposition")
    print("=" * 80)

    # K3 ciphertext
    k3_cipher = (
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

    # K3 known plaintext
    k3_plain = (
        "SLOWLYDESPARATLEYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHELOWER"
        "PARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHINTHEUPPERLEFT"
        "HANDCORNERANDTHENWIDENINGTHEHOLEALITTLEINSERTEDTHECANDLEANDPEEREDINTHEHOTAIR"
        "ESCAPINGFROMTHECHAMBERCAUSEDTHEFLAMETOFLICKERBUTTHENESSENTIALLYDARKNESSAND"
        "BLANKSPACE"
    )

    print(f"Ciphertext: {k3_cipher[:60]}...")
    print(f"Known plaintext: {k3_plain[:60]}...")
    print("\nNote: K3 is columnar transposition, not Vigenère")
    print("Phase 5.3 currently supports Vigenère key recovery only")
    print("Status: SKIP (cipher type not supported yet)")

    return None


def main():
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "KRYPTOS K1/K2/K3 VALIDATION TEST" + " " * 24 + "║")
    print("║" + " " * 15 + "Phase 5.3: Real Cipher Execution Validation" + " " * 19 + "║")
    print("╚" + "=" * 78 + "╝")

    results = {}

    # Test K1
    results['k1'] = test_k1()

    # Test K2
    results['k2'] = test_k2()

    # Test K3
    results['k3'] = test_k3()

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"K1 (Transposition): {'SKIP' if results['k1'] is None else ('PASS' if results['k1'] else 'FAIL')}")
    print(f"K2 (Vigenère):      {'SKIP' if results['k2'] is None else ('✅ PASS' if results['k2'] else '❌ FAIL')}")
    print(f"K3 (Transposition): {'SKIP' if results['k3'] is None else ('PASS' if results['k3'] else 'FAIL')}")

    if results['k2']:
        print("\n✅ SUCCESS: K2 key recovery working!")
        print("Phase 5.3 real cipher execution validated.")
    else:
        print("\n❌ NEEDS WORK: K2 key recovery not finding correct key")
        print("Next step: Tune frequency analysis for Kryptos keyed alphabet")

    return 0 if results['k2'] else 1


if __name__ == "__main__":
    sys.exit(main())
