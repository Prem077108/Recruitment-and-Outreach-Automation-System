from __future__ import annotations

import csv
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

from gmail_sender import append_history, build_email_body, build_subject

BASE_DIR = Path(__file__).resolve().parent
EMAIL_HISTORY_PATH = BASE_DIR / "email_sent_history.csv"


def _load_history() -> list[dict]:
    if not EMAIL_HISTORY_PATH.exists():
        return []
    with EMAIL_HISTORY_PATH.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return rows


def send_followup(recruiter_email: str, candidate_name: str, role: str, original_message_id: str, job_description: str = "") -> dict:
    followup = {
        "recruiter_name": "Recruiter",
        "recruiter_email": recruiter_email,
        "role": role,
        "candidate": candidate_name,
        "email_sent_status": "sent",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "subject": build_subject(role, candidate_name),
        "message_id": f"<{original_message_id.split('@')[0]}-followup@linkedinoutreach.local>",
        "followup_count": 1,
        "last_followup_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "replied": 0,
    }

    msg = EmailMessage()
    msg["Subject"] = "Re: " + followup["subject"]
    msg["To"] = recruiter_email
    msg["In-Reply-To"] = original_message_id
    msg["References"] = original_message_id
    msg.set_content(
        build_email_body(candidate_name, "Recruiter", role, job_description) + "\n\nFollowing up to confirm whether this opportunity is still active."
    )

    append_history(followup)
    return followup
