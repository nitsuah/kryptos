import json
from src.ciphers import vigenere_decrypt, transposition_decrypt
from src.analysis import frequency_analysis, check_cribs
from src.report import generate_report

def main():
    # Load configuration
    with open("config/config.json", "r") as f:
        config = json.load(f)

    ciphertexts = config["ciphertexts"]
    cribs = config["cribs"]
    parameters = config["parameters"]

    # Decrypt K1
    k1_ciphertext = ciphertexts["K1"]
    k1_keyword = parameters["vigenere_keys"][0]  # Keyword for K1 from config
    print(f"Decrypting K1 with keyword '{k1_keyword}'...")

    k1_plaintext = vigenere_decrypt(k1_ciphertext, k1_keyword)
    print(f"K1 Decrypted Text: {k1_plaintext}")

    # Check for cribs in the decrypted text
    matches = check_cribs(k1_plaintext, cribs)
    if matches:
        print(f"Crib matches found in K1: {matches}")
    else:
        print("No crib matches found in K1.")

    for cipher_name, ciphertext in ciphertexts.items():
        results = {}
        for key in parameters["vigenere_keys"]:
            plaintext = vigenere_decrypt(ciphertext, key)
            frequencies = frequency_analysis(plaintext)
            matches = check_cribs(plaintext, cribs)

            results["frequencies"] = frequencies
            results["cribs"] = matches

            generate_report(results, cipher_name)

if __name__ == "__main__":
    main()