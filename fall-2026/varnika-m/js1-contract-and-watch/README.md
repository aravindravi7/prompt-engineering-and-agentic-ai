# Job-Search Agent 1 — The Contract and the Watch

Varnika M · INFO 7375, Fall 2026

The agent watches one public job board: Anthropic's Greenhouse board. Each time it runs, it reports only the postings that are new since the last run. Each new posting gets two verdicts against a fictional résumé (Aarav Patel):

- a **record** from my written rule, which anyone can recompute;
- a **judgment** from Claude, which is labeled as an opinion.

The specification is [CONTRACT.md](CONTRACT.md). Who did what is in [SOURCES.md](SOURCES.md), and the process log is in [FRICTIONAL.md](FRICTIONAL.md).

## Language and toolchain

| What | Version | Needed for |
|---|---|---|
| Python, standard library only | 3.9 or later (tested on 3.9.6, macOS) | everything |
| Claude Code CLI (`claude`), logged in | tested with 2.1.283 | only the `--claude` judgment step |
| Network access to `boards-api.greenhouse.io` | n/a | only live runs |

Nothing needs to be installed. There is no `requirements.txt`, because nothing outside the standard library is used.

## Commands

Run everything from this folder:

```bash
cd fall-2026/varnika-m/js1-contract-and-watch
```

**Tests.** These run offline, without Claude, on constructed postings only:

```bash
python3 -m unittest discover -s tests -t . -v
```

**A live run.** This fetches the board once and writes into `evidence/raw/`, `runs/` and `state/`:

```bash
python3 -m agent.watch                 # rule verdicts only
python3 -m agent.watch --claude        # also ask Claude about each new posting
```

**A seeded run** from a saved response. The run record and the report label it `seeded`:

```bash
python3 -m agent.watch --fixture path/to/saved-response.json
```

The first run is the baseline: it records every posting id and reports none as new. Each later run reports only the ids that are not in `state/anthropic.state.json`.

## What is in this folder

| Path | What it is |
|---|---|
| `CONTRACT.md` | In, Out, Refuses, the rule, wrong versions, failure; written before any code |
| `persona/aarav-patel.resume.example.json` | The fictional résumé (`@example.com`, 555 phone) |
| `agent/` | The code: `watch.py` (the run), `rule.py` (Rules 1–5), `claude_judge.py` (prompt, call, validator), `fetch.py` (allow-list), `resume.py` (fictional check) |
| `prompts/baseline-v1.txt` | The prompt for Claude's judgment |
| `tests/` | 73 offline tests |
| `evidence/raw/` | Every raw board response, byte for byte, gzip-compressed (`gunzip -c FILE` restores it) |
| `runs/` | One JSON record and one Markdown report per run |
| `state/anthropic.state.json` | Every posting id seen so far, and the list of runs |

## What ran

All runs were on 2026-10-31 (UTC).

### The live watch (`state/anthropic.state.json`)

| Run | When | Source | Postings | New | Raw response | Report |
|---|---|---|---:|---:|---|---|
| 1, baseline | 07:40:11 | **live**, run by me | 675 | 0 (baseline) | [`evidence/raw/anthropic-2026-10-31T074011Z.json.gz`](evidence/raw/anthropic-2026-10-31T074011Z.json.gz) (SHA-256 `1e5b62fe…`) | [report](runs/anthropic-2026-10-31T074011Z.md) |
| 2 | 08:29:09 | **live**, run by Claude Code, with `--claude` | 675 | 0 | [`evidence/raw/anthropic-2026-10-31T082909Z.json.gz`](evidence/raw/anthropic-2026-10-31T082909Z.json.gz) (SHA-256 `1e5b62fe…`) | [report](runs/anthropic-2026-10-31T082909Z.md) |

Live run 2's response is byte-for-byte the same as run 1's (same SHA-256). The board did not change in those 49 minutes, so the live pair shows only that nothing is reported twice. The assignment was due the same day, so the **real change** is shown by the seeded pair below.

