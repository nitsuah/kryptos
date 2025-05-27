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

def transposition_decrypt(ciphertext, key):
    """
    Decrypts a ciphertext encrypted with Route Transposition followed by Keyed Columnar Transposition.
    
    Args:
        ciphertext (str): The encrypted message.
        key (str): The key for columnar transposition (e.g., 'KRYPTOS').
    
    Returns:
        str: The decrypted plaintext.
    """
    # Normalize inputs
    ciphertext = ciphertext.replace(" ", "").upper()
    key = key.upper()
    
    # Hardcode number of columns for K3
    num_columns = 86
    
    # Map key to indices (KRYPTOS -> 0362514)
    key_order = [0, 3, 6, 2, 5, 1, 4]
    
    # Step 1: Calculate dimensions
    msg_length = len(ciphertext)
    logging.debug(f"Ciphertext length: {msg_length}")
    if msg_length != 337:
        raise ValueError(f"Expected ciphertext length 337, got {msg_length}")
    
    num_rows = (msg_length + num_columns - 1) // num_columns  # Ceiling division, 4 for K3
    logging.debug(f"Number of rows: {num_rows}")
    
    # Step 2: Define column lengths based on problem description
    col_lengths = [47] * 7  # Default to 47 for 5 columns
    col_lengths[0] = 51  # Column 0 (K) has 51 characters
    col_lengths[3] = 51  # Column 3 (P) has 51 characters
    logging.debug(f"Column lengths: {col_lengths}")
    
    # Verify total length
    if sum(col_lengths) != msg_length:
        raise ValueError(f"Column lengths {sum(col_lengths)} do not match ciphertext length {msg_length}")
    
    # Step 1: Split ciphertext into columns based on key order
    columns_by_keyorder = []
    pos = 0
    for idx, col_idx in enumerate(key_order):
        col_len = col_lengths[idx]
        col = ciphertext[pos:pos + col_len]
        columns_by_keyorder.append(col)
        logging.debug(f"Step 1 - Column {col_idx} (key order idx={idx}, len={col_len}): {col}")
        pos += col_len
    logging.debug(f"Step 1 - Columns by key order: {columns_by_keyorder}")

    # Step 2: Reorder columns into input order (left-to-right as in the key)
    columns_in_input_order = [None] * len(key_order)
    for idx, col_idx in enumerate(key_order):
        columns_in_input_order[col_idx] = columns_by_keyorder[idx]
    logging.debug(f"Step 2 - Columns in input order: {columns_in_input_order}")
    for i, col in enumerate(columns_in_input_order):
        logging.debug(f"Step 2 - Input order col {i}: {col}")

    # Step 3: Reconstruct the 86x4 grid by filling columns in input order
    width = 86
    height = 4
    grid = [[''] * width for _ in range(height)]
    idx = 0
    for col in range(width):
        for row in range(height):
            if idx < len(ciphertext):
                grid[row][col] = ciphertext[idx]
                idx += 1
    logging.debug(f"Step 3 - Grid (filled column-wise): {grid}")

    # Step 4: Read each row right-to-left and concatenate to form the plaintext
    plaintext = ''
    for row in grid:
        plaintext += ''.join(row[::-1])
    logging.info(f"Step 4 - Decrypted Text (first 100 chars): {plaintext[:100]}")
    logging.info(f"Step 4 - Decrypted Text length: {len(plaintext)}")
    return plaintext

def polybius_decrypt(ciphertext, key_square):
    # Placeholder for Polybius square decryption
    pass