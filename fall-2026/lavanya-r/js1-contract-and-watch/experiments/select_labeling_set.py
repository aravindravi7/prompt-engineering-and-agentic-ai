"""Pick the 20 real postings to hand-label, reproducibly, and split them into
10 development and 10 held-out.

    python3 -m experiments.select_labeling_set

Source: run 2's saved raw response; run 2's 10 new postings are excluded so
the labeled set does not overlap the watch's own output. Strata (8 rule-
relevant, 8 that fail exactly one check, 4 from everything else) keep the set
from being all "not fit"; the stratum is hidden from the labeling sheet.
"""

import json
import random
import re

from agent import persona, rule
from agent.watch import read_saved

RAW = "evidence/raw/databricks-2026-10-30T204649Z.json.gz"
RUN2 = "reports/run-databricks-2026-10-30T204649Z.json"
SEED = 7375
TAKE = {"rule_relevant": 8, "misses_one_check": 8, "other": 4}


def stratum(verdict):
    misses = sum(not c["passed"] for c in verdict["justification"])
    return ("rule_relevant" if misses == 0 else
            "misses_one_check" if misses == 1 else "other")


def requirement_lines(posting, limit=6):
    """Sentences that say what the job expects (years, degrees, level)."""
    text = rule.description_text(posting)
    sents = re.split(r"(?<=[.!?])\s+|\s+(?=[•\-–] )", text)
    pat = re.compile(r"\b(\d+\+? years?|years of|experience|degree|BS|MS|"
                     r"PhD|Bachelor|Master|new grad|graduate)\b", re.I)
    return [s.strip()[:220] for s in sents if pat.search(s)][:limit]


def main():
    resume = persona.load("persona/priya-nair.resume.json")
    jobs = json.loads(read_saved(RAW))["jobs"]
    with open(RUN2, encoding="utf-8") as f:
        exclude = set(json.load(f)["run"]["new_ids"])
    pools = {k: [] for k in TAKE}
    for p in sorted(jobs, key=lambda p: p["id"]):
        if p["id"] not in exclude:
            pools[stratum(rule.judge(p, resume))].append(p)

    rng = random.Random(SEED)
    picked = []
    for name, n in TAKE.items():
        for p in rng.sample(pools[name], n):
            picked.append((name, p))
    rng.shuffle(picked)
    # Alternate within each stratum so dev and held-out get the same mix.
    seen = {k: 0 for k in TAKE}
    items = []
    for name, p in picked:
        split = "dev" if seen[name] % 2 == 0 else "held_out"
        seen[name] += 1
        items.append({"posting_id": p["id"], "title": p["title"],
                      "location": p["location"]["name"],
                      "url": p.get("absolute_url"), "stratum": name,
                      "split": split})
    with open("labels/selection.json", "w", encoding="utf-8") as f:
        json.dump({"source": RAW, "seed": SEED, "take": TAKE,
                   "pool_sizes": {k: len(v) for k, v in pools.items()},
                   "items": items}, f, indent=2, ensure_ascii=False)
        f.write("\n")

    by_id = {p["id"]: p for _, p in picked}
    out = ["# Labeling sheet — 20 real Databricks postings (2026-10-30)", "",
           "Label each **fit** or **not fit** using labels/LABELING-RULE.md. "
           "Rule and Claude verdicts are deliberately not shown here.", ""]
    for n, it in enumerate(items, 1):
        p = by_id[it["posting_id"]]
        out += [f"## {n}. {it['title']}",
                f"- **Location:** {it['location']}",
                f"- **Posting:** {it['url']}",
                f"- **id:** {it['posting_id']}",
                "- **What it asks for (excerpt):**"]
        out += [f"  - {s}" for s in requirement_lines(p)] or ["  - (none found)"]
        out.append("")
    with open("labels/LABELING-SHEET.md", "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(json.dumps({k: len(v) for k, v in pools.items()}),
          "->", len(items), "items")


if __name__ == "__main__":
    main()
