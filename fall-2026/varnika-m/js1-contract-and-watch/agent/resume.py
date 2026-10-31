"""Load the résumé and refuse anything that is not a fictional persona (CONTRACT.md sections 1 and 3)."""

import json
from pathlib import Path


class ResumeRefused(ValueError):
    pass


def load_resume(path):
    resume = json.loads(Path(path).read_text(encoding="utf-8"))
    personal = resume.get("personal") or {}
    email, phone = personal.get("email"), personal.get("phone")
    # The messages never repeat the email or phone, so a real résumé is not echoed to the screen.
    if not isinstance(email, str) or not email.lower().endswith("@example.com"):
        raise ResumeRefused("refused: the résumé's email must end in @example.com (fictional personas only)")
    if not isinstance(phone, str) or "555" not in phone:
        raise ResumeRefused("refused: the résumé's phone must contain 555 (fictional personas only)")
    return resume
