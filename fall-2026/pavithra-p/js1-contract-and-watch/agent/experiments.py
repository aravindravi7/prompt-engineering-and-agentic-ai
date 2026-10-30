"""The sampling report (Chapter 1) and the prompt experiment (Chapter 2), on the frozen 20 postings.

Sampling uses the first five dev postings in frozen order (decided 2026-10-30, before any Claude run),
four fresh conversations each, with the baseline prompt. The experiment asks once per posting per prompt.
Every reply is saved under evidence/claude/. Nothing here changes a hand label.
"""
import csv
import json
from collections import Counter
from datetime import datetime, timezone

from . import claude_judge, rule
from . import config
from .config import ROOT

EXPERIMENT = ROOT / "experiment"


def frozen_jobs():
    """The 20 frozen postings, with their full job objects read back from the saved raw responses."""
    frozen = json.loads((EXPERIMENT / "postings.json").read_text(encoding="utf-8"))
    by_id = {}
    for source in frozen["sources"]:
        for job in json.loads((ROOT / source["file"]).read_text(encoding="utf-8"))["jobs"]:
            by_id[job["id"]] = job
    return [(p, by_id[p["id"]]) for p in frozen["postings"]]


def hand_labels():
    with open(EXPERIMENT / "labels.csv", encoding="utf-8") as f:
        return {int(r["id"]): r["label (Relevant / Not Relevant)"] for r in csv.DictReader(f)}


def verdict_of(record):
    return record["parsed"]["verdict"] if record["valid"] else "invalid"


def sample(resume, prompt_path, times=4, n=5, run=None, out=None):
    out = out or config.CLAUDE_DIR / "sampling"
    labels = hand_labels()
    picked = [(p, j) for p, j in frozen_jobs() if p["split"] == "dev"][:n]
    rows = []
    for posting, job in picked:
        records = []
        for k in range(1, times + 1):
            record = claude_judge.judge(job, resume, prompt_path, **({"run": run} if run else {}))
            claude_judge.save(record, out, f"{job['id']}-run{k}")
            records.append(record)
        rows.append({"posting": posting, "verdicts": [verdict_of(r) for r in records],
                     "reasons": [r["parsed"]["reason"] if r["valid"] else r["error"] for r in records],
                     "hand": labels[job["id"]], "rule": rule.judge(job, resume).verdict})
    return rows


def sampling_table(rows, prompt_name):
    lines = [f"Prompt: `experiment/prompts/{prompt_name}` · model `{claude_judge.MODEL}` · "
             f"{len(rows[0]['verdicts']) if rows else 0} fresh conversations per posting",
             "", "| Job ID | Company | Title | Claude's verdicts | Same every time? | My hand label | Claude's majority = my label? | Rule (record) |",
             "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        counts = Counter(r["verdicts"])
        majority = counts.most_common(1)[0][0]
        p = r["posting"]
        lines.append(f"| {p['id']} | {p['company']} | {p['title']} | {', '.join(r['verdicts'])} | "
                     f"{'yes' if len(counts) == 1 else 'no'} | {r['hand']} | {'yes' if majority == r['hand'] else 'no'} | {r['rule']} |")
    return "\n".join(lines) + "\n"


def run_prompt(resume, prompt_path, split, run=None, out=None):
    out = out or config.CLAUDE_DIR / "experiment"
    labels = hand_labels()
    folder = out / f"{prompt_path.stem}-{split}"
    rows = []
    for posting, job in frozen_jobs():
        if posting["split"] != split:
            continue
        record = claude_judge.judge(job, resume, prompt_path, **({"run": run} if run else {}))
        claude_judge.save(record, folder, str(job["id"]))
        rows.append({"posting": posting, "claude": verdict_of(record), "hand": labels[job["id"]],
                     "rule": rule.judge(job, resume).verdict,
                     "reason": record["parsed"]["reason"] if record["valid"] else record["error"]})
    return rows


def results_table(rows, prompt_name, split):
    n = len(rows)
    passed = sum(r["claude"] == r["hand"] for r in rows)
    invalid = sum(r["claude"] == "invalid" for r in rows)
    always_no = sum(r["hand"] == "Not Relevant" for r in rows)
    rule_agree = sum(r["rule"] == r["hand"] for r in rows)
    at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"## `{prompt_name}` on the {split} set ({at})", "",
             f"- Pass rate (Claude's verdict = my hand label): **{passed}/{n}**",
             f"- Invalid replies (rejected by the validator, counted as a fail): {invalid}",
             f"- For comparison: answering \"Not Relevant\" every time would score {always_no}/{n}; "
             f"the written rule (record) matches my labels on {rule_agree}/{n}",
             "", "| Job ID | Company | Title | Claude (judgment) | My hand label | Pass | Rule (record) | Claude's reason |",
             "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        p = r["posting"]
        reason = r["reason"].replace("|", "/")
        lines.append(f"| {p['id']} | {p['company']} | {p['title']} | {r['claude']} | {r['hand']} | "
                     f"{'yes' if r['claude'] == r['hand'] else 'no'} | {r['rule']} | {reason} |")
    return "\n".join(lines) + "\n"
