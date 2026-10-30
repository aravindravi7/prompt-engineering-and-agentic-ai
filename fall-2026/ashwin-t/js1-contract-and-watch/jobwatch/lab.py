"""Tools for the Chapter 1 sampling report and the Chapter 2 prompt experiment.

    python3 -m jobwatch.lab select --seed N [--pool engineering|all]   # fix the 20 postings, before labeling
    python3 -m jobwatch.lab view ID                                    # read one posting; no verdicts shown
    python3 -m jobwatch.lab label                                      # your hand labels, in shuffled order
    python3 -m jobwatch.lab sample [--repeats 4]                       # Ch. 1: fresh Claude calls per posting
    python3 -m jobwatch.lab experiment --prompt P --set dev            # Ch. 2: one prompt on one set
    python3 -m jobwatch.lab experiment --prompt P --set heldout --final
    python3 -m jobwatch.lab summary                                    # pass-rate table from all results

Everything reads postings from one saved raw response (default: the run 1 baseline), never the network.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import random
import re
import subprocess
import sys
import textwrap
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from . import board, judge, rule
from .persona import load_resume

SOURCE = Path("runs/2026-10-30T23-25-13Z/raw-response.json")
EXPERIMENT = Path("experiment")
SELECTION = EXPERIMENT / "selection.json"
PROTOCOL = EXPERIMENT / "LABELING-PROTOCOL.md"
LABELS = EXPERIMENT / "labels.json"
RESULTS = EXPERIMENT / "results"
SAMPLING = Path("sampling")
RESUME = Path("data/supriya-sharma.resume.json")
POOLS = {
    "engineering": "title contains engineer, engineering, developer or sre (a title filter, not the rule)",
    "all": "every posting on the board",
}
_ENGINEERING = re.compile(r"\b(engineer|engineering|developer|sre)\b", re.I)
LABEL_CHOICES = {"r": rule.RELEVANT, "n": rule.NOT_RELEVANT}


class LabError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json(path: Path) -> dict:
    if not path.exists():
        raise LabError(f"{path} does not exist yet")
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_postings(source: Path) -> dict:
    return {rule.posting_id(p): p for p in board.parse_board(Path(source).read_bytes())}


# ---- selection ------------------------------------------------------------------------------

def select(postings: dict, seed: int, pool: str = "engineering", n_dev: int = 10, n_heldout: int = 10) -> dict:
    """Seeded shuffle of the pool; first n_dev are development, the next n_heldout are held out."""
    ids = sorted(postings, key=int)
    if pool == "engineering":
        ids = [i for i in ids if _ENGINEERING.search(postings[i]["title"])]
    if len(ids) < n_dev + n_heldout:
        raise LabError(f"pool {pool!r} has only {len(ids)} postings")
    random.Random(seed).shuffle(ids)
    dev, heldout = ids[:n_dev], ids[n_dev:n_dev + n_heldout]
    return {"seed": seed, "pool": pool, "pool_rule": POOLS[pool], "pool_size": len(ids),
            "dev": dev, "heldout": heldout, "sampling": dev[:5],
            "note": "Chosen by seeded shuffle before any labeling or Claude call; sampling uses dev[:5] "
                    "so no held-out posting is shown to Claude before the end."}


# ---- reading and labeling -------------------------------------------------------------------

def readable(content: Optional[str]) -> str:
    """Posting text for a person: tags removed, paragraphs and list items kept."""
    text = html.unescape(content or "")
    text = re.sub(r"(?i)<\s*li[^>]*>", "\n- ", text)
    text = re.sub(r"(?i)<\s*(br|/p|/h\d|/li|/div|/ul)[^>]*>", "\n", text)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    lines = [re.sub(r"[ \t ]+", " ", line).strip() for line in text.splitlines()]
    out, blank = [], False
    for line in lines:
        if line:
            out.append(textwrap.fill(line, 100, subsequent_indent="  " if line.startswith("- ") else ""))
            blank = False
        elif not blank:
            out.append("")
            blank = True
    return "\n".join(out).strip()


def view(posting: dict) -> str:
    """Only what the posting says. No rule result, no Claude verdict, no set name."""
    offices = ", ".join(o.get("name", "") for o in posting.get("offices") or []) or "none"
    head = [f"id:        {rule.posting_id(posting)}", f"title:     {posting['title']}",
            f"location:  {(posting.get('location') or {}).get('name')}", f"offices:   {offices}",
            f"url:       {posting.get('absolute_url')}", "-" * 100]
    return "\n".join(head) + "\n" + readable(posting.get("content")) + "\n"


def check_protocol(path: Path = PROTOCOL) -> str:
    if not path.exists():
        raise LabError(f"write {path} (your labeling rule) before labeling")
    text = path.read_text(encoding="utf-8")
    if "TODO" in text or len(text.split()) < 40:
        raise LabError(f"{path} still has TODOs or is too short to be a rule someone else could apply")
    return _sha(text.encode())


def label_interactively(postings: dict, selection: dict, labels_path: Path = LABELS,
                        ask: Callable = input, say: Callable = print, protocol_path: Path = PROTOCOL) -> dict:
    protocol_sha = check_protocol(protocol_path)
    labels = _read_json(labels_path) if labels_path.exists() else {
        "protocol_sha256": protocol_sha, "labeler": "Ashwin Thankachan", "labels": {}}
    if labels["protocol_sha256"] != protocol_sha:
        raise LabError("LABELING-PROTOCOL.md changed after labeling started; say why in FRICTIONAL.md and "
                       "start a new labels file instead of mixing rules")
    order = selection["dev"] + selection["heldout"]
    random.Random(f"label-order-{selection['seed']}").shuffle(order)   # dev and held-out interleaved
    todo = [i for i in order if i not in labels["labels"]]
    say(f"{len(order) - len(todo)} of {len(order)} labeled. Answer r (relevant), n (not relevant) or q (quit).")
    for k, pid in enumerate(todo, 1):
        say("\n" + "=" * 100 + f"\nPosting {k} of {len(todo)} remaining\n" + view(postings[pid]))
        choice = ""
        while choice not in ("r", "n", "q"):
            choice = ask("Label [r/n/q]: ").strip().lower()
        if choice == "q":
            break
        reason = ""
        while not reason:
            reason = ask("One-line reason (which part of your labeling rule decided it): ").strip()
        labels["labels"][pid] = {"label": LABEL_CHOICES[choice], "reason": reason, "labeled_at": _now()}
        _write_json(labels_path, labels)
    return labels


def require_labels(ids: list, labels_path: Path = LABELS) -> dict:
    labels = _read_json(labels_path)["labels"]
    missing = [i for i in ids if i not in labels]
    if missing:
        raise LabError(f"hand-label these first: {missing}")
    return labels


# ---- Claude calls ---------------------------------------------------------------------------

def _ask_many(jobs: list, caller: Callable, workers: int) -> list:
    """jobs: (posting, prompt text). Each call is its own fresh `claude -p` session."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda job: caller(job[1]), jobs))


