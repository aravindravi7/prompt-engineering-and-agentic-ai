# Job-Search Agent 1 — The Contract and the Watch

**Yash Saraf** · INFO 7375 · Fall 2026 · due 2026-10-31

- **Board:** Databricks on Greenhouse (`boards-api.greenhouse.io`, the only allowed host)
- **Résumé:** Priya Nair, a **fictional** persona from The Reallocation Engine (`@example.com`, 555-01xx phone). My real résumé is not used anywhere.
- **Language:** Python 3, standard library only. Tested with Python 3.13.5 on macOS.
- **Claude:** the Claude Code CLI (`claude -p`, tested with 2.1.166), model `claude-sonnet-5-5`, with all tools off for every judgment

The agent watches one job board and reports only the postings that are new since its last run. Each new posting gets two verdicts. The **RECORD** comes from my written rule, so anyone can recompute it. The **JUDGMENT** is Claude's opinion under a prompt contract, checked by a validator that rejects anything else. The agent never applies, emails, messages or logs in anywhere. The last step is always me.

## What is in this folder

| Path | What it is |
|---|---|
| [`CONTRACT.md`](CONTRACT.md) | The contract, written before any code: v1, v2, v3, plus dated notes. Git history shows each version. |
| [`FRICTIONAL.md`](FRICTIONAL.md) | My dated log, with predictions written before results |
| [`watch.py`](watch.py) | The watcher: allow-listed fetch, raw response saved first, new-since-last by id, state file, persona check |
| [`judge.py`](judge.py) | The two judges: RECORD (my rule) and JUDGMENT (Claude, no tools), plus the validator |
| [`prompts/`](prompts/) | `judgment-v1.md` (baseline prompt contract) and `judgment-v2.md` (one change) |
| [`persona/`](persona/) | `priya-nair.resume.example.json`, copied unchanged (sha256 `a4fdbc96…`) |
| [`runs/`](runs/) | Both watch runs: raw responses, run records (JSON) and reports (Markdown) |
| [`state/databricks.state.json`](state/databricks.state.json) | The state file after the second run: 924 seen ids |
| [`tests/`](tests/) | 77 offline tests and two constructed fixture boards |
| [`experiment/`](experiment/) | Labeling rule, selection, my labels, the **sampling report** and the **prompt experiment**, with their runners and results |
| [`action-surface/`](action-surface/) | The **action-surface comparison**: inputs, the three outputs, the checker and the write-up |
| [`evidence/`](evidence/) | `precheck-2026-10-28/` (my rules checked against real data before any code) and `model-check-2026-10-28/` (two pings before any live judgment) |
| [`SOURCES.md`](SOURCES.md) | What I used, what I wrote, what Claude contributed |

## How to run it

From a fresh clone, go into this folder first: `cd fall-2026/yash-s/js1-contract-and-watch`. Nothing needs installing. The **offline** commands need only Python 3. The **live** commands also need the Claude Code CLI, logged in.

**Tests (offline).** Claude and the network are blocked inside the tests.

```bash
python3 -m unittest discover -s tests -v
```

**Replay both watch runs from the saved responses (offline, labeled SEEDED).** This reproduces the second run's 23 new postings and their RECORD verdicts without fetching anything. Run the two commands one after the other; they write to a temporary folder.

```bash
T="$(mktemp -d)"
python3 watch.py --from-file runs/raw-databricks-2026-10-29T005656Z.json --state "$T/state.json" --out "$T/runs" --no-judgment
python3 watch.py --from-file runs/raw-databricks-2026-10-31T061834Z.json --state "$T/state.json" --out "$T/runs" --no-judgment
```

**The live watch, as I ran it.** It fetches the live board and asks Claude about each new posting:

```bash
python3 watch.py --board databricks --resume persona/priya-nair.resume.example.json --state state/databricks.state.json --out runs --prompt prompts/judgment-v1.md --model claude-sonnet-5-5
```

To try it without changing my committed state, use `--state "$T/state.json" --out "$T/runs"`. The first run with a new state file is a baseline and reports 0 new postings.

**Selection (offline, reproducible).**

```bash
python3 experiment/select_postings.py runs/raw-databricks-2026-10-29T005656Z.json --seed 7375
```

This regenerates `experiment/selection.json` and a blank-label `experiment/LABELING-SHEET.md`. **Overwriting the sheet erases my labels**, so to check it, use `--out "$(mktemp -d)"`. The output `selection.json` should have sha256 `9bf3a3d3…`.

**Sampling report, prompt experiment and action surfaces (live).** Use the exact commands in [`experiment/SAMPLING-REPORT.md`](experiment/SAMPLING-REPORT.md), [`experiment/PROMPT-EXPERIMENT.md`](experiment/PROMPT-EXPERIMENT.md) and [`action-surface/ACTION-SURFACE.md`](action-surface/ACTION-SURFACE.md). These offline checks need no Claude:

