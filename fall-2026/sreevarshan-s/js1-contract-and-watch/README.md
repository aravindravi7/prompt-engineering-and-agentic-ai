# Job-Search Agent 1 (INFO 7375)

A job watch for Priya Nair, a fictional persona. It does five things:

1. Fetches the public Databricks Greenhouse board, from one allow-listed host.
2. Remembers which posting ids it has seen.
3. Reports new and removed postings on each run.
4. Judges each new posting for Priya with a fixed set of rules.
5. Offers a separate, isolated Claude judge whose verdict is compared with the rules afterward.

The rules are written in [CONTRACT.md](CONTRACT.md); the Final section supersedes the drafts below it.

- **Language:** Python 3.13.9, standard library only. There are no third-party packages.
- **Tests:** `unittest`. The network and the `claude` subprocess are mocked in every test.
- **Claude judge:** the `claude` CLI (v2.1.117), run as a subprocess in print mode. Model pinned to `claude-sonnet-4-6`, every tool disabled, run from an empty temporary directory.
- **Persona:** `persona/priya-nair.resume.json` and `persona/priya-nair.profile.json`, fictional, from the Reallocation Engine repo.

## Commands

Run from the repository root.

| command | what it does |
|---|---|
| `python3 -m unittest discover -s tests` | Runs all tests. No network and no Claude call. |
| `python3 -m js1 --baseline` | One live fetch from `boards-api.greenhouse.io`. Saves the raw response to `evidence/raw/<UTC stamp>.json` and records every posting id in `state/seen_ids.json`. No judging. Refuses (exit 3) if state already exists. |
| `python3 -m js1` | The watch run. Refuses (exit 5) without a baseline. Steps: 1) one live fetch; 2) save the raw response; 3) report fetched, new and removed posting ids; 4) run the rule judge on new postings only and save records to `evidence/rule/<UTC stamp>.json`; 5) only then update state, keeping the previous state file beside it. A failed fetch leaves state unchanged (exit 6). |
| `python3 -m js1.claude_judge --prompt baseline\|revised --posting-file FILE --posting-id ID` | One Claude judgment of one posting from a saved Greenhouse-shaped file, with one retry on an invalid reply. Saves every attempt and the result under `evidence/claude/`. Exits 0 if valid, 4 if invalid. |
| `python3 -m experiments.run_experiment --split dev` | Prompt experiment on the frozen development split (`LABEL_SET.md`). Runs the rule judge plus the baseline and revised Claude prompts on each posting and scores them against `labels/HAND_LABELS.md`. Writes `experiments/results_dev.md` and evidence under `evidence/experiment/dev/`. |
| `python3 -m experiments.run_experiment --split heldout` | Same, on the held-out split. Refused (exit 7) until `experiments/results_dev.md` exists. |
| `python3 -m experiments.sampling build` | Writes the full baseline prompt for each of the 5 sampling postings to `experiments/sampling/prompts/`. Uses the judge's own prompt-building code. No Claude call. |
| `python3 -m experiments.sampling check experiments/sampling/replies/*.txt` | Checks saved reply files with the judge's JSON validator. Prints valid plus the verdict, or invalid plus the reason. Exits 4 if any reply is invalid. |
| `python3 -m experiments.sampling_report` | Prints the sampling results table used in `experiments/SAMPLING_REPORT.md`, computed from the reply files. |

**Choices Claude Code made where the contract left room:** see [IMPLEMENTATION_CHOICES.md](IMPLEMENTATION_CHOICES.md).

## Sign-off

### Checked

**Automated tests.** The last full run, on 2026-10-31 before this commit, ran 76 tests and all passed:

| test file | tests |
|---|---|
| `tests/test_allowlist.py` | 5 |
| `tests/test_baseline.py` | 3 |
| `tests/test_claude_judge.py` | 15 |
| `tests/test_experiment.py` | 7 |
| `tests/test_fetch.py` | 2 |
| `tests/test_persona.py` | 8 |
| `tests/test_rule_judge.py` | 22 |
| `tests/test_sampling.py` | 2 |
| `tests/test_watch.py` | 4 |
| `tests/test_watch_run.py` | 8 |

**Live runs, with their evidence commits:**

| commit | run | result |
|---|---|---|
| `6beef48` | Baseline, 2026-10-29T22:15:02Z | 905 postings recorded, 0 new |
| `0dd01ab` | Second live watch run, 2026-10-30T23:59:22Z | 901 fetched, 10 new, 14 removed; rule records saved |
| `bb1f877`, `c047608` | Claude judge smoke test on CONSTRUCTED posting 8000002 | First run: "Not logged in" twice. Then valid. Then valid with the pinned model recorded |
| `d7411f4` | Prompt experiment, dev split | Baseline 10/10, revised 9/10, rule 9/10 |
| `4a46925` | Prompt experiment, held-out split | Rule 9/10. 38 of the 39 Claude calls made failed on the usage limit, so the Claude results are not usable |
| `6064e8e` | Sampling in the Claude app, 5 dev postings × 4 chats | 19/20 valid, all "not relevant" |
| `3484999` | Action-surface comparison on 8546367002 | Included one live GET of that posting from Greenhouse. Also the two usage-limit smoke-test failures from 2026-10-31 |

### How

**My words (verbatim):**

