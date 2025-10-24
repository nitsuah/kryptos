"""Berlin Clock Vigenère hypothesis."""


class BerlinClockVigenereHypothesis:
    """Berlin Clock Vigenère - use clock lamp states as Vigenère keys.

    Tests all 24 hours (00:00-23:00) using Berlin Clock lamp sequences
    as shift patterns. Lamp states encode temporal information that may
    relate to K4's BERLIN/CLOCK themes.
    """

    def __init__(self, hours: list[int] | None = None):
        """Initialize Berlin Clock Vigenère hypothesis.

        Args:
            hours: Hours to test (default: 0-23, all 24 hours)
        """
        self.hours = hours or list(range(24))

    def _berlin_clock_vigenere_decrypt(self, ciphertext: str, hour: int) -> str:
        """Decrypt using Berlin Clock lamp state as Vigenère key."""
        from datetime import time

        from kryptos.k4.berlin_clock import full_berlin_clock_shifts

        # Get lamp state for this hour (at minute 0)
        t = time(hour, 0, 0)
        shifts = full_berlin_clock_shifts(t)

        # Apply shifts as Vigenère-style decryption
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ct_clean = ''.join(c for c in ciphertext.upper() if c.isalpha())
        plaintext = ''

        for i, c in enumerate(ct_clean):
            ct_idx = alphabet.index(c)
            shift = shifts[i % len(shifts)]  # Cycle through lamp states
            pt_idx = (ct_idx - shift) % 26
            plaintext += alphabet[pt_idx]

        return plaintext

    def generate_candidates(self, ciphertext: str, limit: int = 10):
        """Generate candidates by testing Berlin Clock states for each hour."""
        from kryptos.k4.hypotheses import Candidate
        from kryptos.k4.scoring import combined_plaintext_score

        candidates_list = []

        for hour in self.hours:
            plaintext = self._berlin_clock_vigenere_decrypt(ciphertext, hour)
            score = combined_plaintext_score(plaintext)

            candidates_list.append(
                Candidate(
                    id=f'berlin_clock_vig_h{hour:02d}',
                    plaintext=plaintext,
                    key_info={'type': 'berlin_clock_vigenere', 'hour': hour},
                    score=score,
                ),
            )

        # Sort by score and return top candidates
        candidates_list.sort(key=lambda c: c.score, reverse=True)
        return candidates_list[:limit]


# Quick test
if __name__ == '__main__':
    K4 = 'OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK'

    print('Testing Berlin Clock Vigenère...')
    bc = BerlinClockVigenereHypothesis(hours=[0, 6, 12, 18])  # Test 4 hours
    cands = bc.generate_candidates(K4, limit=4)
    for c in cands:
        print(f'  {c.score:.2f} hour={c.key_info["hour"]:02d} -> {c.plaintext[:30]}...')
