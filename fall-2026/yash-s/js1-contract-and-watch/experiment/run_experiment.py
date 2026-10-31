#!/usr/bin/env python3
"""Prompt experiment (Chapter 2): a baseline prompt and one revision, development then held-out.

Each run judges every posting in one set once and scores it with my pass definition against
my hand labels. The held-out set is guarded: a held-out run needs --final, and each prompt
name gets one held-out run only, so it cannot be used for tuning.

usage (from the js1-contract-and-watch folder):
  python3 experiment/run_experiment.py run --name baseline --prompt prompts/judgment-v1.md --set development
  python3 experiment/run_experiment.py run --name revision --prompt prompts/judgment-v2.md --set development
  python3 experiment/run_experiment.py run --name baseline --prompt prompts/judgment-v1.md --set held_out --final
  python3 experiment/run_experiment.py run --name revision --prompt prompts/judgment-v2.md --set held_out --final
  python3 experiment/run_experiment.py report

`run` makes live Claude calls, one per posting in the set. `report` is offline: it reads every
saved run in experiment/results/ and writes experiment/results/RESULTS.md.
"""
import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import harness as h

SETS = ("development", "held_out")


def run(name, prompt, set_name, out_dir, final=False, model=h.judge.DEFAULT_MODEL, ask=None,
        selection=None, labels=None, raw_dir=h.RUNS):
    if set_name not in SETS:
        raise h.SetupError(f"set must be one of {SETS}")
    if not Path(prompt).is_file():
        raise h.SetupError(f"prompt file {prompt} not found")
    out = Path(out_dir)
    if set_name == "held_out":
        if not final:
            raise h.SetupError("held_out runs need --final: run them once, at the end")
        done = [p.name for p in out.glob(f"{name}-held_out-*.json")]
        if done:
            raise h.SetupError(f"{name!r} already has a held-out run ({done[0]}); held-out runs once per prompt")
    selection = selection or h.load_selection()
    labels = labels or h.load_labels()
    postings, resume = h.load_postings(selection, raw_dir), h.load_resume()
    started = datetime.now(timezone.utc)
    rows = []
    for r in selection[set_name]:
        pid = r["id"]
        j = h.judge.judgment(postings[pid], resume, prompt, model=model, ask=ask)
        rows.append({"posting_id": pid, "title": postings[pid]["title"].strip(), "label": labels[pid]["label"],
                     "outcome": h.outcome(j), "pass": h.is_pass(j, labels[pid]["label"]), "judgment": j})
    result = {
        "kind": "prompt experiment run", "name": name, "set": set_name,
        "started_at": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "finished_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model_requested": model, **h.prompt_info(prompt),
        "models_reported": sorted({m for x in rows for m in x["judgment"]["models_reported"]}),
        "pass_definition": h.PASS_DEFINITION, "labels_sha256": h.sha256_file(h.SHEET),
        "selection_sha256": h.sha256_file(h.SELECTION), "summary": summarize(rows), "rows": rows,
    }
    path = out / f"{name}-{set_name}-{h.stamp(started)}.json"
    h.write_json(path, result)
    return result, path


def summarize(rows):
    c = Counter(x["outcome"] for x in rows)
    return {"postings": len(rows), "passes": sum(x["pass"] for x in rows),
            "labels": dict(Counter(x["label"] for x in rows)),
            "outcomes": {o: c.get(o, 0) for o in ("relevant", "not relevant", "invalid", "unavailable")},
            "claude_relevant_where_i_said_not": sum(x["outcome"] == "relevant" and x["label"] == "not relevant"
                                                    for x in rows),
            "claude_not_relevant_where_i_said_relevant": sum(x["outcome"] == "not relevant" and x["label"] == "relevant"
                                                             for x in rows)}


def report(out_dir):
    out = Path(out_dir)
    runs = sorted((json.loads(p.read_text(encoding="utf-8")) for p in out.glob("*-*-*.json")),
                  key=lambda r: r["started_at"])
    lines = ["# Prompt experiment results", "",
             f"Every saved run in `experiment/results/`, oldest first. {h.PASS_DEFINITION}.", "",
             "| run | set | prompt (sha256) | model reported | passes | relevant | not relevant | invalid | "
             "unavailable | Claude said relevant, I said not | labels in set |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in runs:
        s, o = r["summary"], r["summary"]["outcomes"]
        lines.append(f"| {r['name']} ({r['started_at']}) | {r['set']} | `{Path(r['prompt_file']).name}` "
                     f"(`{r['prompt_sha256'][:8]}`) | {', '.join(r['models_reported']) or 'none'} | "
                     f"**{s['passes']}/{s['postings']}** | {o['relevant']} | {o['not relevant']} | {o['invalid']} | "
                     f"{o['unavailable']} | {s['claude_relevant_where_i_said_not']} | "
                     f"{', '.join(f'{k} {v}' for k, v in s['labels'].items())} |")
    for set_name in SETS:
        these = [r for r in runs if r["set"] == set_name]
        if not these:
            continue
        lines += ["", f"## {set_name}: each posting, each run", "",
                  "| id | title | my label | " + " | ".join(f"{r['name']} {r['started_at'][:16]}" for r in these) + " |",
                  "|---|---|---|" + "---|" * len(these)]
        ids = [x["posting_id"] for x in these[0]["rows"]]
        by_run = [{x["posting_id"]: x for x in r["rows"]} for r in these]
        for pid in ids:
            first = by_run[0][pid]
            cells = [f"{b[pid]['outcome']} ({'pass' if b[pid]['pass'] else 'FAIL'})" for b in by_run]
            lines.append(f"| {pid} | {first['title']} | {first['label']} | " + " | ".join(cells) + " |")
    path = out / "RESULTS.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path, runs


def main(argv=None):
    ap = argparse.ArgumentParser(description="Prompt experiment: baseline and one revision.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--name", required=True, help="baseline or revision")
    r.add_argument("--prompt", required=True)
    r.add_argument("--set", required=True, choices=SETS)
    r.add_argument("--final", action="store_true", help="required for the one held-out run per prompt")
    r.add_argument("--model", default=h.judge.DEFAULT_MODEL)
    for p in (r, sub.add_parser("report")):
        p.add_argument("--out", default=str(h.HERE / "results"))
    a = ap.parse_args(argv)
    try:
        if a.cmd == "run":
            res, path = run(a.name, a.prompt, a.set, a.out, final=a.final, model=a.model)
            s = res["summary"]
            print(f"{a.name} on {a.set}: {s['passes']}/{s['postings']} passes, outcomes {s['outcomes']}")
            print(f"wrote {path}")
        else:
            path, runs = report(a.out)
            print(f"{len(runs)} saved runs; wrote {path}")
    except h.SetupError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
