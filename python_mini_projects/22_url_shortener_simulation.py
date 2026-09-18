"""URL Shortener Simulation: In-memory and JSON-backed URL shortening engine.

Implements Base62 encoding, custom alias mapping, collision handling,
and click analytics tracking.
"""

import json
import os
import string
import sys
import time
from typing import Dict, Optional, Tuple


BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase
BASE = len(BASE62_ALPHABET)


def base62_encode(num: int) -> str:
    """Encode an integer to a Base62 string."""
    if num == 0:
        return BASE62_ALPHABET[0]
    encoded = []
    while num > 0:
        num, rem = divmod(num, BASE)
        encoded.append(BASE62_ALPHABET[rem])
    return "".join(reversed(encoded))


def base62_decode(s: str) -> int:
    """Decode a Base62 string back to an integer."""
    num = 0
    for char in s:
        idx = BASE62_ALPHABET.find(char)
        if idx == -1:
            raise ValueError(f"Invalid Base62 character: {char}")
        num = num * BASE + idx
    return num


class URLShortener:
    """Manages short codes, custom aliases, metadata, and analytics."""

    def __init__(self, storage_file: str = "url_mappings.json"):
        self.storage_file = storage_file
        self.counter = 100000
        self.records: Dict[str, Dict] = {}
        self.load_from_storage()

    def load_from_storage(self) -> None:
        """Load records from JSON file if present."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.records = data.get("records", {})
                    self.counter = data.get("counter", 100000)
            except (json.JSONDecodeError, OSError):
                self.records = {}
                self.counter = 100000

    def save_to_storage(self) -> None:
        """Persist records and counter to JSON storage."""
        data = {
            "counter": self.counter,
            "records": self.records,
        }
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def shorten_url(self, target_url: str, custom_alias: Optional[str] = None) -> Tuple[bool, str]:
        """Generate a short code or register a custom alias for a target URL."""
        target_url = target_url.strip()
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url

        if custom_alias:
            alias = custom_alias.strip()
            if not alias.isalnum():
                return False, "Custom alias must contain only alphanumeric characters."
            if alias in self.records:
                return False, f"Alias '{alias}' is already in use."
            code = alias
        else:
            self.counter += 1
            code = base62_encode(self.counter)
            while code in self.records:
                self.counter += 1
                code = base62_encode(self.counter)

        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        self.records[code] = {
            "target_url": target_url,
            "created_at": now_str,
            "clicks": 0,
            "last_accessed": None,
            "is_custom": bool(custom_alias),
        }
        self.save_to_storage()
        return True, code

    def expand_url(self, code: str) -> Tuple[bool, str]:
        """Lookup target URL for code, incrementing click telemetry."""
        code = code.strip()
        if code not in self.records:
            return False, f"Short code '{code}' not found."

        record = self.records[code]
        record["clicks"] += 1
        record["last_accessed"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.save_to_storage()
        return True, record["target_url"]

    def get_analytics(self, code: str) -> Optional[Dict]:
        """Retrieve metrics for a specific short code."""
        return self.records.get(code.strip())

    def get_all_records(self) -> Dict[str, Dict]:
        """Return full mapping catalog."""
        return self.records


def run_tests() -> bool:
    """Run automated verification tests on Base62 logic and shortener store."""
    # Test Base62 round-trip
    for test_val in (0, 1, 61, 62, 100000, 987654321):
        enc = base62_encode(test_val)
        dec = base62_decode(enc)
        assert dec == test_val, f"Base62 round-trip failed for {test_val}: {enc} -> {dec}"

    test_storage = "test_url_storage.json"
    if os.path.exists(test_storage):
        os.remove(test_storage)

    try:
        shortener = URLShortener(storage_file=test_storage)

        # Test standard shortening
        ok, code1 = shortener.shorten_url("https://github.com")
        assert ok, f"Failed to shorten URL: {code1}"

        # Test custom alias
        ok, code2 = shortener.shorten_url("https://python.org", custom_alias="pyhome")
        assert ok and code2 == "pyhome", f"Custom alias failed: {code2}"

        # Test duplicate alias prevention
        dup_ok, _ = shortener.shorten_url("https://example.com", custom_alias="pyhome")
        assert not dup_ok, "Duplicate alias was unexpectedly allowed"

        # Test expansion and clicks
        expand_ok, target = shortener.expand_url(code1)
        assert expand_ok and target == "https://github.com", f"Expand error: {target}"
        analytics = shortener.get_analytics(code1)
        assert analytics is not None and analytics["clicks"] == 1, "Click counter failed"

        print("All URL shortener test assertions passed successfully.")
    finally:
        if os.path.exists(test_storage):
            os.remove(test_storage)

    return True


def display_analytics_table(records: Dict[str, Dict], domain_prefix: str = "https://sho.rt/") -> None:
    """Display tabular view of stored URLs and click analytics."""
    if not records:
        print("\nNo URLs have been shortened yet.")
        return

    print("\n" + "=" * 80)
    print(f"{'Short URL':<22} | {'Clicks':<6} | {'Created At':<19} | {'Target URL'}")
    print("-" * 80)
    for code, data in records.items():
        short_url = f"{domain_prefix}{code}"
        target = data["target_url"]
        if len(target) > 30:
            target = target[:27] + "..."
        clicks = data["clicks"]
        created = data.get("created_at", "N/A")
        print(f"{short_url:<22} | {clicks:<6} | {created:<19} | {target}")
    print("=" * 80)


def main() -> None:
    """Interactive command-line interface for URL Shortener."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    shortener = URLShortener()
    prefix = "https://sho.rt/"

    while True:
        print("\n==============================")
        print("    URL Shortener Simulation  ")
        print("==============================")
        print("1. Shorten a URL (Auto-code)")
        print("2. Shorten a URL (Custom alias)")
        print("3. Expand / Simulate click on short URL")
        print("4. View URL analytics and catalog")
        print("5. Run automated self-tests")
        print("6. Exit")

        choice = input("\nSelect an option (1-6): ").strip()
        if choice == "1":
            url = input("Enter destination URL: ").strip()
            if not url:
                print("Error: Destination URL cannot be empty.")
                continue
            ok, result = shortener.shorten_url(url)
            if ok:
                print(f"\nSuccess: Short URL generated: {prefix}{result}")
                print(f"Target: {shortener.records[result]['target_url']}")
            else:
                print(f"Error: {result}")

        elif choice == "2":
            url = input("Enter destination URL: ").strip()
            if not url:
                print("Error: Destination URL cannot be empty.")
                continue
            alias = input("Enter preferred custom alias (letters and numbers only): ").strip()
            ok, result = shortener.shorten_url(url, custom_alias=alias)
            if ok:
                print(f"\nSuccess: Short URL created: {prefix}{result}")
            else:
                print(f"Error: {result}")

        elif choice == "3":
            code_input = input("Enter short code or full short URL: ").strip()
            code = code_input.replace(prefix, "").strip()
            ok, result = shortener.expand_url(code)
            if ok:
                print(f"\nRedirect simulation successful.")
                print(f"Resolved Target URL: {result}")
                analytics = shortener.get_analytics(code)
                print(f"Total clicks recorded: {analytics['clicks']}")
            else:
                print(f"Error: {result}")

        elif choice == "4":
            display_analytics_table(shortener.get_all_records(), prefix)

        elif choice == "5":
            run_tests()

        elif choice == "6":
            print("Exiting URL Shortener Simulation. Goodbye.")
            break
        else:
            print("Invalid choice. Please choose from 1 to 6.")


if __name__ == "__main__":
    main()
