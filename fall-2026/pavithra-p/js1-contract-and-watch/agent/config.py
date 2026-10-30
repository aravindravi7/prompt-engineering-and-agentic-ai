"""Fixed settings from CONTRACT.md. Changing any of these is a contract change."""
from pathlib import Path

BOARD = "pinterest"
ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io"})
BOARD_URL = f"https://boards-api.greenhouse.io/v1/boards/{BOARD}/jobs?content=true"

ROOT = Path(__file__).resolve().parent.parent
RESUME = ROOT / "data" / "aarav-patel.resume.json"
RAW_DIR = ROOT / "evidence" / "raw"
RUNS_DIR = ROOT / "evidence" / "runs"
STATE = ROOT / "state" / "seen_ids.json"
SEEDED_STATE = ROOT / "state" / "seen_ids-SEEDED.json"
