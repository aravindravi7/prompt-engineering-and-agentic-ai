"""Choose the postings used by the sampling report and the prompt experiment.

Deterministic and committed, so that "which 25 postings" is not a thing I can
quietly change after seeing results. Run it and it reproduces the same sets:

    python3 tools/select_experiment_postings.py

The algorithm, stated before the sets were drawn:

1. Classify all 161 postings in the 2026-10-26 saved response by the first gate
   R-v2 fails them on, or ``relevant``.
2. The **sampling set** (5 postings, Chapter 1) is chosen to cover the classes
   the board actually contains, plus one case I care about specifically:
   - the single posting that fails G3_job_family;
   - the lowest-id ``relevant`` posting located in the United States;
   - the lowest-id ``relevant`` posting *not* located in the United States —
     this is the false positive pre-registered in CONTRACT.md §4.2 item 3, and
     I want the model's handling of it on the record;
   - the lowest-id posting that fails G2_discipline;
   - the lowest-id posting that fails G1_title_block.
3. The **experiment set** (20 postings, Chapter 2) is drawn from what is left,
   by lowest id within each class, to the quota
   ``{relevant: 8, G2_discipline: 4, G1_title_block: 8}``.
4. Development / held-out split: within each class, sorted by id, even
   positions go to development and odd positions to held-out. That gives 10 and
   10 with the same class mix in each, and it is arithmetic rather than choice.

Two classes are missing from the experiment set and neither absence is a
convenience: the board has exactly **one** posting that fails G3_job_family and
it is in the sampling set, and **no** posting on this board fails G4_location
at all. Both facts are reported rather than worked around.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from jobagent import fetch, resume as resume_mod, rule as rule_judge  # noqa: E402

SOURCE = ROOT / "evidence" / "raw" / "20261026-reddit-browser-save.json"
OUT = ROOT / "experiments" / "selection.json"

QUOTA = {"relevant": 8, "G2_discipline": 4, "G1_title_block": 8}


def classify(jobs, resume):
    out = {}
    for job in jobs:
        verdict = rule_judge.judge(job, resume)
        out[job["id"]] = verdict["gate_failed"] or "relevant"
    return out


def brief(job, resume):
    family = rule_judge.job_family(job)
    return {
        "id": job["id"],
        "title": job["title"],
        "job_family": family[1] if family else None,
        "location": job["location"]["name"],
        "absolute_url": job["absolute_url"],
        "first_published": job["first_published"],
    }


def main() -> int:
    resume = resume_mod.load(ROOT / "data" / "resume.persona.json")
    jobs = fetch.parse_postings(SOURCE.read_bytes())
    by_id = {j["id"]: j for j in jobs}
    klass = classify(jobs, resume)

    def ids_in(name):
        return sorted(i for i, k in klass.items() if k == name)

    def us(i):
        return "united states" in by_id[i]["location"]["name"].casefold()

    relevant = ids_in("relevant")
    sampling = [
        ids_in("G3_job_family")[0],
        next(i for i in relevant if us(i)),
        next(i for i in relevant if not us(i)),
        ids_in("G2_discipline")[0],
        ids_in("G1_title_block")[0],
    ]

    used = set(sampling)
    experiment, development, heldout = [], [], []
    for name, quota in QUOTA.items():
        picked = [i for i in ids_in(name) if i not in used][:quota]
        if len(picked) < quota:
            raise SystemExit(f"class {name} has only {len(picked)} postings left, need {quota}")
        experiment += picked
        for position, i in enumerate(picked):
            (development if position % 2 == 0 else heldout).append(i)

    payload = {
        "source": SOURCE.name,
        "rule_version": rule_judge.RULE_VERSION,
        "class_sizes": {k: len(ids_in(k)) for k in
                        ("relevant", "G1_title_block", "G2_discipline",
                         "G3_job_family", "G4_location")},
        "sampling_set": [brief(by_id[i], resume) | {"rule_class": klass[i]} for i in sampling],
        "development_set": [brief(by_id[i], resume) | {"rule_class": klass[i]}
                            for i in sorted(development)],
        "heldout_set": [brief(by_id[i], resume) | {"rule_class": klass[i]}
                        for i in sorted(heldout)],
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    print("class sizes:", payload["class_sizes"])
    for name in ("sampling_set", "development_set", "heldout_set"):
        print(f"\n{name} ({len(payload[name])}):")
        for row in payload[name]:
            print(f"  {row['id']}  [{row['rule_class']:15s}] {row['title']}"
                  f"  | {row['job_family']} | {row['location']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
