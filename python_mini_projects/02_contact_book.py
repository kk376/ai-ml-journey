"""Contact Book - simple CLI contact manager."""


def find_contact_key(contacts, name):
    # Case-insensitive linear scan over dictionary keys to preserve canonical casing while allowing loose lookup
    lower_name = name.lower()
    for key in contacts:
        if key.lower() == lower_name:
            return key
    return None


def add_contact(contacts):
    print("\n--- Add New Contact ---")
    name = input("Enter contact name: ").strip()

    if name == "":
        print("Contact name cannot be empty.")
        return

    # Check for existing key collisions regardless of casing
    existing_key = find_contact_key(contacts, name)
    if existing_key is not None:
        print(f"A contact named '{existing_key}' already exists.")
        overwrite = input("Do you want to overwrite it? (y/n): ").strip().lower()
        if overwrite != "y":
            print("Contact addition cancelled.")
            return
        # Delete existing key to allow new casing to take precedence
        del contacts[existing_key]

    phone = input("Enter phone number: ").strip()
    email = input("Enter email address: ").strip()

    contacts[name] = {"phone": phone, "email": email}
    print(f"\nContact '{name}' saved.")
    print(f"  Phone: {phone}")
    print(f"  Email: {email}")



def view_contacts(contacts):
    print("\n--- All Contacts ---")
    if len(contacts) == 0:
        print("Your contact book is empty.")
        return

    print("-" * 55)
    print(f"{'Name':<20} | {'Phone':<15} | {'Email':<15}")
    print("-" * 55)

    for name in contacts:
        info = contacts[name]
        phone = info["phone"]
        email = info["email"]
        print(f"{name:<20} | {phone:<15} | {email:<15}")

    print("-" * 55)
    print(f"Total Contacts: {len(contacts)}")


def search_contact(contacts):
    print("\n--- Search Contact ---")
    name = input("Enter name to search: ").strip()

    key = find_contact_key(contacts, name)
    if key is not None:
        info = contacts[key]
        print("\nContact Found:")
        print(f"  Name : {key}")
        print(f"  Phone: {info['phone']}")
        print(f"  Email: {info['email']}")
    else:
        print(f"No contact found with the name '{name}'.")


def update_contact(contacts):
    print("\n--- Update Contact ---")
    name = input("Enter contact name to update: ").strip()

    key = find_contact_key(contacts, name)
    if key is None:
        print(f"Contact '{name}' does not exist.")
        return

    info = contacts[key]
    print(f"Current Phone: {info['phone']}")
    print(f"Current Email: {info['email']}")
    print("\nWhat would you like to update?")
    print("1. Phone Number")
    print("2. Email Address")
    print("3. Both")

    update_choice = input("Enter choice (1-3): ").strip()

    if update_choice == "1":
        new_phone = input("Enter new phone number: ").strip()
        info["phone"] = new_phone
        print(f"Phone updated for '{key}'.")
    elif update_choice == "2":
        new_email = input("Enter new email address: ").strip()
        info["email"] = new_email
        print(f"Email updated for '{key}'.")
    elif update_choice == "3":
        new_phone = input("Enter new phone number: ").strip()
        new_email = input("Enter new email address: ").strip()
        info["phone"] = new_phone
        info["email"] = new_email
        print(f"Contact details updated for '{key}'.")
    else:
        print("Invalid option selected. Update cancelled.")


def delete_contact(contacts):
    print("\n--- Delete Contact ---")
    name = input("Enter contact name to delete: ").strip()

    key = find_contact_key(contacts, name)
    if key is not None:
        del contacts[key]
        print(f"Contact '{key}' deleted successfully.")
    else:
        print(f"No contact found with the name '{name}'.")


def display_menu():
    print("\n==============================")
    print("       CONTACT BOOK MENU")
    print("==============================")
    print("1. Add Contact")
    print("2. View All Contacts")
    print("3. Search Contact")
    print("4. Update Contact")
    print("5. Delete Contact")
    print("6. Exit")
    print("==============================")


def main():
    contacts = {}

    print("Welcome to the Contact Book!")
    print("Type a number from the menu to get started.\n")

    while True:
        display_menu()
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            add_contact(contacts)
        elif choice == "2":
            view_contacts(contacts)
        elif choice == "3":
            search_contact(contacts)
        elif choice == "4":
            update_contact(contacts)
        elif choice == "5":
            delete_contact(contacts)
        elif choice == "6":
            print("\nExiting Contact Book. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
