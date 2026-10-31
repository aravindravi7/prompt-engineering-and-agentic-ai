"""Score saved Claude replies against the hand labels in experiment/labels.csv. Prints Markdown tables.

    python3 -m tools.score sampling
    python3 -m tools.score experiment [--prompts baseline-v1 revision-v1]

A rejected or failed reply counts as a miss: it is not a verdict.
"""

import argparse
import csv
import gzip
import json
from pathlib import Path

from agent.resume import load_resume
from agent.rule import judge

HERE = Path(__file__).resolve().parent.parent


def load():
    chosen = json.loads((HERE / "experiment" / "postings.json").read_text())
    with open(HERE / "experiment" / "labels.csv", encoding="utf-8") as f:
        labels = {int(row["job_id"]): row for row in csv.DictReader(f)}
    missing = [i for i, row in labels.items() if row["label"].strip() not in ("MATCH", "NOT_MATCH")]
    if missing:
        raise SystemExit("labels.csv: no MATCH/NOT_MATCH label for %s" % missing)
    jobs = {j["id"]: j for j in json.loads(gzip.decompress((HERE / chosen["source"]).read_bytes()))["jobs"]}
    resume = load_resume(HERE / "persona" / "aarav-patel.resume.example.json")
    rule = {p["job_id"]: judge(jobs[p["job_id"]], resume)["verdict"] for p in chosen["postings"]}
    return chosen["postings"], {i: row["label"].strip() for i, row in labels.items()}, rule


def reply(folder, job_id, k):
    path = folder / ("%s-r%d.json" % (job_id, k))
    if not path.exists():
        return None
    record = json.loads(path.read_text())
    return record["verdict"] if record["status"] == "accepted" else "invalid"


def short(verdict):
    return {"MATCH": "M", "NOT_MATCH": "N", "invalid": "×", None: "–"}[verdict]


def sampling(postings, labels, rule):
    folder = HERE / "sampling" / "replies"
    print("| Posting | Hand label | Rule (record) | Claude replies r1–r4 | Same every time? | Agree with hand label |")
    print("|---|---|---|---|---|---|")
    for p in [p for p in postings if p["sampling"]]:
        replies = [reply(folder, p["job_id"], k) for k in range(1, 5)]
        same = "yes" if len(set(replies)) == 1 else "no"
        agree = sum(r == labels[p["job_id"]] for r in replies)
        print("| %s (%s) | %s | %s | %s | %s | %d/4 |" % (p["title"], p["job_id"], labels[p["job_id"]],
              rule[p["job_id"]], " ".join(short(r) for r in replies), same, agree))
    print("\nM = MATCH, N = NOT_MATCH, × = rejected by the validator, – = not asked.")


def experiment(postings, labels, rule, prompts):
    for split in ("development", "held-out"):
        rows = [p for p in postings if p["split"] == split]
        print("\n### %s (%d postings)\n" % (split.capitalize(), len(rows)))
        print("| Posting | Hand label | Rule (record) | %s |" % " | ".join(prompts))
        print("|---|---|---|%s" % "---|" * len(prompts))
        totals = {name: 0 for name in prompts}
        asked = {name: 0 for name in prompts}
        for p in rows:
            cells = []
            for name in prompts:
                r = reply(HERE / "experiment" / "replies" / name, p["job_id"], 1)
                asked[name] += r is not None
                hit = r == labels[p["job_id"]]
                totals[name] += hit
                cells.append("%s %s" % (short(r), "✓" if hit else ("✗" if r else "")))
            print("| %s (%s) | %s | %s %s | %s |" % (p["title"], p["job_id"], labels[p["job_id"]], rule[p["job_id"]],
                  "✓" if rule[p["job_id"]] == labels[p["job_id"]] else "✗", " | ".join(cells)))
        rule_hits = sum(rule[p["job_id"]] == labels[p["job_id"]] for p in rows)
        print("| **Agreement with hand labels** | | **%d/%d** | %s |" % (rule_hits, len(rows), " | ".join(
            ("**%d/%d**" % (totals[n], len(rows))) if asked[n] else "not run" for n in prompts)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("what", choices=["sampling", "experiment"])
    parser.add_argument("--prompts", nargs="+", default=["baseline-v1", "revision-v1"])
    args = parser.parse_args()
    postings, labels, rule = load()
    if args.what == "sampling":
        sampling(postings, labels, rule)
    else:
        experiment(postings, labels, rule, args.prompts)


if __name__ == "__main__":
    main()
