"""Freeze the 20 postings and the 10/10 split for the prompt experiment, before Claude sees any of them.

Selection (decided 2026-10-29, written down before this ran):
  1. From the baseline raw response, keep jobs whose title has "Engineer" plus a role word (rule 1)
     and whose location has United States, USA or US (rule 4).
  2. Group A: those whose title has no experience word (rule 3). Group B: the rest. Each sorted by job ID.
  3. Take all of group A, then group B, until there are 20. If fewer than 20, add other jobs by job ID.
  4. Walk that list in order and alternate dev, held-out, dev, held-out.
No verdict is computed or saved here: the hand labels come first.
"""
import csv
import hashlib
import json
from datetime import datetime, timezone

from . import rule
from .config import ROOT

EXPERIMENT = ROOT / "experiment"
LABEL_COLUMNS = ["id", "split", "title", "location", "role (Y/N)", "skills found", "experience (Y/N)",
                 "location (Y/N)", "label (Relevant / Not Relevant)", "labelled on", "notes"]


def is_candidate(job):
    title, location = job.get("title", ""), (job.get("location") or {}).get("name", "")
    return bool(rule.find_words(title, ("Engineer",)) and rule.find_words(title, rule.ROLE_WORDS)
                and rule.find_words(location, rule.US_WORDS))


def select(jobs, n=20):
    candidates = [j for j in jobs if is_candidate(j)]
    group_a = sorted((j for j in candidates if not rule.find_words(j["title"], rule.EXPERIENCE_WORDS)), key=lambda j: j["id"])
    group_b = sorted((j for j in candidates if rule.find_words(j["title"], rule.EXPERIENCE_WORDS)), key=lambda j: j["id"])
    chosen = [(j, "A") for j in group_a] + [(j, "B") for j in group_b]
    if len(chosen) < n:
        others = sorted((j for j in jobs if not is_candidate(j)), key=lambda j: j["id"])
        chosen += [(j, "other") for j in others]
    return [(j, group, "dev" if i % 2 == 0 else "held-out") for i, (j, group) in enumerate(chosen[:n])]


def freeze(raw_path, out=EXPERIMENT, now=None):
    raw = raw_path.read_bytes()
    jobs = json.loads(raw)["jobs"]
    picked = select(jobs)
    now = now or datetime.now(timezone.utc).replace(microsecond=0)
    (out / "postings").mkdir(parents=True, exist_ok=True)
    rows = []
    for job, group, split in picked:
        location = (job.get("location") or {}).get("name", "")
        text = rule.description_text(job)
        (out / "postings" / f"{job['id']}.txt").write_text(
            f"Job ID: {job['id']}\nSplit: {split}\nTitle: {job['title']}\nLocation: {location}\n"
            f"URL: {job.get('absolute_url', '')}\n\nDescription (plain text from the saved raw response):\n\n{text}\n",
            encoding="utf-8")
        rows.append({"id": job["id"], "split": split, "group": group, "title": job["title"], "location": location,
                     "url": job.get("absolute_url", ""), "first_published": job.get("first_published"),
                     "description_sha256": hashlib.sha256(text.encode()).hexdigest()})
    frozen = {"frozen_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "source": str(raw_path.relative_to(ROOT)),
              "source_sha256": hashlib.sha256(raw).hexdigest(), "selection": __doc__.strip(), "postings": rows}
    (out / "postings.json").write_text(json.dumps(frozen, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with open(out / "labels.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(LABEL_COLUMNS)
        for r in rows:
            writer.writerow([r["id"], r["split"], r["title"], r["location"]] + [""] * (len(LABEL_COLUMNS) - 4))
    return frozen
