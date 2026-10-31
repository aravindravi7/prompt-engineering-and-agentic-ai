"""Sampling report (Chapter 1): the same contract, asked about the same 5
postings, 4 times each, each time in a fresh conversation.

    python3 -m experiments.sampling

The 5 postings are the first 3 rule-relevant and first 2 other development
postings in sheet order, so the sample includes postings where the rule and the
hand label disagree. Writes evidence/claude/sampling/ and
experiments/SAMPLING-RESULTS.json.
"""

import collections
import json

from experiments.common import ask_many, load_set, passes, rule_verdict

PROMPT = "prompts/baseline.md"
REPEATS = 4


def pick(items):
    dev = [i for i in items if i["split"] == "dev"]
    rel = [i for i in dev if i["stratum"] == "rule_relevant"][:3]
    other = [i for i in dev if i["stratum"] != "rule_relevant"][:2]
    return sorted(rel + other, key=lambda i: i["n"])


def main():
    resume, postings, items = load_set()
    chosen = pick(items)
    jobs = [(i["posting_id"], PROMPT, f"{i['posting_id']}-{k}")
            for i in chosen for k in range(1, REPEATS + 1)]
    records = ask_many(jobs, resume, postings, "evidence/claude/sampling")
    by_pid = collections.defaultdict(list)
    for rec in records:
        by_pid[rec["posting_id"]].append(rec)
    rows = []
    for i in chosen:
        recs = by_pid[i["posting_id"]]
        verdicts = [r["verdict"] for r in recs]
        rows.append({
            "n": i["n"], "posting_id": i["posting_id"], "title": i["title"],
            "hand_label": i["label"],
            "rule_verdict": rule_verdict(postings[i["posting_id"]], resume),
            "claude_verdicts": verdicts,
            "counts": dict(collections.Counter(verdicts)),
            "unanimous": len(set(verdicts)) == 1,
            "matches_hand_label": sum(passes(r, i["label"]) for r in recs),
            "asked_at": [r["asked_at"] for r in recs],
            "models_used": sorted({m for r in recs for m in r["models_used"]}),
            "errors": [r["errors"] for r in recs if r["errors"]],
        })
    out = {"prompt": PROMPT, "repeats": REPEATS, "rows": rows}
    with open("experiments/SAMPLING-RESULTS.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    for r in rows:
        print(f"#{r['n']:>2} {r['title'][:55]:55} hand={r['hand_label']:8} "
              f"rule={r['rule_verdict']:12} claude={r['counts']} "
              f"match={r['matches_hand_label']}/{REPEATS}")


if __name__ == "__main__":
    main()
