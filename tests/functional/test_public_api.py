from kryptos import __all__

EXPECTED_MIN = {
    '__version__',
    'vigenere_decrypt',
    'k3_decrypt',
    'double_rotational_transposition',
    'frequency_analysis',
    'check_cribs',
    'k4_decrypt_best',  # convenience
}


def test_public_api_contains_expected_minimum():
    missing = EXPECTED_MIN - set(__all__)
    assert not missing, f'Missing expected exports: {missing}'
