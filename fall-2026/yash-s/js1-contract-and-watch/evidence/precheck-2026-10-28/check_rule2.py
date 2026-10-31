import json, re, html, collections, sys
# usage: python3 check_rule2.py <board-response.json> <resume.json>
BOARD, RESUME = sys.argv[1], sys.argv[2]
board = json.load(open(BOARD))
resume = json.load(open(RESUME))
jobs = board["jobs"]
print("postings:", len(jobs), "| meta total:", board.get("meta", {}).get("total"))
ids = [j["id"] for j in jobs]
print("unique ids:", len(set(ids)), "| unique titles:", len({j['title'] for j in jobs}))

groups = {k: v for k, v in resume["skills"].items() if isinstance(v, list)}
ALL = [s for v in groups.values() for s in v]
PRODUCTS = {"Databricks", "Delta Lake", "MLflow", "Unity Catalog"}
FAMILIAR = set(groups["familiar_with_not_shipped"])

def plain(c):
    t = html.unescape(c or "")          # entity-escaped HTML -> HTML
    t = re.sub(r"<[^>]+>", " ", t)      # drop tags
    return html.unescape(t)             # &nbsp; etc.

def hit(word, text):
    return re.search(r"(?<!\w)" + re.escape(word) + r"(?!\w)", text, re.I) is not None

texts = {j["id"]: plain(j.get("content")) for j in jobs}
freq = collections.Counter()
for t in texts.values():
    for s in ALL:
        if hit(s, t): freq[s] += 1
print("\nskill -> postings containing it (whole word, any case):")
for s in ALL: print(f"  {s:14} {freq[s]:4}")

def passes(skillset):
    return sum(1 for t in texts.values() if sum(hit(s, t) for s in skillset) >= 2)
n = len(jobs)
for label, ss in [("as written (all 12 skills)", ALL),
                  ("without Databricks products", [s for s in ALL if s not in PRODUCTS]),
                  ("without familiar_with_not_shipped", [s for s in ALL if s not in FAMILIAR]),
                  ("without both", [s for s in ALL if s not in PRODUCTS | FAMILIAR])]:
    p = passes(ss); print(f"\nrule 2 {label}: {p}/{n} = {100*p/n:.1f}%")

# boilerplate: which skills appear in the 'About Databricks' paragraph
about = collections.Counter()
for t in texts.values():
    m = re.search(r"About Databricks(.{0,900})", t, re.S)
    if m:
        for s in ALL:
            if hit(s, m.group(1)): about[s] += 1
print("\npostings with an 'About Databricks' section:", sum(1 for t in texts.values() if "About Databricks" in t))
print("skills found inside that section:", dict(about))

# rule 1, rule 3, full rule
TW = ["AI", "ML", "machine learning", "data engineer"]
r1 = {j["id"] for j in jobs if any(hit(w, j["title"]) for w in TW)}
r3_block = {j["id"] for j in jobs if re.search(r"security clearance", j["title"] + " " + texts[j["id"]], re.I)}
full = [j for j in jobs if j["id"] in r1 and j["id"] not in r3_block and sum(hit(s, texts[j["id"]]) for s in ALL) >= 2]
print(f"\nrule 1 (title word): {len(r1)}/{n} | rule 3 blocker found: {len(r3_block)}/{n} | all three (as written): {len(full)}/{n}")
print("titles passing all three:"); [print("  -", j["title"]) for j in full[:40]]
genai_miss = [j["title"] for j in jobs if re.search(r"genai|data engineering", j["title"], re.I) and j["id"] not in r1]
print(f"\ntitles with GenAI / 'Data Engineering' that rule 1 misses: {len(genai_miss)}"); [print("  -", t) for t in genai_miss[:10]]
ray = [re.search(r".{30}(?<!\w)ray(?!\w).{30}", t, re.I | re.S) for t in texts.values()]
ray = [m.group(0).replace("\n", " ") for m in ray if m]
print(f"\n'Ray' matches, first 5 contexts ({len(ray)} postings):"); [print("  ...", c, "...") for c in ray[:5]]
