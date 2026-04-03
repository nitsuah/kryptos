"""Fast tests for explicit thresholding and deterministic ordering in composite chains."""

from kryptos.k4.composite import CompositeChainExecutor


def test_vigenere_then_transposition_applies_threshold_and_is_deterministic(monkeypatch):
    """V→T should filter by threshold and return deterministic tie ordering."""

    monkeypatch.setattr(
        'kryptos.k4.composite.recover_key_by_frequency',
        lambda ciphertext, key_len, top_n=10: ['KEYA'],
    )
    monkeypatch.setattr(
        'kryptos.k4.composite.vigenere_decrypt',
        lambda ciphertext, key: f'DEC-{key}',
    )
    monkeypatch.setattr(
        'kryptos.k4.composite.search_columnar',
        lambda text, min_cols, max_cols: [
            {'text': 'BETA', 'score': 10.0, 'cols': 5, 'perm': [2, 1, 3]},
            {'text': 'ALPHA', 'score': 10.0, 'cols': 5, 'perm': [1, 2, 3]},
            {'text': 'GAMMA', 'score': 8.0, 'cols': 4, 'perm': [1, 3, 2]},
        ],
    )

    executor = CompositeChainExecutor()
    results = executor.vigenere_then_transposition(
        'CIPHERTEXT',
        vigenere_key_length=4,
        transposition_col_range=(4, 6),
        top_n=5,
        min_score_threshold=9.0,
    )

    assert [r['plaintext'] for r in results] == ['ALPHA', 'BETA']
    assert all(r['score'] >= 9.0 for r in results)
    assert all(r['threshold_applied'] == 9.0 for r in results)


def test_transposition_then_vigenere_applies_threshold(monkeypatch):
    """T→V should filter candidates below threshold."""

    monkeypatch.setattr(
        'kryptos.k4.composite.search_columnar',
        lambda text, min_cols, max_cols: [
            {'text': 'T1', 'score': 1.0, 'cols': 5, 'perm': [1, 2, 3]},
            {'text': 'T2', 'score': 1.0, 'cols': 6, 'perm': [1, 3, 2]},
        ],
    )
    monkeypatch.setattr(
        'kryptos.k4.composite.recover_key_by_frequency',
        lambda text, key_len, top_n=3: ['KEY1', 'KEY2'],
    )
    score_map = {
        'T1|KEY1': 11.5,
        'T1|KEY2': 5.0,
        'T2|KEY1': 10.2,
        'T2|KEY2': 4.0,
    }
    monkeypatch.setattr(
        'kryptos.k4.composite.vigenere_decrypt',
        lambda text, key: f'{text}|{key}',
    )
    monkeypatch.setattr(
        'kryptos.k4.composite.combined_plaintext_score',
        lambda plaintext: score_map[plaintext],
    )

    executor = CompositeChainExecutor()
    results = executor.transposition_then_vigenere(
        'CIPHERTEXT',
        transposition_col_range=(5, 6),
        vigenere_key_length=4,
        top_n=10,
        min_score_threshold=10.0,
    )

    assert [r['plaintext'] for r in results] == ['T1|KEY1', 'T2|KEY1']
    assert all(r['score'] >= 10.0 for r in results)
    assert all(r['threshold_applied'] == 10.0 for r in results)
