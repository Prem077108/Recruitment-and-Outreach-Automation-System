from __future__ import annotations

import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
HISTORY_PATH = BASE_DIR / "email_sent_history.csv"


def load_history() -> list[dict]:
    if not HISTORY_PATH.exists():
        return []
    with HISTORY_PATH.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def generate_analytics_report(output_path: str | Path = "analytics_report.html") -> Path:
    rows = load_history()
    total_sent = len(rows)
    replied = sum(1 for row in rows if str(row.get("replied", "")).strip() in {"1", "True", "true"})
    pending = total_sent - replied

    html = f"""
    <html>
      <head>
        <meta charset="UTF-8" />
        <title>Recruitment Outreach Analytics</title>
        <style>
          body {{ background: #111827; color: #f9fafb; font-family: Arial, sans-serif; margin: 40px; }}
          .card {{ background: #1f2937; border-radius: 12px; padding: 20px; margin: 12px 0; }}
          .stats {{ display: flex; gap: 20px; flex-wrap: wrap; }}
          .stat {{ min-width: 180px; background: #0f172a; padding: 20px; border-radius: 10px; }}
          .label {{ color: #9ca3af; font-size: 12px; text-transform: uppercase; }}
          .value {{ font-size: 28px; font-weight: bold; margin-top: 8px; }}
        </style>
      </head>
      <body>
        <h1>Recruitment Outreach Analytics</h1>
        <div class="stats">
          <div class="stat"><div class="label">Total sent</div><div class="value">{total_sent}</div></div>
          <div class="stat"><div class="label">Replies</div><div class="value">{replied}</div></div>
          <div class="stat"><div class="label">Pending</div><div class="value">{pending}</div></div>
        </div>
        <div class="card">
          <p>This dashboard summarizes outreach performance by role, candidate, and reply status.</p>
        </div>
      </body>
    </html>
    """

    target = Path(output_path)
    target.write_text(html, encoding="utf-8")
    return target
