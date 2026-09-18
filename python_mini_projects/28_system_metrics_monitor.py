"""System Metrics Monitor: Lightweight Linux procfs performance telemetrist.

Reads Linux /proc pseudo-filesystem directly without external dependencies
to report real-time CPU utilization, memory pressure, load averages,
and system uptime.
"""

import os
import sys
import time
from typing import Dict, List, Optional, Tuple


def read_proc_uptime() -> Tuple[float, str]:
    """Read total uptime in seconds from /proc/uptime and return formatted string."""
    try:
        with open("/proc/uptime", "r", encoding="utf-8") as f:
            uptime_seconds = float(f.readline().split()[0])
    except (OSError, IndexError, ValueError):
        return 0.0, "Unknown"

    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    parts.append(f"{minutes}m {seconds}s")
    return uptime_seconds, " ".join(parts)


def read_proc_loadavg() -> Tuple[float, float, float]:
    """Read 1, 5, and 15 minute system load averages from /proc/loadavg."""
    try:
        with open("/proc/loadavg", "r", encoding="utf-8") as f:
            tokens = f.readline().split()
            return float(tokens[0]), float(tokens[1]), float(tokens[2])
    except (OSError, IndexError, ValueError):
        return 0.0, 0.0, 0.0


def parse_meminfo_content(content: str) -> Dict[str, int]:
    """Parse key-value pairs from /proc/meminfo text (values in kilobytes)."""
    data = {}
    for line in content.strip().splitlines():
        parts = line.split(":")
        if len(parts) == 2:
            key = parts[0].strip()
            val_str = parts[1].strip().split()[0]
            if val_str.isdigit():
                data[key] = int(val_str)
    return data


def read_proc_meminfo() -> Dict[str, float]:
    """Calculate total, used, available memory and percentages from /proc/meminfo."""
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return {"total_mb": 0.0, "used_mb": 0.0, "avail_mb": 0.0, "used_percent": 0.0}

    info = parse_meminfo_content(content)
    total_kb = info.get("MemTotal", 0)
    avail_kb = info.get("MemAvailable", info.get("MemFree", 0) + info.get("Buffers", 0) + info.get("Cached", 0))
    used_kb = max(0, total_kb - avail_kb)

    total_mb = total_kb / 1024.0
    used_mb = used_kb / 1024.0
    avail_mb = avail_kb / 1024.0
    percent = (used_kb / total_kb * 100.0) if total_kb > 0 else 0.0

    swap_total_kb = info.get("SwapTotal", 0)
    swap_free_kb = info.get("SwapFree", 0)
    swap_used_kb = max(0, swap_total_kb - swap_free_kb)
    swap_percent = (swap_used_kb / swap_total_kb * 100.0) if swap_total_kb > 0 else 0.0

    return {
        "total_mb": round(total_mb, 1),
        "used_mb": round(used_mb, 1),
        "avail_mb": round(avail_mb, 1),
        "used_percent": round(percent, 1),
        "swap_total_mb": round(swap_total_kb / 1024.0, 1),
        "swap_used_mb": round(swap_used_kb / 1024.0, 1),
        "swap_percent": round(swap_percent, 1),
    }


def parse_stat_cpu_lines(content: str) -> Dict[str, Tuple[int, int]]:
    """Parse /proc/stat content and return dict mapping cpu label to (active_jiffies, total_jiffies)."""
    cpu_data = {}
    for line in content.strip().splitlines():
        if line.startswith("cpu"):
            parts = line.split()
            label = parts[0]
            # fields: user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice
            ticks = [int(x) for x in parts[1:]]
            idle = ticks[3] + (ticks[4] if len(ticks) > 4 else 0)
            active = (
                ticks[0]  # user
                + ticks[1]  # nice
                + ticks[2]  # system
                + (ticks[5] if len(ticks) > 5 else 0)  # irq
                + (ticks[6] if len(ticks) > 6 else 0)  # softirq
                + (ticks[7] if len(ticks) > 7 else 0)  # steal
            )
            total = active + idle
            cpu_data[label] = (active, total)
    return cpu_data


def sample_cpu_utilization(sample_interval: float = 0.2) -> Dict[str, float]:
    """Sample /proc/stat twice across sample_interval to calculate exact CPU percentage."""
    try:
        with open("/proc/stat", "r", encoding="utf-8") as f:
            first_raw = f.read()
    except OSError:
        return {"cpu": 0.0}

    time.sleep(sample_interval)

    try:
        with open("/proc/stat", "r", encoding="utf-8") as f:
            second_raw = f.read()
    except OSError:
        return {"cpu": 0.0}

    first = parse_stat_cpu_lines(first_raw)
    second = parse_stat_cpu_lines(second_raw)

    percentages = {}
    for label in first:
        if label in second:
            act_delta = second[label][0] - first[label][0]
            tot_delta = second[label][1] - first[label][1]
            pct = (act_delta / tot_delta * 100.0) if tot_delta > 0 else 0.0
            percentages[label] = round(max(0.0, min(100.0, pct)), 1)

    return percentages


