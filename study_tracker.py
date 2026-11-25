import json
from pathlib import Path
from gpa_calculator import GRADE_POINTS, calculate_gpa

DATA_FILE = Path("courses_data.json")


def load_courses(filepath: Path = DATA_FILE) -> list[dict]:
    if not filepath.exists():
        return []
    with filepath.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_courses(courses: list[dict], filepath: Path = DATA_FILE) -> None:
    with filepath.open("w", encoding="utf-8") as f:
        json.dump(courses, f, indent=2)


def add_course(
    courses: list[dict],
    term: str,
    course_name: str,
    credits: float,
    grade: str,
    study_hours: float = 0.0,
) -> list[dict]:
    clean_grade = grade.strip().upper()
    if clean_grade not in GRADE_POINTS:
        raise ValueError(f"Invalid grade '{grade}'. Valid grades: {', '.join(GRADE_POINTS)}")
    if credits <= 0:
        raise ValueError("Credits must be greater than 0.")
    if study_hours < 0:
        raise ValueError("Study hours cannot be negative.")

    course = {
        "term": term.strip(),
        "course_name": course_name.strip(),
        "credits": float(credits),
        "grade": clean_grade,
        "study_hours": float(study_hours),
    }
    courses.append(course)
    return courses


def log_study_hours(courses: list[dict], course_name: str, hours: float) -> bool:
    if hours <= 0:
        raise ValueError("Logged hours must be greater than 0.")
    target = course_name.strip().lower()
    for course in courses:
        if course["course_name"].lower() == target:
            course["study_hours"] = round(course.get("study_hours", 0.0) + float(hours), 2)
            return True
    return False


def remove_course(courses: list[dict], course_name: str, term: str | None = None) -> list[dict]:
    target_name = course_name.strip().lower()
    target_term = term.strip().lower() if term else None

    return [
        c for c in courses
        if not (
            c["course_name"].lower() == target_name
            and (target_term is None or c["term"].lower() == target_term)
        )
    ]


def gpa_summary(courses: list[dict], term: str | None = None) -> dict:
    filtered = (
        [c for c in courses if c["term"].lower() == term.strip().lower()]
        if term
        else courses
    )
    tuples = [(c["course_name"], c["credits"], c["grade"]) for c in filtered]
    gpa = calculate_gpa(tuples)
    total_credits = sum(c["credits"] for c in filtered)
    total_hours = round(sum(c.get("study_hours", 0.0) for c in filtered), 2)
    return {
        "scope": term if term else "Cumulative",
        "courses_count": len(filtered),
        "total_credits": total_credits,
        "total_study_hours": total_hours,
        "gpa": gpa,
    }


def run_cli() -> None:
    courses = load_courses()

    while True:
        print("\n=== UoPeople Study & GPA Tracker ===")
        print("1. View GPA & Study Summary")
        print("2. Add a Course")
        print("3. Log Study Hours")
        print("4. List All Courses")
        print("5. Save & Exit")
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            term_input = input("Enter term (e.g., 2026-T1) or press Enter for Cumulative: ").strip()
            print(gpa_summary(courses, term_input if term_input else None))
        elif choice == "2":
            term = input("Term (e.g., 2026-T1): ").strip()
            name = input("Course name/code: ").strip()
            credits = float(input("Credits (e.g., 3): ").strip())
            grade = input("Grade (A, A-, B+, B, etc.): ").strip()
            hours = float(input("Initial study hours (0 if none): ").strip() or "0")
            add_course(courses, term, name, credits, grade, hours)
            save_courses(courses)
            print("Course added and saved.")
        elif choice == "3":
            name = input("Course name/code to log hours for: ").strip()
            hours = float(input("Hours studied: ").strip())
            if log_study_hours(courses, name, hours):
                save_courses(courses)
                print("Study hours updated and saved.")
            else:
                print("Course not found.")
        elif choice == "4":
            if not courses:
                print("No courses recorded yet.")
            for c in courses:
                print(
                    f"- [{c['term']}] {c['course_name']} | "
                    f"Credits: {c['credits']} | Grade: {c['grade']} | "
                    f"Study Hours: {c.get('study_hours', 0.0)}"
                )
        elif choice == "5":
            save_courses(courses)
            print("Progress saved. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    run_cli()
