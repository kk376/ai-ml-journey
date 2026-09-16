"""Log File Analyzer: Parse server logs, compute level distributions, extract unique IPs via Sets, and isolate errors."""

import os
import random
import re
from datetime import datetime

LOG_LINE_PATTERN = re.compile(
    r"^\[(?P<timestamp>[^\]]+)\] \[(?P<level>[A-Z]+)\] (?P<ip>\d{1,3}(?:\.\d{1,3}){3}) - (?P<message>.+)$"
)


def generate_sample_log(filepath="sample_server.log", lines=50):
    """Generate a realistic synthetic server log file for testing."""
    levels = ["INFO", "INFO", "INFO", "WARNING", "ERROR", "CRITICAL"]
    ips = [
        "192.168.1.10", "192.168.1.15", "10.0.0.5", "10.0.0.8",
        "172.16.0.22", "127.0.0.1", "198.51.100.42", "203.0.113.19"
    ]
    messages = [
        "GET /api/v1/users HTTP/1.1 200 OK",
        "POST /api/v1/auth/login HTTP/1.1 200 OK",
        "GET /dashboard HTTP/1.1 200 OK",
        "POST /api/v1/auth/login HTTP/1.1 401 Unauthorized",
        "GET /api/v1/products/404 HTTP/1.1 404 Not Found",
        "GET /static/bundle.js HTTP/1.1 304 Not Modified",
        "Database query timeout after 5000ms: SELECT * FROM orders",
        "High memory utilization detected: 88.4% capacity reached",
        "Connection reset by peer during TLS handshake",
        "Unhandled exception in payment processing pipeline: ZeroDivisionError",
        "Failed database connection pool checkout: max connections reached",
    ]

    try:
        with open(filepath, "w", encoding="utf-8") as file:
            for i in range(lines):
                level = random.choice(levels)
                ip = random.choice(ips)
                msg = random.choice(messages)
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"[{now_str}] [{level}] {ip} - {msg}\n")
        print(f"\n[Success] Generated sample log file with {lines} entries at '{filepath}'.")
        return True
    except OSError as error:
        print(f"\n[Error] Failed to generate log file: {error}")
        return False


def parse_log_file(filepath):
    """Read and parse a log file into structured dictionaries."""
    if not os.path.exists(filepath):
        print(f"\nError: Log file '{filepath}' does not exist.")
        return None

    parsed_records = []
    unparsed_count = 0

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            for line_no, line in enumerate(file, start=1):
                clean_line = line.strip()
                if not clean_line:
                    continue
                match = LOG_LINE_PATTERN.match(clean_line)
                if match:
                    data = match.groupdict()
                    data["line_no"] = line_no
                    parsed_records.append(data)
                else:
                    unparsed_count += 1
    except (OSError, UnicodeDecodeError) as error:
        print(f"\n[Error] Reading log file failed: {error}")
        return None

    if unparsed_count > 0:
        print(f"[Notice] {unparsed_count} line(s) did not match standard format and were skipped.")

    return parsed_records


