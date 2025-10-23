import pytest

from kryptos.k4 import DecryptResult, decrypt_best


@pytest.mark.slow(False)
def test_decrypt_best_structure():
    # Minimal synthetic ciphertext (not real K4) just to exercise code path.
    ciphertext = "ABCD" * 25  # length 100; pipeline will trim/operate
    result = decrypt_best(ciphertext, limit=5, report=False)
    assert isinstance(result, DecryptResult)
    assert isinstance(result.plaintext, str)
    assert isinstance(result.score, (int, float))
    assert result.candidates  # has at least one candidate
    assert result.lineage and isinstance(result.lineage, list)
    # Ensure best candidate plaintext matches first candidate text
    first = result.candidates[0]
    assert 'text' in first
    assert result.plaintext == first['text']
