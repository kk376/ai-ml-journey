"""Unit Converter: Comprehensive multi-category measurement conversion tool.

Supports Length, Weight/Mass, Temperature, Digital Storage, and Speed
with precision formatting, validation, and self-test verification.
"""

import sys
from typing import Dict, Tuple


# Conversion factors normalized to base unit: meter (m)
LENGTH_UNITS: Dict[str, float] = {
    "m": 1.0,
    "km": 1000.0,
    "cm": 0.01,
    "mm": 0.001,
    "mi": 1609.344,
    "yd": 0.9144,
    "ft": 0.3048,
    "in": 0.0254,
}

LENGTH_NAMES: Dict[str, str] = {
    "m": "Meter",
    "km": "Kilometer",
    "cm": "Centimeter",
    "mm": "Millimeter",
    "mi": "Mile",
    "yd": "Yard",
    "ft": "Foot",
    "in": "Inch",
}

# Conversion factors normalized to base unit: kilogram (kg)
MASS_UNITS: Dict[str, float] = {
    "kg": 1.0,
    "g": 0.001,
    "mg": 0.000001,
    "t": 1000.0,
    "lb": 0.45359237,
    "oz": 0.028349523125,
}

MASS_NAMES: Dict[str, str] = {
    "kg": "Kilogram",
    "g": "Gram",
    "mg": "Milligram",
    "t": "Metric Tonne",
    "lb": "Pound",
    "oz": "Ounce",
}

# Conversion factors normalized to base unit: byte (B)
STORAGE_UNITS: Dict[str, float] = {
    "b": 1.0,
    "kb": 1000.0,
    "mb": 1000.0**2,
    "gb": 1000.0**3,
    "tb": 1000.0**4,
    "kib": 1024.0,
    "mib": 1024.0**2,
    "gib": 1024.0**3,
    "tib": 1024.0**4,
}

STORAGE_NAMES: Dict[str, str] = {
    "b": "Byte",
    "kb": "Kilobyte (decimal)",
    "mb": "Megabyte (decimal)",
    "gb": "Gigabyte (decimal)",
    "tb": "Terabyte (decimal)",
    "kib": "Kibibyte (binary)",
    "mib": "Mebibyte (binary)",
    "gib": "Gibibyte (binary)",
    "tib": "Tebibyte (binary)",
}

# Conversion factors normalized to base unit: meters per second (m/s)
SPEED_UNITS: Dict[str, float] = {
    "mps": 1.0,
    "kmh": 1.0 / 3.6,
    "mph": 0.44704,
    "knot": 0.514444,
}

SPEED_NAMES: Dict[str, str] = {
    "mps": "Meters per second",
    "kmh": "Kilometers per hour",
    "mph": "Miles per hour",
    "knot": "Knots",
}


