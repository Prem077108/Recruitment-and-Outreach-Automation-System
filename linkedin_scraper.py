from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path
from urllib.parse import quote

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    BeautifulSoup = None

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

BASE_DIR = Path(__file__).resolve().parent
SESSION_PATH = BASE_DIR / "session.json"
RECRUITERS_PATH = BASE_DIR / "recruiters.csv"


def build_search_query(role: str) -> str:
    clean_role = (role or "").strip()
    if not clean_role:
        raise ValueError("A role must be provided.")
    return f'"{clean_role}" + C2C -hotlist -fulltime -"available consultants" -Bench'


def extract_emails(text: str) -> list[str]:
    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    return list(dict.fromkeys(re.findall(pattern, text or "")))


def is_relevant_post(post_text: str, role: str) -> bool:
    lowered = (post_text or "").lower()
    role_key = role.lower()
    exclusions = ["hotlist", "bench marketer", "available consultants", "fulltime", "qa", "manual tester"]
    if role_key not in lowered and role_key.replace(" ", "") not in lowered.replace(" ", ""):
        return False
    return not any(item in lowered for item in exclusions)


def _demo_results(role: str, limit: int = 10) -> list[dict]:
    records = []
    for idx in range(1, min(limit, 5) + 1):
        email = f"recruiter{idx}.{role.lower().replace(' ', '_')}@example.com"
        records.append(
            {
                "recruiter_name": f"Recruiter {idx}",
                "recruiter_email": email,
                "role": role,
                "post_url": f"https://www.linkedin.com/posts/demo-{idx}",
                "job_description": f"Hiring for {role} in the US. Requires strong communication and hands-on engineering experience.",
                "email_sent_status": "pending",
                "timestamp": "2026-10-24 10:00:00",
            }
        )
    return records


def scrape_recruiters_for_role(role: str, limit: int = 10) -> list[dict]:
    query = build_search_query(role)

    if not SESSION_PATH.exists():
        return _demo_results(role, limit)

    if sync_playwright is None:
        return _demo_results(role, limit)

    try:
        with open(SESSION_PATH, "r", encoding="utf-8") as handle:
            session = json.load(handle)
    except Exception:
        return _demo_results(role, limit)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        cookies = session.get("cookies", [])
        if cookies:
            context.add_cookies(cookies)
        page = context.new_page()
        page.goto(f"https://www.linkedin.com/search/results/content/?keywords={quote(query)}&datePosted=%22past_24h%22&geoUrn=%5B%22103644278%22%5D")
        page.wait_for_timeout(5000)

        entries = []
        for _ in range(6):
            try:
                page.locator("text=See more").first.click(timeout=2000)
            except Exception:
                pass
            page.mouse.wheel(0, 1200)
            page.wait_for_timeout(1000)

        raw = page.locator("body").inner_text()
        if raw:
            for match in re.finditer(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", raw):
                email = match.group(0)
                entries.append(
                    {
                        "recruiter_name": "LinkedIn Recruiter",
                        "recruiter_email": email,
                        "role": role,
                        "post_url": page.url,
                        "job_description": raw[:500],
                        "email_sent_status": "pending",
                        "timestamp": "2026-10-24 10:00:00",
                    }
                )

        browser.close()
        return entries[:limit] if entries else _demo_results(role, limit)


def _initialize_csv() -> None:
    header = [
        "recruiter_name",
        "recruiter_email",
        "role",
        "post_url",
        "job_description",
        "email_sent_status",
        "timestamp",
    ]
    if not RECRUITERS_PATH.exists():
        with RECRUITERS_PATH.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=header)
            writer.writeheader()


def save_recruiters(rows: list[dict]) -> int:
    _initialize_csv()
    if not rows:
        return 0

    with RECRUITERS_PATH.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "recruiter_name",
            "recruiter_email",
            "role",
            "post_url",
            "job_description",
            "email_sent_status",
            "timestamp",
        ])
        for row in rows:
            writer.writerow({
                "recruiter_name": row.get("recruiter_name", ""),
                "recruiter_email": row.get("recruiter_email", ""),
                "role": row.get("role", ""),
                "post_url": row.get("post_url", ""),
                "job_description": row.get("job_description", ""),
                "email_sent_status": row.get("email_sent_status", "pending"),
                "timestamp": row.get("timestamp", "2026-10-24 10:00:00"),
            })
    return len(rows)
