"""Shared pieces of the prompt experiment: hand labels, postings, and the Claude call.

Postings come from the fixed baseline raw file, looked up by id, and the run date is fixed
at 2026-10-27, the date the labels used (experiments/LABELING-RULE.md). The Claude call,
output format and validator are the agent's own (agent.claude_judge), so an experiment
request differs from an agent request only in the system prompt file it names.

labels.csv and selection.json are read, never written.
"""

import csv
import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from agent import PROJECT_DIR, claude_judge
from agent.allowlist import check_url
from agent.config import load_config
from agent.errors import AgentError, ConfigError
from agent.persona import load_rule_fields
from agent.run import display_path, parse_board
from agent.text import strip_html
from agent.validator import VERDICTS

EXPERIMENTS_DIR = PROJECT_DIR / "experiments"
RAW_PATH = PROJECT_DIR / "raw" / "greenhouse-stripe-2026-10-27T203128.json"
LABELS_PATH = EXPERIMENTS_DIR / "labels.csv"
SELECTION_PATH = EXPERIMENTS_DIR / "selection.json"
RESULTS_DIR = EXPERIMENTS_DIR / "results"
RUN_DATE = date(2026, 10, 27)
SPLIT_KEYS = {"dev": "dev", "held-out": "held_out"}  # CLI name -> selection.json key

# No request sets temperature, so the API default applies. Recorded in every result file.
TEMPERATURE = "not set in the request (API default)"


class ExperimentError(AgentError):
    """The experiment inputs are inconsistent, or a run was refused."""


@dataclass
class Setup:
    config: dict
    fields: dict
    prompt_text: str
    prompt_sha256: str
    prompt_display: str
    client: object


def load_labels(path: Path = LABELS_PATH) -> dict[int, dict]:
    """{posting_id: {"label", "split"}}. A later row for the same id is a correction and wins."""
    with Path(path).open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    labels = {}
    for row in rows:
        pid = int(row["posting_id"])
        label = (row.get("label") or "").strip()
        if label not in VERDICTS:
            raise ExperimentError(f"labels.csv: posting {pid} has label {label!r}, not one of {VERDICTS}")
        labels[pid] = {"label": label, "split": row["split"].strip()}
    return labels


def split_ids(split: str, path: Path = SELECTION_PATH) -> list[int]:
    if split not in SPLIT_KEYS:
        raise ExperimentError(f"split must be one of {sorted(SPLIT_KEYS)}, not {split!r}")
    return list(json.loads(Path(path).read_text(encoding="utf-8"))[SPLIT_KEYS[split]])


def load_postings(ids, raw_path: Path = RAW_PATH) -> dict[int, dict]:
    jobs = parse_board(Path(raw_path).read_bytes(), display_path(raw_path))
    by_id = {}
    for job in jobs:
        by_id.setdefault(job["id"], job)
    missing = [pid for pid in ids if pid not in by_id]
    if missing:
        raise ExperimentError(f"{display_path(raw_path)} has no posting with id {missing}")
    return {pid: by_id[pid] for pid in ids}


def check_labels(ids, split: str, labels: dict[int, dict]) -> None:
    for pid in ids:
        if pid not in labels:
            raise ExperimentError(f"labels.csv has no label for posting {pid}")
        if labels[pid]["split"] != split:
            raise ExperimentError(f"posting {pid} is {labels[pid]['split']} in labels.csv, not {split}")


def prepare(prompt_path: Path, *, env=None, client_factory=claude_judge.make_client,
            config: dict | None = None) -> Setup:
    """Everything that can stop a run, checked before the first API call."""
    prompt_text, prompt_sha256 = claude_judge.load_prompt(prompt_path)
    config = config or load_config()
    fields = load_rule_fields(config["persona_path"])
    env = os.environ if env is None else env
    api_key = env.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ConfigError("ANTHROPIC_API_KEY is not set; export it in your shell")
    check_url(config["claude_base_url"])
    return Setup(config, fields, prompt_text, prompt_sha256, display_path(prompt_path),
                 client_factory(api_key, config["claude_base_url"]))


def judge_once(setup: Setup, job: dict, reply_path: Path) -> dict:
    """One fresh request with a single user message: no conversation is shared between calls."""
    request = claude_judge.build_request(
        job, strip_html(job.get("content")), setup.fields, RUN_DATE,
        setup.config["model"], setup.config["max_tokens"], setup.prompt_text,
    )
    result = claude_judge.judge(setup.client, request, job["id"], reply_path)
    result["claude_reply_path"] = display_path(reply_path)
    return result


def yes_no(value: bool) -> str:
    return "yes" if value else "no"
