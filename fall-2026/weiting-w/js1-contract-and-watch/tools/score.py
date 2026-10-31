"""Score the recorded judgments against the rule and against the hand labels.

Reads `experiments/results/transcript.json` (the raw model outputs, verbatim),
revalidates every one of them through the agent's own validator, recomputes the
R-v2 verdict for each posting from `evidence/raw/`, and, when
`experiments/labels/labels-L-v1.json` exists, compares both against the hand
labels. Writes `experiments/results/scores.json` and prints a summary.

Three separate numbers are reported for each prompt variant, because they
measure three different things and collapsing them would hide which one failed:

* **validator pass rate** - did the output meet the output contract at all;
* **rule fidelity** - did the model's verdict match what R-v2 computes, which
  is what the prompt actually asks for;
* **hand-label agreement** - did the verdict match my own L-v1 label, which is
  rule quality and model fidelity mixed together.

    python3 tools/score.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from jobagent import claude_judge, fetch, resume as resume_mod, rule as rule_judge  # noqa: E402

RAW = ROOT / "evidence" / "raw" / "20261026-reddit-browser-save.json"
TRANSCRIPT = ROOT / "experiments" / "results" / "transcript.json"
LABELS = ROOT / "experiments" / "labels" / "labels-L-v1.json"
OUT = ROOT / "experiments" / "results" / "scores.json"


def main() -> int:
    resume = resume_mod.load(ROOT / "data" / "resume.persona.json")
    postings = {j["id"]: j for j in fetch.parse_postings(RAW.read_bytes())}
    rows = json.loads(TRANSCRIPT.read_text(encoding="utf-8"))["responses"]

    labels = {}
    if LABELS.exists():
        labels = {
            int(k): v for k, v in
            json.loads(LABELS.read_text(encoding="utf-8"))["labels"].items()
        }

    judged = []
    for row in rows:
        posting = postings[row["posting_id"]]
        wrapped = claude_judge.from_transcript(row, posting, resume)
        rule = rule_judge.judge(posting, resume)
        label = labels.get(row["posting_id"], {}).get("label")
        judged.append(
            {
                "n": row["n"],
                "group": row["group"],
                "variant": row["variant"],
                "rep": row["rep"],
                "posting_id": posting["id"],
                "title": posting["title"],
                "validator": wrapped["validator"],
                "validator_error": wrapped["validator_error"],
                "claude_verdict": wrapped["verdict"],
                "claude_gate": wrapped["gate_failed"],
                "claude_confidence": wrapped["confidence"],
                "rule_verdict": rule["verdict"],
                "rule_gate": rule["gate_failed"],
                "hand_label": label,
                "hand_verdict": (
                    None if label is None
                    else ("relevant" if label == "yes" else "not_relevant")
                ),
            }
        )

    def rate(items, predicate):
        items = list(items)
        if not items:
            return None
        hits = sum(1 for i in items if predicate(i))
        return {"hits": hits, "of": len(items), "rate": round(hits / len(items), 3)}

    def block(items):
        items = list(items)
        valid = [i for i in items if i["validator"] == "pass"]
        labelled = [i for i in valid if i["hand_verdict"] is not None]
        return {
            "n": len(items),
            "validator_pass": rate(items, lambda i: i["validator"] == "pass"),
            "rule_fidelity_verdict": rate(
                valid, lambda i: i["claude_verdict"] == i["rule_verdict"]
            ),
            "rule_fidelity_gate": rate(
                valid, lambda i: i["claude_gate"] == i["rule_gate"]
            ),
            "hand_label_agreement": rate(
                labelled, lambda i: i["claude_verdict"] == i["hand_verdict"]
            ),
            "rule_vs_hand_label": rate(
                labelled, lambda i: i["rule_verdict"] == i["hand_verdict"]
            ),
        }

    sampling = [j for j in judged if j["group"] == "sampling"]
    spread = {}
    for pid in sorted({j["posting_id"] for j in sampling}):
        reps = [j for j in sampling if j["posting_id"] == pid]
        spread[str(pid)] = {
            "title": reps[0]["title"],
            "n_reps": len(reps),
            "verdicts": dict(Counter(j["claude_verdict"] for j in reps)),
            "gates": dict(Counter(str(j["claude_gate"]) for j in reps)),
            "distinct_raw_outputs": len({r["raw"] for r in rows
                                         if r["group"] == "sampling"
                                         and r["posting_id"] == pid}),
            "rule_verdict": reps[0]["rule_verdict"],
            "rule_gate": reps[0]["rule_gate"],
            "hand_label": reps[0]["hand_label"],
            "validator": dict(Counter(j["validator"] for j in reps)),
        }

    experiment = defaultdict(dict)
    for group in ("development", "heldout"):
        for variant in ("baseline", "revision"):
            experiment[group][variant] = block(
                j for j in judged if j["group"] == group and j["variant"] == variant
            )

    scores = {
        "generated_from": {
            "transcript": str(TRANSCRIPT.relative_to(ROOT)),
            "raw_response": str(RAW.relative_to(ROOT)),
            "rule_version": rule_judge.RULE_VERSION,
            "hand_labels_present": bool(labels),
        },
        "sampling": {"spread": spread, "overall": block(sampling)},
        "experiment": dict(experiment),
        "rows": judged,
    }
    OUT.write_text(json.dumps(scores, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"wrote {OUT}")
    print(f"\nhand labels present: {bool(labels)}")
    print("\nSAMPLING (5 postings x 4 fresh contexts, baseline prompt)")
    for pid, s in spread.items():
        print(f"  {pid}  {s['title'][:46]:46s} verdicts={s['verdicts']} "
              f"gates={s['gates']} distinct_raw={s['distinct_raw_outputs']} "
              f"rule={s['rule_verdict']}/{s['rule_gate']} hand={s['hand_label']}")
    print("\nPROMPT EXPERIMENT")
    for group in ("development", "heldout"):
        for variant in ("baseline", "revision"):
            b = experiment[group][variant]
            print(f"  {group:12s} {variant:9s} n={b['n']:2d} "
                  f"validator={b['validator_pass']} "
                  f"rule_verdict={b['rule_fidelity_verdict']} "
                  f"rule_gate={b['rule_fidelity_gate']} "
                  f"hand={b['hand_label_agreement']}")
    print("\nVALIDATOR REJECTIONS")
    for j in judged:
        if j["validator"] == "reject":
            print(f"  #{j['n']} {j['group']}/{j['variant']} posting {j['posting_id']}: "
                  f"{j['validator_error'][:110]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
