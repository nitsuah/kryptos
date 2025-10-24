"""Additional cipher hypotheses for K4 testing."""

from dataclasses import dataclass


@dataclass(slots=True)
class Candidate:
    """A candidate decryption result."""

    id: str
    plaintext: str
    key_info: dict
    score: float


class FourSquareHypothesis:
    """Four-square cipher - tests KRYPTOS/BERLIN/CLOCK/ABSCISSA combinations."""

    def __init__(self, keywords: list[str] | None = None):
        self.keywords = keywords or ['KRYPTOS', 'BERLIN', 'CLOCK', 'ABSCISSA']

    def _build_grid(self, keyword: str) -> list[list[str]]:
        """Build 5×5 keyed Polybius grid."""
        alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'
        kw = ''.join(c if c != 'J' else 'I' for c in keyword.upper() if c.isalpha())
        chars = []
        seen = set()
        for c in kw + alphabet:
            if c not in seen:
                chars.append(c)
                seen.add(c)
        return [list(chars[i : i + 5]) for i in range(0, 25, 5)]

    def _plain_grid(self) -> list[list[str]]:
        """Standard alphabet grid."""
        alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'
        return [list(alphabet[i : i + 5]) for i in range(0, 25, 5)]

    def _find(self, grid: list[list[str]], char: str) -> tuple[int, int]:
        """Find character position."""
        for i, row in enumerate(grid):
            for j, c in enumerate(row):
                if c == char:
                    return (i, j)
        return (0, 0)

    def _decrypt(self, ct: str, key1: str, key2: str) -> str:
        """Decrypt using four-square."""
        pt_grid = self._plain_grid()
        ct1 = self._build_grid(key1)
        ct2 = self._build_grid(key2)
        text = ''.join(c if c != 'J' else 'I' for c in ct.upper() if c.isalpha())
        if len(text) % 2 == 1:
            text += 'X'
        result = ''
        for i in range(0, len(text), 2):
            r1, c1 = self._find(ct1, text[i])
            r2, c2 = self._find(ct2, text[i + 1])
            result += pt_grid[r1][c2] + pt_grid[r2][c1]
        return result

    def generate_candidates(self, ciphertext: str, limit: int = 10) -> list[Candidate]:
        """Generate four-square candidates."""
        from kryptos.k4.scoring import combined_plaintext_score

        cands = []
        for i, k1 in enumerate(self.keywords):
            for k2 in self.keywords[i:]:
                pt = self._decrypt(ciphertext, k1, k2)
                score = combined_plaintext_score(pt)
                cands.append(
                    Candidate(
                        id=f"foursquare_{k1.lower()}_{k2.lower()}",
                        plaintext=pt,
                        key_info={'type': 'foursquare', 'key1': k1, 'key2': k2},
                        score=score,
                    ),
                )
        cands.sort(key=lambda c: c.score, reverse=True)
        return cands[:limit]


class BifidHypothesis:
    """Bifid cipher - combines Polybius square with transposition."""

    def __init__(self, keyword: str = 'KRYPTOS', periods: list[int] | None = None):
        self.keyword = keyword
        self.periods = periods or list(range(5, 21))

    def _build_grid(self, keyword: str) -> list[list[str]]:
        """Build 5×5 Polybius square."""
        alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'
        kw = ''.join(c if c != 'J' else 'I' for c in keyword.upper() if c.isalpha())
        chars = []
        seen = set()
        for c in kw + alphabet:
            if c not in seen:
                chars.append(c)
                seen.add(c)
        return [list(chars[i : i + 5]) for i in range(0, 25, 5)]

    def _find(self, grid: list[list[str]], char: str) -> tuple[int, int]:
        """Find coordinates."""
        for i, row in enumerate(grid):
            for j, c in enumerate(row):
                if c == char:
                    return (i, j)
        return (0, 0)

    def _decrypt(self, ct: str, keyword: str, period: int) -> str:
        """Decrypt using bifid."""
        grid = self._build_grid(keyword)
        text = ''.join(c if c != 'J' else 'I' for c in ct.upper() if c.isalpha())
        coords = [self._find(grid, c) for c in text]

        # Simplified bifid decryption (period-based transposition)
        result = ''
        for chunk_start in range(0, len(coords), period):
            chunk = coords[chunk_start : chunk_start + period]
            n = len(chunk)
            # De-transpose coordinates
            rows = []
            cols = []
            for r, c in chunk:
                rows.append(r)
                cols.append(c)

            # Reconstruct plaintext (simplified)
            for i in range(n):
                result += grid[rows[i]][cols[i]]

        return result

    def generate_candidates(self, ciphertext: str, limit: int = 10) -> list[Candidate]:
        """Generate bifid candidates."""
        from kryptos.k4.scoring import combined_plaintext_score

        cands = []
        for period in self.periods:
            pt = self._decrypt(ciphertext, self.keyword, period)
            score = combined_plaintext_score(pt)
            cands.append(
                Candidate(
                    id=f"bifid_{self.keyword.lower()}_p{period}",
                    plaintext=pt,
                    key_info={'type': 'bifid', 'keyword': self.keyword, 'period': period},
                    score=score,
                ),
            )
        cands.sort(key=lambda c: c.score, reverse=True)
        return cands[:limit]


# Quick test
if __name__ == '__main__':
    K4 = 'OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK'

    print('Testing FourSquare...')
    fs = FourSquareHypothesis()
    fs_cands = fs.generate_candidates(K4, limit=3)
    for c in fs_cands:
        print(f'  {c.score:.2f} {c.key_info["key1"]}/{c.key_info["key2"]} -> {c.plaintext[:30]}...')

    print('\nTesting Bifid...')
    bf = BifidHypothesis()
    bf_cands = bf.generate_candidates(K4, limit=3)
    for c in bf_cands:
        print(f'  {c.score:.2f} period={c.key_info["period"]} -> {c.plaintext[:30]}...')
