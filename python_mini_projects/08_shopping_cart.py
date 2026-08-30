"""Shopping Cart - browse products, manage a cart, checkout with discounts."""


def get_product_catalog():
    catalog = [
        {"name": "Laptop", "price": 850.0, "category": "Electronics"},
        {"name": "Smartphone", "price": 450.0, "category": "Electronics"},
        {"name": "Headphones", "price": 60.0, "category": "Electronics"},
        {"name": "Smart Watch", "price": 120.0, "category": "Electronics"},
        {"name": "T-Shirt", "price": 25.0, "category": "Clothing"},
        {"name": "Jeans", "price": 45.0, "category": "Clothing"},
        {"name": "Jacket", "price": 95.0, "category": "Clothing"},
        {"name": "Apples (1kg)", "price": 4.5, "category": "Groceries"},
        {"name": "Milk (1L)", "price": 2.5, "category": "Groceries"},
        {"name": "Coffee Beans", "price": 14.0, "category": "Groceries"},
        {"name": "Rice Bag (5kg)", "price": 22.0, "category": "Groceries"},
    ]
    return catalog


def display_products(catalog):
    print("\n--- Product Categories ---")
    print("1. All Products")
    print("2. Electronics")
    print("3. Clothing")
    print("4. Groceries")
    cat_choice = input("Select category to view (1-4): ").strip()

    selected_category = ""
    if cat_choice == "2":
        selected_category = "Electronics"
    elif cat_choice == "3":
        selected_category = "Clothing"
    elif cat_choice == "4":
        selected_category = "Groceries"

    print("\n" + "=" * 55)
    print(f"{'ID':<4} | {'PRODUCT NAME':<20} | {'CATEGORY':<12} | {'PRICE ($)':<8}")
    print("=" * 55)

    index = 1
    for item in catalog:
        if selected_category == "" or item["category"] == selected_category:
            print(
                f"{index:<4} | {item['name']:<20} | {item['category']:<12} | ${item['price']:<7.2f}"
            )
        index += 1
    print("=" * 55)


def add_to_cart(catalog, cart):
    print("\n--- Add Product to Cart ---")
    prod_input = input(f"Enter Product ID (1-{len(catalog)}): ").strip()

    if not prod_input.isdigit():
        print("Invalid product ID. Please enter a number.")
        return

    prod_id = int(prod_input)
    if prod_id < 1 or prod_id > len(catalog):
        print("Product ID out of range.")
        return

    qty_input = input("Enter quantity: ").strip()
    if not qty_input.isdigit() or int(qty_input) <= 0:
        print("Invalid quantity. Must be a positive integer.")
        return

    quantity = int(qty_input)
    selected_product = catalog[prod_id - 1]

    # Linear search for existing cart item to increment quantity in-place rather than creating duplicate entries
    found = False
    for cart_item in cart:
        if cart_item["name"] == selected_product["name"]:
            cart_item["quantity"] += quantity
            found = True
            break

    if not found:
        cart.append(
            {
                "name": selected_product["name"],
                "price": selected_product["price"],
                "quantity": quantity,
            }
        )

    print(f"Added {quantity} x '{selected_product['name']}' to your cart.")


def view_cart(cart):
    print("\n" + "=" * 55)
    print("                   YOUR SHOPPING CART")
    print("=" * 55)

    if not cart:
        print("Your cart is empty.")
        print("=" * 55)
        return 0.0

    print(f"{'ID':<4} | {'ITEM':<20} | {'PRICE':<8} | {'QTY':<5} | {'SUBTOTAL':<9}")
    print("-" * 55)

    total = 0.0
    index = 1
    for cart_item in cart:
        subtotal = cart_item["price"] * cart_item["quantity"]
        total += subtotal
        print(
            f"{index:<4} | {cart_item['name']:<20} | ${cart_item['price']:<7.2f} | {cart_item['quantity']:<5} | ${subtotal:<8.2f}"
        )
        index += 1

    print("-" * 55)
    print(f"Total Cart Subtotal: ${total:.2f}")
    print("=" * 55)
    return total


def remove_from_cart(cart):
    if not cart:
        print("\nYour cart is empty. Nothing to remove.")
        return

    view_cart(cart)
    item_input = input(f"Enter Item ID to remove (1-{len(cart)}): ").strip()

    if not item_input.isdigit():
        print("Invalid item number.")
        return

    item_id = int(item_input)
    if item_id < 1 or item_id > len(cart):
        print("Item number out of range.")
        return

    target_item = cart[item_id - 1]
    qty_input = input(
        f"Enter quantity to remove (Current: {target_item['quantity']}): "
    ).strip()

    if not qty_input.isdigit() or int(qty_input) <= 0:
        print("Invalid quantity.")
        return

    remove_qty = int(qty_input)
    # Remove record entirely if target quantity is depleted, else decrement in-place
    if remove_qty >= target_item["quantity"]:
        cart.pop(item_id - 1)
        print(f"Removed '{target_item['name']}' from cart.")
    else:
        target_item["quantity"] -= remove_qty
        print(f"Reduced '{target_item['name']}' quantity by {remove_qty}.")


def checkout(cart):
    if not cart:
        print("\nYour cart is empty. Add items before checking out.")
        return

    subtotal = view_cart(cart)
    discount = 0.0

    # 10% volume discount applied when cart subtotal crosses the $500 threshold
    if subtotal > 500.0:
        discount = subtotal * 0.10
        print(f"\nYou received a 10% discount of ${discount:.2f} for spending over $500!")

    final_total = subtotal - discount
    print(f"Discount Applied : -${discount:.2f}")
    print(f"Final Amount Due : ${final_total:.2f}")
    print("\nThank you for shopping with us! Order placed successfully.")
    cart.clear()



def run_shopping_cart():
    catalog = get_product_catalog()
    cart = []

    while True:
        print("\n=== SHOPPING CART MENU ===")
        print("1. Browse Products")
        print("2. Add to Cart")
        print("3. View Cart")
        print("4. Remove from Cart")
        print("5. Checkout")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            display_products(catalog)
        elif choice == "2":
            display_products(catalog)
            add_to_cart(catalog, cart)
        elif choice == "3":
            view_cart(cart)
        elif choice == "4":
            remove_from_cart(cart)
        elif choice == "5":
            checkout(cart)
        elif choice == "6":
            print("\nThank you for visiting. Have a great day!")
            break
        else:
            print("Invalid menu choice. Please select from 1 to 6.")


if __name__ == "__main__":
    try:
        run_shopping_cart()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
