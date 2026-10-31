"""The watch's memory: which posting ids this agent has already seen.

Identity is the Greenhouse ``id`` and nothing else (CONTRACT.md §1.4). Titles
get edited and ``updated_at`` moves for reasons that have nothing to do with a
posting being new, so neither is used to decide newness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

STATE_VERSION = 1


def empty_state(board_token: str, host: str) -> dict:
    return {
        "state_version": STATE_VERSION,
        "host": host,
        "board_token": board_token,
        "seen_ids": [],
        "runs": 0,
        "first_seen_at": None,
        "last_run_at": None,
    }


def load(path: str | Path, board_token: str, host: str) -> tuple[dict, bool]:
    """Return ``(state, is_baseline)``.

    ``is_baseline`` is true exactly when there was no state file to read, which
    is the only condition under which the agent reports nothing as new
    (CONTRACT.md R5).
    """
    path = Path(path)
    if not path.exists():
        return empty_state(board_token, host), True
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("board_token") != board_token or state.get("host") != host:
        raise ValueError(
            f"state file {path} belongs to {state.get('host')}/"
            f"{state.get('board_token')}, not {host}/{board_token}"
        )
    state.setdefault("seen_ids", [])
    return state, False


def new_postings(postings: list[dict], state: dict) -> list[dict]:
    seen = set(state.get("seen_ids", []))
    return [p for p in postings if p["id"] not in seen]


def save(path: str | Path, state: dict, postings: list[dict]) -> dict:
    """Record every posting in this response as seen, and write the state.

    Called only after the verdicts for this run exist (CONTRACT.md W3): if the
    reporter raises, the state on disk is left as it was and the next run sees
    these postings as new again.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    merged = sorted({*state.get("seen_ids", []), *(p["id"] for p in postings)})
    state = {
        **state,
        "seen_ids": merged,
        "runs": int(state.get("runs", 0)) + 1,
        "first_seen_at": state.get("first_seen_at") or now,
        "last_run_at": now,
    }
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return state
