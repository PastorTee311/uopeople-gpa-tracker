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


def add_course(courses: list[dict], term: str, course_name: str, credits: float, grade: str) -> list[dict]:
    clean_grade = grade.strip().upper()
    if clean_grade not in GRADE_POINTS:
        raise ValueError(f"Invalid grade '{grade}'. Valid grades: {', '.join(GRADE_POINTS)}")
    if credits <= 0:
        raise ValueError("Credits must be greater than 0.")

    course = {
        "term": term.strip(),
        "course_name": course_name.strip(),
        "credits": float(credits),
        "grade": clean_grade,
    }
    courses.append(course)
    return courses


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
    return {
        "scope": term if term else "Cumulative",
        "courses_count": len(filtered),
        "total_credits": total_credits,
        "gpa": gpa,
    }


if __name__ == "__main__":
    courses = load_courses()

    if not courses:
        add_course(courses, "2026-T1", "CS 1101 - Programming Fundamentals", 3, "A")
        add_course(courses, "2026-T1", "UNIV 1001 - Online Education Strategies", 3, "A-")
        add_course(courses, "2026-T2", "CS 1102 - Programming 1", 3, "B+")
        save_courses(courses)

    print("Term 2026-T1:", gpa_summary(courses, "2026-T1"))
    print("Cumulative:  ", gpa_summary(courses))
    print(f"Saved {len(courses)} courses to {DATA_FILE}")
