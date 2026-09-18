"""Currency Exchange Calculator: Multi-currency conversion engine with spread fees.

Features cross-currency conversion matrices, transaction fee accounting,
simulated multi-currency wallet management, and itemized receipt generation.
"""

from datetime import datetime
import hashlib
import sys
from typing import Dict, Optional, Tuple


# Exchange rates relative to base currency: USD (1.00)
EXCHANGE_RATES: Dict[str, float] = {
    "USD": 1.0000,
    "EUR": 0.9250,
    "GBP": 0.7850,
    "INR": 83.4500,
    "JPY": 155.6000,
    "CAD": 1.3680,
    "AUD": 1.5120,
    "CHF": 0.9080,
    "SGD": 1.3520,
}

CURRENCY_NAMES: Dict[str, str] = {
    "USD": "United States Dollar",
    "EUR": "Euro",
    "GBP": "British Pound",
    "INR": "Indian Rupee",
    "JPY": "Japanese Yen",
    "CAD": "Canadian Dollar",
    "AUD": "Australian Dollar",
    "CHF": "Swiss Franc",
    "SGD": "Singapore Dollar",
}


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    fee_percent: float = 1.0,
    rates: Optional[Dict[str, float]] = None,
) -> Dict[str, float]:
    """Calculate cross-rate conversion, fee deductions, and net yield."""
    if rates is None:
        rates = EXCHANGE_RATES

    from_c = from_currency.upper()
    to_c = to_currency.upper()

    if from_c not in rates or to_c not in rates:
        raise ValueError(f"Unsupported currency pair: {from_c} to {to_c}")

    if amount < 0:
        raise ValueError("Conversion amount cannot be negative.")

    # Cross-rate calculation via USD base
    base_usd = amount / rates[from_c]
    gross_target = base_usd * rates[to_c]

    # Spread fee calculation
    fee_amount = gross_target * (fee_percent / 100.0)
    net_target = gross_target - fee_amount
    effective_rate = net_target / amount if amount > 0 else 0.0

    return {
        "source_amount": amount,
        "gross_target": gross_target,
        "fee_percent": fee_percent,
        "fee_amount": fee_amount,
        "net_target": net_target,
        "nominal_rate": rates[to_c] / rates[from_c],
        "effective_rate": effective_rate,
    }