```bash
python3 experiment/run_experiment.py report        # rebuilds experiment/results/RESULTS.md from the four saved runs
python3 action-surface/check.py                     # rebuilds action-surface/CHECK.md from the saved outputs
python3 experiment/run_experiment.py run --name baseline --prompt prompts/judgment-v1.md --set held_out --out "$(mktemp -d)"   # refused: held-out needs --final
```

## What ran

All times are as recorded. Files use UTC; Eastern Time is given for my calendar.

| When (ET) | When (UTC) | What | Ran by | Evidence |
|---|---|---|---|---|
| Wed Oct 28, 4:22 pm | 2026-10-28T20:22:07Z | One fetch of the board to check my v1 rules. This was not the agent. | Claude (`curl`) | `evidence/precheck-2026-10-28/` |
| Wed Oct 28, 8:56 pm | 2026-10-29T00:56:56Z | **Baseline watch run:** 901 postings, 0 new | me | `runs/*2026-10-29T005656Z*` |
| Wed Oct 28, ~10:19 and 10:21 pm | 2026-10-29T02:19–02:21Z | Two pings to confirm the model (no posting or résumé sent) | me | `evidence/model-check-2026-10-28/` |
| Sat Oct 31, 2:18 am | 2026-10-31T06:18:34Z | **Second watch run, live:** 23 new, 23 no longer listed, both judges on each | me | `runs/*2026-10-31T061834Z*` |
| Sat Oct 31, 2:32 am | 2026-10-31T06:32:15Z | Sampling report: 5 postings × 4 fresh calls | me | `experiment/sampling/` |
| Sat Oct 31, 2:34–2:43 am | 2026-10-31T06:34:30–06:43:13Z | Prompt experiment: 4 runs of 10 | me | `experiment/results/` |
| Sat Oct 31, ~3:20–3:27 am | ~2026-10-31T07:20–07:27Z | Action surfaces (a), (b) and (c) | me | `action-surface/` |

**Date and time.** The watcher names its files in UTC, so a file's date can differ from my local date. The baseline ran on **October 28 at 8:56 pm ET**, but its files say `2026-10-29T005656Z`; both describe the same run. I use Eastern dates when I describe which day something ran, and I keep the UTC times in the files unchanged. The second run was three calendar days after the baseline.

## Results

- **The watch.** The baseline recorded 901 ids and reported 0 new. The second run found **23 new** and 23 no longer listed, leaving 924 seen ids. I had predicted about 5. RECORD found 0 of 23 relevant. JUDGMENT gave 22 valid answers, all `not relevant`, and **1 invalid**: Claude wrote valid JSON, then added *"Wait, I need to correct the matched terms…"*, and the validator rejected it as the contract says. Report: [`runs/report-databricks-2026-10-31T061834Z.md`](runs/report-databricks-2026-10-31T061834Z.md).
- **The contract changed twice before the judges were built, because of real data.**
  - **v1:** rule 2 matched **897 of 897** postings, because every posting's "About Databricks" text names Databricks and Unity Catalog, two of Priya's skills.
  - **v2:** dropped four product names and marked **2** postings relevant. Two of those names (MLflow, Delta Lake) were dropped because of a wrong claim in Claude's review.
  - **v3:** excludes only Databricks and Unity Catalog, and marks **4 of 897** relevant.

  Evidence: `evidence/precheck-2026-10-28/`.
- **Sampling report:** 20 of 20 answers were valid and matched my labels, with the same verdict in all 4 runs of each posting. The reasons varied, and 18 of the 20 named Priya's skills while every `matched_terms` list was empty. All 5 postings were clear-cut cases. [`experiment/SAMPLING-REPORT.md`](experiment/SAMPLING-REPORT.md)
- **Prompt experiment:** v1 scored 10/10 on development and 10/10 on held-out. v2 scored 10/10 and **9/10**. The one failure was not the targeted one: v2 cited `mlflow`, which the posting does not contain, and v1 made the same claim in prose, where the validator does not look. All 20 labels were `not relevant`, so recall was not tested. [`experiment/PROMPT-EXPERIMENT.md`](experiment/PROMPT-EXPERIMENT.md)
- **Action surfaces:** chat and file-read both passed. The agent that fetched and wrote its own state **failed**: it returned the posting id as a string, and wrote **117 of 901** ids to its state file. [`action-surface/ACTION-SURFACE.md`](action-surface/ACTION-SURFACE.md)

## Tests and wrong versions

`tests/` holds 77 offline tests: 76 when the runs were made, plus the overwrite test added afterwards.
- **Wrong version 1** (a verdict on the wrong posting id): `test_judge.WrongVersion1VerdictOnTheWrongId`.
- **Wrong version 2** (a reason with no evidence): `test_judge.WrongVersion2ReasonWithoutEvidence`, plus the `Validator` tests for Claude's answers.

On 2026-10-28, Claude planted six bugs in a scratch copy of the code and confirmed that tests failed for each one:
- verdicts paired with the wrong ids;
- a RECORD reason that cites nothing;
- a validator that skips the matched-term check;
- a validator that silently strips code fences;
- comparing postings by title instead of id;
- writing state before the response is parsed.

