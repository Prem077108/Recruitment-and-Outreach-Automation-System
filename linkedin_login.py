from __future__ import annotations

import json
import os
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover
    sync_playwright = None

BASE_DIR = Path(__file__).resolve().parent
SESSION_PATH = BASE_DIR / "session.json"


def validate_linkedin_credentials() -> bool:
    email = os.getenv("LINKEDIN_EMAIL", "").strip()
    password = os.getenv("LINKEDIN_PASSWORD", "").strip()
    return bool(email and password)


def setup_linkedin_session(email: str | None = None, password: str | None = None) -> Path:
    if email is None:
        email = os.getenv("LINKEDIN_EMAIL", "").strip()
    if password is None:
        password = os.getenv("LINKEDIN_PASSWORD", "").strip()

    if not email or not password:
        raise RuntimeError("Missing LinkedIn credentials. Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in your .env file.")

    if sync_playwright is None:
        raise RuntimeError("Playwright is not installed. Run: pip install -r requirements.txt and playwright install")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.linkedin.com/login")
        page.fill("input[name='session_key']", email)
        page.fill("input[name='session_password']", password)
        page.click("button[type='submit']")
        page.wait_for_timeout(15000)

        try:
            page.wait_for_selector("nav", timeout=30000)
        except Exception:
            pass

        state = browser.contexts[0].storage_state()
        SESSION_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")
        browser.close()

    return SESSION_PATH
