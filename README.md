# KRYPTOS

Inspired by *The Unexplained* with William Shatner, I set out to solve Kryptos using Python! This project focuses on implementing cryptographic techniques, specifically the Vigenère cipher and structural transposition analysis, to decrypt the famous Kryptos sculpture.

## Current Progress

### K1: "Between subtle shading and the absence of light lies the nuance of iqlusion"

- **Status**: Solved.
- **Details**: Decrypted via Vigenère using keyed alphabet `KRYPTOSABCDEFGHIJLMNQUVWXZ`. Intentional misspelling preserved: `IQLUSION`.

### K2: "It was totally invisible. How's that possible?"

- **Status**: Solved.
- **Details**: Vigenère (key: `ABSCISSA`). Includes embedded null/structural padding (`S`) for historical alignment. Contains geospatial coordinates and narrative text.

### K3: "Slowly, desperately slowly, the remains of passage debris..."

- **Status**: Solved (double rotational transposition method).
- **Details**: Implemented the documented 24×14 grid → 90° rotation → reshape to 8-column grid → second 90° rotation. Resulting plaintext matches known solution including deliberate misspelling `DESPARATLY` (analogous to `IQLUSION` in K1).

### K4: The unsolved mystery

- **Status**: Unsolved.
- **Next Focus**: Research masking techniques, positional/overlay hypotheses, layered transposition, and potential null insertion strategies (see Kryptosfan blog & CIA hints: `BERLIN`, `CLOCK`).

## Deliberate Misspellings / Anomalies

| Section | Cipher Plaintext Form | Expected Modern Spelling | Note |
|---------|-----------------------|---------------------------|------|
| K1      | IQLUSION              | ILLUSION                  | Intentional artistic alteration |
| K3      | DESPARATLY            | DESPERATELY               | Preserved from sculpture transcription |

## Features

- **Vigenère Cipher** with keyed alphabet handling
- **K3 Double Rotational Transposition** implementation
- **Config Driven** (`config/config.json`) for ciphertexts, keys, and parameters
- **Test Suite** validating K1–K3 solutions
- **Exploratory Utilities** for frequency & crib analysis

## Roadmap Toward K4

Planned analytical modules:

- Layered transposition brute-force scaffolding
- Probable word / crib placement scoring (BERLIN, CLOCK, EASTNORTHEAST)
- Recursive masking / null removal heuristics
- N-gram fitness ranking over candidate decrypts
- Overlay & spiral path experiments (grid-based)

## How to Run

```bash
git clone https://github.com/nitsuah/kryptos.git
cd kryptos
pip install -r requirements.txt
python -m unittest discover -s tests
```

## References & Research

- [UCSD Crypto Project by Karl Wang](https://mathweb.ucsd.edu/~crypto/Projects/KarlWang/index2.html)
- [Kryptos Wiki](https://en.wikipedia.org/wiki/Kryptos)
- [Vigenère Cipher Explanation](https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher)
- [Kryptosfan Blog](https://kryptosfan.wordpress.com/k3/k3-solution-3/)
