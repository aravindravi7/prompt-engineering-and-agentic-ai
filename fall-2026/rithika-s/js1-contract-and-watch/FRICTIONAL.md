# FRICTIONAL — Job-Search Agent 1

## 2026-10-30

### Choosing the persona
- Compared all four fictional personas from the Reallocation Engine's
  search/examples/ (Aarav, Maya, Priya, Rohan)
- - I chose Priya Nair (AI/ML Engineer, Data Engineer). Reason: AI/ML and data roles are my own field, so I can label those postings by hand with confidence. Her skills (Python, SQL, Databricks, MLflow, LangGraph) appear word-for-word in postings, and her security-clearance exclusion gives clear "not relevant" cases.

- Rejected Rohan: his skills list is so broad almost any SWE job would match,
  and his exclusions are "none", so few postings would be "not relevant".
- Noticed Priya has no PyTorch/TensorFlow, which many ML postings ask for.
  This will force real decisions in my rule.

### Choosing the job board
- Tested three Greenhouse endpoints in the browser (~11:37–11:41):
  databricks, anthropic, scaleai. All three returned JSON.
- Rejected Databricks: every posting ends with an "About Databricks"
  paragraph that mentions Databricks and Unity Catalog, both on Priya's
  skills list. A keyword rule would mark every job relevant, including
  sales roles. Some postings were also in Japanese.
- Chose Scale AI: English postings, US locations, mix of engineering and
  non-engineering roles, and it likely has clearance-related postings that
  test Priya's "no security clearance" exclusion.
- Scale AI board total: 169 postings ("meta": {"total": 169}).
- Confusion I had: the endpoint looked like raw text with no Apply button.
  Learned it is the JSON data feed meant for programs; each posting's
   "absolute_url" points to the normal human page. I opened one and confirmed it is the same job with an Apply button.

### Setup mistake and fix
- Typed a bare `cd`, which took me to my home folder. `git pull` failed
  ("not a git repository") and `mkdir` created fall-2026/... in my home
  folder instead of the course repo (~11:58).
- Removed the empty folders with `rmdir` (it only deletes empty folders).
- Ran `mdfind -name week-01-video` and found TWO clones of the course repo.
  Checked both with `git log -1`: ~/info-7375-... had my latest commit
  (Oct 21), the Downloads copy stopped at Sep 25. Using ~/info-7375-...
- Downloaded Priya's resume.example.json from the professor's repo with
  curl and verified it with a one-line Python check: printed
  "Priya Nair priya.nair@example.com".
- Created .gitignore (blocks resume.json, *.real.json, .env, caches) before writing any code or the contract.

