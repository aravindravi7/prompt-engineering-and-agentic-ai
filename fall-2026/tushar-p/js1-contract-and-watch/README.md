# Job-Search Agent 1 — The Contract and the Watch

Tushar Patel · INFO 7375 · Fall 2026

An agent that watches one public job board (Stripe, on Greenhouse), reports only postings that are new since the last run, and judges each one twice:

- a **rule judge**, which is a record anyone can recompute from the raw response;
- a **Claude judge**, which is a model judgment, labeled as one.

The résumé is a fictional persona, Cole Palmer.

- The spec is **[CONTRACT.md](CONTRACT.md)** (v0.4). v0.1 was committed before any code; each later version has a changelog saying when and why it changed.
- The persona is `persona/cole-palmer.example.json` (fictional: 555 phone, `@example.com` email).

## What I started from

My own Python code. I used the Reallocation Engine only for reference: the Greenhouse endpoint pattern, and its example personas, which I inspected to see the format. I didn't copy any of its code. Its scripts are Node, and this project is Python.

## Toolchain

- macOS, zsh
- Python 3.12.10, with a local `.venv`
- `anthropic==2.3.0`, `pytest==9.2.0` (pinned in `requirements.txt`)
- git, curl
- Claude Code
- Claude chat
- Model for the Claude judge: `claude-sonnet-5-5`; temperature is not set (API default)

## Setup (fresh clone)

```
cd fall-2026/tushar-p/js1-contract-and-watch
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```

The tests run offline, with no network and no API calls. Expected: **268 passed**.

## Commands

**Running these against the real `state/seen_ids.json` changes the committed evidence.** To try them without touching it, add `--state /tmp/js1-state.json`. A missing state file makes the run a baseline.

Rule judge only (no API key needed):
```
python -m agent --no-claude
```

Both judges:
```
export ANTHROPIC_API_KEY=...   # your own key; it is read from the environment only
python -m agent
```

Seeded run against a saved raw response (no network call; the run is labeled seeded):
```
python -m agent --from-raw raw/<file>.json --state <state file> --run-date YYYY-MM-DD
```

Prompt experiment and sampling report (each makes 10 or 20 API calls):
```
python -m experiments.select
python -m experiments.run_prompt --prompt prompts/baseline.txt --split dev
python -m experiments.run_prompt --prompt prompts/revised.txt --split dev
python -m experiments.run_prompt --prompt prompts/baseline.txt --split held-out --final
python -m experiments.run_prompt --prompt prompts/revised.txt --split held-out --final
python -m experiments.sample --prompt prompts/baseline.txt --repeats 4
```

`experiments.select` re-creates the same 20 postings (seed 7375). It never overwrites `labels.csv`.

## What ran (all real; times are America/New_York)

| When | What | Result | Evidence |
|---|---|---|---|
| 2026-10-27 | Board check (no `content=true`) | 711 postings, titles only | `raw/check-2026-10-27.json` |
| 2026-10-27 | My pytest run, then a mutation test (R4 `max`→`min`) | 236 passed; the mutant failed 1 test ("5+ years backend, 2+ years Go") | `evidence/` |
| 2026-10-27 20:31 | **Run 1, live, baseline** (`--no-claude`) | 715 fetched, 0 new | `raw/greenhouse-stripe-2026-10-27T203128.json`, `out/run-2026-10-27T203128.*`, `state/seen_ids.json` |
| 2026-10-28 14:16 | **Run 2, live**, both judges | 719 fetched, **16 new**. Rule judge OK. **Claude judge: all 16 invalid, HTTP 401** (a bad API key) | `raw/greenhouse-stripe-2026-10-28T141616.json`, `out/run-2026-10-28T141616.*` |
| 2026-10-28 | Independent check of run 2 | A set difference of ids between the two raw files gave 16, matching the agent | command in FRICTIONAL.md |
| 2026-10-28 14:59 | **Seeded re-run of run 2**, same raw file, state restored from git (715 ids), with a working key | 16 new; **16/16 Claude replies valid; the rule and Claude agreed 16/16** (all `not_relevant`) | `out/run-2026-10-28T145919.*`, `state/seen_ids-run2-seeded.json` |
| 2026-10-29 | Prompt experiment | Baseline: dev 9/10, held-out 10/10. Revised: dev 10/10, held-out 10/10 | [experiments/PROMPT-EXPERIMENT.md](experiments/PROMPT-EXPERIMENT.md) |
| 2026-10-29 | Sampling report (5 postings × 4 fresh calls) | No spread; 8314283 was `cannot_tell` 4/4 against my label `relevant` | [experiments/SAMPLING-REPORT.md](experiments/SAMPLING-REPORT.md) |
| 2026-10-29 | Action-surface comparison | see file | [ACTION-SURFACE.md](ACTION-SURFACE.md) |

Run 2's Claude verdicts come from the **seeded** re-run, not from the live run. The live run's Claude judge failed because of my key. CONTRACT v0.4 now stops a run at the first 401.

## Files

