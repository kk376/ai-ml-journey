"""Bank Account Simulator: Object-Oriented banking with encapsulation, custom exceptions, and statements."""

import json
import os
from datetime import datetime

BANK_DATA_FILE = "bank_accounts.json"


class BankingError(Exception):
    """Base exception class for banking operation failures."""
    pass


class InsufficientFundsError(BankingError):
    """Raised when a withdrawal exceeds available account balance."""
    pass


class InvalidAmountError(BankingError):
    """Raised when a transaction amount is negative, zero, or not a number."""
    pass


class BankAccount:
    """Represents a bank account with balance tracking and transaction auditing."""

    def __init__(self, account_number, holder_name, initial_balance=0.0):
        if initial_balance < 0:
            raise InvalidAmountError("Initial deposit cannot be negative.")
        self.account_number = str(account_number)
        self.holder_name = holder_name.strip()
        self.balance = float(initial_balance)
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transactions = []

        if self.balance > 0:
            self._record_transaction("OPENING_DEPOSIT", self.balance, self.balance)

    def _record_transaction(self, tx_type, amount, balance_after):
        """Append an immutable audit entry to account transaction history."""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": tx_type,
            "amount": round(amount, 2),
            "balance_after": round(balance_after, 2),
        }
        self.transactions.append(entry)

    def deposit(self, amount):
        """Add funds to balance and record transaction."""
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be strictly positive.")
        self.balance += amount
        self._record_transaction("DEPOSIT", amount, self.balance)
        return self.balance

    def withdraw(self, amount):
        """Deduct funds from balance if adequate funds exist."""
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be strictly positive.")
        if amount > self.balance:
            raise InsufficientFundsError(
                f"Requested Rs.{amount:.2f}, but current balance is only Rs.{self.balance:.2f}."
            )
        self.balance -= amount
        self._record_transaction("WITHDRAWAL", amount, self.balance)
        return self.balance

    def to_dict(self):
        """Serialize instance state to a dictionary for JSON persistence."""
        return {
            "account_number": self.account_number,
            "holder_name": self.holder_name,
            "balance": self.balance,
            "created_at": self.created_at,
            "transactions": self.transactions,
        }

    @classmethod
    def from_dict(cls, data):
        """Construct a BankAccount instance from stored dictionary data."""
        account = cls(
            account_number=data["account_number"],
            holder_name=data["holder_name"],
            initial_balance=0.0,
        )
        account.balance = float(data.get("balance", 0.0))
        account.created_at = data.get("created_at", "")
        account.transactions = data.get("transactions", [])
        return account


class BankManager:
    """Manages the collection of bank accounts with persistent file storage."""

    def __init__(self, filepath=BANK_DATA_FILE):
        self.filepath = filepath
        self.accounts = {}
        self.load()

    def load(self):
        """Load accounts from JSON file."""
        if not os.path.exists(self.filepath):
            return
        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
                for item in data:
                    acc = BankAccount.from_dict(item)
                    self.accounts[acc.account_number] = acc
        except (json.JSONDecodeError, OSError) as error:
            print(f"[Warning] Failed loading bank data: {error}. Starting fresh.")

    def save(self):
        """Save all accounts to JSON file."""
        try:
            serialized = [acc.to_dict() for acc in self.accounts.values()]
            with open(self.filepath, "w", encoding="utf-8") as file:
                json.dump(serialized, file, indent=4)
            return True
        except OSError as error:
            print(f"[Error] Failed saving bank accounts: {error}")
            return False

    def create_account(self, holder_name, initial_deposit=0.0):
        """Create a new unique account."""
        next_num = 1001
        if self.accounts:
            existing = [int(num) for num in self.accounts.keys() if num.isdigit()]
            if existing:
                next_num = max(existing) + 1
        acc_num = str(next_num)
        account = BankAccount(acc_num, holder_name, initial_deposit)
        self.accounts[acc_num] = account
        self.save()
        return account

    def get_account(self, account_number):
        """Retrieve an account by its account number string."""
        return self.accounts.get(str(account_number))

    def transfer(self, from_acc_num, to_acc_num, amount):
        """Transfer funds between two accounts atomically."""
        if from_acc_num == to_acc_num:
            raise BankingError("Cannot transfer funds to the same account.")

        source = self.get_account(from_acc_num)
        dest = self.get_account(to_acc_num)

        if not source:
            raise BankingError(f"Source account #{from_acc_num} not found.")
        if not dest:
            raise BankingError(f"Destination account #{to_acc_num} not found.")

        # Atomic transaction: withdraw first, deposit only if withdrawal succeeds
        source.withdraw(amount)
        dest.deposit(amount)
        source._record_transaction(f"TRANSFER_TO_#{to_acc_num}", amount, source.balance)
        dest._record_transaction(f"TRANSFER_FROM_#{from_acc_num}", amount, dest.balance)
        self.save()


