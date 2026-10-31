# SOURCES — Job-Search Agent 1

Yash Saraf · INFO 7375 · 2026-10-31

## What I used

| Tool or source | Version / date | Licence | Used for |
|---|---|---|---|
| The Reallocation Engine (`github.com/nikbearbrown/the-reallocation-engine`), through my fork | local checkout, commit `9fe8d93` | code MIT | **Persona:** `search/examples/priya-nair/resume.example.json`, copied unchanged to `persona/` (sha256 `a4fdbc96…`). It is fictional (`@example.com`, 555-01xx). **Ideas only, no code copied:** its `greenhouse-watch` skill's allow-list, refusing redirects, saving the raw response first, the seen-id state file, and a baseline that reports nothing. |
| Course materials (`nikbearbrown/info-7375-prompt-engineering-for-generative-ai`) | pulled 2026-10-28 | per the course repo | The assignment brief. The instructor's `fall-2026/nik-bear-brown/greenhouse-watch-demo/`, as a worked example of a two-day watch. Design principles from `SDD-job-search-project.md`: P1 keep the source's fields, P2 raw response first, P7 the last step is a person, P8 a number points to a file. |
| Greenhouse Job Board API, public endpoint | fetched 2026-10-28 (the pre-check and the baseline) and 2026-10-31 (the second run; the agent in action surface (c) fetched it too) | Databricks' public postings | `https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true`. The raw responses are saved unmodified in `runs/` as evidence. The posting text belongs to Databricks. |
| Python | 3.13.5, standard library only | PSF | All code and tests |
| Claude Code CLI | 2.1.166 | Anthropic terms | `claude -p` for every JUDGMENT, with all tools off. Model requested: `claude-sonnet-5-5`; Claude Code also reported `claude-haiku-4-5-20251001` on every call. |
| Claude.ai | Sonnet 5.5, 2026-10-31 | Anthropic terms | Action surface (a) only: one posting pasted into a chat |
| `curl` | macOS system version | curl licence | The one pre-check fetch on 2026-10-28, run by Claude |

## What I made

- **CONTRACT.md:** v1 (committed before any code), v2 and v3, and the dated notes. Every rule is mine, including each change after the pre-checks.
- **The labeling rule** and its eight decisions (`experiment/LABELING-RULE.md`), and **all 25 labels and notes** (`experiment/LABELING-SHEET.md`).
- **The pass definition**, written and committed before any run.
- **Prompt v1**, the **one change in v2**, and my **prediction**, committed before v2 ran.
- **The conclusions** in `experiment/SAMPLING-REPORT.md` and `experiment/PROMPT-EXPERIMENT.md`, and the **least-autonomy choice**, two rewritten paragraphs, the chat-run details and two corrections in `action-surface/ACTION-SURFACE.md`.
- **FRICTIONAL.md**, the sign-off and the reasons in the driver's seat table.
- **Every live step and every git command:** both watch runs, the two pings, the sampling report, the four experiment runs, all three action surfaces, every test run I report, and every commit.

## What Claude contributed

Claude Code (Claude Opus 5.5) in this session, 2026-10-28 to 2026-10-31.

**Code, all checked by tests I ran:**
- `watch.py`, `judge.py`, the `tests/` files, and the two **constructed** fixture boards in `tests/fixtures/`, which are labeled as not real data;
- `experiment/select_postings.py`, `harness.py`, `sample.py` and `run_experiment.py`;
- `action-surface/make_inputs.py` and `check.py`;
- the pre-check scripts in `evidence/precheck-2026-10-28/`.

**Checks and analysis:**
- The one pre-check fetch on 2026-10-28, and its analysis: v1's rule 2 matched 897 of 897 postings, v2 marked 2 relevant, and v3's rule marks 4.
- Checking each run's files after I ran it (fingerprints, id sets, state), and spot-checking my label notes and Claude's own claims against the posting text.
- Planting six bugs in a scratch copy to confirm the tests catch them (not saved here).

**Writing:**
- Reviews of each contract version, and suggestions I accepted: showing Claude the location, the hard-case selection, structured answer fields, all tools off, and the model choice.
- The evidence READMEs.
- The setup, results and limitations sections of the sampling report, the prompt experiment and the action-surface comparison, drafted from the saved records.
- Drafts of this README and of SOURCES.md.

**Where Claude was wrong:**
- Its first review said the "About Databricks" text named Delta Lake and MLflow. The data showed only Databricks and Unity Catalog. I had already removed MLflow and Delta Lake in v2 because of that claim, and restored them in v3.
- Its first count of hard-case postings was 10, from a rough location match; the exact US test found 11.
- One line in its action-surface table claimed something it had not tested (that reading outside the folder is refused). I corrected it to say it was not tested.

**Other AI tools:** none.
