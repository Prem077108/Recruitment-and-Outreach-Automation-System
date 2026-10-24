from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    def load_dotenv(*args, **kwargs):
        return False

from analytics import generate_analytics_report
from client_config import get_candidate, get_target_roles
from gmail_sender import send_outreach_email
from imap_reply_detector import check_replies
from linkedin_login import setup_linkedin_session, validate_linkedin_credentials
from linkedin_scraper import scrape_recruiters_for_role, save_recruiters
from resume_customizer import customize_resume

BASE_DIR = Path(__file__).resolve().parent


def ensure_environment() -> None:
    load_dotenv(BASE_DIR / ".env")


def print_banner() -> None:
    print("\nRecruitment and Outreach Automation")
    print("=" * 40)


def menu() -> None:
    print_banner()
    print("1. Setup and validate LinkedIn login session")
    print("2. Validate environment variables")
    print("3. Scrape LinkedIn recruiters for a role")
    print("4. Show candidate roles")
    print("5. Send a live or test email")
    print("6. Sync Gmail replies")
    print("7. Generate analytics report")
    print("8. Run full automated batch")
    print("0. Exit")


def action_setup_linkedin() -> None:
    ensure_environment()
    try:
        result = setup_linkedin_session()
        print(f"LinkedIn session saved to: {result}")
    except Exception as exc:  # pragma: no cover
        print(f"Failed to initialize LinkedIn session: {exc}")


def action_validate_environment() -> None:
    ensure_environment()
    required = [
        "LINKEDIN_EMAIL",
        "LINKEDIN_PASSWORD",
        "GMAIL_EMAIL",
        "GMAIL_APP_PASSWORD",
    ]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        print("Missing values:", ", ".join(missing))
    else:
        print("Environment variables look configured.")

    print("LinkedIn credentials present:", validate_linkedin_credentials())


def action_scrape_recruiters() -> None:
    ensure_environment()
    role = input("Enter target role (e.g. Java Developer): ").strip() or "Java Developer"
    rows = scrape_recruiters_for_role(role, limit=10)
    count = save_recruiters(rows)
    print(f"Saved {count} recruiter records to recruiters.csv")


def action_show_roles() -> None:
    candidate_key = input("Candidate key (demo/safi/tanuja): ").strip() or "demo"
    candidate = get_candidate(candidate_key)
    print(f"Candidate: {candidate['name']}")
    for role, details in candidate.get("role_map", {}).items():
        print(f"- {role}: {', '.join(details.get('search_roles', []))}")


def action_send_email() -> None:
    ensure_environment()
    candidate = get_candidate("demo")
    recruiter = {
        "recruiter_name": "Demo Recruiter",
        "recruiter_email": "demo.recruiter@example.com",
        "role": "Java Developer",
        "post_url": "https://linkedin.example.com/post/demo",
        "job_description": "Java developer role requiring Spring Boot, AWS, microservices, and backend system design.",
    }
    resume_path = customize_resume("clients/demo_resume.docx" if Path("clients/demo_resume.docx").exists() else "README.md", recruiter["job_description"], candidate["name"], candidate.get("name", "demo"))
    result = send_outreach_email(recruiter, candidate, resume_path=str(resume_path), live_send=False)
    print("Email record saved:", result)


def action_sync_replies() -> None:
    ensure_environment()
    updates = check_replies()
    if not updates:
        print("No new replies detected.")
        return
    print(f"Updated {len(updates)} reply records.")


def action_generate_analytics() -> None:
    report = generate_analytics_report(BASE_DIR / "analytics_report.html")
    print(f"Analytics report generated: {report}")


def action_full_pipeline() -> None:
    ensure_environment()
    candidate_key = input("Candidate key (demo/safi/tanuja): ").strip() or "demo"
    candidate = get_candidate(candidate_key)
    roles = get_target_roles(candidate_key)
    saved_rows = []

    for role in roles:
        rows = scrape_recruiters_for_role(role, limit=5)
        save_recruiters(rows)
        saved_rows.extend(rows)
        print(f"Fetched {len(rows)} recruiters for {role}.")

    if not saved_rows:
        print("No recruiter records found for this candidate. Nothing to send.")
        return

    for row in saved_rows[:5]:
        resume_path = customize_resume(
            "clients/demo_resume.docx" if Path("clients/demo_resume.docx").exists() else "README.md",
            row.get("job_description", ""),
            candidate["name"],
            candidate_key,
        )
        send_outreach_email(row, candidate, resume_path=str(resume_path), live_send=False)
        print(f"Queued outreach for {row.get('recruiter_email')}")


def main() -> None:
    while True:
        menu()
        choice = input("Choose an option: ").strip()
        if choice == "1":
            action_setup_linkedin()
        elif choice == "2":
            action_validate_environment()
        elif choice == "3":
            action_scrape_recruiters()
        elif choice == "4":
            action_show_roles()
        elif choice == "5":
            action_send_email()
        elif choice == "6":
            action_sync_replies()
        elif choice == "7":
            action_generate_analytics()
        elif choice == "8":
            action_full_pipeline()
        elif choice == "0":
            print("Exiting.")
            break
        else:
            print("Invalid choice. Please pick a valid option.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