### The seeded pair (`seeded/`, with its own state file)

| Run | When | Source | Postings | New | Raw response | Report |
|---|---|---|---:|---:|---|---|
| A, baseline | 07:45:34 | **seeded, CONSTRUCTED**: run 1's saved response minus the 9 postings first published on or after 2026-10-30 ([`tools/make_seeded_fixture.py`](tools/make_seeded_fixture.py)) | 666 | 0 (baseline) | [`seeded/evidence/raw/anthropic-2026-10-31T074534Z.json.gz`](seeded/evidence/raw/anthropic-2026-10-31T074534Z.json.gz) | [report](seeded/runs/anthropic-2026-10-31T074534Z.md) |
| B | 07:45:35 | **seeded**: run 1's saved live response, replayed, with `--claude` | 675 | **9** | [`seeded/evidence/raw/anthropic-2026-10-31T074535Z.json.gz`](seeded/evidence/raw/anthropic-2026-10-31T074535Z.json.gz) (SHA-256 `1e5b62fe…`, the same bytes as run 1) | [report](seeded/runs/anthropic-2026-10-31T074535Z.md) |

The 9 postings run B reports as new are real postings, first published on 2026-10-30. Each has both judges: the rule's **record**, and **Claude's judgment** with the validator passed. All 9 are `NOT_MATCH` from both. Nobody ever received run A's response; it approximates the board before those 9 appeared, and it cannot include postings that closed before run 1.

To replay the seeded pair from a fresh clone, without network or Claude, into a scratch folder:

```bash
python3 -m agent.watch --fixture seeded/fixtures/anthropic-CONSTRUCTED-before-2026-10-30.json.gz --state /tmp/js1/state.json --out /tmp/js1
python3 -m agent.watch --fixture evidence/raw/anthropic-2026-10-31T074011Z.json.gz --state /tmp/js1/state.json --out /tmp/js1
```

The second command should report the same 9 new ids, with the same rule verdicts, as seeded run B.

### Claude replies on record

There are 76 replies in total, and every one passed the validator. 75 are fresh Claude Code conversations with model `claude-opus-5-5`. One (way 1) is my own claude.ai chat, which used Sonnet 5.5 on the Free plan.

| Group | Replies | Where |
|---|---:|---|
| Seeded run B | 9 | `seeded/runs/anthropic-2026-10-31T074535Z.json` |
| Sampling | 20, plus 4 added after the results | `sampling/` |
| Prompt experiment | 40 | `experiment/replies/` |
| Action surface, ways 1–3 | 3 (way 1 is my claude.ai chat) | `action-surface/` |

A practice call made while building the agent is not evidence and is not in this folder (see `SOURCES.md`).

## The three Chapter artifacts

- **Sampling report (Chapter 1):** [sampling/SAMPLING-REPORT.md](sampling/SAMPLING-REPORT.md)
- **Prompt experiment (Chapter 2):** [experiment/PROMPT-EXPERIMENT.md](experiment/PROMPT-EXPERIMENT.md). Also: the labeling rule [`LABELING-RULE.md`](experiment/LABELING-RULE.md), the labels [`labels.csv`](experiment/labels.csv), the prompts [`prompts/`](prompts/), and the decision [`REVISION-DECISION.md`](experiment/REVISION-DECISION.md).
- **Action-surface comparison (Chapter 3):** [action-surface/ACTION-SURFACE.md](action-surface/ACTION-SURFACE.md)

## Sign-off — Job-Search Agent 1

*Drafted by Claude Code from the record of what was done. Each line is for me to check, change, and then sign or withhold.*

**Checked.**

- **New since last run, by id.**
  - Tests: `test_first_run_is_a_baseline_with_zero_new`, `test_same_id_with_a_changed_title_is_not_new`, `test_new_id_with_an_old_title_is_new`, `test_posting_that_disappears_and_comes_back_is_not_new`.
  - Real runs: live run 2 reported 0 new on bytes identical to run 1 (same SHA-256), and seeded run B reported exactly the 9 postings removed from its baseline.
