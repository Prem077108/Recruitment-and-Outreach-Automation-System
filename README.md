# Recruitment and Outreach Automation

This project implements a Python-based recruitment outreach workflow for LinkedIn recruiter discovery, resume customization, Gmail outreach, follow-up handling, and reply detection.

## Features

- LinkedIn login/session capture using Playwright
- Search and filtering of recruiter job posts
- Candidate role configuration and client profile management
- Resume customization pipeline for DOCX/PDF workflows
- Gmail SMTP outreach with deduplication history
- Threaded follow-ups using `In-Reply-To` and `References`
- IMAP-based inbox sync for reply detection
- HTML analytics dashboard export

## Project structure

- `main.py` – terminal CLI entry point
- `client_config.py` – client and role configuration
- `linkedin_login.py` – LinkedIn session setup
- `linkedin_scraper.py` – recruiter scraping logic
- `resume_customizer.py` – resume tailoring and PDF export
- `gmail_sender.py` – outreach email dispatch
- `followup_sender.py` – threaded follow-up sending
- `imap_reply_detector.py` – Gmail reply detection
- `analytics.py` – dashboard generation
- `lock_util.py` – thread-safe lock
- `recruiters.csv` and `email_sent_history.csv` – local state stores

## Quick start

1. Install dependencies:
   `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill your credentials.
3. Run:
   `python main.py`
4. Follow the menu to validate setup, scrape recruiter posts, or run the full pipeline.

## Notes

This implementation is intentionally production-lean and uses graceful fallback behavior when credentials or external integrations are missing. It is designed to match the blueprint in the project specification while remaining safe to run in development or demo mode.
