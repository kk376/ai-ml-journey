"""
A simple quiz program that tests general Python knowledge.
"""

def load_questions():
    # questions
    questions = [
        {
            "question": "What is the correct file extension for Python files?",
            "options": ["a) .pyt", "b) .pt", "c) .py", "d) .python"],
            "answer": "c"
        },
        {
            "question": "Which keyword is used to define a function in Python?",
            "options": ["a) func", "b) def", "c) define", "d) function"],
            "answer": "b"
        },
        {
            "question": "What built-in data structure uses curly braces {} with key-value pairs?",
            "options": ["a) List", "b) Tuple", "c) Set", "d) Dictionary"],
            "answer": "d"
        },
        {
            "question": "Which operator is used for exponentiation (power) in Python?",
            "options": ["a) ^", "b) **", "c) *", "d) //"],
            "answer": "b"
        },
        {
            "question": "How do you start a single-line comment in Python?",
            "options": ["a) //", "b) <!--", "c) #", "d) /*"],
            "answer": "c"
        },
        {
            "question": "Which of the following data types is immutable?",
            "options": ["a) List", "b) Dictionary", "c) Set", "d) Tuple"],
            "answer": "d"
        },
        {
            "question": "What function is used to get input from the user in Python?",
            "options": ["a) scan()", "b) read()", "c) input()", "d) get()"],
            "answer": "c"
        },
        {
            "question": "What does the range(3) function generate?",
            "options": ["a) 1, 2, 3", "b) 0, 1, 2", "c) 0, 1, 2, 3", "d) 1, 2"],
            "answer": "b"
        },
        {
            "question": "Which method adds an element to the end of a list?",
            "options": ["a) append()", "b) add()", "c) insert()", "d) push()"],
            "answer": "a"
        },
        {
            "question": "What will bool(0) evaluate to in Python?",
            "options": ["a) True", "b) False", "c) None", "d) Error"],
            "answer": "b"
        }
    ]
    return questions


def print_header():
    print("=" * 50)
    print("         WELCOME TO THE PYTHON QUIZ APP")
    print("=" * 50)
    print("Answer each question by choosing a, b, c, or d.\n")


def ask_question(index, item):
    print(f"Question {index}: {item['question']}")
    for opt in item['options']:
        print(f"  {opt}")
    
    # keep asking until we get a/b/c/d
    valid_choices = ["a", "b", "c", "d"]
    user_choice = ""
    while user_choice not in valid_choices:
        user_choice = input("Your answer (a/b/c/d): ").lower().strip()
        if user_choice not in valid_choices:
            print("Invalid input. Please enter a, b, c, or d.")
    
    return user_choice


def evaluate_answer(user_choice, correct_choice):
    if user_choice == correct_choice:
        print("Correct!\n")
        return True
    else:
        print(f"Wrong answer. The correct answer was: {correct_choice.upper()}\n")
        return False


def get_performance_remark(percentage):
    # pick a remark based on how they did
    if percentage >= 90:
        return "Outstanding achievement!"
    elif percentage >= 75:
        return "Great job! Solid understanding."
    elif percentage >= 50:
        return "Good effort, but there's room for improvement."
    else:
        return "Keep practicing. You'll get better!"


def show_final_score(score, total):
    percentage = (score / total) * 100
    remark = get_performance_remark(percentage)

    print("=" * 50)
    print("                 QUIZ RESULTS")
    print("=" * 50)
    print(f"Total Questions : {total}")
    print(f"Correct Answers : {score}")
    print(f"Your Score      : {score}/{total}")
    print(f"Percentage      : {percentage:.2f}%")
    print(f"Remark          : {remark}")
    print("=" * 50)


def run_quiz():
    print_header()
    questions = load_questions()
    score = 0
    total = len(questions)

    for i in range(total):
        item = questions[i]
        choice = ask_question(i + 1, item)
        if evaluate_answer(choice, item["answer"]):
            score += 1

    show_final_score(score, total)


if __name__ == "__main__":
    try:
        run_quiz()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")