def convert_linear(value: float, from_unit: str, to_unit: str, factors: Dict[str, float]) -> float:
    """Convert value between linear scale units using normalized factors."""
    from_key = from_unit.lower()
    to_key = to_unit.lower()
    if from_key not in factors or to_key not in factors:
        raise ValueError(f"Unsupported unit: '{from_unit}' or '{to_unit}'.")
    base_value = value * factors[from_key]
    return base_value / factors[to_key]


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert value between Celsius, Fahrenheit, and Kelvin."""
    src = from_unit.upper()
    dst = to_unit.upper()

    # Step 1: Normalize source to Celsius
    if src == "C":
        celsius = value
    elif src == "F":
        celsius = (value - 32.0) * (5.0 / 9.0)
    elif src == "K":
        celsius = value - 273.15
    else:
        raise ValueError(f"Unsupported temperature unit: '{from_unit}'. Use C, F, or K.")

    # Step 2: Convert Celsius to destination
    if dst == "C":
        return celsius
    elif dst == "F":
        return (celsius * 9.0 / 5.0) + 32.0
    elif dst == "K":
        return celsius + 273.15
    else:
        raise ValueError(f"Unsupported temperature unit: '{to_unit}'. Use C, F, or K.")


def print_unit_table(names: Dict[str, str]) -> None:
    """Display available units formatted neatly in two columns."""
    print("Available units:")
    for code, name in names.items():
        print(f"  [{code:<5}] : {name}")


def run_tests() -> bool:
    """Execute automated unit tests across all conversion domains."""
    tolerance = 1e-4

    # Length test: 1 mile == 1609.344 meters
    assert abs(convert_linear(1.0, "mi", "m", LENGTH_UNITS) - 1609.344) < tolerance

    # Mass test: 1 lb == 453.59237 grams
    assert abs(convert_linear(1.0, "lb", "g", MASS_UNITS) - 453.59237) < tolerance

    # Temperature test: 100 C == 212 F == 373.15 K
    assert abs(convert_temperature(100.0, "C", "F") - 212.0) < tolerance
    assert abs(convert_temperature(32.0, "F", "C") - 0.0) < tolerance
    assert abs(convert_temperature(0.0, "C", "K") - 273.15) < tolerance

    # Storage test: 1 GiB == 1024 MiB == 1,073,741,824 bytes
    assert abs(convert_linear(1.0, "gib", "mib", STORAGE_UNITS) - 1024.0) < tolerance
    assert abs(convert_linear(1.0, "gib", "b", STORAGE_UNITS) - 1073741824.0) < tolerance

    # Speed test: 100 km/h == 27.7778 m/s
    assert abs(convert_linear(100.0, "kmh", "mps", SPEED_UNITS) - 27.777777) < tolerance

    print("All unit conversion test assertions passed successfully.")
    return True


def prompt_float(prompt_text: str) -> float:
    """Prompt user for a valid floating point number."""
    while True:
        raw = input(prompt_text).strip()
        try:
            return float(raw)
        except ValueError:
            print("Invalid input. Please enter a numerical value.")


def handle_linear_flow(category_name: str, units: Dict[str, float], names: Dict[str, str]) -> None:
    """Generic interactive handler for linear scale conversions."""
    print(f"\n--- {category_name} Converter ---")
    print_unit_table(names)

    from_unit = input("Enter source unit code: ").strip().lower()
    if from_unit not in units:
        print(f"Error: Unknown source unit '{from_unit}'.")
        return

    to_unit = input("Enter target unit code: ").strip().lower()
    if to_unit not in units:
        print(f"Error: Unknown target unit '{to_unit}'.")
        return

    val = prompt_float(f"Enter value in {names[from_unit]} ({from_unit}): ")
    result = convert_linear(val, from_unit, to_unit, units)
    print(f"\nResult: {val:g} {from_unit} = {result:g} {to_unit}")
    print(f"Details: {val:g} {names[from_unit]} is equal to {result:.6f} {names[to_unit]}")


def handle_temperature_flow() -> None:
    """Interactive handler for temperature conversions."""
    print("\n--- Temperature Converter ---")
    print("Available units:")
    print("  [C] : Celsius")
    print("  [F] : Fahrenheit")
    print("  [K] : Kelvin")

    from_unit = input("Enter source unit (C/F/K): ").strip().upper()
    if from_unit not in ("C", "F", "K"):
        print("Error: Source unit must be C, F, or K.")
        return

    to_unit = input("Enter target unit (C/F/K): ").strip().upper()
    if to_unit not in ("C", "F", "K"):
        print("Error: Target unit must be C, F, or K.")
        return

    val = prompt_float(f"Enter temperature in {from_unit}: ")
    result = convert_temperature(val, from_unit, to_unit)
    print(f"\nResult: {val:g} degrees {from_unit} = {result:g} degrees {to_unit}")
    print(f"Details: {val:g} {from_unit} is equal to {result:.4f} {to_unit}")


def main() -> None:
    """Main menu loop for the Unit Converter."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    while True:
        print("\n==============================")
        print("     Unit Converter Hub      ")
        print("==============================")
        print("1. Length Conversion")
        print("2. Weight / Mass Conversion")
        print("3. Temperature Conversion")
        print("4. Digital Storage Conversion")
        print("5. Speed Conversion")
        print("6. Run Automated Self-Tests")
        print("7. Exit")

        choice = input("\nSelect an option (1-7): ").strip()
        if choice == "1":
            handle_linear_flow("Length", LENGTH_UNITS, LENGTH_NAMES)
        elif choice == "2":
            handle_linear_flow("Weight / Mass", MASS_UNITS, MASS_NAMES)
        elif choice == "3":
            handle_temperature_flow()
        elif choice == "4":
            handle_linear_flow("Digital Storage", STORAGE_UNITS, STORAGE_NAMES)
        elif choice == "5":
            handle_linear_flow("Speed", SPEED_UNITS, SPEED_NAMES)
        elif choice == "6":
            run_tests()
        elif choice == "7":
            print("Exiting Unit Converter. Goodbye.")
            break
        else:
            print("Invalid choice. Please choose from 1 to 7.")


if __name__ == "__main__":
    main()
