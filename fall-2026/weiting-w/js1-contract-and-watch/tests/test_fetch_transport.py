"""The GET itself, against a stub server on this machine.

Honest about what this proves and what it does not. The allow-list is widened
inside this test, by monkeypatch, so that a real socket can be opened to
127.0.0.1. That means the test proves the *transport*: the request is a GET
with no body, a 200 returns the raw bytes unchanged, and a redirect is refused
rather than followed. It does not prove the policy - the policy is tested in
test_refusals.py, where the allow-list is not touched.

A test that both widens the allow-list and claims to test the allow-list would
be worth nothing, so these are two separate files on purpose.
"""

from __future__ import annotations

import http.server
import threading

import pytest

from jobagent import allowlist, fetch
from jobagent.errors import FetchFailed

BODY = b'{"jobs":[{"id":4242,"title":"Software Engineer, Stub"}]}'


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "https://evil.example/jobs")
            self.end_headers()
            return
        if self.path == "/boom":
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"nope")
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(BODY)))
        self.end_headers()
        self.wfile.write(BODY)

    def do_POST(self):  # noqa: N802
        self.send_response(405)
        self.end_headers()

    def log_message(self, *args):
        pass


@pytest.fixture
def stub(monkeypatch):
    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setattr(allowlist, "ALLOWED_HOSTS", frozenset({"127.0.0.1"}))
    monkeypatch.setattr(allowlist, "ALLOWED_SCHEMES", frozenset({"http"}))
    monkeypatch.setattr(
        allowlist,
        "check_url",
        _relaxed_check(server.server_address[1]),
        raising=True,
    )
    monkeypatch.setattr(fetch, "check_url", allowlist.check_url, raising=True)
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def _relaxed_check(port):
    from urllib.parse import urlsplit

    def check(url):
        parts = urlsplit(url)
        if parts.hostname != "127.0.0.1" or parts.port != port:
            raise FetchFailed(f"stub check refused {url}")
        return url

    return check


def test_a_200_returns_the_raw_bytes_unchanged(stub):
    raw, status = fetch.fetch_raw(stub + "/v1/boards/stub/jobs")
    assert status == 200
    assert raw == BODY
    assert fetch.parse_postings(raw)[0]["id"] == 4242


def test_a_redirect_is_refused_not_followed(stub):
    with pytest.raises(FetchFailed):
        fetch.fetch_raw(stub + "/redirect")


def test_a_500_is_a_failed_run(stub):
    with pytest.raises(FetchFailed):
        fetch.fetch_raw(stub + "/boom")


def test_save_raw_writes_the_bytes_and_a_matching_digest(tmp_path):
    info = fetch.save_raw(BODY, tmp_path, "stub")
    from pathlib import Path

    assert Path(info["path"]).read_bytes() == BODY
    assert info["bytes"] == len(BODY)
    import hashlib

    assert info["sha256"] == hashlib.sha256(BODY).hexdigest()


def test_a_response_that_is_not_a_job_board_is_a_failed_run():
    with pytest.raises(FetchFailed):
        fetch.parse_postings(b'{"results": []}')
    with pytest.raises(FetchFailed):
        fetch.parse_postings(b"<html>maintenance</html>")
    with pytest.raises(FetchFailed):
        fetch.parse_postings(b'{"jobs":[{"title":"no id here"}]}')
