"""Refuses: any host not on the allow-list, non-https, and off-list redirect hops."""

import email.message
import io
import urllib.error
import urllib.request
from datetime import datetime

import pytest

from agent import claude_judge
from agent.allowlist import ALLOWED_HOSTS, check_url
from agent.errors import FetchError, HostNotAllowed
from agent.fetch import AllowListRedirectHandler, fetch_board
from agent.timeutil import NEW_YORK
from support import FakeOpener

BOARD_URL = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"
NOW = datetime(2026, 10, 27, 19, 30, 12, tzinfo=NEW_YORK)


def test_allow_list_is_exactly_the_contract_hosts():
    assert ALLOWED_HOSTS == {"boards-api.greenhouse.io", "api.anthropic.com"}


@pytest.mark.parametrize("url", [BOARD_URL, "https://api.anthropic.com", "https://api.anthropic.com/v1/messages"])
def test_allowed_urls_pass(url):
    assert check_url(url) == url


@pytest.mark.parametrize("url", [
    "https://evil.example/v1/boards/stripe/jobs",
    "https://boards-api.greenhouse.io.evil.com/v1/boards/stripe/jobs",
    "https://boards-api.greenhouse.io@evil.com/v1/boards/stripe/jobs",
    "https://user:pw@boards-api.greenhouse.io/v1/boards/stripe/jobs",
    "http://boards-api.greenhouse.io/v1/boards/stripe/jobs",
    "ftp://boards-api.greenhouse.io/x",
    "https://boards-api.greenhouse.io:8443/v1/boards/stripe/jobs",
    "https://greenhouse.io/v1/boards/stripe/jobs",
    "https://api.openai.com/v1/chat/completions",
    "not a url",
])
def test_refused_urls(url):
    with pytest.raises(HostNotAllowed):
        check_url(url)


def test_fetch_refuses_other_host_before_opening_anything(tmp_path):
    opener = FakeOpener(b"{}")
    with pytest.raises(HostNotAllowed):
        fetch_board("https://evil.example/jobs", tmp_path / "raw", opener=opener, now=NOW)
    assert opener.urls == []
    assert not (tmp_path / "raw").exists()


def test_redirect_to_other_host_is_refused():
    handler = AllowListRedirectHandler()
    request = urllib.request.Request(BOARD_URL)
    with pytest.raises(HostNotAllowed):
        handler.redirect_request(request, None, 302, "Found", email.message.Message(), "https://evil.example/jobs")


def test_redirect_within_allow_list_is_followed():
    handler = AllowListRedirectHandler()
    request = urllib.request.Request(BOARD_URL)
    new = handler.redirect_request(request, None, 302, "Found", email.message.Message(),
                                   "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true&page=2")
    assert new.full_url.endswith("page=2")


def test_fetch_saves_exact_bytes_with_date_in_filename(tmp_path):
    body = b'{"jobs": [], "meta": {"total": 0}}  \n'
    returned, raw_path = fetch_board(BOARD_URL, tmp_path / "raw", opener=FakeOpener(body), now=NOW)
    assert returned == body
    assert raw_path.name == "greenhouse-stripe-2026-10-27T193012.json"
    assert raw_path.read_bytes() == body


def test_second_fetch_in_same_second_does_not_overwrite(tmp_path):
    _, first = fetch_board(BOARD_URL, tmp_path / "raw", opener=FakeOpener(b"one"), now=NOW)
    _, second = fetch_board(BOARD_URL, tmp_path / "raw", opener=FakeOpener(b"two"), now=NOW)
    assert first != second
    assert first.read_bytes() == b"one" and second.read_bytes() == b"two"


def test_non_200_response_is_saved_then_stops(tmp_path):
    error = urllib.error.HTTPError(BOARD_URL, 503, "Service Unavailable", email.message.Message(),
                                   io.BytesIO(b"upstream down"))
    with pytest.raises(FetchError, match="HTTP 503"):
        fetch_board(BOARD_URL, tmp_path / "raw", opener=FakeOpener(error=error), now=NOW)
    saved = list((tmp_path / "raw").iterdir())
    assert [p.read_bytes() for p in saved] == [b"upstream down"]


def test_claude_client_refuses_off_list_base_url():
    # Fails on the allow-list check, before the SDK is imported or any client is built.
    with pytest.raises(HostNotAllowed):
        claude_judge.make_client("sk-test", "https://proxy.evil.example")
