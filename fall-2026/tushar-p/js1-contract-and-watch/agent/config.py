"""config.json: model name, board URL, and default paths (relative to the project folder)."""

import json
from pathlib import Path

from . import PROJECT_DIR
from .errors import ConfigError

DEFAULTS = {
    "model": "claude-sonnet-5-5",
    "max_tokens": 16000,
    "board_url": "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true",
    "claude_base_url": "https://api.anthropic.com",
    "persona_path": "persona/cole-palmer.example.json",
    "state_path": "state/seen_ids.json",
    "raw_dir": "raw",
    "out_dir": "out",
}

PATH_KEYS = ("persona_path", "state_path", "raw_dir", "out_dir")


def load_config(path: Path | None = None) -> dict:
    path = Path(path) if path else PROJECT_DIR / "config.json"
    config = dict(DEFAULTS)
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as err:
            raise ConfigError(f"cannot read {path}: {err}") from None
        if not isinstance(loaded, dict):
            raise ConfigError(f"{path} must hold a JSON object")
        config.update(loaded)
    for key in PATH_KEYS:
        value = Path(config[key])
        config[key] = value if value.is_absolute() else PROJECT_DIR / value
    return config
