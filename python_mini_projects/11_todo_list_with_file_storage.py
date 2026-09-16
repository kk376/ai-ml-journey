"""Todo List with File Storage - persistent task manager with priority and status."""

import json
import os
from datetime import datetime

DATA_FILE = "tasks.json"


def load_tasks(filepath=DATA_FILE):
    """Load tasks from a JSON file. Return an empty list if file does not exist or is invalid."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            tasks = json.load(file)
            if isinstance(tasks, list):
                return tasks
            return []
    except (json.JSONDecodeError, OSError) as error:
        print(f"\n[Warning] Could not read '{filepath}': {error}. Starting with empty list.")
        return []


def save_tasks(tasks, filepath=DATA_FILE):
    """Save the tasks list to a JSON file safely."""
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(tasks, file, indent=4)
        return True
    except OSError as error:
        print(f"\n[Error] Failed to save tasks to '{filepath}': {error}")
        return False


def get_next_id(tasks):
    """Generate the next unique integer ID for a new task."""
    if not tasks:
        return 1
    return max(task.get("id", 0) for task in tasks) + 1


def add_task(tasks):
    """Prompt user to add a new task with description and priority."""
    print("\n=== Add New Task ===")
    title = input("Enter task title: ").strip()
    if not title:
        print("Task title cannot be empty.")
        return

    print("Select Priority:")
    print("  1. High")
    print("  2. Medium")
    print("  3. Low")
    p_choice = input("Enter choice (1-3, default 2): ").strip()
    priority_map = {"1": "High", "2": "Medium", "3": "Low"}
    priority = priority_map.get(p_choice, "Medium")

    category = input("Enter category (e.g. Work, Study, Personal, default 'General'): ").strip()
    if not category:
        category = "General"

    new_task = {
        "id": get_next_id(tasks),
        "title": title,
        "priority": priority,
        "category": category,
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "completed_at": None,
    }

    tasks.append(new_task)
    if save_tasks(tasks):
        print(f"\n[Success] Task #{new_task['id']} added: '{title}' [{priority} Priority]")


def display_tasks(tasks, filter_status=None):
    """Display tasks in a formatted table with optional completion filter."""
    filtered = tasks
    if filter_status is True:
        filtered = [t for t in tasks if t.get("completed")]
    elif filter_status is False:
        filtered = [t for t in tasks if not t.get("completed")]

    if not filtered:
        label = "completed " if filter_status is True else ("pending " if filter_status is False else "")
        print(f"\nNo {label}tasks found.")
        return

    print("\n" + "=" * 80)
    print(f"{'ID':<5} {'Status':<10} {'Priority':<10} {'Category':<12} {'Title':<28} {'Created At'}")
    print("=" * 80)

    for task in filtered:
        status_str = "[DONE]" if task.get("completed") else "[TODO]"
        t_id = task.get("id", 0)
        priority = task.get("priority", "Medium")
        category = task.get("category", "General")
        title = task.get("title", "")
        created_at = task.get("created_at", "")

        # Truncate title if too long for clean table layout
        if len(title) > 26:
            title = title[:23] + "..."

        print(f"{t_id:<5} {status_str:<10} {priority:<10} {category:<12} {title:<28} {created_at}")

    print("=" * 80)
    total = len(filtered)
    done_count = sum(1 for t in filtered if t.get("completed"))
    print(f"Total shown: {total} | Completed: {done_count} | Pending: {total - done_count}\n")


def mark_task_complete(tasks):
    """Mark a task as completed by ID."""
    print("\n=== Mark Task as Complete ===")
    id_input = input("Enter task ID to complete: ").strip()
    if not id_input.isdigit():
        print("Invalid ID. Please enter a number.")
        return

    task_id = int(id_input)
    for task in tasks:
        if task.get("id") == task_id:
            if task.get("completed"):
                print(f"Task #{task_id} is already marked as completed.")
                return
            task["completed"] = True
            task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if save_tasks(tasks):
                print(f"\n[Success] Task #{task_id} ('{task['title']}') marked as completed!")
            return

    print(f"Task with ID #{task_id} not found.")


def delete_task(tasks):
    """Remove a task by ID."""
    print("\n=== Delete Task ===")
    id_input = input("Enter task ID to delete: ").strip()
    if not id_input.isdigit():
        print("Invalid ID. Please enter a number.")
        return

    task_id = int(id_input)
    for index, task in enumerate(tasks):
        if task.get("id") == task_id:
            deleted = tasks.pop(index)
            if save_tasks(tasks):
                print(f"\n[Success] Deleted task #{task_id}: '{deleted.get('title')}'")
            return

    print(f"Task with ID #{task_id} not found.")


def clear_completed_tasks(tasks):
    """Remove all completed tasks in one operation."""
    initial_count = len(tasks)
    remaining = [t for t in tasks if not t.get("completed")]
    removed_count = initial_count - len(remaining)

    if removed_count == 0:
        print("\nNo completed tasks to clear.")
        return tasks

    confirm = input(f"Are you sure you want to delete {removed_count} completed task(s)? (y/n): ").strip().lower()
    if confirm == "y":
        if save_tasks(remaining):
            print(f"\n[Success] Cleared {removed_count} completed task(s).")
            return remaining
    else:
        print("\nClear operation cancelled.")
    return tasks


def main():
    tasks = load_tasks()

    while True:
        print("=" * 45)
        print("       TODO LIST MANAGER (PERSISTENT)")
        print("=" * 45)
        print("1. View All Tasks")
        print("2. View Pending Tasks")
        print("3. View Completed Tasks")
        print("4. Add New Task")
        print("5. Mark Task Complete")
        print("6. Delete Task")
        print("7. Clear All Completed Tasks")
        print("8. Exit")
        print("=" * 45)

        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            display_tasks(tasks)
        elif choice == "2":
            display_tasks(tasks, filter_status=False)
        elif choice == "3":
            display_tasks(tasks, filter_status=True)
        elif choice == "4":
            add_task(tasks)
        elif choice == "5":
            mark_task_complete(tasks)
        elif choice == "6":
            delete_task(tasks)
        elif choice == "7":
            tasks = clear_completed_tasks(tasks)
        elif choice == "8":
            print("\nSaving data. Goodbye!")
            save_tasks(tasks)
            break
        else:
            print("\nInvalid option. Please choose between 1 and 8.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
