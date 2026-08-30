"""
Rock Paper Scissors Game
"""

import random

def get_total_rounds():
    while True:
        rounds_input = input("How many rounds would you like to play? ").strip()
        # need a positive int
        if rounds_input.isdigit():
            num_rounds = int(rounds_input)
            if num_rounds > 0:
                return num_rounds
            else:
                print("Please enter a number greater than 0.")
        else:
            print("Invalid input. Please enter a valid number.")


def get_user_choice():
    valid_choices = ["rock", "paper", "scissors"]

    while True:
        choice = (
            input("Enter your choice (rock, paper, or scissors): ")
            .strip()
            .lower()
        )
        if choice in valid_choices:
            return choice
        print("Invalid move. Please choose rock, paper, or scissors.")


def get_computer_choice():
    moves = ["rock", "paper", "scissors"]
    return random.choice(moves)


def determine_round_winner(user_move, comp_move):
    if user_move == comp_move:
        return "tie"

    # player wins these matchups
    if (
        (user_move == "rock" and comp_move == "scissors")
        or (user_move == "paper" and comp_move == "rock")
        or (user_move == "scissors" and comp_move == "paper")
    ):
        return "player"
    else:
        return "computer"


def print_round_result(round_num, user_move, comp_move, winner):
    print(f"\n--- Round {round_num} ---")
    print(f"You chose     : {user_move.capitalize()}")
    print(f"Computer chose: {comp_move.capitalize()}")

    if winner == "tie":
        print("Result: It's a tie!")
    elif winner == "player":
        print("Result: You win this round!")
    else:
        print("Result: Computer wins this round!")


def print_final_scoreboard(player_wins, computer_wins, ties):
    print("\n" + "=" * 40)
    print("           FINAL SCOREBOARD")
    print("=" * 40)
    print(f"Player Wins   : {player_wins}")
    print(f"Computer Wins : {computer_wins}")
    print(f"Ties          : {ties}")
    print("-" * 40)

    if player_wins > computer_wins:
        print("OVERALL WINNER: Congratulations! You won the game!")
    elif computer_wins > player_wins:
        print("OVERALL WINNER: The computer won the game. Better luck next time!")
    else:
        print("OVERALL RESULT: The match ended in a draw!")

    print("=" * 40 + "\n")


def play_match():
    print("\nStarting a new match...")
    total_rounds = get_total_rounds()

    player_wins = 0
    computer_wins = 0
    ties = 0

    for current_round in range(1, total_rounds + 1):
        print(f"\n--- Round {current_round} of {total_rounds} ---")
        user_move = get_user_choice()
        comp_move = get_computer_choice()

        winner = determine_round_winner(user_move, comp_move)
        print_round_result(current_round, user_move, comp_move, winner)

        if winner == "player":
            player_wins += 1
        elif winner == "computer":
            computer_wins += 1
        else:
            ties += 1

        print(
            f"Current Score -> Player: {player_wins} | Computer: {computer_wins} | Ties: {ties}"
        )

    print_final_scoreboard(player_wins, computer_wins, ties)


def main():
    print("=" * 40)
    print("     ROCK PAPER SCISSORS GAME")
    print("=" * 40)

    while True:
        play_match()

        again = input("Do you want to play another match? (y/n): ").strip().lower()
        if again != "y" and again != "yes":
            print("\nThanks for playing Rock Paper Scissors! Goodbye!")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
