"""Constructed test postings shaped like Greenhouse's board response.

None of these are real Anthropic postings. Greenhouse sends `content` as
HTML that is itself HTML-escaped, so the helpers escape it the same way.
"""

import html
import json
from pathlib import Path

FOLDER = Path(__file__).resolve().parent.parent
PERSONA = FOLDER / "persona" / "aarav-patel.resume.example.json"


def posting(job_id, title, location="San Francisco, CA", body=""):
    return {
        "id": job_id,
        "title": title,
        "location": {"name": location},
        "content": html.escape(body),
        "absolute_url": "https://job-boards.greenhouse.io/anthropic/jobs/%d" % job_id,
        "company_name": "Anthropic",
        "first_published": "2026-10-30T10:00:00-04:00",
        "updated_at": "2026-10-30T10:00:00-04:00",
    }


def board_bytes(*postings):
    return json.dumps({"jobs": list(postings), "meta": {"total": len(postings)}}).encode("utf-8")


def load_persona():
    return json.loads(PERSONA.read_text(encoding="utf-8"))
