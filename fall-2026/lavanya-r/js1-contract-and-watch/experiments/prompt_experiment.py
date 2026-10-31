"""Prompt experiment (Chapter 2): score one prompt contract on one split of the
hand-labeled set. Each posting is one fresh Claude call.

    python3 -m experiments.prompt_experiment prompts/baseline.md dev
    python3 -m experiments.prompt_experiment prompts/revision.md held_out

A reply passes only if the validator accepts it AND its verdict matches
Lavanya's hand label; INVALID counts as a fail. Writes
evidence/claude/experiment/<prompt>-<split>/ and
experiments/results/<prompt>-<split>.json.
"""

import json
import os
import sys

from experiments.common import ask_many, load_set, passes, rule_verdict


def main(prompt, split):
    resume, postings, items = load_set()
    chosen = [i for i in items if i["split"] == split]
    name = f"{os.path.splitext(os.path.basename(prompt))[0]}-{split}"
    jobs = [(i["posting_id"], prompt, str(i["posting_id"])) for i in chosen]
    records = ask_many(jobs, resume, postings,
                       os.path.join("evidence/claude/experiment", name))
    rows = [{"n": i["n"], "posting_id": i["posting_id"], "title": i["title"],
             "hand_label": i["label"],
             "rule_verdict": rule_verdict(postings[i["posting_id"]], resume),
             "claude_verdict": r["verdict"], "pass": passes(r, i["label"]),
             "errors": r["errors"], "asked_at": r["asked_at"],
             "models_used": r["models_used"]}
            for i, r in zip(chosen, records)]
    out = {"prompt": prompt, "split": split, "n": len(rows),
           "passed": sum(r["pass"] for r in rows),
           "invalid": sum(r["claude_verdict"] == "INVALID" for r in rows),
           "rows": rows}
    os.makedirs("experiments/results", exist_ok=True)
    with open(f"experiments/results/{name}.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    for r in rows:
        print(f"#{r['n']:>2} {r['title'][:55]:55} hand={r['hand_label']:8} "
              f"rule={r['rule_verdict']:12} claude={r['claude_verdict']:12} "
              f"{'PASS' if r['pass'] else 'fail'}")
    print(f"{name}: {out['passed']}/{out['n']} pass, {out['invalid']} INVALID")


if __name__ == "__main__":
    main(*sys.argv[1:3])
