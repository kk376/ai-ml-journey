"""Sudoku Validator and Solver: Backtracking constraint satisfaction engine.

Validates 9x9 Sudoku grids according to standard rules and solves puzzles
using recursive backtracking with Minimum Remaining Values (MRV) candidate pruning.
"""

import copy
import sys
from typing import List, Optional, Set, Tuple


Board = List[List[int]]

# Sample test puzzles (0 denotes empty cell)
SAMPLE_PUZZLE_EASY: Board = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

SAMPLE_PUZZLE_HARD: Board = [
    [0, 0, 0, 6, 0, 0, 4, 0, 0],
    [7, 0, 0, 0, 0, 3, 6, 0, 0],
    [0, 0, 0, 0, 9, 1, 0, 8, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 5, 0, 1, 8, 0, 0, 0, 3],
    [0, 0, 0, 3, 0, 6, 0, 4, 5],
    [0, 4, 0, 2, 0, 0, 0, 6, 0],
    [9, 0, 3, 0, 0, 0, 0, 0, 0],
    [0, 2, 0, 0, 0, 0, 1, 0, 0],
]


def format_board(board: Board) -> str:
    """Format 9x9 board into a clean ASCII grid with 3x3 block dividers."""
    lines = []
    divider = "+-------+-------+-------+"
    for r in range(9):
        if r % 3 == 0:
            lines.append(divider)
        row_str = "| "
        for c in range(9):
            val = str(board[r][c]) if board[r][c] != 0 else "."
            row_str += val + " "
            if (c + 1) % 3 == 0:
                row_str += "| "
        lines.append(row_str)
    lines.append(divider)
    return "\n".join(lines)