def generate_receipt(
    from_curr: str,
    to_curr: str,
    details: Dict[str, float],
) -> str:
    """Format an itemized exchange receipt with unique audit hash."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hash_seed = f"{timestamp}:{from_curr}:{to_curr}:{details['source_amount']}"
    txn_id = hashlib.sha256(hash_seed.encode("utf-8")).hexdigest()[:12].upper()

    lines = [
        "=" * 50,
        "          OFFICIAL EXCHANGE RECEIPT               ",
        "=" * 50,
        f"Transaction ID   : TXN-{txn_id}",
        f"Timestamp        : {timestamp}",
        f"Source Currency  : {from_curr} ({CURRENCY_NAMES.get(from_curr, '')})",
        f"Target Currency  : {to_curr} ({CURRENCY_NAMES.get(to_curr, '')})",
        "-" * 50,
        f"Amount Exchanged : {details['source_amount']:,.2f} {from_curr}",
        f"Nominal Rate     : 1 {from_curr} = {details['nominal_rate']:.4f} {to_curr}",
        f"Gross Converted  : {details['gross_target']:,.2f} {to_curr}",
        f"Service Fee ({details['fee_percent']:.1f}%) : -{details['fee_amount']:,.2f} {to_curr}",
        "-" * 50,
        f"Net Disbursed    : {details['net_target']:,.2f} {to_curr}",
        f"Effective Rate   : 1 {from_curr} = {details['effective_rate']:.4f} {to_curr}",
        "=" * 50,
    ]
    return "\n".join(lines)


class MultiCurrencyWallet:
    """Tracks balances across multiple foreign currencies with deposit/exchange support."""

    def __init__(self) -> None:
        self.balances: Dict[str, float] = {code: 0.0 for code in EXCHANGE_RATES}

    def deposit(self, currency: str, amount: float) -> bool:
        """Add funds to specific currency balance."""
        curr = currency.upper()
        if curr not in self.balances or amount <= 0:
            return False
        self.balances[curr] += amount
        return True

    def exchange(self, from_c: str, to_c: str, amount: float, fee_percent: float = 1.0) -> Tuple[bool, str]:
        """Convert funds between balances within wallet."""
        from_c = from_c.upper()
        to_c = to_c.upper()
        if from_c not in self.balances or to_c not in self.balances:
            return False, "Unsupported currency."
        if self.balances[from_c] < amount:
            return False, f"Insufficient balance in {from_c}. Available: {self.balances[from_c]:.2f}"

        res = convert_currency(amount, from_c, to_c, fee_percent=fee_percent)
        self.balances[from_c] -= amount
        self.balances[to_c] += res["net_target"]
        return True, f"Successfully converted {amount:.2f} {from_c} to {res['net_target']:.2f} {to_c}"


def run_tests() -> bool:
    """Verify conversion calculations and wallet transactions."""
    tolerance = 1e-4

    # 100 USD to EUR with 0% fee
    res0 = convert_currency(100.0, "USD", "EUR", fee_percent=0.0)
    assert abs(res0["net_target"] - 92.50) < tolerance

    # 100 USD to EUR with 1% fee -> 92.50 * 0.99 = 91.575
    res1 = convert_currency(100.0, "USD", "EUR", fee_percent=1.0)
    assert abs(res1["net_target"] - 91.575) < tolerance
    assert abs(res1["fee_amount"] - 0.925) < tolerance

    # Cross-rate: EUR to GBP
    res_cross = convert_currency(100.0, "EUR", "GBP", fee_percent=0.0)
    expected_cross = 100.0 * (0.7850 / 0.9250)
    assert abs(res_cross["net_target"] - expected_cross) < tolerance

    # Multi-currency wallet tests
    wallet = MultiCurrencyWallet()
    wallet.deposit("USD", 1000.0)
    assert wallet.balances["USD"] == 1000.0
    ok, msg = wallet.exchange("USD", "INR", 500.0, fee_percent=1.0)
    assert ok, f"Wallet exchange failed: {msg}"
    assert wallet.balances["USD"] == 500.0
    assert wallet.balances["INR"] > 0

    print("All currency exchange test assertions passed successfully.")
    return True


def display_rates_table() -> None:
    """Display table of all supported currency exchange rates."""
    print("\n" + "=" * 60)
    print(f"{'Code':<6} | {'Currency Name':<25} | {'Rate per 1 USD'}")
    print("-" * 60)
    for code, rate in EXCHANGE_RATES.items():
        print(f"{code:<6} | {CURRENCY_NAMES[code]:<25} | {rate:>10.4f}")
    print("=" * 60)


def main() -> None:
    """Interactive command-line interface for Currency Exchange Calculator."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    wallet = MultiCurrencyWallet()
    wallet.deposit("USD", 5000.0)  # Starting mock liquidity

    while True:
        print("\n==================================")
        print("   Currency Exchange Calculator   ")
        print("==================================")
        print("1. Calculate Currency Conversion & Receipt")
        print("2. View Current Exchange Rate Sheet")
        print("3. Manage Multi-Currency Wallet")
        print("4. Run Automated Self-Tests")
        print("5. Exit")

        choice = input("\nSelect an option (1-5): ").strip()
        if choice == "1":
            display_rates_table()
            src = input("Enter source currency code (e.g. USD): ").strip().upper()
            dst = input("Enter target currency code (e.g. EUR): ").strip().upper()

            if src not in EXCHANGE_RATES or dst not in EXCHANGE_RATES:
                print("Error: Invalid currency code.")
                continue

            try:
                amt = float(input(f"Enter amount in {src}: ").strip())
                if amt <= 0:
                    print("Amount must be greater than zero.")
                    continue
            except ValueError:
                print("Invalid numerical amount.")
                continue

            details = convert_currency(amt, src, dst, fee_percent=1.0)
            receipt = generate_receipt(src, dst, details)
            print("\n" + receipt)

        elif choice == "2":
            display_rates_table()

        elif choice == "3":
            print("\n--- Multi-Currency Wallet ---")
            for code, bal in wallet.balances.items():
                if bal > 0:
                    print(f"  {code}: {bal:,.2f}")
            w_choice = input("\nAction: [d]eposit, [e]xchange, or [b]ack: ").strip().lower()
            if w_choice == "d":
                c = input("Enter currency code: ").strip().upper()
                try:
                    a = float(input("Enter deposit amount: ").strip())
                    if wallet.deposit(c, a):
                        print(f"Deposited {a:.2f} {c}. New balance: {wallet.balances[c]:.2f}")
                    else:
                        print("Deposit failed. Check currency code and amount.")
                except ValueError:
                    print("Invalid amount.")
            elif w_choice == "e":
                c1 = input("From currency: ").strip().upper()
                c2 = input("To currency: ").strip().upper()
                try:
                    a = float(input(f"Amount of {c1} to convert: ").strip())
                    ok, msg = wallet.exchange(c1, c2, a)
                    print(msg)
                except ValueError:
                    print("Invalid amount.")

        elif choice == "4":
            run_tests()

        elif choice == "5":
            print("Exiting Currency Exchange Calculator. Goodbye.")
            break
        else:
            print("Invalid option. Please choose from 1 to 5.")


if __name__ == "__main__":
    main()