def parse_float_input(prompt):
    """Safely prompt and convert input to a positive float."""
    raw = input(prompt).strip()
    try:
        val = float(raw)
        return val
    except ValueError:
        raise InvalidAmountError("Please enter a valid numeric value.")


def ui_create_account(bank):
    print("\n=== Open New Account ===")
    name = input("Enter account holder name: ").strip()
    if not name:
        print("Account holder name cannot be empty.")
        return

    try:
        deposit = parse_float_input("Enter initial deposit amount (Rs.): ")
        account = bank.create_account(name, deposit)
        print("\n" + "=" * 50)
        print("ACCOUNT CREATED SUCCESSFULLY")
        print("=" * 50)
        print(f"Account Number : #{account.account_number}")
        print(f"Holder Name    : {account.holder_name}")
        print(f"Current Balance: Rs.{account.balance:.2f}")
        print("=" * 50 + "\n")
    except BankingError as error:
        print(f"[Error] {error}")


def ui_deposit(bank):
    print("\n=== Deposit Funds ===")
    acc_num = input("Enter account number: ").strip()
    account = bank.get_account(acc_num)
    if not account:
        print(f"Account #{acc_num} does not exist.")
        return

    try:
        amount = parse_float_input("Enter amount to deposit (Rs.): ")
        account.deposit(amount)
        bank.save()
        print(f"\n[Success] Deposited Rs.{amount:.2f}. New Balance: Rs.{account.balance:.2f}")
    except BankingError as error:
        print(f"[Error] {error}")


def ui_withdraw(bank):
    print("\n=== Withdraw Funds ===")
    acc_num = input("Enter account number: ").strip()
    account = bank.get_account(acc_num)
    if not account:
        print(f"Account #{acc_num} does not exist.")
        return

    try:
        amount = parse_float_input("Enter amount to withdraw (Rs.): ")
        account.withdraw(amount)
        bank.save()
        print(f"\n[Success] Withdrew Rs.{amount:.2f}. New Balance: Rs.{account.balance:.2f}")
    except BankingError as error:
        print(f"[Error] {error}")


def ui_transfer(bank):
    print("\n=== Fund Transfer ===")
    from_acc = input("Enter source account number: ").strip()
    to_acc = input("Enter destination account number: ").strip()
    try:
        amount = parse_float_input("Enter amount to transfer (Rs.): ")
        bank.transfer(from_acc, to_acc, amount)
        print(f"\n[Success] Transferred Rs.{amount:.2f} from #{from_acc} to #{to_acc} successfully.")
    except BankingError as error:
        print(f"[Error] {error}")


def ui_view_statement(bank):
    print("\n=== Account Statement ===")
    acc_num = input("Enter account number: ").strip()
    account = bank.get_account(acc_num)
    if not account:
        print(f"Account #{acc_num} does not exist.")
        return

    print("\n" + "=" * 75)
    print(f"STATEMENT FOR ACCOUNT #{account.account_number} ({account.holder_name})")
    print(f"Created: {account.created_at} | Current Balance: Rs.{account.balance:.2f}")
    print("=" * 75)
    print(f"{'Timestamp':<20} {'Transaction Type':<26} {'Amount':<14} {'Balance After'}")
    print("-" * 75)

    if not account.transactions:
        print("No transactions recorded yet.")
    else:
        for tx in account.transactions:
            t_time = tx.get("timestamp", "")
            t_type = tx.get("type", "")
            t_amt = f"Rs.{tx.get('amount', 0.0):.2f}"
            t_bal = f"Rs.{tx.get('balance_after', 0.0):.2f}"
            print(f"{t_time:<20} {t_type:<26} {t_amt:<14} {t_bal}")

    print("=" * 75 + "\n")


def main():
    bank = BankManager()

    while True:
        print("=" * 45)
        print("       BANK ACCOUNT SIMULATOR (OOP)")
        print("=" * 45)
        print("1. Open New Account")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Transfer Funds")
        print("5. View Account Statement")
        print("6. List All Accounts")
        print("7. Exit")
        print("=" * 45)

        choice = input("Enter choice (1-7): ").strip()

        if choice == "1":
            ui_create_account(bank)
        elif choice == "2":
            ui_deposit(bank)
        elif choice == "3":
            ui_withdraw(bank)
        elif choice == "4":
            ui_transfer(bank)
        elif choice == "5":
            ui_view_statement(bank)
        elif choice == "6":
            print("\n=== Registered Accounts ===")
            if not bank.accounts:
                print("No accounts opened yet.\n")
            else:
                for acc in bank.accounts.values():
                    print(f"  Account #{acc.account_number}: {acc.holder_name} (Balance: Rs.{acc.balance:.2f})")
                print()
        elif choice == "7":
            print("\nThank you for using Bank Account Simulator. Goodbye!")
            bank.save()
            break
        else:
            print("\nInvalid choice. Please select 1 to 7.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