- `agent/`: the agent (allow-list, fetch, state, rules R1–R6, Claude judge, validator, report)
- `tests/`: offline tests and fixtures
- `prompts/`: the Claude judge prompts (`baseline.txt` is the default; `revised.txt` holds the one change)
- `raw/`, `state/`, `out/`: saved raw responses, the seen-ids state, and the run outputs
- `experiments/`: labeling rule, selection, hand labels, results, and the two reports
- `evidence/`: my own pytest and mutation-test output
- [CONTRACT.md](CONTRACT.md), [ACTION-SURFACE.md](ACTION-SURFACE.md), [SOURCES.md](SOURCES.md), [FRICTIONAL.md](FRICTIONAL.md)

---

## Sign-off — Job-Search Agent 1

**Checked**

| Property | Test or check | How |
|---|---|---|
| R4 uses the largest minimum | `test_r4_experience[5+ years backend, 2+ years Go-fail]`, plus a mutation (`max`→`min`) that made exactly that test fail | By hand: I made the mutation and saved the output |
| New postings are counted correctly in a real run | A set difference of ids between the two raw files (16), compared with the agent's report (16) | By recomputation, with a command independent of the agent's code |
| The real API key is in no file | `grep -r "sk-ant"`; the only hit is the fake test secret | By hand |
| Claude output is validated, not repaired | Run 2: 16 replies rejected as invalid on a 401; seeded re-run: 16/16 valid. Validator tests in `tests/test_validator.py` | By running it, and by tests Claude Code wrote, which I ran |
| Allow-list, state and baseline, the two wrong versions, persona missing-field | `tests/test_allowlist_and_fetch.py`, `test_runs_and_state.py`, `test_persona.py`, `test_validator.py` | With Claude's help: Claude Code wrote these tests from my contract; I ran them myself (268 passed). Only R4 was mutation-checked by me |
| The double-escaped `&nbsp;` bug | A test written first, as I asked; it **passed**, so there was no bug, and I rejected the code change | With Claude's help: Claude Code wrote the test; I decided |
| Claude's verdicts against my labels | 20 hand labels, 4 prompt runs, 20 sampling calls | By hand (labels) and by recomputation (exact match) |

**How:** none of the tests were written by me before reading Claude's code. Claude Code wrote all of them against my contract. My own checks were the mutation test, the independent diff, the key grep, the hand labels, and reading Claude's saved justifications.

**Not checked**

- **R5 on real text.** No Stripe posting mentions visa sponsorship; all 14 "sponsor" sentences were business uses. The "won't sponsor" rule has never fired on real data.
- **Whether a cited field is the right one.** For R2, Claude cited `job_search.years_experience`, which R2 doesn't use, and the validator accepted it. Wrong-version test 1 can be passed by citing the wrong field.
- **R3 on most real locations.** Only about 35 of the 292 real location values have a recorded expected answer.
- **The real network path.** Redirect handling and the live fetch code are tested only with fakes.
- **The Claude judge on a live run.** It worked only on the seeded re-run.
- **My labels.** I had no second labeler.
- **Proxy environment variables,** which the allow-list doesn't cover.
- **Temperature behavior.** Claude Code's claim that the model rejects non-default values is unverified.

**Not claiming**

- That any verdict means a posting is worth applying to.
- That the agent works on other boards, other personas, or other dates.
- That Claude judges better than the rule, or the rule better than Claude. They agreed on 16 easy rejects, and that's all.
- That the revised prompt generalizes. Held-out had no relevant posting, and a constant `not_relevant` judge would score the same as the baseline.

**Signed or withheld:** ____________ (name, date)

## Driver's seat

| Task | What Claude did | What I did | Why that part stays mine | Evidence |
|---|---|---|---|---|
| Contract | Claude chat formatted CONTRACT.md from my answers. Claude Code's plan found 16 gaps (A–P) | I answered every question and decided each gap. I approved the R3 city list built from the real data | The rule decides what reaches me; it has to be my rule | CONTRACT.md changelog v0.1–v0.4; commit "CONTRACT.md v0.1 … before build" |
| Build | Claude Code wrote the code and the tests | I reviewed the plan before any code, ran the tests myself, and made the mutation test | Passing tests written by the same author prove little; I needed a check of my own | `evidence/pytest-2026-10-27-*`; commit "test evidence … R4 mutant" |
| Suspected bug | Claude Code wrote the test first, saw it pass, and stopped | I rejected the "fix" | Changing code for a bug that doesn't exist adds risk | commit "regression test for double-escaped nbsp … no code change" |
| Hand labels | Nothing | I labeled all 20, before any Claude run | The labels are the yardstick; if Claude made them, I'd be grading Claude with Claude | `experiments/labels.csv`, commit "hand labels for 20 postings" |
| The one prompt change | Claude chat proposed it, after reading Claude's saved justification | I approved it, from the dev results only, and ran held-out last | Choosing what to change is the experiment; held-out has to stay untouched by that choice | `prompts/revised.txt`, `experiments/results/HELDOUT-LOG.md` |
| Is a posting worth my time | Gives a labeled model judgment | Decides | Claude can apply my criteria; it can't know whether a job is worth a day of my life. The 16 agreements show only that both judges reject easy cases | `out/run-2026-10-28T145919.md` |