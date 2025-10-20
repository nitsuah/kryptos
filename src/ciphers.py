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
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug(f"[{i}] Ciphertext char: {c}, Key char: {key[key_index % len(key)]}, "
                              f"Decrypted char: {decrypted_char}, C-Index: {c_index}, K-Index: {k_index}, P-Index: {p_index}")
            key_index += 1
        elif preserve_non_alpha:
            plaintext.append(c)  # Preserve non-alphabetic characters as-is
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                logging.debug(f"[{i}] Non-alphabetic char preserved: {c}")

    return ''.join(plaintext)

def kryptos_k3_decrypt(ciphertext):
    """
    Decrypts Kryptos K3 using the historically verified double rotational transposition method.
    
    Method (from kryptosfan.wordpress.com):
    1. Remove the leading '?' 
    2. Grid into 24×14 matrix (24 columns, 14 rows)
    3. Rotate right 90 degrees  
    4. Change column width to 8 and rotate right 90 degrees again
    5. This gives the final plaintext
    
    This is pure transposition - no Vigenère cipher needed for K3!
    """
    # Step 1: Clean the ciphertext - remove spaces and leading '?'
    clean_text = ''.join(ciphertext.split())
    if clean_text.startswith('?'):
        clean_text = clean_text[1:]
    
    # Step 2: Apply the double rotational transposition
    return double_rotational_transposition(clean_text)

def double_rotational_transposition(text):
    """
    Apply the K3 double rotational transposition method:
    1. Grid into 24×14 matrix
    2. Rotate right 90 degrees
    3. Change to 8-column width and rotate right 90 degrees again
    """
    # Step 1: Create 24×14 grid (24 columns, 14 rows)
    cols1, rows1 = 24, 14
    
    if len(text) != cols1 * rows1:
        raise ValueError(f"K3 ciphertext must be exactly {cols1 * rows1} characters (got {len(text)}).")
    
    
    # Fill the 24×14 matrix row by row
    matrix1 = []
    for i in range(rows1):
        row = text[i * cols1:(i + 1) * cols1]
        matrix1.append(list(row))
    
    # Step 2: Rotate right 90 degrees
    # After rotation: 14 columns, 24 rows
    matrix2 = rotate_matrix_right_90(matrix1)
    
    # Convert rotated matrix to string
    rotated_text = ''
    for row in matrix2:
        rotated_text += ''.join(row)
    
    # Step 3: Change column width to 8 and rotate right 90 degrees again
    cols3 = 8
    rows3 = len(rotated_text) // cols3
    
    # Fill the 8-column matrix row by row
    matrix3 = []
    for i in range(rows3):
        row = rotated_text[i * cols3:(i + 1) * cols3]
        matrix3.append(list(row))
    
    # Rotate right 90 degrees again
    matrix4 = rotate_matrix_right_90(matrix3)
    
    # Convert final matrix to string
    result = ''
    for row in matrix4:
        result += ''.join(row)
    
    return result

def rotate_matrix_right_90(matrix):
    """
    Rotate a matrix 90 degrees clockwise (right)
    Original: matrix[row][col]
    After rotation: new_matrix[col][num_rows - 1 - row]
    """
    rows = len(matrix)
    cols = len(matrix[0])
    
    # New matrix dimensions: original cols become new rows, original rows become new cols
    new_matrix = [[''] * rows for _ in range(cols)]
    
    for row in range(rows):
        for col in range(cols):
            new_row = col
            new_col = rows - 1 - row
            new_matrix[new_row][new_col] = matrix[row][col]
    
    return new_matrix

def transposition_decrypt(ciphertext, key=None):
    """
    Legacy transposition function - kept for compatibility.
    For K3, use kryptos_k3_decrypt() instead.
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
        # Use the K3-specific method
        return kryptos_k3_decrypt(ciphertext)

def polybius_decrypt(ciphertext, key_square):
    """
    Decrypts a Polybius cipher using the provided key square.

    Args:
        ciphertext (str): The encrypted message, consisting of pairs of digits.
        key_square (list of list of str): A 5x5 grid representing the Polybius square.

    Returns:
        str: The decrypted plaintext message.
    """
    # Ensure the key square is a 5x5 grid
    if len(key_square) != 5 or any(len(row) != 5 for row in key_square):
        raise ValueError("Key square must be a 5x5 grid.")

    # Split ciphertext into pairs of digits
    if len(ciphertext) % 2 != 0:
        raise ValueError("Ciphertext length must be even.")

    pairs = [ciphertext[i:i+2] for i in range(0, len(ciphertext), 2)]
    plaintext = []

    for pair in pairs:
        try:
            row, col = int(pair[0]) - 1, int(pair[1]) - 1
            plaintext.append(key_square[row][col])
        except (IndexError, ValueError):
            raise ValueError(f"Invalid pair in ciphertext: {pair}")

    return ''.join(plaintext)