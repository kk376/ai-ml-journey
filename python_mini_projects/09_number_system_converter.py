# Lookup table for hexadecimal character to numeric value (0-15) conversion
HEX_LOOKUP = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
    '8': 8, '9': 9, 'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15
}
# Direct index mapping for numeric remainder (0-15) to hex glyph
HEX_DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']


# Input validators checking character set constraints and non-empty strings
def is_valid_decimal(s):
    if len(s) == 0:
        return False
    for char in s:
        if char < '0' or char > '9':
            return False
    return True


def is_valid_binary(s):
    if len(s) == 0:
        return False
    for char in s:
        if char != '0' and char != '1':
            return False
    return True


def is_valid_octal(s):
    if len(s) == 0:
        return False
    for char in s:
        if char < '0' or char > '7':
            return False
    return True


def is_valid_hex(s):
    if len(s) == 0:
        return False
    valid = "0123456789ABCDEFabcdef"
    for char in s:
        if char not in valid:
            return False
    return True


# Decimal to base-N conversion via successive integer division and remainder concatenation
def decimal_to_binary(num):
    if num == 0:
        return "0"
    binary_str = ""
    temp = num
    while temp > 0:
        remainder = temp % 2
        binary_str = str(remainder) + binary_str
        temp = temp // 2
    return binary_str


def decimal_to_octal(num):
    if num == 0:
        return "0"
    octal_str = ""
    temp = num
    while temp > 0:
        remainder = temp % 8
        octal_str = str(remainder) + octal_str
        temp = temp // 8
    return octal_str


def decimal_to_hexadecimal(num):
    if num == 0:
        return "0"
    hex_str = ""
    temp = num
    while temp > 0:
        remainder = temp % 16
        hex_str = HEX_DIGITS[remainder] + hex_str
        temp = temp // 16
    return hex_str


# Base-N to decimal conversion via positional polynomial summation: sum(digit * base^i) from LSB to MSB
def binary_to_decimal(binary_str):
    decimal_val = 0
    power = 0
    i = len(binary_str) - 1
    while i >= 0:
        digit = int(binary_str[i])
        decimal_val += digit * (2 ** power)
        power += 1
        i -= 1
    return decimal_val


def octal_to_decimal(octal_str):
    decimal_val = 0
    power = 0
    i = len(octal_str) - 1
    while i >= 0:
        digit = int(octal_str[i])
        decimal_val += digit * (8 ** power)
        power += 1
        i -= 1
    return decimal_val


def hexadecimal_to_decimal(hex_str):
    decimal_val = 0
    power = 0
    hex_clean = hex_str.upper()
    i = len(hex_clean) - 1
    while i >= 0:
        char = hex_clean[i]
        value = HEX_LOOKUP[char]
        decimal_val += value * (16 ** power)
        power += 1
        i -= 1
    return decimal_val



def print_menu():
    print("\n=========================================")
    print("    NUMBER SYSTEM CONVERTER MENU         ")
    print("=========================================")
    print("1. Decimal to Binary")
    print("2. Decimal to Octal")
    print("3. Decimal to Hexadecimal")
    print("4. Binary to Decimal")
    print("5. Octal to Decimal")
    print("6. Hexadecimal to Decimal")
    print("7. Exit")


def main():
    running = True
    while running:
        print_menu()
        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            raw_input = input("Enter a non-negative decimal integer: ").strip()
            if is_valid_decimal(raw_input):
                num = int(raw_input)
                res = decimal_to_binary(num)
                print(f"Binary equivalent: {res}")
            else:
                print("Invalid input! Please enter digits only.")

        elif choice == "2":
            raw_input = input("Enter a non-negative decimal integer: ").strip()
            if is_valid_decimal(raw_input):
                num = int(raw_input)
                res = decimal_to_octal(num)
                print(f"Octal equivalent: {res}")
            else:
                print("Invalid input! Please enter digits only.")

        elif choice == "3":
            raw_input = input("Enter a non-negative decimal integer: ").strip()
            if is_valid_decimal(raw_input):
                num = int(raw_input)
                res = decimal_to_hexadecimal(num)
                print(f"Hexadecimal equivalent: {res}")
            else:
                print("Invalid input! Please enter digits only.")

        elif choice == "4":
            raw_input = input("Enter a binary string: ").strip()
            if is_valid_binary(raw_input):
                res = binary_to_decimal(raw_input)
                print(f"Decimal equivalent: {res}")
            else:
                print("Invalid binary input! Only 0s and 1s allowed.")

        elif choice == "5":
            raw_input = input("Enter an octal string: ").strip()
            if is_valid_octal(raw_input):
                res = octal_to_decimal(raw_input)
                print(f"Decimal equivalent: {res}")
            else:
                print("Invalid octal input! Digits must be between 0 and 7.")

        elif choice == "6":
            raw_input = input("Enter a hexadecimal string: ").strip()
            if is_valid_hex(raw_input):
                res = hexadecimal_to_decimal(raw_input)
                print(f"Decimal equivalent: {res}")
            else:
                print("Invalid hexadecimal input! Valid characters are 0-9 and A-F.")

        elif choice == "7":
            print("Exiting Number System Converter. Goodbye!")
            running = False
        else:
            print("Invalid choice! Please select an option between 1 and 7.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
