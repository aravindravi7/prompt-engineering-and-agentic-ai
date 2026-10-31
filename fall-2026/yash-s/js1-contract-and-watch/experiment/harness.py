"""Shared pieces for the sampling report (sample.py) and the prompt experiment (run_experiment.py).

Reads the committed selection, the hand labels in LABELING-SHEET.md and the saved baseline
response; never changes any of them. Python 3 standard library only.
"""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOLDER = HERE.parent
sys.path.insert(0, str(FOLDER))
import judge  # noqa: E402
import watch  # noqa: E402

SELECTION = HERE / "selection.json"
SHEET = HERE / "LABELING-SHEET.md"
PERSONA = FOLDER / "persona" / "priya-nair.resume.example.json"
RUNS = FOLDER / "runs"
PASS_DEFINITION = ("pass = the answer passes the validator AND its verdict matches my label; "
                   "invalid, unavailable or disagreeing answers fail (FRICTIONAL.md, 'My Pass Definition')")
LABEL_LINE = re.compile(r"^- \*\*My label \(relevant / not relevant\):\*\*[ \t]*(.*)$", re.M)
NOTE_LINE = re.compile(r"^- \*\*My note:\*\*[ \t]*(.*)$", re.M)


class SetupError(Exception):
    """Something the run depends on is missing or does not match: nothing is asked."""


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_selection(path=SELECTION):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_labels(path=SHEET):
    """{posting id: {"label", "note"}} from the labeling sheet. Every label must be exact."""
    labels = {}
    for block in re.split(r"^## \d+\. ", Path(path).read_text(encoding="utf-8"), flags=re.M)[1:]:
        pid = int(block.split(":", 1)[0])
        lab, note = LABEL_LINE.search(block), NOTE_LINE.search(block)
        label = lab.group(1).strip() if lab else ""
        if label not in judge.VERDICTS:
            raise SetupError(f"posting {pid}: label {label!r} is not 'relevant' or 'not relevant'")
        labels[pid] = {"label": label, "note": note.group(1).strip() if note else ""}
    return labels


def load_postings(selection, raw_dir=RUNS):
    """The selected postings from the saved response the selection was made from, checked by sha256."""
    raw_path = Path(raw_dir) / selection["source"]
    raw = raw_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != selection["source_sha256"]:
        raise SetupError(f"{raw_path.name} does not match the sha256 recorded in selection.json")
    return {j["id"]: j for j in json.loads(raw)["jobs"]}


def load_resume(path=PERSONA):
    try:
        return watch.load_resume(path)          # the same persona check as the watcher
    except watch.InputError as e:
        raise SetupError(str(e)) from e


def outcome(j):
    """What one answer came to: 'relevant', 'not relevant', 'invalid' or 'unavailable'."""
    return j["verdict"] if j["status"] == "valid" else j["status"]


def is_pass(j, label):
    return j["status"] == "valid" and j["verdict"] == label


def stamp(now=None):
    return (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H%M%SZ")


def write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def prompt_info(prompt):
    return {"prompt_file": str(Path(prompt).as_posix()), "prompt_sha256": sha256_file(prompt)}
