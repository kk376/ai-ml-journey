"""Typing Speed Tester: Terminal-based typing speed and accuracy evaluator.

Measures Gross WPM, Net WPM, Accuracy percentage, and Character Error Rate
with randomized test prompts and automated verification.
"""

import random
import sys
import time
from typing import Dict, List, Tuple


TEST_PROMPTS: List[Dict[str, str]] = [
    {
        "category": "Standard English",
        "text": "The quick brown fox jumps over the lazy dog near the riverbank on a warm sunny afternoon.",
    },
    {
        "category": "Technology and Architecture",
        "text": "Distributed systems require careful coordination between consensus protocols and persistent storage engines.",
    },
    {
        "category": "Programming and Algorithms",
        "text": "Binary search trees maintain sorted order to achieve logarithmic search and insertion performance.",
    },
    {
        "category": "Science and Engineering",
        "text": "Theoretical physics explores the mathematical structure of space and time across cosmological scales.",
    },
    {
        "category": "Short Reflex",
        "text": "Practice makes permanent when discipline guides every deliberate keystroke.",
    },
]


def calculate_metrics(target_text: str, typed_text: str, elapsed_seconds: float) -> Dict[str, float]:
    """Compute WPM, CPM, accuracy, and error counts.

    Gross WPM is defined as (total typed characters / 5) / (time in minutes).
    Net WPM deducts errors from gross word count.
    Accuracy is (correct characters / max(target len, typed len)) * 100.
    """
    if elapsed_seconds <= 0:
        elapsed_seconds = 0.001

    minutes = elapsed_seconds / 60.0
    typed_len = len(typed_text)
    target_len = len(target_text)

    # Character-level matching
    min_len = min(target_len, typed_len)
    correct_chars = sum(1 for i in range(min_len) if target_text[i] == typed_text[i])
    char_errors = abs(target_len - typed_len) + sum(1 for i in range(min_len) if target_text[i] != typed_text[i])

    # Word-level comparison
    target_words = target_text.split()
    typed_words = typed_text.split()
    min_words = min(len(target_words), len(typed_words))
    word_errors = sum(1 for i in range(min_words) if target_words[i] != typed_words[i])
    word_errors += abs(len(target_words) - len(typed_words))

    # WPM standards (1 word = 5 keystrokes standard)
    gross_wpm = (typed_len / 5.0) / minutes if minutes > 0 else 0.0
    net_wpm = max(0.0, ((typed_len / 5.0) - word_errors) / minutes)
    cpm = typed_len / minutes if minutes > 0 else 0.0

    eval_base = max(target_len, typed_len)
    accuracy = (correct_chars / eval_base * 100.0) if eval_base > 0 else 100.0

    return {
        "elapsed_seconds": elapsed_seconds,
        "typed_chars": float(typed_len),
        "target_chars": float(target_len),
        "correct_chars": float(correct_chars),
        "char_errors": float(char_errors),
        "word_errors": float(word_errors),
        "gross_wpm": round(gross_wpm, 2),
        "net_wpm": round(net_wpm, 2),
        "cpm": round(cpm, 2),
        "accuracy": round(accuracy, 2),
    }


def analyze_errors(target_text: str, typed_text: str) -> List[Tuple[str, str, str]]:
    """Produce detailed word-level comparison highlighting differences."""
    target_words = target_text.split()
    typed_words = typed_text.split()
    results = []

    max_len = max(len(target_words), len(typed_words))
    for i in range(max_len):
        tgt = target_words[i] if i < len(target_words) else "<omitted>"
        typ = typed_words[i] if i < len(typed_words) else "<missing>"
        status = "Match" if tgt == typ else "Mismatch"
        results.append((tgt, typ, status))
    return results


