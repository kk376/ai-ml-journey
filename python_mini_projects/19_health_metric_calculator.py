"""Health Metric Calculator: Compute BMI, BMR, TDEE, water intake, and track progress via CSV."""

import csv
import os
from datetime import datetime

HISTORY_FILE = "health_history.csv"


def calculate_bmi(weight_kg, height_cm):
    """Compute BMI and return tuple of (bmi_value, category, healthy_weight_range)."""
    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m ** 2)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25.0:
        category = "Normal weight"
    elif bmi < 30.0:
        category = "Overweight"
    else:
        category = "Obesity"

    # Healthy weight range for BMI between 18.5 and 24.9
    min_healthy = 18.5 * (height_m ** 2)
    max_healthy = 24.9 * (height_m ** 2)

    return round(bmi, 2), category, (round(min_healthy, 1), round(max_healthy, 1))


def calculate_bmr(weight_kg, height_cm, age_years, gender):
    """Calculate Basal Metabolic Rate using the Mifflin-St Jeor Equation."""
    # Men: BMR = (10 * weight in kg) + (6.25 * height in cm) - (5 * age in years) + 5
    # Women: BMR = (10 * weight in kg) + (6.25 * height in cm) - (5 * age in years) - 161
    base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age_years)
    if gender.lower() == "m":
        return round(base + 5, 1)
    else:
        return round(base - 161, 1)


def calculate_tdee(bmr, activity_multiplier):
    """Compute Total Daily Energy Expenditure from BMR and activity level."""
    return round(bmr * activity_multiplier, 1)


def calculate_water_intake(weight_kg, exercise_minutes=0):
    """Estimate recommended daily water intake in liters."""
    # Baseline: ~35ml per kg body weight + 350ml per 30 mins exercise
    base_ml = weight_kg * 35
    exercise_ml = (exercise_minutes / 30.0) * 350
    liters = (base_ml + exercise_ml) / 1000.0
    return round(liters, 2)


def calculate_ideal_weight_devine(height_cm, gender):
    """Calculate Ideal Body Weight in kg using the Devine Formula."""
    inches_total = height_cm / 2.54
    inches_over_5ft = max(0.0, inches_total - 60)
    if gender.lower() == "m":
        ibw = 50.0 + (2.3 * inches_over_5ft)
    else:
        ibw = 45.5 + (2.3 * inches_over_5ft)
    return round(ibw, 1)