Those outputs are not saved in this folder, and the check was not rerun after the 2026-10-31 location change.

**Found and fixed after the committed runs.** On 2026-10-31, while replaying both runs myself, I pasted the two commands together. They started in the same second, and file names only go down to the second, so both runs wrote to `raw-databricks-2026-10-31T083036Z.json`. The second run overwrote the first run's raw response, run record and report. The state file and the result (23 new) were still correct. After that, Claude changed `watch.py` so a run never overwrites an earlier run's files: a second run in the same second gets `-2`, and so on. The test `test_watch.Baseline.test_same_second_runs_keep_both_raw_responses` fails on the old code and passes on the new. **None of the committed runs was affected**: they ran days apart, and every file in `runs/` is the one written at the time.

## Known limitations

- All 25 hand labels are `not relevant`. Neither judge was tested on a posting I would call relevant.
- The 20 experiment postings are hard cases plus random non-topic titles from one day's board, not a sample of jobs in general.
- Every judgment call also reported `claude-haiku-4-5-20251001`. In the file-read surface, Haiku used 469 input tokens; in the agent surface, 35,378. The judge's own runs recorded model names only, so what Haiku did in them is not known.
- Claude Code adds about 170 tokens of its own to every call, even from an empty folder (`evidence/model-check-2026-10-28/`).
- The validator checks the structured fields, not the prose reason.
- RECORD does not use location or seniority. My labels and the JUDGMENT prompt do.

## Sign-off — Job-Search Agent 1

Checked:
- All 77 offline tests passed, including the new test for preventing evidence files from being overwritten.
- The baseline recorded 901 postings and 0 new jobs.
- The second watch run found 23 new postings.
- The offline replay reproduced the same 23 new IDs and RECORD verdicts.
- The action-surface checker reported two passes and one failure.

How:
- I ran the automated tests and live commands.
- I reviewed the saved results and reports.
- I used Claude to help write code, check results, and identify problems.
- I compared the action-surface results using the same validator.

Not checked:
- Whether the agent correctly identifies genuinely relevant jobs.
- Whether the results stay consistent across different days and models.
- Whether the system recovers correctly from an interrupted run.
- Whether reading files outside the temporary folder would be refused.

Not claiming:
- That the agent can apply for jobs automatically.
- That it identifies every suitable job.
- That my experiment proves one prompt is better in general.
- That the system has been tested on multiple job boards.

Signed: Yash Saraf, October 31, 2026

## Driver's seat

| Part of the task | What Claude did | What I did | Why that part stays mine | Evidence |
|---|---|---|---|---|
| The contract | Reviewed each version against the brief and the data, and suggested gaps | Wrote v1, v2 and v3 and every rule in them | I am responsible for deciding what the agent is allowed to do and what it must never do. | `16ecbcd` (v1, before any code), `172fe24` (v2), `2cadf12` (v3), all before the code they govern |
| Changing the rule after real data | Ran the pre-checks (897/897, then 2 and 4 of 897); was wrong once, about MLflow and Delta Lake | Decided what to keep and drop | I need to review the evidence and decide whether changing a rule makes sense. | `evidence/precheck-2026-10-28/`, FRICTIONAL entries of 2026-10-28 |
| What "relevant" means | Pointed out ambiguities (experience cutoff, location, roles) and showed how few postings could pass | Wrote the labeling rule and its eight decisions | Relevance depends on my chosen persona and job requirements, not just Claude's opinion. | `f67a170`, `experiment/LABELING-RULE.md` |
| The labels | Built the selection script and the sheet | Labeled all 25 postings | The labels define what I compare Claude's answers against, so I am responsible for reviewing them. | `d93ab09` |
| What counts as a pass | Suggested wording | Wrote and committed the pass definition before any run | I must decide how success is measured before seeing the results. | `ee7f57e` |
| The prompt and the one change | Checked the prompt against the contract | Wrote v1, chose the one change for v2, and predicted the result before running it | I choose what to test and make the final decision about which prompt to use. | `13b75f0`, committed 12 s before the first v2 run |
| The code and tests | Wrote `watch.py`, `judge.py`, the runners, the checkers and the tests | Ran every test and every live command | I am responsible for running tests, checking failures, and deciding whether the code is acceptable. | `ac93993`, `76a86db`, `0a9b18b`, `188db22` |
| Git and anything live | Gave exact commands; never ran git or a live judgment itself | Ran every commit, the watch runs, the pings, the sampling, the experiment and the action surfaces | I control when commands run, what gets committed, and whether anything is submitted. | the commits above, and the run records' timestamps |
| Checking Claude | Flagged its own wrong MLflow/Delta Lake claim, and one of its overclaims in the comparison | Rewrote passages Claude had drafted | I need to verify Claude's claims instead of assuming its explanations are correct. | FRICTIONAL.md; `action-surface/ACTION-SURFACE.md` "What happened" |