def run_tests() -> bool:
    """Automated unit tests for typing speed calculation metrics."""
    # Perfect typing test
    sample = "Hello world from Python test."
    metrics = calculate_metrics(sample, sample, 12.0)
    assert metrics["accuracy"] == 100.0, f"Expected 100% accuracy, got {metrics['accuracy']}"
    assert metrics["word_errors"] == 0.0, "Expected 0 word errors"
    assert metrics["net_wpm"] == metrics["gross_wpm"], "Net and gross WPM should match on zero errors"

    # Typing with 1 word mistake
    mistyped = "Hello world from Python rust."
    metrics_err = calculate_metrics(sample, mistyped, 12.0)
    assert metrics_err["accuracy"] < 100.0, "Accuracy should be under 100%"
    assert metrics_err["word_errors"] == 1.0, f"Expected 1 word error, got {metrics_err['word_errors']}"
    assert metrics_err["net_wpm"] < metrics_err["gross_wpm"], "Net WPM must be lower than gross on errors"

    print("All typing speed tester test assertions passed successfully.")
    return True


def display_results(metrics: Dict[str, float]) -> None:
    """Format and print test performance report."""
    print("\n" + "=" * 45)
    print("           Typing Performance Scorecard       ")
    print("=" * 45)
    print(f"Time Taken       : {metrics['elapsed_seconds']:.2f} seconds")
    print(f"Gross Speed      : {metrics['gross_wpm']} WPM")
    print(f"Net Speed        : {metrics['net_wpm']} WPM")
    print(f"Characters / Min : {metrics['cpm']} CPM")
    print(f"Accuracy         : {metrics['accuracy']}%")
    print(f"Character Errors : {int(metrics['char_errors'])}")
    print(f"Word Errors      : {int(metrics['word_errors'])}")
    print("=" * 45)


def run_interactive_test(category: str, text: str) -> None:
    """Run an interactive typing test session for the user."""
    print(f"\nCategory: {category}")
    print("\nPrompt text to type:")
    print("-" * 70)
    print(text)
    print("-" * 70)

    input("\nPress Enter when ready to start typing...")
    print("\n[Timer Started] Type the text and press Enter when finished:\n")

    start_time = time.perf_counter()
    user_input = input()
    end_time = time.perf_counter()

    elapsed = end_time - start_time
    metrics = calculate_metrics(text, user_input, elapsed)
    display_results(metrics)

    show_breakdown = input("\nView detailed word breakdown? (y/n): ").strip().lower()
    if show_breakdown == "y":
        breakdown = analyze_errors(text, user_input)
        print("\n" + "-" * 60)
        print(f"{'Target Word':<20} | {'Typed Word':<20} | Status")
        print("-" * 60)
        for tgt, typ, status in breakdown:
            print(f"{tgt:<20} | {typ:<20} | {status}")
        print("-" * 60)


def main() -> None:
    """CLI menu for Typing Speed Tester."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    while True:
        print("\n==============================")
        print("     Typing Speed Tester      ")
        print("==============================")
        print("1. Random Typing Test")
        print("2. Select Prompt Category")
        print("3. Custom Text Test")
        print("4. Run Automated Self-Tests")
        print("5. Exit")

        choice = input("\nSelect an option (1-5): ").strip()
        if choice == "1":
            selected = random.choice(TEST_PROMPTS)
            run_interactive_test(selected["category"], selected["text"])

        elif choice == "2":
            print("\nAvailable Categories:")
            for idx, p in enumerate(TEST_PROMPTS, 1):
                print(f"  {idx}. {p['category']}")
            sub_choice = input(f"Select category (1-{len(TEST_PROMPTS)}): ").strip()
            if sub_choice.isdigit() and 1 <= int(sub_choice) <= len(TEST_PROMPTS):
                selected = TEST_PROMPTS[int(sub_choice) - 1]
                run_interactive_test(selected["category"], selected["text"])
            else:
                print("Invalid category selection.")

        elif choice == "3":
            custom = input("\nEnter custom text for test: ").strip()
            if len(custom) < 5:
                print("Text must be at least 5 characters long.")
                continue
            run_interactive_test("Custom Input", custom)

        elif choice == "4":
            run_tests()

        elif choice == "5":
            print("Exiting Typing Speed Tester. Keep practicing.")
            break
        else:
            print("Invalid choice. Please select from 1 to 5.")


if __name__ == "__main__":
    main()
