import string

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
            print(f"[{i}] Ciphertext char: {c}, Key char: {key[key_index % len(key)]}, "
                  f"Decrypted char: {decrypted_char}, C-Index: {c_index}, K-Index: {k_index}, P-Index: {p_index}")
            key_index += 1
        elif preserve_non_alpha:
            plaintext.append(c)  # Preserve non-alphabetic characters as-is
            print(f"[{i}] Non-alphabetic char preserved: {c}")

    return ''.join(plaintext)

def transposition_decrypt(ciphertext, key_length):
    """
    Decrypts a transposition cipher by rearranging the ciphertext into a grid.
    """
    # Calculate the number of rows and columns
    num_rows = len(ciphertext) // key_length
    num_extra = len(ciphertext) % key_length
    rows = [''] * key_length

    # Fill the grid column by column
    index = 0
    for col in range(key_length):
        for row in range(num_rows + (1 if col < num_extra else 0)):
            rows[col] += ciphertext[index]
            index += 1

    # Read the grid row by row
    plaintext = ''.join(''.join(row) for row in zip(*rows))
    return plaintext

def polybius_decrypt(ciphertext, key_square):
    # Placeholder for Polybius square decryption
    pass