"""CONTRACT.md R1 (allow-list) and R2 (persona guard)."""

from __future__ import annotations

import json

import pytest

from jobagent import resume as resume_mod
from jobagent.allowlist import ALLOWED_HOSTS, check_url
from jobagent.claude_judge import MODEL_HOSTS, _check_model_url
from jobagent.errors import DisallowedHost, FetchFailed, NonPersonaResume


@pytest.mark.parametrize(
    "url",
    [
        "https://boards.greenhouse.io/v1/boards/reddit/jobs",
        "https://api.lever.co/v0/postings/reddit",
        "https://boards-api.greenhouse.io.evil.example/v1/boards/reddit/jobs",
        "https://evil.example/?x=https://boards-api.greenhouse.io/",
        "http://boards-api.greenhouse.io/v1/boards/reddit/jobs",
        "https://boards-api.greenhouse.io:8443/v1/boards/reddit/jobs",
        "file:///etc/passwd",
        "https://127.0.0.1:8000/v1/boards/reddit/jobs",
    ],
)
def test_off_allowlist_urls_are_refused_before_any_socket(url):
    with pytest.raises(DisallowedHost):
        check_url(url)


def test_the_one_allowed_url_passes():
    assert ALLOWED_HOSTS == {"boards-api.greenhouse.io"}
    url = "https://boards-api.greenhouse.io/v1/boards/reddit/jobs"
    assert check_url(url) == url


def test_the_model_allowlist_is_separate_and_also_single_host():
    assert MODEL_HOSTS == {"api.anthropic.com"}
    assert "api.anthropic.com" not in ALLOWED_HOSTS
    with pytest.raises(FetchFailed):
        _check_model_url("https://boards-api.greenhouse.io/v1/messages")


def test_persona_resume_in_the_repo_is_accepted(persona):
    assert persona["persona"] is True


@pytest.mark.parametrize(
    "mutation",
    [
        {"persona": False},
        {"email": "a.real.person@university.example"},
        {"phone": "+1-617-555-0137"},
        {"title_block": []},
        {"locations_ok": ["New York"]},
    ],
)
def test_a_resume_that_is_not_a_validated_persona_is_refused(persona, mutation):
    candidate = {**json.loads(json.dumps(persona)), **mutation}
    with pytest.raises(NonPersonaResume):
        resume_mod.validate(candidate)


def test_public_summary_never_contains_identifying_fields(persona):
    summary = resume_mod.public_summary(persona)
    blob = json.dumps(summary)
    for field in ("name", "email", "phone"):
        assert field not in summary
        assert persona[field] not in blob
