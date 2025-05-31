import string
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def vigenere_decrypt(ciphertext, key, preserve_non_alpha=False):
    """
    Decrypts a Vigenère cipher using the provided key and a keyed alphabet.
    Uses the KRYPTOS keyed alphabet: KRYPTOSABCDEFGHIJLMNQUVWXZ.
    """
    # Define the keyed alphabet
    keyed_alphabet = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
    
    # Ensure ciphertext and key are uppercase and alphabetic
    key = ''.join(c for c in key.upper() if c.isalpha())
    
    plaintext = []
    key_index = 0  # Track the position in the key

    for i, c in enumerate(ciphertext):
        if c.isalpha():  # Only decrypt alphabetic characters
            c_index = keyed_alphabet.index(c)
            k_index = keyed_alphabet.index(key[key_index % len(key)])
            p_index = (c_index - k_index) % len(keyed_alphabet)
            decrypted_char = keyed_alphabet[p_index]
            plaintext.append(decrypted_char)
            logging.debug(f"[{i}] Ciphertext char: {c}, Key char: {key[key_index % len(key)]}, "
                  f"Decrypted char: {decrypted_char}, C-Index: {c_index}, K-Index: {k_index}, P-Index: {p_index}")
            key_index += 1
        elif preserve_non_alpha:
            plaintext.append(c)  # Preserve non-alphabetic characters as-is
            logging.debug(f"[{i}] Non-alphabetic char preserved: {c}")

    return ''.join(plaintext)

def transposition_decrypt(ciphertext, key=None):
    """
    Decrypts Kryptos K3 using route transposition:
    1. Remove spaces from ciphertext.
    2. Remove leading '?' if present (not part of the grid).
    3. Fill a 4-row x 86-column grid row-wise (left-to-right, top-to-bottom).
    4. Read the grid column-wise (top-to-bottom, left-to-right) to get the plaintext.
    """
    # Step 1: Remove spaces
    ciphertext = ''.join(ciphertext.split())
    # Step 2: Remove leading '?' if present
    if ciphertext.startswith('?'):
        ciphertext = ciphertext[1:]
    width = 86
    height = 4
    # Pad ciphertext if too short
    if len(ciphertext) < width * height:
        ciphertext = ciphertext.ljust(width * height, 'X')
    if len(ciphertext) != width * height:
        raise ValueError(f"Expected ciphertext length {width*height}, got {len(ciphertext)}")

    if key is not None:
        key = key.upper()
        repeated_key = (key * ((width // len(key)) + 1))[:width]
        # Get column order: sort (letter, index) pairs
        key_tuples = sorted([(char, idx) for idx, char in enumerate(repeated_key)])
        col_order = [idx for char, idx in key_tuples]
        # Now, split ciphertext into columns in this order
        col_lengths = [height] * width
        cols = []
        start = 0
        for i in range(width):
            cols.append(ciphertext[start:start+col_lengths[i]])
            start += col_lengths[i]
        # Reconstruct the grid: place each column in its original position
        grid = [[''] * width for _ in range(height)]
        for order, orig_col in enumerate(col_order):
            for row in range(height):
                grid[row][orig_col] = cols[order][row]
        # Read the grid row-wise
        plaintext = ''
        for row in range(height):
            for col in range(width):
                plaintext += grid[row][col]
        return plaintext
    else:
        # Default: read columns left-to-right
        grid = [[''] * width for _ in range(height)]
        idx = 0
        for row in range(height):
            for col in range(width):
                grid[row][col] = ciphertext[idx]
                idx += 1
        plaintext = ''
        for col in range(width):
            for row in range(height):
                plaintext += grid[row][col]
        return plaintext

def polybius_decrypt(ciphertext, key_square):
    # Placeholder for Polybius square decryption
    pass