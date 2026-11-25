# UoPeople GPA & Study Tracker (Serverless AWS)

A serverless GPA and study-hour tracker built with **Python**, **AWS Lambda**, **Amazon DynamoDB**, and **Amazon S3**, designed to store course records, compute cumulative or term-filtered GPAs, and export JSON summary reports to S3.

## Architecture Overview

- **Compute (AWS Lambda):** `uopeople-gpa-tracker-api` (`eu-north-1`) handles `add_course` and `summary` actions, calculates weighted GPA on a 4.00 scale, aggregates study hours and credits, and writes summary reports to S3.
- **Database (Amazon DynamoDB):** Table `uopeople-gpa-tracker` using `student_id` as the Partition Key (PK) and `course_key` (`<term>#<course_name>`) as the Sort Key (SK).
- **Object Storage (Amazon S3):** Bucket `uopeople-gpa-reports-230372368557` stores generated reports under `reports/<student_id>/<scope>.json` (for example, `Cumulative.json` or a specific term).
- **Version Control (GitHub):** Source code managed in `PastorTee311/uopeople-gpa-tracker`.

## DynamoDB Data Model

| Attribute | Type | Role | Example |
| :--- | :--- | :--- | :--- |
| `student_id` | String | Partition Key (PK) | `student-001` |
| `course_key` | String | Sort Key (SK) | `2026-T1#CS 1101` |
| `term` | String | Academic term | `2026-T1` |
| `course_name` | String | Course title/code | `CS 1101` |
| `credits` | Number | Course credit weight | `3` |
| `grade` | String | Letter grade (`A` to `F`) | `A` |
| `study_hours` | Number | Logged study hours | `5` |

## Example Payloads

### 1. Add a Course
```json
{
  "action": "add_course",
  "student_id": "student-001",
  "term": "2026-T1",
  "course_name": "CS 1101",
  "credits": 3,
  "grade": "A",
  "study_hours": 5
}
```json
{
  "action": "summary",
  "student_id": "student-001"
}
{
  "action": "summary",
  "student_id": "student-001",
  "term": "2026-T1"
}
uopeople-gpa-tracker/
├── lambda_function.py
└── README.md
