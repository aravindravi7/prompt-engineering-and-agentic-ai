#!/usr/bin/env python3
"""Pick the postings for the prompt experiment and the sampling report.

Follows experiment/LABELING-RULE.md, decisions 5-8 and the choices accepted from Claude:
  development + held-out: 10 "hard cases" (topic word in the title, a US location, no
  seniority word in the title) and 10 postings without a topic word, picked at random;
  each group is split 5 / 5 between development and held-out.
  sampling report: 5 more postings with a topic word, picked at random, none overlapping the 20.
Every group has one posting per title. Same input file and seed give the same output.

usage (from the js1-contract-and-watch folder):
  python3 experiment/select_postings.py runs/raw-databricks-2026-10-29T005656Z.json --seed 7375

Writes experiment/selection.json and experiment/LABELING-SHEET.md.
Offline, Python 3 standard library only. It reads one saved board response and asks nobody.
"""
import argparse
import hashlib
import json
import random
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import judge  # noqa: E402

TOPIC_WORDS = ("AI", "ML", "GenAI", "machine learning", "data")                     # decision 8
SENIORITY_WORDS = ("Senior", "Sr.", "Sr", "Staff", "Principal", "Lead", "Manager", "Director")   # decisions 1, 6
US_STATES = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
    "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
    "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
    "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
    "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"}
DC = {"Washington, D.C.", "Washington D.C.", "District of Columbia"}
UNCLEAR = {"USCA"}                                     # could be US and Canada: not counted as US, shown as unclear


def us_part(part):
    p = re.sub(r"^remote\s*-\s*", "", part.strip(), flags=re.I)
    return ("united states" in p.lower() or p in DC or p in US_STATES
            or p.rsplit(",", 1)[-1].strip() in US_STATES)


def location_class(name):
    """'US' if any listed place is in the United States, 'unclear', or 'not US'."""
    parts = [x.strip() for x in (name or "").split(";") if x.strip()]
    if any(us_part(x) for x in parts):
        return "US"
    if any(x in UNCLEAR for x in parts):
        return "unclear"
    return "not US"


def words_in(title, words):
    return [w for w in words if judge.has_phrase(w, title)]


def describe(j):
    title, loc = (j.get("title") or "").strip(), judge.location_name(j)
    return {"id": j["id"], "title": title, "location": loc, "location_class": location_class(loc),
            "topic_words": words_in(title, TOPIC_WORDS), "seniority_words": words_in(title, SENIORITY_WORDS),
            "absolute_url": j.get("absolute_url")}


def one_per_title(rows):
    """Lowest id per title, so a title repeated across locations is used once."""
    best = {}
    for r in sorted(rows, key=lambda r: r["id"]):
        best.setdefault(r["title"].lower(), r)
    return sorted(best.values(), key=lambda r: r["id"])


def select(jobs, seed):
    rows = [describe(j) for j in {j["id"]: j for j in jobs}.values()]
    hard_pool = one_per_title([r for r in rows if r["topic_words"] and r["location_class"] == "US"
                               and not r["seniority_words"]])
    other_pool = one_per_title([r for r in rows if not r["topic_words"]])
    rng = random.Random(seed)
    hard = rng.sample(hard_pool, 10) if len(hard_pool) > 10 else list(hard_pool)
    rng.shuffle(hard)
    other = rng.sample(other_pool, 10)
    used_titles = {r["title"].lower() for r in hard + other}
    sampling_pool = one_per_title([r for r in rows if r["topic_words"] and r["title"].lower() not in used_titles])
    sampling = rng.sample(sampling_pool, 5)
    for r in hard:
        r["picked_as"] = "hard case: topic word, US location, no seniority word"
    for r in other:
        r["picked_as"] = "random: no topic word in the title"
    for r in sampling:
        r["picked_as"] = "random: topic word in the title, not in the 20"
    return {
        "development": hard[:5] + other[:5],
        "held_out": hard[5:] + other[5:],
        "sampling": sampling,
        "pool_sizes": {"unique_ids": len(rows), "hard_cases": len(hard_pool),
                       "no_topic_word_titles": len(other_pool), "sampling_pool_titles": len(sampling_pool)},
    }


def sheet(sel, jobs_by_id, meta):
    out = [
        "# Labeling sheet: Job-Search Agent 1",
        "",
        f"Made by `experiment/select_postings.py` from `{meta['source']}` (sha256 `{meta['source_sha256'][:16]}...`), "
        f"seed {meta['seed']}. Real Databricks postings from the 2026-10-28 baseline.",
        "",
        "Label each posting by `experiment/LABELING-RULE.md`, before looking at the RECORD verdict or any Claude "
        "answer. Fill in both lines under each posting. Commit this file before any live judgment.",
        "",
        "| # | set | id | title | location |",
        "|---|---|---|---|---|",
    ]
    order = [("development", r) for r in sel["development"]] + [("held-out", r) for r in sel["held_out"]] + \
            [("sampling", r) for r in sel["sampling"]]
    for n, (s, r) in enumerate(order, 1):
        out.append(f"| {n} | {s} | {r['id']} | {r['title']} | {r['location']} |")
    for n, (s, r) in enumerate(order, 1):
        text = judge.clean_text(jobs_by_id[r["id"]].get("content"))
        out += [
            "", f"## {n}. {r['id']}: {r['title']}", "",
            f"- Set: {s}. Picked as: {r['picked_as']}.",
            f"- Location: {r['location']} ({r['location_class']})",
            f"- Title words: topic {r['topic_words'] or 'none'}, seniority {r['seniority_words'] or 'none'}",
            f"- Posting: {r['absolute_url']}",
            "- **My label (relevant / not relevant):** ",
            "- **My note:** ",
            "", "<details><summary>Posting text (HTML removed)</summary>", "", text, "", "</details>",
        ]
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("raw", help="a saved Greenhouse board response")
    ap.add_argument("--seed", type=int, default=7375)
    ap.add_argument("--out", default=str(HERE))
    a = ap.parse_args(argv)
    raw = Path(a.raw).read_bytes()
    jobs = json.loads(raw)["jobs"]
    sel = select(jobs, a.seed)
    meta = {"source": Path(a.raw).name, "source_sha256": hashlib.sha256(raw).hexdigest(), "seed": a.seed,
            "topic_words": TOPIC_WORDS, "seniority_words": SENIORITY_WORDS, "unclear_locations": sorted(UNCLEAR)}
    out = Path(a.out)
    (out / "selection.json").write_text(json.dumps({**meta, **sel}, indent=2, ensure_ascii=False) + "\n",
                                        encoding="utf-8")
    (out / "LABELING-SHEET.md").write_text(sheet(sel, {j["id"]: j for j in jobs}, meta), encoding="utf-8")
    print(f"pools: {sel['pool_sizes']}")
    for name in ("development", "held_out", "sampling"):
        print(f"{name}: {[r['id'] for r in sel[name]]}")
    print(f"wrote {out / 'selection.json'} and {out / 'LABELING-SHEET.md'}")


if __name__ == "__main__":
    main()
