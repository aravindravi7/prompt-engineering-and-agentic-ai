"""Live board fetch. Saves the exact response bytes before anything parses them."""

import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from .allowlist import check_url
from .errors import FetchError
from .timeutil import NEW_YORK, stamp


class AllowListRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Checks every redirect hop against the allow-list before following it."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def build_opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(AllowListRedirectHandler())


def unique_path(path: Path) -> Path:
    """path, or path with -2, -3, ... before the suffix if it already exists."""
    candidate, n = path, 2
    while candidate.exists():
        candidate = path.with_name(f"{path.stem}-{n}{path.suffix}")
        n += 1
    return candidate


def save_raw(raw_dir: Path, body: bytes, now: datetime) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = unique_path(raw_dir / f"greenhouse-stripe-{stamp(now)}.json")
    path.write_bytes(body)
    return path


def fetch_board(url: str, raw_dir: Path, opener=None, now: datetime | None = None) -> tuple[bytes, Path]:
    """GET the board, save the raw bytes, and return (bytes, raw path)."""
    check_url(url)
    opener = opener or build_opener()
    now = now or datetime.now(NEW_YORK)
    try:
        with opener.open(url, timeout=30) as response:
            body = response.read()
    except urllib.error.HTTPError as err:
        raw_path = save_raw(raw_dir, err.read(), now)
        raise FetchError(f"board answered HTTP {err.code}; raw response saved to {raw_path}") from None
    except urllib.error.URLError as err:
        raise FetchError(f"could not reach the board: {err.reason}") from None
    return body, save_raw(raw_dir, body, now)
