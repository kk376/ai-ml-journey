"""Student Grade Manager - collects marks, calculates grades, prints reports."""

def calculate_grade(percentage):
    # Discrete 10-point percentage threshold tier mapping
    if percentage >= 90:
        return "A"
    elif percentage >= 80:
        return "B"
    elif percentage >= 70:
        return "C"
    elif percentage >= 60:
        return "D"
    else:
        return "F"


def get_subject_marks():
    # Fixed subject list matched with sequential input scores in parallel list
    subjects = ["Math", "Science", "English", "History", "Computer"]
    marks = []
    
    for subject in subjects:
        score = float(input(f"  Enter marks for {subject} (out of 100): "))
        marks.append(score)
        
    return subjects, marks


def collect_students():
    print("=" * 50)
    print("        STUDENT GRADE MANAGEMENT SYSTEM")
    print("=" * 50)
    
    num_students = int(input("Enter total number of students: "))
    students = []

    for i in range(num_students):
        print(f"\n--- Entering details for Student {i + 1} ---")
        name = input("Enter student name: ").strip()
        subjects, marks = get_subject_marks()

        # Compute aggregate metrics dynamically from subject count
        total_marks = 0.0
        for m in marks:
            total_marks += m

        num_subjects = len(marks)
        max_possible = num_subjects * 100.0
        percentage = (total_marks / max_possible) * 100
        average_marks = total_marks / num_subjects
        grade = calculate_grade(percentage)

        # Composite student schema containing both raw score lists and derived statistics
        student_record = {
            "name": name,
            "subjects": subjects,
            "marks": marks,
            "total": total_marks,
            "average": average_marks,
            "percentage": percentage,
            "grade": grade
        }
        students.append(student_record)

    return students


def print_report_card(student):
    print("\n" + "=" * 45)
    print(f"           REPORT CARD: {student['name'].upper()}")
    print("=" * 45)
    # Left-aligned fixed width formatting (<15, <10) for tabular columnar output
    print(f"{'Subject':<15}{'Marks':<10}")
    print("-" * 45)

    for i in range(len(student['subjects'])):
        subj = student['subjects'][i]
        score = student['marks'][i]
        print(f"{subj:<15}{score:<10.1f}")

    print("-" * 45)
    print(f"Total Marks : {student['total']:.1f} / 500")
    print(f"Average     : {student['average']:.2f}")
    print(f"Percentage  : {student['percentage']:.2f}%")
    print(f"Final Grade : {student['grade']}")
    print("=" * 45)


def show_class_summary(students):
    # Guard against ZeroDivisionError on empty class records
    if len(students) == 0:
        print("\nNo student records available.")
        return

    for student in students:
        print_report_card(student)

    # O(N) single-pass accumulation of class percentage and linear scan for peak performer
    class_total_percentage = 0.0
    topper = students[0]

    for student in students:
        class_total_percentage += student['percentage']
        if student['percentage'] > topper['percentage']:
            topper = student

    class_average = class_total_percentage / len(students)

    print("\n" + "*" * 50)
    print("              CLASS SUMMARY REPORT")
    print("*" * 50)
    print(f"Total Students Processed : {len(students)}")
    print(f"Class Average Percentage : {class_average:.2f}%")
    print(f"Class Topper             : {topper['name']} ({topper['percentage']:.2f}%, Grade {topper['grade']})")
    print("*" * 50)


def main():
    students_list = collect_students()
    show_class_summary(students_list)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[Exited by user]")

