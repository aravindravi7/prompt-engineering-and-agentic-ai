"""Paths, a posting builder, and fakes for the Anthropic client and HTTP opener."""

import io
import json
from datetime import date
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
PERSONA = PROJECT_DIR / "persona" / "cole-palmer.example.json"
BOARD_SMALL = FIXTURES / "board_small.json"
BOARD_NO_CONTENT = FIXTURES / "board_no_content.json"
RUN_DATE = date(2026, 10, 27)


def posting(**overrides) -> dict:
    """A posting that passes every check on run date 2026-10-27, unless overridden."""
    base = {
        "id": 42,
        "title": "Software Engineer, New Grad",
        "absolute_url": "https://stripe.com/jobs/search?gh_jid=42",
        "location": {"name": "Seattle, WA"},
        "first_published": "2026-10-20T10:00:00-04:00",
        "updated_at": "2026-10-21T10:00:00-04:00",
        "content": "&lt;p&gt;Python services. 2+ years of experience.&lt;/p&gt;",
    }
    base.update(overrides)
    return base


def valid_reply(posting_id, verdict="relevant") -> str:
    return json.dumps({
        "posting_id": str(posting_id),
        "verdict": verdict,
        "justification": [
            {"resume_field": "job_search.target_titles", "posting_field": "title",
             "evidence": "title contains Software Engineer"},
        ],
    })


class FakeBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class FakeResponse:
    def __init__(self, text, stop_reason="end_turn", model="claude-sonnet-5-5"):
        self.content = [] if text is None else [FakeBlock(text)]
        self.stop_reason = stop_reason
        self.model = model

    def model_dump_json(self, indent=None):
        return json.dumps({
            "model": self.model,
            "stop_reason": self.stop_reason,
            "content": [{"type": b.type, "text": b.text} for b in self.content],
        }, indent=indent)


class FakeAPIStatusError(Exception):
    """Stands in for the SDK's APIStatusError subclasses, which carry status_code."""

    def __init__(self, status_code):
        super().__init__(f"Error code: {status_code}")
        self.status_code = status_code


class FakeMessages:
    def __init__(self, reply):
        self._reply = reply
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        posting_id = json.loads(kwargs["messages"][0]["content"])["posting"]["posting_id"]
        result = self._reply(posting_id) if callable(self._reply) else self._reply
        if isinstance(result, Exception):
            raise result
        return result


class FakeClient:
    def __init__(self, reply=lambda pid: FakeResponse(valid_reply(pid))):
        self.messages = FakeMessages(reply)


class FakeFactory:
    """Stands in for claude_judge.make_client and records how it was called."""

    def __init__(self, client=None):
        self.client = client or FakeClient()
        self.calls = []

    def __call__(self, api_key, base_url):
        self.calls.append((api_key, base_url))
        return self.client


class FakeHTTPResponse(io.BytesIO):
    status = 200


class FakeOpener:
    def __init__(self, body: bytes = b"", error: Exception | None = None):
        self.body = body
        self.error = error
        self.urls = []

    def open(self, url, timeout=None):
        self.urls.append(url)
        if self.error:
            raise self.error
        return FakeHTTPResponse(self.body)
