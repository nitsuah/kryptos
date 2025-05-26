# KRYPTOS

Inspired by *The Unexplained* with William Shatner, I set out to solve Kryptos using Python! This project focuses on implementing cryptographic techniques, specifically the Vigenère cipher, to decrypt the famous Kryptos sculpture.

## Current Progress

### K1: "Between subtle shading and the absence of light lies the nuance of iqlusion"
- **Status**: Successfully decrypted.
- **Details**: K1 was decrypted using the Vigenère cipher with the KRYPTOS keyed alphabet. The plaintext reveals a poetic phrase with a deliberate misspelling of "illusion" as "iqlusion."

### K2: "It was totally invisible. How's that possible?"
- **Status**: Successfully decrypted.
- **Details**: K2 was decrypted using the Vigenère cipher. Adjustments were made to the ciphertext to include a null character (`'S'`) for proper alignment. The plaintext describes the use of Earth's magnetic field to transmit information.

### K3: "Slowly, desperately slowly, the remains of passage debris..."
- **Status**: In progress.
- **Details**: Work on K3 is ongoing. This section is believed to use a similar cipher but may include additional complexities, such as transposition.

### K4: The unsolved mystery
- **Status**: Not yet solved.
- **Details**: K4 remains one of the greatest cryptographic challenges. Efforts will focus on advanced cryptographic techniques and pattern analysis to uncover its secrets. Where there is a will, there is a way!

## Features

- **Vigenère Cipher Implementation**: A robust implementation of the Vigenère cipher, supporting keyed alphabets and configurable options for preserving non-alphabetic characters.
- **Configurable Inputs**: Ciphertext and keys are loaded dynamically from a configuration file (`config.json`), allowing for easy updates and experimentation.
- **Debugging Tools**: Detailed logging and debugging outputs to trace decryption steps and identify issues.

## Next Steps

- Finalize the decryption of K3 and K4.
- Explore potential solutions for the unsolved K4 section using advanced cryptographic techniques and pattern analysis.
- Refactor and optimize the codebase for better performance and readability.

## How to Run

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/kryptos.git
   cd kryptos
   pip install -r requirements.txt
   python -m unittest discover -s tests
    ```

## Works Cited

- [UCSD Crypto Project by Karl Wang](https://mathweb.ucsd.edu/~crypto/Projects/KarlWang/index2.html)
- [Kryptos Wiki](https://en.wikipedia.org/wiki/Kryptos)
- [Vigenère Cipher Explanation](https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher)
