"""Pick the 20 prompt-experiment postings and the 5 sampling postings from run 1's saved response.

The method was fixed before anyone labeled anything:
- Pool: every posting in run 1's raw response, except
  - the 9 first published on or after 2026-10-30 (Claude judges those in seeded run B, before any hand
    labels exist), and
  - 5440427008 (Claude judged it in a practice run).
- Stratum A: postings that pass Rules 1-3 (listed engineering title, no seniority word, US location).
  Stratum B: all the others. A random 20 from the whole board would be almost all sales, finance and
  research roles, every label would be "not a fit", and the experiment could show nothing.
- Draw 10 from each stratum with random.Random(7375). In each stratum the first 5 drawn are development
  and the next 5 are held-out.
- Sampling report: the first 3 development postings of stratum A and the first 2 of stratum B.

The sheet shows each posting's own words (title, location, department, the role section of the
description) and no rule verdicts, so the hand labels are not anchored on the rule.

    python3 tools/select_experiment.py
"""

import csv
import gzip
import html
import json
import random
import re
from pathlib import Path

from agent.resume import load_resume
from agent.rule import description_text, judge

HERE = Path(__file__).resolve().parent.parent
RUN1_RAW = HERE / "evidence" / "raw" / "anthropic-2026-10-31T074011Z.json.gz"
RESUME = HERE / "persona" / "aarav-patel.resume.example.json"
OUT = HERE / "experiment"
SEED = 7375
EXCLUDED = {5440427008}


def readable(content):
    """The description with its paragraphs and bullet lists kept, for a person to read."""
    markup = html.unescape(content or "")
    markup = re.sub(r"(?i)<li[^>]*>", "\n- ", markup)
    markup = re.sub(r"(?i)</(p|li|ul|ol|div|h\d)>|<br\s*/?>", "\n", markup)
    lines = [re.sub(r"[ \t\xa0]+", " ", html.unescape(line)).strip() for line in re.sub(r"<[^>]+>", " ", markup).split("\n")]
    text = "\n".join(line for line in lines if line and line != "-")
    return re.sub(r"(?m)^(You may be a good fit if you.*|Strong candidates may also.*|About the role.*)$", r"\n**\1**\n", text)


def role_section(content):
    text = readable(content)
    start = text.find("**About the role")
    end = min([i for i in (text.find("The annual compensation"), text.find("Logistics")) if i > 0] or [len(text)])
    return text[start if start >= 0 else 0:end].strip()


def main():
    resume = load_resume(RESUME)
    jobs = json.loads(gzip.decompress(RUN1_RAW.read_bytes()))["jobs"]
    pool = [j for j in jobs if j["first_published"][:10] < "2026-10-30" and j["id"] not in EXCLUDED]
    pool.sort(key=lambda j: j["id"])
    a = [j for j in pool if all(c["passed"] for c in judge(j, resume)["checks"][:3])]
    b = [j for j in pool if j not in a]
    rng = random.Random(SEED)
    chosen = []
    for stratum, group in (("A", a), ("B", b)):
        for i, job in enumerate(rng.sample(group, 10)):
            split = "development" if i < 5 else "held-out"
            chosen.append({"job_id": job["id"], "stratum": stratum, "split": split,
                           "sampling": split == "development" and i < (3 if stratum == "A" else 2),
                           "title": job["title"], "location": job["location"]["name"],
                           "absolute_url": job["absolute_url"], "job": job})
    chosen.sort(key=lambda c: (c["split"] != "development", c["job_id"]))

    OUT.mkdir(exist_ok=True)
    (OUT / "postings.json").write_text(json.dumps(
        {"source": RUN1_RAW.relative_to(HERE).as_posix(), "seed": SEED, "pool": len(pool),
         "stratum_sizes": {"A": len(a), "B": len(b)},
         "postings": [{k: v for k, v in c.items() if k != "job"} for c in chosen]}, indent=2) + "\n")

    if not (OUT / "labels.csv").exists():  # never overwrite labels someone has started
        with open(OUT / "labels.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["n", "job_id", "split", "title", "label", "note"])
            for n, c in enumerate(chosen, 1):
                writer.writerow([n, c["job_id"], c["split"], c["title"], "", ""])

    lines = ["# Labeling sheet: 20 real postings from run 1 (2026-10-31 07:40 UTC)", "",
             "Selected by `tools/select_experiment.py` (seed %d). Label each one in `labels.csv` with `MATCH` "
             "or `NOT_MATCH` by **your labeling rule**, plus a short note on why. The rule's verdicts are "
             "deliberately not shown." % SEED, ""]
    for n, c in enumerate(chosen, 1):
        job = c["job"]
        lines += ["---", "", "## %d. %s" % (n, job["title"]), "",
                  "- **id:** %s (%s)" % (job["id"], c["split"]),
                  "- **Location:** %s" % job["location"]["name"],
                  "- **Department:** %s" % ", ".join(d["name"] for d in job.get("departments", [])),
                  "- **Link:** %s" % job["absolute_url"], "", role_section(job["content"]), ""]
    (OUT / "labeling-sheet.md").write_text("\n".join(lines), encoding="utf-8")
    print("pool %d (A %d, B %d); wrote experiment/postings.json, labels.csv, labeling-sheet.md" % (len(pool), len(a), len(b)))
    for c in chosen:
        print("  %-11s %s %s%s  %s" % (c["split"], c["stratum"], c["job_id"], " [sampling]" if c["sampling"] else "", c["title"]))


if __name__ == "__main__":
    main()