def is_valid_placement(board: Board, row: int, col: int, num: int) -> bool:
    """Check if placing 'num' at (row, col) respects Sudoku rules."""
    # Check row
    for c in range(9):
        if c != col and board[row][c] == num:
            return False

    # Check column
    for r in range(9):
        if r != row and board[r][col] == num:
            return False

    # Check 3x3 subgrid box
    box_r = (row // 3) * 3
    box_c = (col // 3) * 3
    for r in range(box_r, box_r + 3):
        for c in range(box_c, box_c + 3):
            if (r != row or c != col) and board[r][c] == num:
                return False

    return True


def validate_board(board: Board) -> Tuple[bool, str]:
    """Validate entire board state for duplicate conflicts."""
    for r in range(9):
        for c in range(9):
            num = board[r][c]
            if num != 0:
                if num < 1 or num > 9:
                    return False, f"Invalid value {num} at ({r + 1}, {c + 1}). Values must be 1 to 9."
                if not is_valid_placement(board, r, c, num):
                    return False, f"Conflict detected for value {num} at row {r + 1}, col {c + 1}."
    return True, "Board state is valid."


def get_candidates(board: Board, row: int, col: int) -> Set[int]:
    """Determine set of valid numbers that can be placed at (row, col)."""
    candidates = set(range(1, 10))
    # Eliminate row and column neighbors
    for i in range(9):
        candidates.discard(board[row][i])
        candidates.discard(board[i][col])

    # Eliminate box neighbors
    box_r = (row // 3) * 3
    box_c = (col // 3) * 3
    for r in range(box_r, box_r + 3):
        for c in range(box_c, box_c + 3):
            candidates.discard(board[r][c])

    return candidates


def find_mrv_cell(board: Board) -> Optional[Tuple[int, int, Set[int]]]:
    """Find empty cell with Minimum Remaining Values (fewest candidates)."""
    best_cell = None
    min_candidates = 10

    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                cands = get_candidates(board, r, c)
                if len(cands) < min_candidates:
                    min_candidates = len(cands)
                    best_cell = (r, c, cands)
                    if min_candidates == 1:
                        return best_cell  # Cannot get fewer than 1 candidate

    return best_cell


def solve_sudoku(board: Board) -> Tuple[bool, int]:
    """Solve Sudoku puzzle in-place using MRV-directed recursive backtracking.

    Returns (is_solved, step_counter).
    """
    steps = [0]

    def backtrack() -> bool:
        steps[0] += 1
        mrv = find_mrv_cell(board)
        if mrv is None:
            return True  # All cells filled successfully

        r, c, candidates = mrv
        if not candidates:
            return False  # Dead end

        for num in candidates:
            board[r][c] = num
            if backtrack():
                return True
            board[r][c] = 0

        return False

    solved = backtrack()
    return solved, steps[0]


def run_tests() -> bool:
    """Automated tests validating solver correctness and detection of invalid boards."""
    # Test valid solver on Easy puzzle
    board = copy.deepcopy(SAMPLE_PUZZLE_EASY)
    is_valid, _ = validate_board(board)
    assert is_valid, "Initial sample puzzle must be valid"

    solved, steps = solve_sudoku(board)
    assert solved, "Solver failed to find solution for easy puzzle"
    is_valid, msg = validate_board(board)
    assert is_valid, f"Solved board failed validation: {msg}"
    assert all(board[r][c] != 0 for r in range(9) for c in range(9)), "Board contains empty cells"

    # Test invalid board detection (row conflict)
    conflict_board = copy.deepcopy(SAMPLE_PUZZLE_EASY)
    conflict_board[0][2] = 5  # Duplicate 5 in row 0
    is_valid, _ = validate_board(conflict_board)
    assert not is_valid, "Validator should have flagged row conflict"

    print("All Sudoku validator and solver test assertions passed successfully.")
    return True


def main() -> None:
    """CLI menu for Sudoku Validator and Solver."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    while True:
        print("\n================================")
        print("   Sudoku Validator and Solver  ")
        print("================================")
        print("1. Solve Sample Easy Puzzle")
        print("2. Solve Sample Hard Puzzle")
        print("3. Validate and Solve Custom Puzzle")
        print("4. Run Automated Self-Tests")
        print("5. Exit")

        choice = input("\nSelect an option (1-5): ").strip()
        if choice in ("1", "2"):
            target = copy.deepcopy(SAMPLE_PUZZLE_EASY if choice == "1" else SAMPLE_PUZZLE_HARD)
            print("\nInitial Puzzle:")
            print(format_board(target))

            is_valid, msg = validate_board(target)
            if not is_valid:
                print(f"Validation Error: {msg}")
                continue

            print("\nSolving using MRV Backtracking...")
            solved, steps = solve_sudoku(target)
            if solved:
                print(f"Solution Found in {steps} steps:")
                print(format_board(target))
            else:
                print("No solution exists for this configuration.")

        elif choice == "3":
            print("\nEnter 9 lines of 9 numbers (0 for empty cells), or 'back' to cancel:")
            custom: Board = []
            abort = False
            for i in range(9):
                row_raw = input(f"Row {i + 1}: ").strip().replace(" ", "")
                if row_raw.lower() == "back":
                    abort = True
                    break
                if len(row_raw) != 9 or not row_raw.isdigit():
                    print("Error: Row must be exactly 9 digits (0-9). Aborting.")
                    abort = True
                    break
                custom.append([int(d) for d in row_raw])

            if abort:
                continue

            print("\nInput Board:")
            print(format_board(custom))
            is_valid, msg = validate_board(custom)
            if not is_valid:
                print(f"Validation Error: {msg}")
                continue

            solved, steps = solve_sudoku(custom)
            if solved:
                print(f"\nSolved in {steps} steps:")
                print(format_board(custom))
            else:
                print("No solution exists.")

        elif choice == "4":
            run_tests()

        elif choice == "5":
            print("Exiting Sudoku Solver. Goodbye.")
            break
        else:
            print("Invalid option. Please choose from 1 to 5.")


if __name__ == "__main__":
    main()
