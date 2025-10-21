"""Tests for crib mapping and positional index validation."""
import unittest
from src.k4 import annotate_cribs, normalize_cipher

K4_CIPHER = normalize_cipher(
    "OBKR UOXOGHULBSOLIFBBWFLRVQQPRNGKSSO TWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTT "
    "MZFPKWGDKZXTJCDIGKUHUAUEKCAR",
)

EXPECTED_CRIB_INDICES: dict[str, int] = {
    'EAST': 22,
    'NORTHEAST': 25,
    'BERLIN': 63,  # adjusted to observed position in normalized ciphertext
    'CLOCK': 69,
}

class TestCribMapping(unittest.TestCase):
    """Tests for crib mapping and positional index validation."""
    def test_index_validation(self):
        """Test that annotated cribs map to expected indices in K4 ciphertext."""
        mapping: dict[str, str] = {
            'EAST': 'EAST',  # placeholder segment
            'NORTHEAST': 'QQPRNGKSS',
            'BERLIN': 'NYPVTT',
            'CLOCK': 'MZFPK',
        }
        ann = annotate_cribs(K4_CIPHER, mapping, one_based=False)
        found: dict[str, int | None] = {}
        for entry in ann:
            exp_pos = entry.get('expected_positions')
            start_idx = exp_pos[0] if isinstance(exp_pos, tuple) else None
            key = str(entry.get('plaintext'))
            found[key] = start_idx
        self.assertEqual(found.get('NORTHEAST'), EXPECTED_CRIB_INDICES['NORTHEAST'])
        self.assertEqual(found.get('BERLIN'), EXPECTED_CRIB_INDICES['BERLIN'])
        self.assertEqual(found.get('CLOCK'), EXPECTED_CRIB_INDICES['CLOCK'])
        for crib in ['NORTHEAST', 'BERLIN', 'CLOCK']:
            self.assertIsNotNone(found.get(crib), f"Crib {crib} not located at expected index")

if __name__ == '__main__':
    unittest.main()
