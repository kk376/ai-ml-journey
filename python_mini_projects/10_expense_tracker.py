"""Expense Tracker - log expenses, view summaries, set budgets."""


def add_expense(expenses):
    description = input("Enter expense description: ").strip()
    if len(description) == 0:
        print("Description cannot be empty.")
        return

    amount_input = input("Enter amount spent: ").strip()

    # Character-level floating-point string validation: enforces single decimal point invariant and digit characters
    is_valid = True
    dot_count = 0
    for char in amount_input:
        if char == '.':
            dot_count += 1
        elif not char.isdigit():
            is_valid = False
    if dot_count > 1 or len(amount_input) == 0 or amount_input == ".":
        is_valid = False

    if not is_valid:
        print("Invalid amount. Please enter a positive number.")
        return

    amount = float(amount_input)
    if amount <= 0:
        print("Amount must be greater than zero.")
        return

    # Fixed category schema represented as an immutable tuple
    categories = ("Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other")
    print("\nAvailable categories:")
    for i in range(len(categories)):
        print(f"  {i + 1}. {categories[i]}")

    choice = input("Select category number: ").strip()

    if not choice.isdigit():
        print("Invalid choice. Expense not added.")
        return

    choice_num = int(choice)
    if choice_num < 1 or choice_num > len(categories):
        print("Invalid choice. Expense not added.")
        return

    category = categories[choice_num - 1]

    # Append structured expense dictionary record to state list
    expense = {
        "description": description,
        "amount": amount,
        "category": category
    }
    expenses.append(expense)
    print(f"\nAdded: {description} - Rs.{amount:.2f} [{category}]")


def view_all_expenses(expenses):
    if len(expenses) == 0:
        print("\nNo expenses recorded yet.")
        return

    print("\n" + "=" * 55)
    print("              ALL EXPENSES")
    print("=" * 55)
    print(f"  {'No.':<5} {'Description':<20} {'Category':<14} {'Amount':>10}")
    print("-" * 55)

    total = 0.0
    for i in range(len(expenses)):
        exp = expenses[i]
        print(f"  {i + 1:<5} {exp['description']:<20} {exp['category']:<14} Rs.{exp['amount']:>7.2f}")
        total += exp["amount"]

    print("-" * 55)
    print(f"  {'TOTAL':<39} Rs.{total:>7.2f}")
    print("=" * 55)


def view_by_category(expenses):
    if len(expenses) == 0:
        print("\nNo expenses recorded yet.")
        return

    # Extract distinct categories present across records using a set
    used_categories = set()
    for exp in expenses:
        used_categories.add(exp["category"])

    # Aggregate total expenditure per category into an accumulator map
    category_totals = {}
    for exp in expenses:
        cat = exp["category"]
        if cat in category_totals:
            category_totals[cat] += exp["amount"]
        else:
            category_totals[cat] = exp["amount"]

    print("\n" + "=" * 40)
    print("        SPENDING BY CATEGORY")
    print("=" * 40)

    grand_total = 0.0
    for cat in sorted(used_categories):
        cat_total = category_totals[cat]
        grand_total += cat_total
        print(f"  {cat:<18} Rs.{cat_total:>9.2f}")

    print("-" * 40)
    print(f"  {'TOTAL':<18} Rs.{grand_total:>9.2f}")
    print("=" * 40)


def view_top_expenses(expenses):
    if len(expenses) == 0:
        print("\nNo expenses recorded yet.")
        return

    # Shallow copy to preserve original chronological insertion order in caller list
    sorted_expenses = []
    for exp in expenses:
        sorted_expenses.append(exp)

    # In-place Selection Sort O(N^2) descending by expense amount
    for i in range(len(sorted_expenses)):
        max_index = i
        for j in range(i + 1, len(sorted_expenses)):
            if sorted_expenses[j]["amount"] > sorted_expenses[max_index]["amount"]:
                max_index = j

        temp = sorted_expenses[i]
        sorted_expenses[i] = sorted_expenses[max_index]
        sorted_expenses[max_index] = temp

    # Clamp output display slice to top 5 records or total length
    count = 5
    if len(sorted_expenses) < 5:
        count = len(sorted_expenses)

    print("\n" + "=" * 50)
    print(f"           TOP {count} EXPENSES")
    print("=" * 50)
    print(f"  {'Rank':<6} {'Description':<20} {'Category':<12} {'Amount':>8}")
    print("-" * 50)

    for i in range(count):
        exp = sorted_expenses[i]
        print(f"  {i + 1:<6} {exp['description']:<20} {exp['category']:<12} Rs.{exp['amount']:>7.2f}")

    print("=" * 50)