**Q24.** I'll manually verify selected posting verdicts and inspect the saved response and state files. I'll use automated tests to check the contract's rules and compare their outputs with my own expectations. I'll distinguish tests based on my contract decisions from tests Claude Code wrote. [correction: all 76 tests in `tests/` were written by Claude Code; some encode my contract decisions, but the repo does not yet mark which ones.]

**What I ran myself, by commit:**
- **In Terminal:**
  - `6beef48`: the baseline run, `python3 -m js1 --baseline`.
  - `bb1f877`: the first smoke test, which failed with "Not logged in". I logged in with `/login` and reran (`NOTES_FOR_FRICTIONAL.md`).
  - `0dd01ab`: the second live watch run, `python3 -m js1`. I also made this commit.
  - `d7411f4`: the dev experiment. I also made this commit.
  - `4a46925`: the held-out experiment. I also made this commit.
  - `3484999`: the smoke test at 2026-10-31T01-36-35Z, which hit the usage limit.
- **In the Claude app:**
  - `6064e8e`: the 20 sampling chats, with the replies saved by hand. I also made this commit.

### Not checked

**My words (verbatim):**

**Q25.** I haven't verified redirects against every real-world scenario; redirect protection was tested only with simulated data. Experience requirements written as number words beyond "five" aren't handled by the current rules. [correction: `js1/rule_judge.py` handles number words "one" through "ten"; number words beyond "ten" are not handled.] I also can't directly control Claude's temperature through the CLI, so I can't guarantee identical outputs across repeated runs.

**Further gaps, from the evidence:**
- **Validator bug:** the validator rejects `resume_field: "resume_experience_tools"`, a key the judge's own input provides.
  - It caused the invalid sampling reply 8921476002-4.
  - In the dev run (`d7411f4`) it rejected 4 replies. Two of them were the revised prompt's two "relevant" replies on 8401114002, a Staff title, which showed up only as "invalid".
- **8546367002:** the rule judge passed it as "relevant" even though the description says it "is not intended for internship, new graduate, or entry-level applicants" (`results_dev.md`).
- **8760167002:** the rule judge passed it as "relevant" despite its Secret-clearance-eligibility requirement (`results_heldout.md`).
- **Unity Catalog:** it appears in the Databricks boilerplate of every posting (905 of 905 in the baseline, 901 of 901 in the second run), so it matches every posting.
- **Sponsorship:** no posting among the 905 mentions visa sponsorship. The word "visa" appears in none, and every "sponsor" match is business usage. So check 6 returned "unknown" for every live posting and never decided a verdict.
- **Hand labels:** all 20 are "not relevant", so no relevant posting has been tested against a hand label.
- **Held-out Claude results:** still pending a rerun after the usage limit.

### Not claiming

**My words (verbatim):**

**Q26.** I'm not claiming that this agent can guarantee job eligibility, predict whether a company will hire someone, or submit applications. It only identifies potentially relevant new postings based on the supplied persona and documented rules.

## Driver's seat

**My words (verbatim):**

**Q27.** I should decide the target roles, eligibility requirements, hand labels, success criteria, and whether the final results are acceptable. Claude Code can implement the program, generate test code, and help organize the reports. The final decisions stay with me because the agent is supposed to reflect my requirements, not make those decisions on my behalf.

**Q28.** The first contract commit, 8cfa417, predates implementation. The baseline evidence commit is 6beef48. I'll reference the actual final contract commit and the relevant transcript or edits to show which decisions I reviewed and approved.

**Final contract commit:** `b8a5b81` (Draft 8) is the last commit that changes `CONTRACT.md`.

**Who did what, by commit:**

| commits | what | who | co-author line |
|---|---|---|---|
| `8cfa417`, `d6c24ff`, `2860740`, `67d61b8`, `9b34061`, `c8c2772`, `4da69e5`, `dfb37a7`, `b8a5b81` | Contract Drafts 0–8 | My text, appended verbatim by Claude Code. In Drafts 6, 7 and 8 the same commit also folds my sentences into the Final section | none |
| `31d20fa`, `e7f7362` | Contract Final section (restructure, then the Draft 5 fold) | My sentences verbatim, arranged and source-tagged by Claude Code; I approved before commit | none |
| `ee73eca`, `04ef802`, `1110661`, `a4021ff`, `bb1f877`, `c047608`, `388e788`, `9b2ef89`, `f3399e8`, `3484999` | Code, tests, prompts, smoke-test evidence, sampling prompts and report, action-surface comparison | Claude Code | Claude Code |
| `24ffb13` | `LABELING_RULE.md` | My text | none |
| `f18cbae` | Label set: label sheets and the method paragraph in `LABEL_SET.md` | Written by Claude Code, committed with no co-author line (the exception) | none |
| `f55b88d` | `labels/HAND_LABELS.md` | My labels and reasons; ChatGPT formatted my notes into the table | none |
| `6beef48`, `0dd01ab`, `d7411f4`, `4a46925` | Live run evidence | Run by me in Terminal. I committed `0dd01ab`, `d7411f4` and `4a46925` myself | none |
| `6064e8e` | Sampling replies | Run by me in the Claude app and committed by me | none |

The Final-section commits (`31d20fa`, `e7f7362`) and the fold parts of `4da69e5`, `dfb37a7` and `b8a5b81` also contain Claude Code's arrangement of my sentences without a co-author line. The words are mine; the ordering and source tags are Claude Code's.
