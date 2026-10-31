#!/usr/bin/env python3
"""Sampling report (Chapter 1): ask Claude about the same postings several times.

Each of the 5 sampling postings in experiment/selection.json is judged --repeats times
(at least 4). Every call is a fresh conversation: judge.call_claude saves no session and
runs from a new empty folder. Each answer is compared with my hand label under my pass
definition. Repeating a verdict shows repeatability, not correctness.

usage (from the js1-contract-and-watch folder):
  python3 experiment/sample.py --repeats 4 --prompt prompts/judgment-v1.md --model claude-sonnet-5-5

Writes experiment/sampling/sampling-<UTC time>.json (every answer, raw text included) and a
Markdown table next to it. This makes live Claude calls: 5 x repeats of them.
"""
import argparse
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import harness as h

OUTCOMES = ("relevant", "not relevant", "invalid", "unavailable")


def sample(repeats, prompt, model, out_dir, ask=None, selection=None, labels=None, raw_dir=h.RUNS):
    if repeats < 4:
        raise h.SetupError("the brief asks for at least 4 fresh runs per posting")
    if not Path(prompt).is_file():
        raise h.SetupError(f"prompt file {prompt} not found")
    selection = selection or h.load_selection()
    labels = labels or h.load_labels()
    postings, resume = h.load_postings(selection, raw_dir), h.load_resume()
    ids = [r["id"] for r in selection["sampling"]]
    started = datetime.now(timezone.utc)
    calls = []
    for pid in ids:
        for n in range(1, repeats + 1):
            j = h.judge.judgment(postings[pid], resume, prompt, model=model, ask=ask)
            calls.append({"posting_id": pid, "repeat": n, "label": labels[pid]["label"],
                          "outcome": h.outcome(j), "pass": h.is_pass(j, labels[pid]["label"]), "judgment": j})
    per_posting = []
    for pid in ids:
        mine = [c for c in calls if c["posting_id"] == pid]
        counts = Counter(c["outcome"] for c in mine)
        per_posting.append({
            "posting_id": pid, "title": postings[pid]["title"].strip(), "label": labels[pid]["label"],
            "outcomes": [c["outcome"] for c in mine], "counts": {o: counts.get(o, 0) for o in OUTCOMES},
            "distinct_outcomes": len(counts), "most_common_share": counts.most_common(1)[0][1] / len(mine),
            "passes": sum(c["pass"] for c in mine), "runs": len(mine)})
    result = {
        "kind": "sampling report", "started_at": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "finished_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repeats": repeats, "model_requested": model, **h.prompt_info(prompt),
        "models_reported": sorted({m for c in calls for m in c["judgment"]["models_reported"]}),
        "pass_definition": h.PASS_DEFINITION, "labels_file": "experiment/LABELING-SHEET.md",
        "labels_sha256": h.sha256_file(h.SHEET), "selection_sha256": h.sha256_file(h.SELECTION),
        "summary": {"calls": len(calls), "passes": sum(c["pass"] for c in calls),
                    "outcomes": {o: sum(c["outcome"] == o for c in calls) for o in OUTCOMES},
                    "postings_with_more_than_one_outcome": sum(p["distinct_outcomes"] > 1 for p in per_posting)},
        "per_posting": per_posting, "calls": calls,
    }
    out = Path(out_dir)
    base = out / f"sampling-{h.stamp(started)}"
    h.write_json(base.with_suffix(".json"), result)
    base.with_suffix(".md").write_text(markdown(result), encoding="utf-8")
    return result, base


def markdown(r):
    s = r["summary"]
    lines = [
        f"# Sampling report data, {r['started_at']}",
        "",
        f"- Prompt: `{r['prompt_file']}` (sha256 `{r['prompt_sha256'][:12]}...`); model requested "
        f"`{r['model_requested']}`, reported {r['models_reported'] or 'none'}",
        f"- {len(r['per_posting'])} postings x {r['repeats']} fresh calls = {s['calls']} calls",
        f"- {r['pass_definition']}",
        f"- Passes: **{s['passes']} of {s['calls']}**. Outcomes: " +
        ", ".join(f"{o} {n}" for o, n in s["outcomes"].items()),
        f"- Postings whose answers were not all the same: {s['postings_with_more_than_one_outcome']} of "
        f"{len(r['per_posting'])}",
        "",
        "| id | title | my label | " + " | ".join(f"run {i}" for i in range(1, r["repeats"] + 1)) +
        " | passes | same answer every time? |",
        "|---|---|---|" + "---|" * r["repeats"] + "---|---|",
    ]
    for p in r["per_posting"]:
        lines.append(f"| {p['posting_id']} | {p['title']} | {p['label']} | " + " | ".join(p["outcomes"]) +
                     f" | {p['passes']}/{p['runs']} | {'yes' if p['distinct_outcomes'] == 1 else 'no'} |")
    lines += ["", "Claude's reasons, per call:", ""]
    for c in r["calls"]:
        j = c["judgment"]
        why = j["answer"]["reason"] if j["status"] == "valid" else "; ".join(j["errors"])
        lines.append(f"- {c['posting_id']} run {c['repeat']}: **{c['outcome']}**. {why}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Sampling report: repeated fresh Claude judgments.")
    ap.add_argument("--repeats", type=int, default=4)
    ap.add_argument("--prompt", default="prompts/judgment-v1.md")
    ap.add_argument("--model", default=h.judge.DEFAULT_MODEL)
    ap.add_argument("--out", default=str(h.HERE / "sampling"))
    a = ap.parse_args(argv)
    try:
        r, base = sample(a.repeats, a.prompt, a.model, a.out)
    except h.SetupError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    s = r["summary"]
    print(f"{s['calls']} calls, {s['passes']} passes, outcomes {s['outcomes']}")
    for p in r["per_posting"]:
        print(f"  {p['posting_id']}  label {p['label']:13} answers {p['outcomes']}")
    print(f"wrote {base.with_suffix('.json')} and {base.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
