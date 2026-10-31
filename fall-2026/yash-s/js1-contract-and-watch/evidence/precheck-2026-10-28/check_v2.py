"""Pre-build check of CONTRACT.md v2's three rules against one saved board response.

usage: python3 check_v2.py <board-response.json> <resume.json> [--exclude "Name,Name"]

--exclude lists the résumé skills not counted because they are the company's own
product names. The default is v2 as written: Databricks, Unity Catalog, MLflow, Delta Lake.
"""
import argparse, collections, html, json, re

ap = argparse.ArgumentParser()
ap.add_argument("board")
ap.add_argument("resume")
ap.add_argument("--exclude", default="Databricks,Unity Catalog,MLflow,Delta Lake")
a = ap.parse_args()

jobs = json.load(open(a.board))["jobs"]
skills = json.load(open(a.resume))["skills"]
n = len(jobs)

GROUPS = ["languages", "data_bi", "backend_automation", "database_cloud"]   # not familiar_with_not_shipped, not agent_note
EXCLUDED = {s.strip().lower() for s in a.exclude.split(",") if s.strip()}
SKILLS = [s for g in GROUPS for s in skills[g] if s.lower() not in EXCLUDED]
TITLE_PHRASES = ["AI Engineer", "ML Engineer", "Machine Learning Engineer",
                 "Applied AI Engineer", "Data Engineer", "GenAI Engineer"]
SWE_WORDS = ["AI", "ML", "GenAI", "Machine Learning"]


def plain(content):
    t = html.unescape(content or "")        # entity-escaped HTML -> HTML
    t = re.sub(r"<[^>]+>", " ", t)          # drop tags
    return html.unescape(t)                 # &nbsp; and the like


def hit(phrase, text):
    return re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text, re.I) is not None


def rule1(title):
    if any(hit(p, title) for p in TITLE_PHRASES):
        return True
    return hit("Software Engineer", title) and any(hit(w, title) for w in SWE_WORDS)


rows = []
for j in jobs:
    text = plain(j.get("content"))
    matched = [s for s in SKILLS if hit(s, text)]
    blocked = re.search(r"security clearance", j["title"] + " " + text, re.I) is not None
    rows.append({"id": j["id"], "title": j["title"].strip(), "r1": rule1(j["title"]),
                 "skills": matched, "blocked": blocked})

p1 = [r for r in rows if r["r1"]]
p2 = [r for r in rows if len(r["skills"]) >= 2]
relevant = [r for r in p1 if len(r["skills"]) >= 2 and not r["blocked"]]

print("excluded product names:", sorted(EXCLUDED))
print("counted skills:", SKILLS)
print("skill -> postings containing it:", dict(collections.Counter(s for r in rows for s in r["skills"])))
print(f"rule 1 (title): {len(p1)}/{n} | rule 2 (2+ skills): {len(p2)}/{n} = {100 * len(p2) / n:.1f}% "
      f"| rule 3 blocker found: {sum(r['blocked'] for r in rows)}/{n} | RELEVANT (all three): {len(relevant)}/{n}")
print("\nRELEVANT:")
for r in relevant:
    print(f"  {r['id']}  {r['title']}  {r['skills']}")
print("\npass rule 1, fail rule 2:")
for r in p1:
    if len(r["skills"]) < 2:
        print(f"  {r['id']}  {r['title']}  {r['skills']}")
print("\npass rule 1, blocked by rule 3:", [r["title"] for r in p1 if r["blocked"]])
