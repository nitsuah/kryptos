import pytest

import ciphers


def test_rotate_matrix_right_90_square():
    m = [["a", "b"], ["c", "d"]]
    r = ciphers.rotate_matrix_right_90(m)
    assert r == [["c", "a"], ["d", "b"]]


def test_transposition_decrypt_padding_and_key():
    # use a small synthetic example by padding to required size
    sample = 'A' * 10
    # transposition_decrypt expects width=86 height=4 -> 344 chars; function pads shorter inputs
    out = ciphers.transposition_decrypt(sample, key='KEY')
    assert isinstance(out, str)
    assert len(out) == 86 * 4


def test_k3_decrypt_size_error():
    with pytest.raises(ValueError):
        ciphers.double_rotational_transposition('TOO_SHORT')
