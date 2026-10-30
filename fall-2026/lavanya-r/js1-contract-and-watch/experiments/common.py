"""Shared plumbing for the sampling report and the prompt experiment: the
labeled postings, real Claude calls (saved one file per reply), and scoring
against Lavanya's hand labels."""

import json
import os
from concurrent.futures import ThreadPoolExecutor

from agent import claude_judge, persona, rule
from agent.watch import read_saved

RESUME = "persona/priya-nair.resume.json"
SELECTION = "labels/selection.json"
LABELS = "labels/hand_labels.json"
LABEL_TO_VERDICT = {"fit": "relevant", "not_fit": "not_relevant"}


def load_set():
    """(resume, postings by id, labeled items in sheet order)."""
    with open(SELECTION, encoding="utf-8") as f:
        sel = json.load(f)
    with open(LABELS, encoding="utf-8") as f:
        labels = {l["posting_id"]: l for l in json.load(f)["labels"]}
    postings = {p["id"]: p for p in json.loads(read_saved(sel["source"]))["jobs"]}
    items = []
    for n, it in enumerate(sel["items"], 1):
        items.append(dict(it, n=n, label=labels[it["posting_id"]]["label"]))
    return persona.load(RESUME), postings, items


def ask_many(jobs, resume, postings, out_dir, workers=4,
             runner=claude_judge.run_claude):
    """jobs: list of (posting_id, prompt_path, name). Each is one fresh Claude
    call; every record is saved as out_dir/<name>.json. Returns records in
    job order."""
    def one(job):
        pid, prompt, name = job
        rec = claude_judge.judge(postings[pid], resume, prompt, runner=runner)
        claude_judge.save(rec, out_dir, name)
        return rec
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(one, jobs))


def passes(record, label):
    """A Claude reply passes only if it is valid AND matches the hand label."""
    return record["verdict"] == LABEL_TO_VERDICT[label]


def rule_verdict(posting, resume):
    return rule.judge(posting, resume)["verdict"]
