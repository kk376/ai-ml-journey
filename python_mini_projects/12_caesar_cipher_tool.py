"""Caesar Cipher Tool: encrypt, decrypt, brute-force crack, and process text files."""

import os


def shift_character(char, shift):
    """Shift a single alphabetical character preserving case. Non-alphabetic chars remain unchanged."""
    if "a" <= char <= "z":
        base = ord("a")
        return chr((ord(char) - base + shift) % 26 + base)
    if "A" <= char <= "Z":
        base = ord("A")
        return chr((ord(char) - base + shift) % 26 + base)
    return char


def transform_text(text, shift):
    """Encrypt or decrypt a string by applying a Caesar cipher shift key."""
    return "".join(shift_character(char, shift) for char in text)


def encrypt_mode():
    """Handle interactive text encryption."""
    print("\n=== Encrypt Text ===")
    text = input("Enter text to encrypt: ").strip()
    if not text:
        print("Text cannot be empty.")
        return

    shift_input = input("Enter shift key (integer, e.g. 1 to 25): ").strip()
    try:
        shift = int(shift_input)
    except ValueError:
        print("Invalid shift value. Must be an integer.")
        return

    encrypted = transform_text(text, shift)
    print("\n" + "=" * 45)
    print("ENCRYPTION RESULT")
    print("=" * 45)
    print(f"Original : {text}")
    print(f"Shift    : {shift % 26}")
    print(f"Ciphertext: {encrypted}")
    print("=" * 45 + "\n")


def decrypt_mode():
    """Handle interactive text decryption with known shift."""
    print("\n=== Decrypt Text ===")
    ciphertext = input("Enter ciphertext to decrypt: ").strip()
    if not ciphertext:
        print("Ciphertext cannot be empty.")
        return

    shift_input = input("Enter known shift key: ").strip()
    try:
        shift = int(shift_input)
    except ValueError:
        print("Invalid shift value. Must be an integer.")
        return

    decrypted = transform_text(ciphertext, -shift)
    print("\n" + "=" * 45)
    print("DECRYPTION RESULT")
    print("=" * 45)
    print(f"Ciphertext: {ciphertext}")
    print(f"Shift Used: {shift % 26}")
    print(f"Plaintext : {decrypted}")
    print("=" * 45 + "\n")


def brute_force_mode():
    """Display all 25 possible Caesar cipher shifts to assist cryptanalysis."""
    print("\n=== Brute-Force Decryption (Crack Ciphertext) ===")
    ciphertext = input("Enter ciphertext to crack: ").strip()
    if not ciphertext:
        print("Ciphertext cannot be empty.")
        return

    print("\n" + "=" * 60)
    print(f"{'Shift':<8} {'Candidate Plaintext'}")
    print("=" * 60)

    for shift in range(1, 26):
        candidate = transform_text(ciphertext, -shift)
        print(f"Shift {shift:<2}: {candidate}")

    print("=" * 60)
    print("Review the outputs above to identify readable English plaintext.\n")


def file_cipher_mode():
    """Encrypt or decrypt an entire text file and save output to disk."""
    print("\n=== File Cipher Processing ===")
    input_path = input("Enter path to input file: ").strip()

    if not os.path.isfile(input_path):
        print(f"Error: File '{input_path}' does not exist.")
        return

    mode = input("Choose action (1 for Encrypt, 2 for Decrypt): ").strip()
    if mode not in ("1", "2"):
        print("Invalid action selected.")
        return

    shift_input = input("Enter shift key (integer): ").strip()
    try:
        shift = int(shift_input)
    except ValueError:
        print("Invalid shift value. Must be an integer.")
        return

    effective_shift = shift if mode == "1" else -shift

    output_path = input("Enter path for output file: ").strip()
    if not output_path:
        print("Output path cannot be empty.")
        return

    try:
        with open(input_path, "r", encoding="utf-8") as infile:
            content = infile.read()

        transformed = transform_text(content, effective_shift)

        with open(output_path, "w", encoding="utf-8") as outfile:
            outfile.write(transformed)

        action_name = "Encrypted" if mode == "1" else "Decrypted"
        print(f"\n[Success] {action_name} '{input_path}' -> '{output_path}' with shift {abs(shift)}.")
    except (OSError, UnicodeDecodeError) as error:
        print(f"\n[Error] File operation failed: {error}")


def main():
    while True:
        print("=" * 45)
        print("      CAESAR CIPHER TOOLKIT")
        print("=" * 45)
        print("1. Encrypt Text")
        print("2. Decrypt Text (Known Shift)")
        print("3. Brute-Force Crack (All Shifts)")
        print("4. Encrypt/Decrypt File")
        print("5. Exit")
        print("=" * 45)

        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            encrypt_mode()
        elif choice == "2":
            decrypt_mode()
        elif choice == "3":
            brute_force_mode()
        elif choice == "4":
            file_cipher_mode()
        elif choice == "5":
            print("\nExiting Caesar Cipher Toolkit. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please choose 1 to 5.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