def save_assessment_record(record, filepath=HISTORY_FILE):
    """Append health assessment record to history CSV file."""
    file_exists = os.path.exists(filepath)
    fieldnames = [
        "timestamp", "name", "gender", "age", "height_cm",
        "weight_kg", "bmi", "category", "bmr_kcal", "tdee_kcal"
    ]
    try:
        with open(filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(record)
        return True
    except OSError as error:
        print(f"[Error] Failed to save record to CSV: {error}")
        return False


def run_full_assessment():
    """Interactive user evaluation pipeline."""
    print("\n=== Comprehensive Health Metric Assessment ===")
    name = input("Enter your name: ").strip()
    if not name:
        name = "User"

    gender = input("Enter gender (M/F): ").strip().lower()
    if gender not in ("m", "f"):
        print("Invalid gender. Please enter 'M' or 'F'.")
        return

    try:
        age = int(input("Enter age in years: ").strip())
        height = float(input("Enter height in centimeters (e.g. 175): ").strip())
        weight = float(input("Enter weight in kilograms (e.g. 70.5): ").strip())
        if age <= 0 or height <= 0 or weight <= 0:
            print("Age, height, and weight must be positive numbers.")
            return
    except ValueError:
        print("Invalid numeric input.")
        return

    print("\nSelect Your Typical Activity Level:")
    print("  1. Sedentary (little or no exercise, desk job)")
    print("  2. Lightly Active (light exercise 1 to 3 days/week)")
    print("  3. Moderately Active (moderate exercise 3 to 5 days/week)")
    print("  4. Very Active (hard exercise 6 to 7 days/week)")
    print("  5. Extra Active (very hard exercise, physical job)")
    act_choice = input("Enter choice (1-5, default 2): ").strip()
    act_map = {
        "1": (1.2, "Sedentary"),
        "2": (1.375, "Lightly Active"),
        "3": (1.55, "Moderately Active"),
        "4": (1.725, "Very Active"),
        "5": (1.9, "Extra Active"),
    }
    mult, act_desc = act_map.get(act_choice, (1.375, "Lightly Active"))

    # Perform calculations
    bmi, category, (min_wt, max_wt) = calculate_bmi(weight, height)
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, mult)
    ibw = calculate_ideal_weight_devine(height, gender)
    water = calculate_water_intake(weight, exercise_minutes=30)

    # Print Report
    print("\n" + "=" * 60)
    print(f"HEALTH ASSESSMENT REPORT FOR: {name.upper()}")
    print("=" * 60)
    print(f"Body Mass Index (BMI)   : {bmi} [{category}]")
    print(f"Healthy Weight Range    : {min_wt} kg to {max_wt} kg")
    print(f"Ideal Body Weight (Devine): {ibw} kg")
    print("-" * 60)
    print(f"Basal Metabolic Rate (BMR): {bmr} kcal/day")
    print(f"Activity Multiplier     : {mult} ({act_desc})")
    print(f"Daily Maintenance (TDEE): {tdee} kcal/day")
    print(f"Recommended Water Intake: {water} Liters/day (~30 min exercise)")
    print("=" * 60)

    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": name,
        "gender": gender.upper(),
        "age": age,
        "height_cm": height,
        "weight_kg": weight,
        "bmi": bmi,
        "category": category,
        "bmr_kcal": bmr,
        "tdee_kcal": tdee,
    }

    if save_assessment_record(record):
        print(f"[Logged] Assessment recorded in '{HISTORY_FILE}'.\n")


def view_history():
    """Display past assessment logs from CSV."""
    if not os.path.exists(HISTORY_FILE):
        print("\nNo assessment history found. Complete an assessment first.")
        return

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        if not rows:
            print("\nHistory file is empty.")
            return

        print("\n" + "=" * 85)
        print(f"{'Date':<12} {'Name':<14} {'Weight':<10} {'BMI':<8} {'Category':<16} {'BMR (kcal)':<12} {'TDEE'}")
        print("=" * 85)

        for r in rows:
            dt = r.get("timestamp", "")[:10]
            name = r.get("name", "")
            wt = f"{r.get('weight_kg', '')} kg"
            bmi = r.get("bmi", "")
            cat = r.get("category", "")
            bmr = r.get("bmr_kcal", "")
            tdee = r.get("tdee_kcal", "")
            print(f"{dt:<12} {name:<14} {wt:<10} {bmi:<8} {cat:<16} {bmr:<12} {tdee}")

        print("=" * 85)
        print(f"Total entries logged: {len(rows)}\n")
    except OSError as error:
        print(f"\n[Error] Failed to read history file: {error}")


def main():
    while True:
        print("=" * 45)
        print("      HEALTH METRIC CALCULATOR")
        print("=" * 45)
        print("1. Run Full Health Assessment")
        print("2. Quick BMI Calculator Only")
        print("3. View Saved Assessment History (CSV)")
        print("4. Exit")
        print("=" * 45)

        choice = input("Select option (1-4): ").strip()

        if choice == "1":
            run_full_assessment()
        elif choice == "2":
            try:
                h = float(input("Enter height in cm: ").strip())
                w = float(input("Enter weight in kg: ").strip())
                bmi, cat, (low, high) = calculate_bmi(w, h)
                print(f"\nResult: BMI = {bmi} [{cat}]")
                print(f"Normal weight bounds for your height: {low} kg to {high} kg\n")
            except ValueError:
                print("Invalid input numbers.")
        elif choice == "3":
            view_history()
        elif choice == "4":
            print("\nStay healthy! Goodbye.")
            break
        else:
            print("\nInvalid choice. Please choose 1 to 4.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
