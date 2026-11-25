import json
import os
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key

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

TABLE_NAME = os.environ.get("TABLE_NAME", "uopeople-gpa-tracker")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "uopeople-gpa-reports-230372368557")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
s3 = boto3.client("s3")


def calculate_gpa(items):
    total_points = 0.0
    total_credits = 0.0
    for item in items:
        grade = str(item.get("grade", "")).strip().upper()
        credits = float(item.get("credits", 0))
        if grade in GRADE_POINTS and credits > 0:
            total_points += GRADE_POINTS[grade] * credits
            total_credits += credits
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.00


def lambda_handler(event, context):
    action = event.get("action", "summary")
    student_id = event.get("student_id", "student-001")

    if action == "add_course":
        term = str(event["term"]).strip()
        course_name = str(event["course_name"]).strip()
        credits = Decimal(str(event["credits"]))
        grade = str(event["grade"]).strip().upper()
        study_hours = Decimal(str(event.get("study_hours", 0)))

        if grade not in GRADE_POINTS:
            return {"statusCode": 400, "body": json.dumps({"error": f"Invalid grade: {grade}"})}

        course_key = f"{term}#{course_name}"
        item = {
            "student_id": student_id,
            "course_key": course_key,
            "term": term,
            "course_name": course_name,
            "credits": credits,
            "grade": grade,
            "study_hours": study_hours,
        }
        table.put_item(Item=item)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Course saved to DynamoDB", "course_key": course_key}),
        }

    resp = table.query(KeyConditionExpression=Key("student_id").eq(student_id))
    items = resp.get("Items", [])
    term_filter = event.get("term")
    if term_filter:
        items = [i for i in items if str(i.get("term", "")).lower() == str(term_filter).strip().lower()]

    scope = term_filter if term_filter else "Cumulative"
    total_hours = round(sum(float(i.get("study_hours", 0)) for i in items), 2)
    total_credits = sum(float(i.get("credits", 0)) for i in items)

    summary_payload = {
        "student_id": student_id,
        "scope": scope,
        "courses_count": len(items),
        "total_credits": total_credits,
        "total_study_hours": total_hours,
        "gpa": calculate_gpa(items),
    }

    report_key = f"reports/{student_id}/{scope}.json"
    if event.get("export_to_s3", True):
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=report_key,
            Body=json.dumps(summary_payload, indent=2).encode("utf-8"),
            ContentType="application/json",
        )

    return {
        "statusCode": 200,
        "body": json.dumps({
            **summary_payload,
            "s3_report": f"s3://{BUCKET_NAME}/{report_key}",
        }),
    }