def make_bar(percent: float, width: int = 25) -> str:
    """Generate an ASCII visual gauge bar."""
    filled = int(round((percent / 100.0) * width))
    filled = max(0, min(width, filled))
    empty = width - filled
    return f"[{'=' * filled}{' ' * empty}] {percent:>5.1f}%"


def run_tests() -> bool:
    """Automated tests checking parser and calculation bounds."""
    # Test synthetic meminfo parsing
    fake_meminfo = (
        "MemTotal:       16384000 kB\n"
        "MemFree:         4096000 kB\n"
        "MemAvailable:    8192000 kB\n"
        "Buffers:          500000 kB\n"
        "Cached:          4000000 kB\n"
        "SwapTotal:       2097152 kB\n"
        "SwapFree:        1048576 kB\n"
    )
    parsed_mem = parse_meminfo_content(fake_meminfo)
    assert parsed_mem["MemTotal"] == 16384000
    assert parsed_mem["MemAvailable"] == 8192000

    # Test synthetic stat line parsing
    fake_stat = (
        "cpu  1000 200 300 5000 50 10 20 0 0 0\n"
        "cpu0 500 100 150 2500 25 5 10 0 0 0\n"
    )
    cpu_dict = parse_stat_cpu_lines(fake_stat)
    assert "cpu" in cpu_dict
    assert "cpu0" in cpu_dict

    # Test bar renderer
    assert make_bar(50.0, 10) == "[=====     ]  50.0%"
    assert make_bar(0.0, 10) == "[          ]   0.0%"
    assert make_bar(100.0, 10) == "[==========] 100.0%"

    # Live proc check if running on Linux
    if os.path.exists("/proc/stat"):
        pcts = sample_cpu_utilization(sample_interval=0.05)
        assert "cpu" in pcts
        assert 0.0 <= pcts["cpu"] <= 100.0

    print("All system metrics monitor test assertions passed successfully.")
    return True


def render_snapshot() -> None:
    """Print complete system telemetry snapshot."""
    uptime_sec, uptime_str = read_proc_uptime()
    l1, l5, l15 = read_proc_loadavg()
    mem = read_proc_meminfo()
    cpu = sample_cpu_utilization(sample_interval=0.25)

    print("\n" + "=" * 65)
    print("                 System Metrics Telemetry Snapshot                ")
    print("=" * 65)
    print(f"System Uptime    : {uptime_str}")
    print(f"Load Averages    : {l1:.2f} (1m), {l5:.2f} (5m), {l15:.2f} (15m)")
    print("-" * 65)

    print(f"CPU Utilization  : {make_bar(cpu.get('cpu', 0.0))}")
    print(f"Physical Memory  : {make_bar(mem['used_percent'])}")
    print(f"  RAM Breakdown  : {mem['used_mb']:,.1f} MB used / {mem['total_mb']:,.1f} MB total (Free: {mem['avail_mb']:,.1f} MB)")

    if mem["swap_total_mb"] > 0:
        print(f"Swap Memory      : {make_bar(mem['swap_percent'])}")
        print(f"  Swap Breakdown : {mem['swap_used_mb']:,.1f} MB used / {mem['swap_total_mb']:,.1f} MB total")

    # Per-core breakdown if multiple cores detected
    cores = [k for k in sorted(cpu.keys()) if k != "cpu"]
    if len(cores) > 1:
        print("-" * 65)
        print("Per-Core Utilization:")
        for idx in range(0, len(cores), 2):
            c1 = cores[idx]
            line = f"  {c1:<5}: {cpu[c1]:>5.1f}%"
            if idx + 1 < len(cores):
                c2 = cores[idx + 1]
                line += f"   |   {c2:<5}: {cpu[c2]:>5.1f}%"
            print(line)

    print("=" * 65)


def main() -> None:
    """CLI entry point for System Metrics Monitor."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    while True:
        print("\n================================")
        print("    System Metrics Monitor      ")
        print("================================")
        print("1. Display System Metrics Snapshot")
        print("2. Run Automated Self-Tests")
        print("3. Exit")

        choice = input("\nSelect an option (1-3): ").strip()
        if choice == "1":
            render_snapshot()
        elif choice == "2":
            run_tests()
        elif choice == "3":
            print("Exiting System Metrics Monitor. Goodbye.")
            break
        else:
            print("Invalid option. Please choose from 1 to 3.")


if __name__ == "__main__":
    main()
