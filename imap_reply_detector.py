from __future__ import annotations

import csv
import email
import imaplib
import os
from datetime import datetime, timedelta
from email.header import decode_header
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
EMAIL_HISTORY_PATH = BASE_DIR / "email_sent_history.csv"


def _parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _load_history() -> list[dict]:
    if not EMAIL_HISTORY_PATH.exists():
        return []
    with EMAIL_HISTORY_PATH.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def find_oldest_pending_timestamp() -> datetime:
    history = _load_history()
    timestamps = []
    for row in history:
        if row.get("replied") in {"1", 1, True}:
            continue
        ts = _parse_dt(row.get("timestamp", ""))
        if ts is not None:
            timestamps.append(ts)
    if not timestamps:
        return datetime.utcnow() - timedelta(days=30)
    return min(timestamps)


def _clean_sender(value: str) -> str:
    decoded = decode_header(value or "")
    cleaned_parts = []
    for item, encoding in decoded:
        if isinstance(item, bytes):
            text = item.decode(encoding or "utf-8", errors="ignore")
        else:
            text = str(item)
        cleaned_parts.append(text)
    return "".join(cleaned_parts).strip().lower()


def check_replies() -> list[dict]:
    gmail_email = os.getenv("GMAIL_EMAIL", "").strip()
    gmail_password = os.getenv("GMAIL_APP_PASSWORD", "").strip()
    if not gmail_email or not gmail_password:
        return []

    oldest_ts = find_oldest_pending_timestamp()
    mail = imaplib.IMAP4_SSL(os.getenv("IMAP_SERVER", "imap.gmail.com"), 993)
    mail.login(gmail_email, gmail_password)
    mail.select("INBOX")
    search_date = oldest_ts.strftime("%d-%b-%Y")
    status, data = mail.search(None, f'(SINCE "{search_date}")')
    mail_ids = data[0].split() if status == "OK" else []

    seen_senders = set()
    for msg_id in mail_ids:
        status, msg_data = mail.fetch(msg_id, "(RFC822)")
        if status != "OK" or not msg_data or not msg_data[0]:
            continue
        raw_email = msg_data[0][1]
        parsed = email.message_from_bytes(raw_email)
        sender = _clean_sender(parsed.get("From", ""))
        if "@" in sender:
            seen_senders.add(sender)

    mail.logout()

    history = _load_history()
    updated = []
    for row in history:
        sender_match = row.get("recruiter_email", "").strip().lower()
        if sender_match and sender_match in seen_senders:
            row["replied"] = "1"
            updated.append(row)

    if updated:
        with EMAIL_HISTORY_PATH.open("w", newline="", encoding="utf-8") as handle:
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
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(history)

    return updated
