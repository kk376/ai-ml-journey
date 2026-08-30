"""Password Strength Checker"""


def check_criteria(password):
    # Enforce minimum character length baseline
    has_length = len(password) >= 8

    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False

    special_characters = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"

    # Single-pass O(N) evaluation across character classes
    for char in password:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char.isdigit():
            has_digit = True
        elif char in special_characters:
            has_special = True

    # Aggregate total criteria met
    score = 0
    if has_length:
        score += 1
    if has_upper:
        score += 1
    if has_lower:
        score += 1
    if has_digit:
        score += 1
    if has_special:
        score += 1

    # Discrete classification tiers: 0-2 Weak, 3-4 Medium, 5 Strong
    if score <= 2:
        rating = "Weak"
    elif score <= 4:
        rating = "Medium"
    else:
        rating = "Strong"

    results = {
        "has_length": has_length,
        "has_upper": has_upper,
        "has_lower": has_lower,
        "has_digit": has_digit,
        "has_special": has_special,
        "score": score,
        "rating": rating,
    }

    return results



def print_report(password, results):
    print("\n" + "=" * 45)
    print("         PASSWORD STRENGTH REPORT")
    print("=" * 45)
    print(f"Password checked: {password}")
    print(f"Total Score     : {results['score']} / 5")
    print(f"Overall Rating  : {results['rating'].upper()}")
    print("-" * 45)
    print("Criteria Checklist:")

    checks = [
        ("At least 8 characters long", results["has_length"]),
        ("Contains uppercase letter (A-Z)", results["has_upper"]),
        ("Contains lowercase letter (a-z)", results["has_lower"]),
        ("Contains numeric digit (0-9)", results["has_digit"]),
        ("Contains special character (!@#$..)", results["has_special"]),
    ]

    for description, passed in checks:
        status = "[ PASS ]" if passed else "[ FAIL ]"
        print(f"  {status} {description}")

    print("-" * 45)

    # suggestions for anything that didn't pass
    if results["score"] < 5:
        print("Suggestions to improve your password:")
        if not results["has_length"]:
            print("  - Make the password at least 8 characters long.")
        if not results["has_upper"]:
            print("  - Add at least one uppercase letter.")
        if not results["has_lower"]:
            print("  - Add at least one lowercase letter.")
        if not results["has_digit"]:
            print("  - Add at least one number.")
        if not results["has_special"]:
            print("  - Add at least one special character (e.g. !@#$).")
    else:
        print("Great job! Your password meets all security criteria.")

    print("=" * 45 + "\n")


def main():
    print("=" * 45)
    print("      WELCOME TO PASSWORD STRENGTH CHECKER")
    print("=" * 45)
    print("Type 'quit' at any time to exit the program.\n")

    while True:
        user_input = input("Enter password to check: ").strip()

        if user_input.lower() == "quit":
            print("\nThank you for using Password Strength Checker. Goodbye!")
            break

        if len(user_input) == 0:
            print("Password cannot be empty. Please try again.\n")
            continue

        results = check_criteria(user_input)
        print_report(user_input, results)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
