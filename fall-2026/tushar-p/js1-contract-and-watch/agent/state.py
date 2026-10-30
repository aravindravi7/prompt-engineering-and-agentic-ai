"""Seen posting ids. A missing file means a baseline run; ids are only ever added."""

import json
import os
from pathlib import Path

from .errors import StateError


def load_seen(path: Path) -> set[int] | None:
    """The seen ids, or None if the state file is missing (baseline run)."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        raise StateError(f"cannot read state file {path}: {err}") from None
    if not isinstance(data, list) or not all(isinstance(i, int) and not isinstance(i, bool) for i in data):
        raise StateError(f"state file {path} must be a JSON list of integer posting ids")
    return set(data)


def new_ids(board_ids: list[int], seen: set[int] | None) -> list[int]:
    """Ids not seen before, in board order. A baseline run reports none."""
    if seen is None:
        return []
    fresh, emitted = [], set()
    for posting_id in board_ids:
        if posting_id not in seen and posting_id not in emitted:
            fresh.append(posting_id)
            emitted.add(posting_id)
    return fresh


def save_seen(path: Path, seen: set[int] | None, board_ids: list[int]) -> None:
    """Write seen ∪ board ids, sorted. Written via a temp file so a crash cannot truncate it."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    merged = sorted(set(seen or ()) | set(board_ids))
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(merged, indent=0) + "\n", encoding="utf-8")
    os.replace(tmp, path)