def _graded(posting: dict, resume: dict, result: dict) -> dict:
    if not result.get("ok"):
        return {"status": judge.CALL_FAILED, "verdict": None, "errors": [result.get("error")]}
    reply, errors = judge.validate_reply(result["text"], posting, resume)
    if errors:
        return {"status": judge.VALIDATION_FAILED, "verdict": None, "errors": errors}
    return {"status": judge.VALID, "verdict": reply["verdict"], "reason": reply["reason"], "errors": []}


def _save_replies(folder: Path, rows: list) -> None:
    (folder / "replies").mkdir(parents=True, exist_ok=True)
    for row in rows:
        if row.get("raw_reply") is not None:
            (folder / "replies" / f"{row['reply_file']}").write_text(row["raw_reply"], encoding="utf-8")


def _git_head() -> Optional[str]:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def sample(postings: dict, resume: dict, ids: list, labels: dict, prompt_path: Path, repeats: int,
           caller: Callable, out_root: Path = SAMPLING, workers: int = 4) -> Path:
    name, template = judge.load_prompt(prompt_path)
    jobs = [(postings[i], judge.build_prompt(template, postings[i], resume)) for i in ids for _ in range(repeats)]
    results = _ask_many(jobs, caller, workers)
    rows = []
    for (posting, _), k, result in zip(jobs, [k for _ in ids for k in range(1, repeats + 1)], results):
        pid = rule.posting_id(posting)
        rows.append({"posting_id": pid, "ask": k, "called_at": result.get("called_at"), "model": result.get("model"),
                     "reply_file": f"{pid}-{k}.txt", "raw_reply": result.get("text"),
                     **_graded(posting, resume, result)})
    per = []
    for pid in ids:
        mine = [r for r in rows if r["posting_id"] == pid]
        verdicts = [r["verdict"] or "INVALID" for r in mine]
        hand = labels[pid]["label"]
        per.append({"posting_id": pid, "title": postings[pid]["title"], "hand_label": hand,
                    "rule_record": rule.classify(postings[pid], resume)["verdict"], "verdicts": verdicts,
                    "agree_with_hand": sum(v == hand for v in verdicts), "asks": len(verdicts),
                    "unanimous": len(set(verdicts)) == 1})
    folder = out_root / datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    _save_replies(folder, rows)
    report = {"kind": "sampling (Chapter 1)", "prompt": name, "prompt_sha256": _sha(Path(prompt_path).read_bytes()),
              "git_head": _git_head(), "repeats": repeats, "postings": per,
              "calls": [{k: v for k, v in r.items() if k != "raw_reply"} for r in rows]}
    _write_json(folder / "results.json", report)
    (folder / "report.md").write_text(render_sampling(report), encoding="utf-8")
    return folder


