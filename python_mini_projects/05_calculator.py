"""CLI calculator with basic arithmetic, power, and modulus."""

def add(num1, num2):
    return num1 + num2


def subtract(num1, num2):
    return num1 - num2


def multiply(num1, num2):
    return num1 * num2


def divide(num1, num2):
    # can't divide by zero
    if num2 == 0:
        return None
    return num1 / num2


def power(base, exponent):
    return base ** exponent


def modulus(num1, num2):
    # same zero check as divide
    if num2 == 0:
        return None
    return num1 % num2


def show_menu():
    print("\n" + "=" * 40)
    print("         SIMPLE CALCULATOR")
    print("=" * 40)
    print("1. Addition (+)")
    print("2. Subtraction (-)")
    print("3. Multiplication (*)")
    print("4. Division (/)")
    print("5. Power (**)")
    print("6. Modulus (%)")
    print("7. Exit")
    print("=" * 40)


def get_number(prompt):

    value = float(input(prompt))
    return value


def perform_calculation(choice):
    print(f"\nYou selected operation {choice}.")
    num1 = get_number("Enter first number: ")
    num2 = get_number("Enter second number: ")

    if choice == "1":
        result = add(num1, num2)
        print(f"Result: {num1} + {num2} = {result}")

    elif choice == "2":
        result = subtract(num1, num2)
        print(f"Result: {num1} - {num2} = {result}")

    elif choice == "3":
        result = multiply(num1, num2)
        print(f"Result: {num1} * {num2} = {result}")

    elif choice == "4":
        result = divide(num1, num2)
        if result is None:
            print("Error: Cannot divide by zero!")
        else:
            print(f"Result: {num1} / {num2} = {result}")

    elif choice == "5":
        result = power(num1, num2)
        print(f"Result: {num1} ^ {num2} = {result}")

    elif choice == "6":
        result = modulus(num1, num2)
        if result is None:
            print("Error: Cannot perform modulus with divisor zero!")
        else:
            print(f"Result: {num1} % {num2} = {result}")


def run_calculator():
    running = True

    while running:
        show_menu()
        choice = input("Choose an option (1-7): ").strip()

        if choice == "7":
            print("Exiting calculator. Have a great day!")
            running = False
        elif choice in ["1", "2", "3", "4", "5", "6"]:
            perform_calculation(choice)
            

            again = input("\nDo you want to perform another calculation? (y/n): ").lower().strip()
            if again != "y" and again != "yes":
                print("Thank you for using Calculator! Goodbye.")
                running = False
        else:
            print("Invalid selection. Please choose a number from 1 to 7.")


if __name__ == "__main__":
    try:
        run_calculator()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
