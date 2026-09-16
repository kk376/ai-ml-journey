"""Flashcard Study Tool: Interactive quiz tool using Sets for spaced mastery tracking and JSON persistence."""

import json
import os
import random

FLASHCARDS_FILE = "flashcards.json"

DEFAULT_FLASHCARDS = [
    {
        "id": 1,
        "question": "What is the difference between a list and a tuple in Python?",
        "answer": "Lists are mutable (can be changed); tuples are immutable (cannot be changed after creation).",
        "category": "Data Structures",
    },
    {
        "id": 2,
        "question": "What mathematical property characterizes Python Sets?",
        "answer": "Sets contain only unique elements, are unordered, and support set operations like union and intersection.",
        "category": "Data Structures",
    },
    {
        "id": 3,
        "question": "Which keyword is used to handle exceptions in Python?",
        "answer": "try / except / else / finally blocks.",
        "category": "Exception Handling",
    },
    {
        "id": 4,
        "question": "Why is the 'with' statement recommended for file handling?",
        "answer": "It acts as a context manager that guarantees the file is properly closed even if exceptions occur.",
        "category": "File Handling",
    },
    {
        "id": 5,
        "question": "What is the purpose of the __init__ method in a Python class?",
        "answer": "It is the constructor method called automatically when an instance of the class is initialized.",
        "category": "OOP",
    },
    {
        "id": 6,
        "question": "What does the dictionary method .get(key, default) do?",
        "answer": "Retrieves the value for key if present; otherwise returns the default value without raising KeyError.",
        "category": "Data Structures",
    },
]


def load_flashcards(filepath=FLASHCARDS_FILE):
    """Load cards from JSON file, falling back to defaults if not found."""
    if not os.path.exists(filepath):
        save_flashcards(DEFAULT_FLASHCARDS, filepath)
        return list(DEFAULT_FLASHCARDS)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                return data
            return list(DEFAULT_FLASHCARDS)
    except (json.JSONDecodeError, OSError) as error:
        print(f"[Warning] Failed loading flashcards: {error}. Using defaults.")
        return list(DEFAULT_FLASHCARDS)