def set_budget(budget_info):
    print(f"\nCurrent monthly budget: ", end="")
    if budget_info["limit"] > 0:
        print(f"Rs.{budget_info['limit']:.2f}")
    else:
        print("Not set")

    amount_input = input("Enter new monthly budget (or 0 to remove): ").strip()

    is_valid = True
    dot_count = 0
    for char in amount_input:
        if char == '.':
            dot_count += 1
        elif not char.isdigit():
            is_valid = False
    if dot_count > 1 or len(amount_input) == 0 or amount_input == ".":
        is_valid = False

    if not is_valid:
        print("Invalid amount.")
        return

    new_limit = float(amount_input)
    if new_limit < 0:
        print("Budget cannot be negative.")
        return

    # Mutate budget state dictionary in-place
    budget_info["limit"] = new_limit
    if new_limit == 0:
        print("Budget removed.")
    else:
        print(f"Monthly budget set to Rs.{new_limit:.2f}")


def check_budget(expenses, budget_info):
    if budget_info["limit"] <= 0:
        print("\nNo budget has been set. Use option 5 to set one.")
        return

    total_spent = 0.0
    for exp in expenses:
        total_spent += exp["amount"]

    budget = budget_info["limit"]
    remaining = budget - total_spent

    print("\n" + "=" * 40)
    print("          BUDGET STATUS")
    print("=" * 40)
    print(f"  Monthly Budget : Rs.{budget:>9.2f}")
    print(f"  Total Spent    : Rs.{total_spent:>9.2f}")
    print("-" * 40)

    # Budget threshold alerting: 75% warning, 90% critical threshold, or deficit overrun
    if remaining >= 0:
        print(f"  Remaining      : Rs.{remaining:>9.2f}")
    
        percent_used = (total_spent / budget) * 100
        print(f"  Budget Used    : {percent_used:.1f}%")

        if percent_used >= 90:
            print("\n  WARNING: You've used 90%+ of your budget!")
        elif percent_used >= 75:
            print("\n  HEADS UP: You've crossed 75% of your budget.")
        else:
            print("\n  You're on track. Keep it up!")
    else:
        over_by = total_spent - budget
        print(f"  OVER BUDGET BY : Rs.{over_by:>9.2f}")
        print("\n  You have exceeded your monthly budget!")

    print("=" * 40)


def delete_expense(expenses):
    if len(expenses) == 0:
        print("\nNo expenses to delete.")
        return

    # Display 1-indexed listing for user selection
    print("\n" + "-" * 45)
    for i in range(len(expenses)):
        exp = expenses[i]
        print(f"  {i + 1}. {exp['description']} - Rs.{exp['amount']:.2f} [{exp['category']}]")
    print("-" * 45)

    choice = input("Enter the number of the expense to delete (0 to cancel): ").strip()

    if not choice.isdigit():
        print("Invalid input.")
        return

    choice_num = int(choice)
    if choice_num == 0:
        print("Cancelled.")
        return
    if choice_num < 1 or choice_num > len(expenses):
        print("Invalid choice.")
        return

    # Remove element by index (O(N) shift in dynamic list)
    removed = expenses[choice_num - 1]
    expenses.pop(choice_num - 1)
    print(f"Deleted: {removed['description']} - Rs.{removed['amount']:.2f}")


def main():
    expenses = []
    budget_info = {"limit": 0.0}

    print("=" * 45)
    print("        WELCOME TO EXPENSE TRACKER")
    print("=" * 45)

    running = True
    while running:
        print("\n--- MENU ---")
        print("  1. Add Expense")
        print("  2. View All Expenses")
        print("  3. View by Category")
        print("  4. Top Expenses")
        print("  5. Set Monthly Budget")
        print("  6. Check Budget Status")
        print("  7. Delete an Expense")
        print("  8. Exit")

        choice = input("\nSelect an option (1-8): ").strip()

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            view_all_expenses(expenses)
        elif choice == "3":
            view_by_category(expenses)
        elif choice == "4":
            view_top_expenses(expenses)
        elif choice == "5":
            set_budget(budget_info)
        elif choice == "6":
            check_budget(expenses, budget_info)
        elif choice == "7":
            delete_expense(expenses)
        elif choice == "8":
            running = False
        else:
            print("Invalid option. Please choose 1-8.")

    # Compute aggregate session summary across recorded items
    if len(expenses) > 0:
        total = 0.0
        for exp in expenses:
            total += exp["amount"]
        print(f"\nSession Summary: {len(expenses)} expenses totalling Rs.{total:.2f}")

    print("\nThank you for using Expense Tracker. Goodbye!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")

