"""Validators for both judges' justifications (CONTRACT.md, wrong version 1)."""

import json

from .errors import ValidationError
from .persona import RULE_FIELDS

POSTING_FIELDS = ("title", "location.name", "content", "first_published", "updated_at")
VERDICTS = ("relevant", "not_relevant", "cannot_tell")
RESULTS = ("pass", "fail", "unknown")
CHECKS = ("R1", "R2", "R3", "R4", "R5", "R6")
RULE_ENTRY_PARTS = ("resume_field", "posting_field", "value_found", "result")
CLAUDE_TOP_KEYS = {"posting_id", "verdict", "justification"}
CLAUDE_ENTRY_KEYS = {"resume_field", "posting_field", "evidence"}

# R2 compares the posting date with the run date; no résumé field is involved.
R2_RESUME_FIELD = "none (R2 compares the posting date with the run date)"


def _non_empty_string(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def validate_rule_justification(entries) -> None:
    """One entry per check R1–R6, in order, each naming all four parts."""
    if not isinstance(entries, list) or [e.get("check") if isinstance(e, dict) else None for e in entries] != list(CHECKS):
        raise ValidationError("rule justification must be one entry per check R1–R6, in order")
    for entry in entries:
        check = entry["check"]
        for part in RULE_ENTRY_PARTS:
            if not _non_empty_string(entry.get(part)):
                raise ValidationError(f"{check} justification is missing {part}")
        allowed_resume = (R2_RESUME_FIELD,) if check == "R2" else RULE_FIELDS
        if entry["resume_field"] not in allowed_resume:
            raise ValidationError(f"{check} justification cites unlisted résumé field {entry['resume_field']!r}")
        if entry["posting_field"] not in POSTING_FIELDS:
            raise ValidationError(f"{check} justification cites unlisted posting field {entry['posting_field']!r}")
        if entry["result"] not in RESULTS:
            raise ValidationError(f"{check} result must be pass, fail or unknown, not {entry['result']!r}")


def _reject_duplicate_keys(pairs):
    keys = [key for key, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValidationError(f"duplicate keys in Claude reply: {keys}")
    return dict(pairs)


def validate_claude_reply(text, posting_id) -> dict:
    """Parse and check Claude's reply. Never repairs it: any mismatch raises."""
    if not isinstance(text, str):
        raise ValidationError("Claude reply has no text")
    try:
        data = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as err:
        raise ValidationError(f"Claude reply is not JSON: {err}") from None

    if not isinstance(data, dict):
        raise ValidationError("Claude reply must be a JSON object")
    if set(data) != CLAUDE_TOP_KEYS:
        raise ValidationError(f"Claude reply keys must be exactly {sorted(CLAUDE_TOP_KEYS)}, got {sorted(data)}")
    if not isinstance(data["posting_id"], str) or data["posting_id"] != str(posting_id):
        raise ValidationError(f"posting_id must be the string {str(posting_id)!r}, got {data['posting_id']!r}")
    if data["verdict"] not in VERDICTS:
        raise ValidationError(f"verdict must be one of {VERDICTS}, got {data['verdict']!r}")

    justification = data["justification"]
    if not isinstance(justification, list) or not justification:
        raise ValidationError("justification must be a non-empty list")
    for i, entry in enumerate(justification):
        if not isinstance(entry, dict) or set(entry) != CLAUDE_ENTRY_KEYS:
            got = sorted(entry) if isinstance(entry, dict) else type(entry).__name__
            raise ValidationError(f"justification[{i}] keys must be exactly {sorted(CLAUDE_ENTRY_KEYS)}, got {got}")
        if entry["resume_field"] not in RULE_FIELDS:
            raise ValidationError(f"justification[{i}] resume_field {entry['resume_field']!r} is not a listed persona key")
        if entry["posting_field"] not in POSTING_FIELDS:
            raise ValidationError(f"justification[{i}] posting_field {entry['posting_field']!r} is not a listed posting field")
        if not isinstance(entry["evidence"], str):
            raise ValidationError(f"justification[{i}] evidence must be a string")
    return data
