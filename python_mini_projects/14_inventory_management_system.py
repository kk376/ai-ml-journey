"""Inventory Management System: Track warehouse stock, sales, valuations, and CSV exports."""

import csv
import json
import os
from datetime import datetime

INVENTORY_FILE = "inventory.json"
CATEGORIES = ("Electronics", "Apparel", "Home & Kitchen", "Books", "Sports", "Other")


def load_inventory(filepath=INVENTORY_FILE):
    """Load inventory dictionary from JSON storage."""
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, dict):
                return data
            return {}
    except (json.JSONDecodeError, OSError) as error:
        print(f"[Warning] Failed to load '{filepath}': {error}. Starting fresh.")
        return {}


def save_inventory(inventory, filepath=INVENTORY_FILE):
    """Persist inventory dictionary to JSON storage."""
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(inventory, file, indent=4)
        return True
    except OSError as error:
        print(f"[Error] Failed to save inventory: {error}")
        return False


def add_product(inventory):
    """Add a new product with unique SKU/ID."""
    print("\n=== Add New Product ===")
    sku = input("Enter unique Product SKU / ID: ").strip().upper()
    if not sku:
        print("SKU cannot be empty.")
        return
    if sku in inventory:
        print(f"Error: Product SKU '{sku}' already exists in inventory.")
        return

    name = input("Enter product name: ").strip()
    if not name:
        print("Product name cannot be empty.")
        return

    print("\nSelect Category:")
    for idx, cat in enumerate(CATEGORIES, start=1):
        print(f"  {idx}. {cat}")
    cat_choice = input("Enter category number (1-6): ").strip()
    if not cat_choice.isdigit() or not (1 <= int(cat_choice) <= len(CATEGORIES)):
        print("Invalid category choice.")
        return
    category = CATEGORIES[int(cat_choice) - 1]

    qty_input = input("Enter initial stock quantity: ").strip()
    price_input = input("Enter unit price (Rs.): ").strip()

    try:
        quantity = int(qty_input)
        price = float(price_input)
        if quantity < 0 or price < 0:
            print("Quantity and price must be non-negative.")
            return
    except ValueError:
        print("Invalid numeric values for quantity or price.")
        return

    product = {
        "sku": sku,
        "name": name,
        "category": category,
        "quantity": quantity,
        "price": round(price, 2),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    inventory[sku] = product
    save_inventory(inventory)
    print(f"\n[Success] Added '{name}' (SKU: {sku}) with {quantity} units @ Rs.{price:.2f}")


def view_all_products(inventory):
    """Display all products in a tabulated overview."""
    if not inventory:
        print("\nInventory is currently empty.")
        return

    print("\n" + "=" * 85)
    print(f"{'SKU':<10} {'Product Name':<28} {'Category':<16} {'Stock':<8} {'Price (Rs.)':<12} {'Valuation'}")
    print("=" * 85)

    total_units = 0
    total_value = 0.0

    for sku, item in sorted(inventory.items()):
        name = item.get("name", "")
        if len(name) > 26:
            name = name[:23] + "..."
        cat = item.get("category", "")
        qty = item.get("quantity", 0)
        price = item.get("price", 0.0)
        val = qty * price
        total_units += qty
        total_value += val
        print(f"{sku:<10} {name:<28} {cat:<16} {qty:<8} {price:<12.2f} Rs.{val:.2f}")

    print("=" * 85)
    print(f"Total Unique SKUs: {len(inventory)} | Total Units: {total_units} | Inventory Value: Rs.{total_value:.2f}\n")


def update_stock(inventory):
    """Adjust or restock product quantity."""
    print("\n=== Update Stock Quantity ===")
    sku = input("Enter product SKU: ").strip().upper()
    if sku not in inventory:
        print(f"SKU '{sku}' not found.")
        return

    item = inventory[sku]
    print(f"Current stock for {item['name']} ({sku}): {item['quantity']} units")
    print("  1. Restock (Add units)")
    print("  2. Manual Override (Set exact quantity)")
    choice = input("Select option (1-2): ").strip()

    if choice == "1":
        amt_str = input("Enter units to add: ").strip()
        try:
            amt = int(amt_str)
            if amt <= 0:
                print("Units to add must be positive.")
                return
            item["quantity"] += amt
        except ValueError:
            print("Invalid number.")
            return
    elif choice == "2":
        amt_str = input("Enter new total stock count: ").strip()
        try:
            amt = int(amt_str)
            if amt < 0:
                print("Stock count cannot be negative.")
                return
            item["quantity"] = amt
        except ValueError:
            print("Invalid number.")
            return
    else:
        print("Invalid selection.")
        return

    item["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_inventory(inventory)
    print(f"\n[Success] Updated stock for {item['name']}: {item['quantity']} units.")


def record_sale(inventory):
    """Sell items, deduct stock, and print sale receipt."""
    print("\n=== Record Sale Transaction ===")
    sku = input("Enter product SKU to sell: ").strip().upper()
    if sku not in inventory:
        print(f"SKU '{sku}' not found.")
        return

    item = inventory[sku]
    current_qty = item.get("quantity", 0)
    print(f"Product: {item['name']} | Available stock: {current_qty} | Price: Rs.{item['price']:.2f}")

    qty_str = input("Enter units sold: ").strip()
    try:
        qty_sold = int(qty_str)
        if qty_sold <= 0:
            print("Sold quantity must be greater than zero.")
            return
        if qty_sold > current_qty:
            print(f"Error: Insufficient stock. Only {current_qty} units available.")
            return
    except ValueError:
        print("Invalid quantity.")
        return

    subtotal = qty_sold * item["price"]
    item["quantity"] -= qty_sold
    item["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_inventory(inventory)

    print("\n" + "=" * 45)
    print("           SALE RECEIPT")
    print("=" * 45)
    print(f"Item       : {item['name']} ({sku})")
    print(f"Quantity   : {qty_sold}")
    print(f"Unit Price : Rs.{item['price']:.2f}")
    print(f"Total Sale : Rs.{subtotal:.2f}")
    print(f"Stock Left : {item['quantity']}")
    print("=" * 45 + "\n")


def low_stock_report(inventory):
    """List products that fall below safety stock threshold."""
    print("\n=== Low Stock Threshold Alert ===")
    thresh_input = input("Enter threshold value (default 5): ").strip()
    threshold = 5
    if thresh_input:
        try:
            threshold = int(thresh_input)
        except ValueError:
            print("Invalid threshold. Defaulting to 5.")

    low_items = [item for item in inventory.values() if item.get("quantity", 0) <= threshold]

    if not low_items:
        print(f"\nGreat! No products are at or below {threshold} units.")
        return

    print("\n" + "=" * 70)
    print(f"LOW STOCK WARNING (Quantity <= {threshold})")
    print("=" * 70)
    print(f"{'SKU':<10} {'Product Name':<30} {'Category':<16} {'Stock Left'}")
    print("-" * 70)
    for item in sorted(low_items, key=lambda x: x.get("quantity", 0)):
        print(f"{item['sku']:<10} {item['name']:<30} {item['category']:<16} {item['quantity']}")
    print("=" * 70 + "\n")


def export_to_csv(inventory):
    """Export the current inventory table to a CSV file."""
    print("\n=== Export Inventory to CSV ===")
    filename = input("Enter output CSV filename (default 'inventory_export.csv'): ").strip()
    if not filename:
        filename = "inventory_export.csv"

    fieldnames = ["sku", "name", "category", "quantity", "price", "valuation", "last_updated"]

    try:
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in inventory.values():
                row = dict(item)
                row["valuation"] = round(row.get("quantity", 0) * row.get("price", 0.0), 2)
                writer.writerow(row)
        print(f"\n[Success] Exported {len(inventory)} products to '{filename}'.")
    except OSError as error:
        print(f"\n[Error] CSV Export failed: {error}")


def main():
    inventory = load_inventory()

    while True:
        print("=" * 45)
        print("     INVENTORY MANAGEMENT SYSTEM")
        print("=" * 45)
        print("1. View All Products & Valuation")
        print("2. Add New Product")
        print("3. Update Stock Quantity")
        print("4. Record Sale Transaction")
        print("5. Low Stock Alert Report")
        print("6. Export Inventory to CSV")
        print("7. Exit")
        print("=" * 45)

        choice = input("Select option (1-7): ").strip()

        if choice == "1":
            view_all_products(inventory)
        elif choice == "2":
            add_product(inventory)
        elif choice == "3":
            update_stock(inventory)
        elif choice == "4":
            record_sale(inventory)
        elif choice == "5":
            low_stock_report(inventory)
        elif choice == "6":
            export_to_csv(inventory)
        elif choice == "7":
            print("\nSaving inventory state. Goodbye!")
            save_inventory(inventory)
            break
        else:
            print("\nInvalid choice. Please select 1 to 7.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