def save_flashcards(cards, filepath=FLASHCARDS_FILE):
    """Save flashcard list to JSON file."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(cards, f, indent=4)
        return True
    except OSError as error:
        print(f"[Error] Failed to save flashcards: {error}")
        return False


def run_quiz_session(cards, review_filter_ids=None):
    """Run interactive study session and track mastery using Python sets."""
    pool = cards
    if review_filter_ids is not None:
        pool = [c for c in cards if c["id"] in review_filter_ids]

    if not pool:
        print("\nNo cards available for this session.")
        return set(), set()

    deck = list(pool)
    random.shuffle(deck)

    mastered_ids = set()
    review_ids = set()

    print("\n" + "=" * 60)
    print(f"STARTING STUDY SESSION ({len(deck)} Flashcards)")
    print("Type 'q' during any prompt to end session early.")
    print("=" * 60)

    for idx, card in enumerate(deck, start=1):
        print(f"\nCard {idx} of {len(deck)} [{card.get('category', 'General')}]")
        print(f"QUESTION: {card['question']}")
        action = input("Press [Enter] to reveal answer (or 'q' to stop): ").strip().lower()
        if action == "q":
            print("\nSession paused early.")
            break

        print(f"ANSWER  : {card['answer']}")
        print("-" * 60)
        feedback = input("Did you get it right? (y = Yes / n = Needs Practice): ").strip().lower()

        if feedback == "y":
            mastered_ids.add(card["id"])
            print("[Marked: Mastered]")
        else:
            review_ids.add(card["id"])
            print("[Marked: Needs Practice]")

    total_answered = len(mastered_ids) + len(review_ids)
    if total_answered > 0:
        accuracy = (len(mastered_ids) / total_answered) * 100
        print("\n" + "=" * 55)
        print("SESSION SUMMARY REPORT")
        print("=" * 55)
        print(f"Cards Studied        : {total_answered}")
        print(f"Mastered (Set Count) : {len(mastered_ids)}")
        print(f"Review (Set Count)   : {len(review_ids)}")
        print(f"Mastery Score        : {accuracy:.1f}%")
        print("=" * 55 + "\n")

    return mastered_ids, review_ids


def add_flashcard(cards):
    """Add a new custom flashcard with unique ID."""
    print("\n=== Add New Flashcard ===")
    question = input("Enter question / term: ").strip()
    if not question:
        print("Question cannot be empty.")
        return

    answer = input("Enter answer / definition: ").strip()
    if not answer:
        print("Answer cannot be empty.")
        return

    category = input("Enter category (e.g. Python, Linux, Math, default 'General'): ").strip()
    if not category:
        category = "General"

    next_id = max((c.get("id", 0) for c in cards), default=0) + 1
    new_card = {
        "id": next_id,
        "question": question,
        "answer": answer,
        "category": category,
    }

    cards.append(new_card)
    save_flashcards(cards)
    print(f"\n[Success] Added Card #{next_id} to category '{category}'.")


def view_all_cards(cards):
    """Display all flashcards grouped by category."""
    if not cards:
        print("\nNo flashcards found.")
        return

    categories = set(c.get("category", "General") for c in cards)

    print("\n" + "=" * 70)
    print(f"FLASHCARD REPOSITORY ({len(cards)} cards across {len(categories)} categories)")
    print("=" * 70)

    for cat in sorted(categories):
        print(f"\nCATEGORY: {cat.upper()}")
        cat_cards = [c for c in cards if c.get("category", "General") == cat]
        for c in cat_cards:
            print(f"  #{c['id']:<2} Q: {c['question']}")
            print(f"      A: {c['answer']}")

    print("=" * 70 + "\n")


def delete_flashcard(cards):
    """Delete a flashcard by ID."""
    print("\n=== Delete Flashcard ===")
    id_str = input("Enter card ID to delete: ").strip()
    if not id_str.isdigit():
        print("Invalid ID.")
        return
    card_id = int(id_str)

    for i, c in enumerate(cards):
        if c.get("id") == card_id:
            removed = cards.pop(i)
            save_flashcards(cards)
            print(f"\n[Success] Removed card #{card_id}: '{removed['question']}'")
            return

    print(f"Card #{card_id} not found.")


def main():
    cards = load_flashcards()
    active_review_set = set()

    while True:
        print("=" * 45)
        print("       FLASHCARD STUDY TOOLKIT")
        print("=" * 45)
        print("1. Start Full Study Session")
        print(f"2. Practice Weak Cards Only ({len(active_review_set)} in queue)")
        print("3. View All Flashcards")
        print("4. Add New Flashcard")
        print("5. Delete Flashcard")
        print("6. Reset to Default Starter Deck")
        print("7. Exit")
        print("=" * 45)

        choice = input("Select option (1-7): ").strip()

        if choice == "1":
            mastered, needs_review = run_quiz_session(cards)
            # Update active review set using set union and difference
            active_review_set.update(needs_review)
            active_review_set.difference_update(mastered)
        elif choice == "2":
            if not active_review_set:
                print("\nGreat work! Your weak cards queue is currently empty. Run a full session first.")
            else:
                mastered, needs_review = run_quiz_session(cards, review_filter_ids=active_review_set)
                active_review_set.update(needs_review)
                active_review_set.difference_update(mastered)
        elif choice == "3":
            view_all_cards(cards)
        elif choice == "4":
            add_flashcard(cards)
        elif choice == "5":
            delete_flashcard(cards)
        elif choice == "6":
            confirm = input("Reset deck back to default starter cards? (y/n): ").strip().lower()
            if confirm == "y":
                cards = list(DEFAULT_FLASHCARDS)
                save_flashcards(cards)
                active_review_set.clear()
                print("\n[Success] Deck reset to default cards.")
        elif choice == "7":
            print("\nExiting Flashcard Study Toolkit. Happy learning!")
            save_flashcards(cards)
            break
        else:
            print("\nInvalid selection. Please choose 1 to 7.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
