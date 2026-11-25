GRADE_POINTS = {
    "A": 4.00,
    "A-": 3.67,
    "B+": 3.33,
    "B": 3.00,
    "B-": 2.67,
    "C+": 2.33,
    "C": 2.00,
    "C-": 1.67,
    "D+": 1.33,
    "D": 1.00,
    "F": 0.00,
}


def calculate_gpa(courses):
    """Calculate weighted GPA from a list of (course_name, credits, grade) tuples."""
    total_points = 0.0
    total_credits = 0.0

    for course_name, credits, grade in courses:
        clean_grade = grade.strip().upper()
        if clean_grade not in GRADE_POINTS:
            raise ValueError(f"Unknown grade '{grade}' for {course_name}")
        total_points += GRADE_POINTS[clean_grade] * credits
        total_credits += credits

    if total_credits == 0:
        return 0.00

    return round(total_points / total_credits, 2)


if __name__ == "__main__":
    sample_courses = [
        ("CS 1101 - Programming Fundamentals", 3, "A"),
        ("CS 1102 - Programming 1", 3, "A-"),
        ("MATH 1201 - College Algebra", 3, "B+"),
    ]
    gpa = calculate_gpa(sample_courses)
    print(f"Sample UoPeople GPA: {gpa:.2f}")