- **The raw response is saved byte for byte, before parsing.** Tests: `test_raw_response_saved_byte_for_byte_with_its_hash`, `test_raw_response_saved_before_processing`.
- **Both wrong versions in my contract are caught.** Tests: `test_wrong_version_1_skills_only_in_description_still_count` and `test_wrong_version_2_javascript_does_not_count_as_java`. `tests/test_wrong_versions_are_caught.py` shows that each fails against its wrong version.
- **Claude's judgment is validated and kept separate from the record.** Tests: `test_reply_that_fails_the_validator_is_rejected_not_counted`, `test_claude_disagreeing_does_not_change_the_rule_verdict`.
- **One rule verdict recomputed.** Data Engineer (5464234008): Rule 4 fails. I found "5+ years" on the live posting myself.

**How.**

- **By hand:** the Data Engineer Rule 4 recomputation, my 20 hand labels, and running the test suite myself (73/73 OK).
- **By tests written before the code:** Claude Code wrote the tests from my contract. They were committed (`7681e8e`) before any implementation existed (`9397fac`). I did not write them.
- **With Claude's help:** the SHA-256 comparisons between runs, checking my 11 years notes against the postings' must-have sections, and the agent's rule on the whole board agreeing with an independent count (1 match of 675).

**Not checked.**

1. I did not read the test code line by line. The tests and the code were both written by Claude Code, so a misunderstanding they share would not be caught.
2. On real data, the "new posting" path was shown only by the seeded pair, whose earlier response was constructed. Live run 2 saw no change.
3. Redirect refusal was tested only with a constructed redirect, never with a real one.
4. I recomputed only one of the rule's verdicts by hand, not all 675.
5. Claude's ability to recognize a `MATCH` is barely tested: 1 of my 20 labels is `MATCH`, and the held-out set has none.
6. I did not read Greenhouse's or Anthropic's terms of use for the board API. I relied on it being a public endpoint, and made 4 requests to it in total: the board check, live runs 1 and 2, and way 3's single-posting fetch.

**Not claiming.**

- That this agent finds good jobs for Aarav or for anyone real.
- That Claude's judgments are correct.
- That seeded run A shows what the board actually looked like before 2026-10-30.
- That revision-v1 is better than baseline-v1.
- That any result holds for another board, persona, model or day.

**Signed or withheld:** ____________ (name, date)

## Driver's seat

| Task | What Claude did | What I did | Why that part stays mine | Where it shows |
|---|---|---|---|---|
| The contract | Drafted a version I discarded; reviewed mine three times; wrote the dated Rules 1–3 addition at my request | Wrote `CONTRACT.md` in my own words; committed it before any code | I have to predict and defend every verdict when a TA asks | `93afbb8`; `SOURCES.md` contract rows |
| Code and tests | Wrote all of them | Ran the tests myself and the live baseline (run 1) | Running is my check that the code does what the contract says | `9397fac` ("I ran the tests: 72/72 pass"); `e976c58` |
| Labeling | Drafted the labeling rule; fixed CSV quoting | **Labeled all 20 postings** | The labels are the human answer Claude is scored against. Claude labeling them would score Claude against Claude. | `808270d` (rule) before `3ff2be4` (my labels) |
| The revision | Suggested three single changes; ran every call | Chose "must-haves only"; made the prediction before it ran | Which change to test, and the prediction, are my reasoning | `31f068e`, frozen at 08:28:34, before the revision's first call at 08:28:59 |
| Verification | Comparisons and the full-board check | Recomputed Data Engineer's Rule 4 on the live page | One verdict I checked with my own eyes | `SOURCES.md`, "Recomputation by hand" |
| The sign-off | Drafted the lines above | Decide whether to sign, and change anything untrue | My name is the one on it | the line above |
