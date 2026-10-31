"""The fetch, GET only, allow-listed, with the raw bytes kept as evidence.

CONTRACT.md O5 requires every verdict to be recomputable from a file on disk,
so the raw response is written before anything parses it, and its sha256 goes
into the run report.
"""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from .allowlist import check_url
from .errors import FetchFailed

USER_AGENT = (
    "INFO7375-JS1-job-search-agent/1.0 (coursework; read-only; "
    "contact via GitHub course repo)"
)

TIMEOUT_SECONDS = 30


class _NoRedirects(urllib.request.HTTPRedirectHandler):
    """A redirect is a failed run, not a thing to follow (CONTRACT.md R1)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise FetchFailed(
            f"refusing to follow a redirect ({code}) to {newurl!r}: the "
            "allow-list is checked on the URL this agent was told to fetch"
        )


_OPENER = urllib.request.build_opener(_NoRedirects)


def board_url(host: str, board_token: str, path_template: str) -> str:
    return check_url("https://" + host + path_template.format(board_token=board_token))


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def fetch_raw(url: str) -> tuple[bytes, int]:
    """GET ``url`` and return its raw body. No body is ever sent."""
    check_url(url)
    request = urllib.request.Request(
        url, method="GET", headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with _OPENER.open(request, timeout=TIMEOUT_SECONDS) as response:
            return response.read(), response.status
    except urllib.error.HTTPError as exc:  # pragma: no cover - network dependent
        raise FetchFailed(f"HTTP {exc.code} from {url}") from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network dependent
        raise FetchFailed(f"could not reach {url}: {exc.reason}") from exc


def save_raw(raw: bytes, raw_dir: str | Path, label: str) -> dict:
    """Write the raw bytes to evidence and describe what was written."""
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{utc_stamp()}-{label}.json"
    path.write_bytes(raw)
    return {
        "path": str(path),
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def parse_postings(raw: bytes) -> list[dict]:
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FetchFailed(f"response was not JSON: {exc}") from exc
    jobs = payload.get("jobs")
    if not isinstance(jobs, list):
        raise FetchFailed('response has no "jobs" array')
    for job in jobs:
        if not isinstance(job, dict) or "id" not in job:
            raise FetchFailed('a posting in "jobs" has no "id"')
    return jobs


def sha256_of_file(path: str | Path) -> str | None:
    path = Path(path)
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()