def print_general_summary(records, filepath):
    """Compute and print distribution of log levels and unique IPs using Sets."""
    if not records:
        print("\nNo valid log records to analyze.")
        return

    total = len(records)
    level_counts = {}
    unique_ips = set()
    error_messages = []

    for item in records:
        lvl = item["level"]
        level_counts[lvl] = level_counts.get(lvl, 0) + 1
        unique_ips.add(item["ip"])
        if lvl in ("ERROR", "CRITICAL"):
            error_messages.append(item["message"])

    print("\n" + "=" * 65)
    print(f"LOG ANALYSIS REPORT: {filepath}")
    print("=" * 65)
    print(f"Total Parsed Entries : {total}")
    print(f"Unique IP Addresses  : {len(unique_ips)} (extracted via Python Set)")
    print("-" * 65)
    print("Severity Level Distribution:")

    for lvl in ("INFO", "WARNING", "ERROR", "CRITICAL"):
        cnt = level_counts.get(lvl, 0)
        pct = (cnt / total * 100) if total > 0 else 0
        bar = "#" * int(pct // 4)
        print(f"  {lvl:<10} : {cnt:>4} ({pct:>5.1f}%) | {bar}")

    print("-" * 65)
    total_failures = level_counts.get("ERROR", 0) + level_counts.get("CRITICAL", 0)
    failure_rate = (total_failures / total * 100) if total > 0 else 0
    print(f"Failure Rate (ERROR + CRITICAL): {failure_rate:.1f}%\n")


def print_unique_ips(records):
    """Show detailed breakdown of IP addresses using set operations."""
    if not records:
        print("\nNo records loaded.")
        return

    # Aggregate frequency per IP
    ip_counts = {}
    for item in records:
        ip = item["ip"]
        ip_counts[ip] = ip_counts.get(ip, 0) + 1

    unique_ip_set = set(ip_counts.keys())

    print("\n" + "=" * 55)
    print(f"UNIQUE IP ADDRESS ANALYSIS ({len(unique_ip_set)} Unique IPs)")
    print("=" * 55)
    print(f"{'IP Address':<20} {'Requests':<10} {'Percentage'}")
    print("-" * 55)

    total = len(records)
    for ip, count in sorted(ip_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total * 100) if total > 0 else 0
        print(f"{ip:<20} {count:<10} {pct:.1f}%")

    print("=" * 55 + "\n")


def filter_by_severity(records):
    """Display only log lines matching selected severity."""
    print("\nSelect Severity to Filter:")
    print("  1. INFO")
    print("  2. WARNING")
    print("  3. ERROR")
    print("  4. CRITICAL")
    print("  5. All Failures (ERROR + CRITICAL)")
    choice = input("Enter choice (1-5): ").strip()

    target_levels = set()
    if choice == "1":
        target_levels.add("INFO")
    elif choice == "2":
        target_levels.add("WARNING")
    elif choice == "3":
        target_levels.add("ERROR")
    elif choice == "4":
        target_levels.add("CRITICAL")
    elif choice == "5":
        target_levels.update(["ERROR", "CRITICAL"])
    else:
        print("Invalid selection.")
        return

    matches = [r for r in records if r["level"] in target_levels]

    if not matches:
        print(f"\nNo entries found with severity: {target_levels}")
        return

    print("\n" + "=" * 80)
    print(f"FILTERED ENTRIES ({len(matches)} match{'es' if len(matches) != 1 else ''})")
    print("=" * 80)
    for r in matches:
        print(f"[Line {r['line_no']:>3}] [{r['timestamp']}] [{r['level']:<8}] {r['ip']} : {r['message']}")
    print("=" * 80 + "\n")


def export_summary_to_file(records, source_path):
    """Export the summary report to a clean text file."""
    if not records:
        print("\nNo records to export.")
        return

    out_name = input("Enter destination filename (default 'log_summary.txt'): ").strip()
    if not out_name:
        out_name = "log_summary.txt"

    total = len(records)
    level_counts = {}
    unique_ips = set()
    for item in records:
        lvl = item["level"]
        level_counts[lvl] = level_counts.get(lvl, 0) + 1
        unique_ips.add(item["ip"])

    try:
        with open(out_name, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write(f"LOG FILE SUMMARY: {source_path}\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total Analyzed Lines : {total}\n")
            f.write(f"Unique IP Addresses  : {len(unique_ips)}\n\n")
            f.write("Level Breakdown:\n")
            for lvl in ("INFO", "WARNING", "ERROR", "CRITICAL"):
                cnt = level_counts.get(lvl, 0)
                pct = (cnt / total * 100) if total > 0 else 0
                f.write(f"  - {lvl:<10}: {cnt} ({pct:.1f}%)\n")
            f.write("\nUnique IP Addresses Set:\n")
            for ip in sorted(unique_ips):
                f.write(f"  * {ip}\n")
        print(f"\n[Success] Summary exported to '{out_name}'.")
    except OSError as error:
        print(f"\n[Error] Export failed: {error}")


def main():
    current_filepath = "sample_server.log"
    current_records = None

    while True:
        print("=" * 45)
        print("       LOG FILE ANALYZER TOOLKIT")
        print("=" * 45)
        print("1. Generate Sample Log File")
        print("2. Load & Analyze Log File")
        print("3. View Severity Distribution")
        print("4. View Unique IP Address Stats (Sets)")
        print("5. Filter Logs by Severity Level")
        print("6. Export Summary to Text File")
        print("7. Exit")
        print("=" * 45)

        choice = input("Select option (1-7): ").strip()

        if choice == "1":
            fname = input("Enter filename to create (default 'sample_server.log'): ").strip()
            if not fname:
                fname = "sample_server.log"
            lines_str = input("Enter number of lines (default 60): ").strip()
            lines = int(lines_str) if lines_str.isdigit() else 60
            if generate_sample_log(fname, lines):
                current_filepath = fname
                current_records = parse_log_file(fname)
        elif choice == "2":
            fname = input(f"Enter log file path (default '{current_filepath}'): ").strip()
            if not fname:
                fname = current_filepath
            records = parse_log_file(fname)
            if records is not None:
                current_filepath = fname
                current_records = records
                print(f"\n[Success] Loaded {len(records)} log entries from '{fname}'.")
                print_general_summary(current_records, current_filepath)
        elif choice == "3":
            if current_records is None:
                print("\nPlease load a log file first (Option 2).")
            else:
                print_general_summary(current_records, current_filepath)
        elif choice == "4":
            if current_records is None:
                print("\nPlease load a log file first (Option 2).")
            else:
                print_unique_ips(current_records)
        elif choice == "5":
            if current_records is None:
                print("\nPlease load a log file first (Option 2).")
            else:
                filter_by_severity(current_records)
        elif choice == "6":
            if current_records is None:
                print("\nPlease load a log file first (Option 2).")
            else:
                export_summary_to_file(current_records, current_filepath)
        elif choice == "7":
            print("\nExiting Log File Analyzer. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please select 1 to 7.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