def render_sampling(report: dict) -> str:
    out = [f"# Sampling report data: prompt `{report['prompt']}`, {report['repeats']} fresh asks per posting", "",
           "Every verdict below is a real `claude -p` reply saved in `replies/`. These are AI JUDGMENTS.", "",
           "| posting | title | my hand label | rule record | Claude verdicts | agree with me | unanimous |",
           "|---|---|---|---|---|---:|:-:|"]
    for p in report["postings"]:
        out.append(f"| {p['posting_id']} | {p['title']} | {p['hand_label']} | {p['rule_record']} | "
                   f"{', '.join(p['verdicts'])} | {p['agree_with_hand']}/{p['asks']} | {'yes' if p['unanimous'] else 'no'} |")
    calls = report["calls"]
    out += ["", f"Calls: {len(calls)} · valid {sum(c['status'] == judge.VALID for c in calls)} · "
                f"models: {', '.join(sorted({c['model'] or '?' for c in calls}))} · "
                f"first {min(c['called_at'] or '' for c in calls)} · last {max(c['called_at'] or '' for c in calls)}", ""]
    return "\n".join(out)


def _prompts_committed(prompt_path: Path) -> bool:
    try:
        dirty = subprocess.run(["git", "status", "--porcelain", "--", str(prompt_path), str(LABELS), str(SELECTION)],
                               capture_output=True, text=True, check=True).stdout.strip()
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(prompt_path)],
                                 capture_output=True, text=True).returncode == 0
    except (OSError, subprocess.CalledProcessError):
        return False
    return tracked and not dirty


def experiment(postings: dict, resume: dict, selection: dict, labels: dict, prompt_path: Path, which: str,
               caller: Callable, final: bool = False, out_root: Path = RESULTS, workers: int = 4,
               committed: Callable = _prompts_committed) -> Path:
    if which == "heldout":
        if not final:
            raise LabError("held-out is the last step: pass --final once both prompts are frozen")
        if not committed(prompt_path):
            raise LabError("commit the prompt, labels and selection before the held-out run, so the order is provable")
    ids = selection[which]
    for i in ids:
        if i not in labels:
            raise LabError(f"posting {i} has no hand label")
    name, template = judge.load_prompt(prompt_path)
    jobs = [(postings[i], judge.build_prompt(template, postings[i], resume)) for i in ids]
    results = _ask_many(jobs, caller, workers)
    rows = []
    for pid, result in zip(ids, results):
        g = _graded(postings[pid], resume, result)
        rows.append({"posting_id": pid, "title": postings[pid]["title"], "hand_label": labels[pid]["label"],
                     "rule_record": rule.classify(postings[pid], resume)["verdict"],
                     "called_at": result.get("called_at"), "model": result.get("model"),
                     "reply_file": f"{pid}.txt", "raw_reply": result.get("text"),
                     "pass": g["status"] == judge.VALID and g["verdict"] == labels[pid]["label"], **g})
    folder = out_root / f"{name}-{which}-{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%SZ')}"
    _save_replies(folder, rows)
    report = {"kind": "prompt experiment (Chapter 2)", "prompt": name, "set": which,
              "prompt_sha256": _sha(Path(prompt_path).read_bytes()), "git_head": _git_head(),
              "passed": sum(r["pass"] for r in rows), "total": len(rows),
              "invalid": sum(r["status"] != judge.VALID for r in rows),
              "rule_agrees_with_hand": sum(r["rule_record"] == r["hand_label"] for r in rows),
              "pass_rule": "valid reply AND verdict == my hand label; an invalid reply counts as a fail",
              "rows": [{k: v for k, v in r.items() if k != "raw_reply"} for r in rows]}
    _write_json(folder / "results.json", report)
    (folder / "report.md").write_text(render_experiment(report), encoding="utf-8")
    return folder


