"""The Claude judge. Its verdicts are model judgment, never a record.

Claude receives only the persona's rule fields, the posting's title, location, dates and
HTML-stripped content, and R1–R6 in plain language. The system prompt is read from a text
file (prompts/baseline.txt by default), so a prompt change is a diff between two files.
Model fallback is off: the request sends no fallback parameter, so the model that answers
is the configured one.
"""

import hashlib
import json
from datetime import date
from pathlib import Path

from . import PROJECT_DIR
from .allowlist import check_url
from .errors import ClaudeAuthError, ConfigError, ValidationError
from .persona import RULE_FIELDS
from .validator import POSTING_FIELDS, VERDICTS, validate_claude_reply

CLAUDE_LABEL = "model judgment"

DEFAULT_PROMPT_PATH = PROJECT_DIR / "prompts" / "baseline.txt"


def load_prompt(path: Path = DEFAULT_PROMPT_PATH) -> tuple[str, str]:
    """(system prompt text, SHA-256 of the file's bytes). The text is sent exactly as stored."""
    try:
        data = Path(path).read_bytes()
    except OSError as err:
        raise ConfigError(f"cannot read prompt file {path}: {err}") from None
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as err:
        raise ConfigError(f"prompt file {path} is not UTF-8: {err}") from None
    if not text.strip():
        raise ConfigError(f"prompt file {path} is empty")
    return text, hashlib.sha256(data).hexdigest()


OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "posting_id": {"type": "string"},
        "verdict": {"type": "string", "enum": list(VERDICTS)},
        "justification": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "resume_field": {"type": "string", "enum": list(RULE_FIELDS)},
                    "posting_field": {"type": "string", "enum": list(POSTING_FIELDS)},
                    "evidence": {"type": "string"},
                },
                "required": ["resume_field", "posting_field", "evidence"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["posting_id", "verdict", "justification"],
    "additionalProperties": False,
}


def build_request(posting: dict, content_text: str, fields: dict, run_date: date,
                  model: str, max_tokens: int, system_prompt: str | None = None) -> dict:
    """Keyword arguments for messages.create. `fields` holds only the five rule fields.

    `system_prompt` is the text from load_prompt; None reads the default prompt file.
    """
    if system_prompt is None:
        system_prompt, _ = load_prompt()
    payload = {
        "run_date": run_date.isoformat(),
        "resume_rule_fields": {key: fields[key] for key in RULE_FIELDS},
        "posting": {
            "posting_id": str(posting["id"]),
            "title": posting.get("title"),
            "location.name": (posting.get("location") or {}).get("name"),
            "first_published": posting.get("first_published"),
            "updated_at": posting.get("updated_at"),
            "content": content_text,
        },
    }
    return {
        "model": model,
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [{"role": "user", "content": json.dumps(payload, ensure_ascii=False, indent=2)}],
        "output_config": {"format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}},
    }


def make_client(api_key: str, base_url: str):
    """Anthropic client pinned to an allow-listed base URL (ANTHROPIC_BASE_URL is not used)."""
    check_url(base_url)
    import anthropic  # imported here so --no-claude runs and tests never need the SDK

    return anthropic.Anthropic(api_key=api_key, base_url=base_url)


def _invalid(reason: str, model, reply_path: Path) -> dict:
    return {
        "claude_verdict": None,
        "claude_justification": None,
        "claude_valid": False,
        "claude_model": model,
        "claude_invalid_reason": reason,
        "claude_reply_path": str(reply_path),
        "claude_label": CLAUDE_LABEL,
    }


def _dump(response) -> str:
    if hasattr(response, "model_dump_json"):
        return response.model_dump_json(indent=2)
    return repr(response)


def judge(client, request: dict, posting_id, reply_path: Path) -> dict:
    """Call Claude once, save the raw reply, and validate it. Invalid output is never repaired.

    A rejected API key (HTTP 401) raises ClaudeAuthError instead: every later call would
    fail the same way, so the run stops rather than marking every posting invalid.
    """
    try:
        response = client.messages.create(**request)
    except Exception as err:  # any API or network failure leaves nothing to validate
        status = getattr(err, "status_code", None)
        if status == 401:
            raise ClaudeAuthError(
                f"Claude API rejected the API key (HTTP 401, {type(err).__name__}) at posting "
                f"{posting_id}; run stopped. Check ANTHROPIC_API_KEY."
            ) from None
        reply_path.parent.mkdir(parents=True, exist_ok=True)
        reason = f"API call failed: {type(err).__name__}" + (f" (HTTP {status})" if status else "")
        reply_path.write_text(reason + "\n", encoding="utf-8")
        return _invalid(reason, None, reply_path)

    reply_path.parent.mkdir(parents=True, exist_ok=True)
    reply_path.write_text(_dump(response), encoding="utf-8")
    model = getattr(response, "model", None)
    if getattr(response, "stop_reason", None) == "refusal":
        return _invalid("refusal", model, reply_path)
    text = next((b.text for b in (response.content or []) if getattr(b, "type", None) == "text"), None)
    try:
        data = validate_claude_reply(text, posting_id)
    except ValidationError as err:
        return _invalid(str(err), model, reply_path)
    return {
        "claude_verdict": data["verdict"],
        "claude_justification": data["justification"],
        "claude_valid": True,
        "claude_model": model,
        "claude_invalid_reason": None,
        "claude_reply_path": str(reply_path),
        "claude_label": CLAUDE_LABEL,
    }
