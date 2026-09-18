"""File Deduplication Checker: High-performance duplicate file detection tool.

Uses multi-tier filtering (file size grouping, fast partial hashing, and
streaming SHA-256 verification) to identify identical files and compute
reclaimable disk storage with zero third-party dependencies.
"""

from collections import defaultdict
import hashlib
import os
import sys
import tempfile
from typing import Dict, List, Set, Tuple


CHUNK_SIZE = 65536  # 64 KB streaming buffer
PARTIAL_HASH_SIZE = 4096  # 4 KB quick probe


def format_bytes(num_bytes: int) -> str:
    """Format raw byte counts into human-readable metric or IEC notation."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num_bytes < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def get_partial_hash(filepath: str) -> str:
    """Compute SHA-256 of the initial 4KB of a file for fast candidate pruning."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        chunk = f.read(PARTIAL_HASH_SIZE)
        hasher.update(chunk)
    return hasher.hexdigest()


def get_full_hash(filepath: str) -> str:
    """Compute complete SHA-256 digest using streaming chunks."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            hasher.update(chunk)
    return hasher.hexdigest()


def scan_directory_for_duplicates(root_dir: str) -> Tuple[Dict[str, List[str]], int]:
    """Scan directory tree and return dictionary of duplicate file groups and total redundant bytes."""
    size_map: Dict[int, List[str]] = defaultdict(list)

    # Step 1: Group files by file size
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            try:
                if os.path.islink(full_path):
                    continue  # Ignore symlinks to prevent cycle traversal
                size = os.path.getsize(full_path)
                if size > 0:  # Skip 0-byte files or handle separately
                    size_map[size].append(full_path)
            except (OSError, PermissionError):
                continue

    # Filter out sizes with only one file
    candidates = {sz: paths for sz, paths in size_map.items() if len(paths) > 1}

    # Step 2: Partial hash comparison on candidates
    partial_map: Dict[Tuple[int, str], List[str]] = defaultdict(list)
    for size, paths in candidates.items():
        for path in paths:
            try:
                p_hash = get_partial_hash(path)
                partial_map[(size, p_hash)].append(path)
            except (OSError, PermissionError):
                continue

    second_stage = {key: paths for key, paths in partial_map.items() if len(paths) > 1}

    # Step 3: Full SHA-256 verification
    duplicates: Dict[str, List[str]] = defaultdict(list)
    for (size, _), paths in second_stage.items():
        full_hash_map: Dict[str, List[str]] = defaultdict(list)
        for path in paths:
            try:
                f_hash = get_full_hash(path)
                full_hash_map[f_hash].append(path)
            except (OSError, PermissionError):
                continue

        for f_hash, dupe_paths in full_hash_map.items():
            if len(dupe_paths) > 1:
                duplicates[f_hash] = dupe_paths

    # Calculate total redundant bytes
    wasted_bytes = 0
    for dupe_paths in duplicates.values():
        try:
            file_size = os.path.getsize(dupe_paths[0])
            wasted_bytes += file_size * (len(dupe_paths) - 1)
        except OSError:
            pass

    return duplicates, wasted_bytes


def run_tests() -> bool:
    """Automated integration test using isolated temporary directories and files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = os.path.join(tmpdir, "original.txt")
        file2 = os.path.join(tmpdir, "copy1.txt")
        file3 = os.path.join(tmpdir, "copy2.txt")
        file4 = os.path.join(tmpdir, "different.txt")

        content_a = b"Consistent deduplication payload for testing purposes." * 100
        content_b = b"Different file payload ensuring non-matching hashes." * 100

        with open(file1, "wb") as f:
            f.write(content_a)
        with open(file2, "wb") as f:
            f.write(content_a)
        with open(file3, "wb") as f:
            f.write(content_a)
        with open(file4, "wb") as f:
            f.write(content_b)

        dupes, wasted = scan_directory_for_duplicates(tmpdir)
        assert len(dupes) == 1, f"Expected 1 group of duplicates, found {len(dupes)}"
        key = list(dupes.keys())[0]
        assert len(dupes[key]) == 3, f"Expected 3 files in duplicate group, got {len(dupes[key])}"
        expected_wasted = len(content_a) * 2
        assert wasted == expected_wasted, f"Wasted bytes mismatch: expected {expected_wasted}, got {wasted}"

    print("All file deduplication test assertions passed successfully.")
    return True


def display_results(duplicates: Dict[str, List[str]], wasted_bytes: int) -> None:
    """Print formatted report of duplicate files."""
    if not duplicates:
        print("\nScan completed: No duplicate files found.")
        return

    print("\n" + "=" * 80)
    print("                     Duplicate File Analysis Report                           ")
    print("=" * 80)
    print(f"Total duplicate groups identified: {len(duplicates)}")
    print(f"Potential space reclaimable      : {format_bytes(wasted_bytes)} ({wasted_bytes:,} bytes)")
    print("-" * 80)

    for idx, (digest, files) in enumerate(duplicates.items(), 1):
        try:
            sz = os.path.getsize(files[0])
            sz_str = format_bytes(sz)
        except OSError:
            sz_str = "Unknown"

        print(f"\nGroup {idx} [SHA-256: {digest[:16]}...] (File size: {sz_str}, Count: {len(files)}):")
        for f_idx, fpath in enumerate(files, 1):
            tag = "[Reference]" if f_idx == 1 else "[Duplicate]"
            print(f"  {tag:<12} {fpath}")

    print("\n" + "=" * 80)


def main() -> None:
    """Interactive CLI for File Deduplication Checker."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    while True:
        print("\n==================================")
        print("   File Deduplication Checker     ")
        print("==================================")
        print("1. Scan directory for duplicate files")
        print("2. Run automated self-tests")
        print("3. Exit")

        choice = input("\nSelect an option (1-3): ").strip()
        if choice == "1":
            target = input("Enter path to scan directory (default: current directory): ").strip()
            if not target:
                target = "."

            if not os.path.isdir(target):
                print(f"Error: Directory '{target}' does not exist.")
                continue

            print(f"\nScanning '{os.path.abspath(target)}'...")
            dupes, wasted = scan_directory_for_duplicates(target)
            display_results(dupes, wasted)

        elif choice == "2":
            run_tests()

        elif choice == "3":
            print("Exiting File Deduplication Checker. Goodbye.")
            break
        else:
            print("Invalid selection. Please choose from 1 to 3.")


if __name__ == "__main__":
    main()