def render_experiment(report: dict) -> str:
    out = [f"# Prompt `{report['prompt']}` on the {report['set']} set: {report['passed']}/{report['total']} pass", "",
           f"Pass rule: {report['pass_rule']}. Invalid replies: {report['invalid']}. "
           f"For comparison, the written rule agrees with my hand label on {report['rule_agrees_with_hand']}/{report['total']}.",
           "", "| posting | title | my label | rule | Claude (AI JUDGMENT) | pass |", "|---|---|---|---|---|:-:|"]
    for r in report["rows"]:
        out.append(f"| {r['posting_id']} | {r['title']} | {r['hand_label']} | {r['rule_record']} | "
                   f"{r['verdict'] or r['status']} | {'yes' if r['pass'] else 'no'} |")
    return "\n".join(out) + "\n"


def summary(root: Path = RESULTS) -> str:
    rows = [json.loads(p.read_text()) for p in sorted(root.glob("*/results.json"))]
    out = ["| prompt | set | pass | invalid | rule agrees with me | git head |", "|---|---|---:|---:|---:|---|"]
    out += [f"| {r['prompt']} | {r['set']} | {r['passed']}/{r['total']} | {r['invalid']} | "
            f"{r['rule_agrees_with_hand']}/{r['total']} | {(r['git_head'] or '?')[:7]} |" for r in rows]
    return "\n".join(out)


# ---- CLI ------------------------------------------------------------------------------------

def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(prog="python3 -m jobwatch.lab", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--source", type=Path, default=SOURCE, help="saved raw Greenhouse response to read postings from")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select")
    s.add_argument("--seed", type=int, required=True)
    s.add_argument("--pool", choices=sorted(POOLS), default="engineering")
    v = sub.add_parser("view")
    v.add_argument("posting_id")
    sub.add_parser("label")
    sm = sub.add_parser("sample")
    sm.add_argument("--repeats", type=int, default=4)
    sm.add_argument("--prompt", type=Path, default=Path("prompts/baseline-v1.md"))
    sm.add_argument("--model")
    ex = sub.add_parser("experiment")
    ex.add_argument("--prompt", type=Path, required=True)
    ex.add_argument("--set", choices=["dev", "heldout"], required=True)
    ex.add_argument("--final", action="store_true")
    ex.add_argument("--model")
    sub.add_parser("summary")
    args = ap.parse_args(argv)

    try:
        postings = load_postings(args.source)
        if args.cmd == "select":
            if SELECTION.exists():
                raise LabError(f"{SELECTION} already exists; the selection is fixed once made")
            sel = {**select(postings, args.seed, args.pool), "source": str(args.source),
                   "source_sha256": _sha(args.source.read_bytes()), "selected_at": _now()}
            _write_json(SELECTION, sel)
            print(f"Wrote {SELECTION}: pool {sel['pool']} ({sel['pool_size']}), seed {sel['seed']}, "
                  f"10 dev + 10 held-out. Commit it before labeling.")
        elif args.cmd == "view":
            print(view(postings[args.posting_id]))
        elif args.cmd == "label":
            labels = label_interactively(postings, _read_json(SELECTION))
            print(f"\n{len(labels['labels'])} labels saved in {LABELS}.")
        elif args.cmd == "summary":
            print(summary())
        else:
            resume = load_resume(RESUME)
            caller = lambda prompt: judge.call_claude(prompt, model=args.model)
            selection = _read_json(SELECTION)
            if args.cmd == "sample":
                labels = require_labels(selection["sampling"])
                folder = sample(postings, resume, selection["sampling"], labels, args.prompt, args.repeats, caller)
            else:
                labels = require_labels(selection[args.set])
                folder = experiment(postings, resume, selection, labels, args.prompt, args.set, caller, args.final)
            print((folder / "report.md").read_text())
            print(f"Saved in {folder}")
    except (LabError, board.BoardError, KeyError, OSError) as exc:
        print(f"STOPPED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
