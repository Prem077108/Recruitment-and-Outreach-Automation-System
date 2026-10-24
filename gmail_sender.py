from __future__ import annotations

import csv
import email
import os
import smtplib
import uuid
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
EMAIL_HISTORY_PATH = BASE_DIR / "email_sent_history.csv"


def _ensure_history_csv() -> None:
    if EMAIL_HISTORY_PATH.exists():
        return

    fieldnames = [
        "recruiter_name",
        "recruiter_email",
        "role",
        "post_url",
        "candidate",
        "email_sent_status",
        "timestamp",
        "subject",
        "message_id",
        "followup_count",
        "last_followup_at",
        "replied",
    ]
    with EMAIL_HISTORY_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()


def build_subject(role: str, candidate_name: str) -> str:
    return f"{candidate_name} | {role} opportunity with U.S. C2C focus"


def extract_keywords(job_description: str, limit: int = 6) -> list[str]:
    words = []
    for token in (job_description or "").replace("/", " ").replace("-", " ").split():
        cleaned = token.strip("()[]{}:,;.")
        if 4 <= len(cleaned) <= 18 and cleaned.isalpha():
            words.append(cleaned)
    seen = set()
    filtered = []
    for word in words:
        if word.lower() not in seen:
            filtered.append(word)
            seen.add(word.lower())
        if len(filtered) >= limit:
            break
    return filtered


def build_email_body(candidate_name: str, recruiter_name: str, role: str, job_description: str) -> str:
    keywords = ", ".join(extract_keywords(job_description)) or "Java, cloud, distributed systems"
    return (
        f"Hi {recruiter_name},\n\n"
        f"I hope you are doing well. I am reaching out about the {role} opportunity you recently posted. "
        f"Based on the JD, I believe my background aligns closely with the key requirements around {keywords}. "
        f"I would welcome the opportunity to discuss a contract engagement for this role and share a tailored resume.\n\n"
        f"Best regards,\n{candidate_name}\n"
    )


def append_history(row: dict[str, Any]) -> None:
    _ensure_history_csv()
    with EMAIL_HISTORY_PATH.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "recruiter_name",
            "recruiter_email",
            "role",
            "post_url",
            "candidate",
            "email_sent_status",
            "timestamp",
            "subject",
            "message_id",
            "followup_count",
            "last_followup_at",
            "replied",
        ])
        writer.writerow({
            "recruiter_name": row.get("recruiter_name", ""),
            "recruiter_email": row.get("recruiter_email", ""),
            "role": row.get("role", ""),
            "post_url": row.get("post_url", ""),
            "candidate": row.get("candidate", ""),
            "email_sent_status": row.get("email_sent_status", "sent"),
            "timestamp": row.get("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
            "subject": row.get("subject", ""),
            "message_id": row.get("message_id", f"<{uuid.uuid4()}@gmail.com>"),
            "followup_count": row.get("followup_count", 0),
            "last_followup_at": row.get("last_followup_at", ""),
            "replied": row.get("replied", 0),
        })


def send_outreach_email(recruiter: dict[str, Any], candidate: dict[str, Any], resume_path: str | None = None, live_send: bool = False) -> dict[str, Any]:
    subject = build_subject(recruiter.get("role", "Role"), candidate.get("name", "Candidate"))
    body = build_email_body(candidate.get("name", "Candidate"), recruiter.get("recruiter_name", "Recruiter"), recruiter.get("role", "Role"), recruiter.get("job_description", ""))
    message_id = f"<{uuid.uuid4()}@gmail.com>"

    record = {
        "recruiter_name": recruiter.get("recruiter_name", "Recruiter"),
        "recruiter_email": recruiter.get("recruiter_email", ""),
        "role": recruiter.get("role", "Role"),
        "post_url": recruiter.get("post_url", ""),
        "candidate": candidate.get("name", "Candidate"),
        "email_sent_status": "sent",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "subject": subject,
        "message_id": message_id,
        "followup_count": 0,
        "last_followup_at": "",
        "replied": 0,
    }

    if live_send:
        gmail_email = os.getenv("GMAIL_EMAIL", "").strip()
        gmail_password = os.getenv("GMAIL_APP_PASSWORD", "").strip()
        if not gmail_email or not gmail_password:
            raise RuntimeError("Missing Gmail SMTP credentials. Configure GMAIL_EMAIL and GMAIL_APP_PASSWORD in .env.")

        msg = MIMEMultipart()
        msg["From"] = gmail_email
        msg["To"] = recruiter.get("recruiter_email", "")
        msg["Subject"] = subject
        msg["Message-ID"] = message_id
        msg.attach(MIMEText(body, "plain", "utf-8"))

        if resume_path and Path(resume_path).exists():
            with open(resume_path, "rb") as attachment_file:
                attachment = MIMEApplication(attachment_file.read(), _subtype="pdf" if resume_path.lower().endswith(".pdf") else "octet-stream")
            attachment.add_header("Content-Disposition", "attachment", filename=Path(resume_path).name)
            msg.attach(attachment)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(gmail_email, gmail_password)
            smtp.send_message(msg)

    append_history(record)
    return record
