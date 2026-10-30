# Job-Search Agent 1 — The Contract and the Watch

**Lavanya R** · INFO 7375 · Fall 2026.

**What it does:**
- Watches one public job board (Greenhouse, `databricks`).
- Saves every raw response as evidence.
- Reports only postings that are new since the last run.
- Gives each new posting two verdicts for a **fictional** persona, Priya Nair:
  - **rule:** a record anyone can recompute from CONTRACT.md;
  - **Claude:** a judgment, labeled as one, under a prompt contract and a strict validator.

The agent never applies, emails, messages or logs in anywhere. No real résumé is used. `persona/priya-nair.resume.json` is fictional (`@example.com`, `555`), and the agent refuses to run on one that isn't.

## Language and toolchain

| Tool | Version used | Needed for |
|---|---|---|
| Python | 3.11.5, **standard library only** (no `pip install`) | everything |
| Claude Code CLI (`claude`) | 2.1.312, logged in with `claude auth login` (NEU Claude account; no API key) | only the Claude steps: `agent.judge` and the experiments |
| Network | `boards-api.greenhouse.io` only | only `agent.watch` |
| OS | macOS (Darwin 25.5) | — |

## Commands

### From a fresh clone

```bash
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai.git
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/lavanya-r/js1-contract-and-watch
```

### Safe checks: offline, no Claude, and nothing in this folder changes

```bash
# Tests: 43, offline
python3 -m unittest discover -s tests -t . -v

# Replay run 1 then run 2 from the saved responses, into /tmp.
# Expect "0 — baseline run", then "New since last run: 10".
rm -rf /tmp/js1-check
python3 -m agent.watch --from-file evidence/raw/databricks-2026-10-29T213155Z.json.gz --seeded --state /tmp/js1-check/state.json --raw-dir /tmp/js1-check/raw --report-dir /tmp/js1-check/reports
python3 -m agent.watch --from-file evidence/raw/databricks-2026-10-30T204649Z.json.gz --seeded --state /tmp/js1-check/state.json --raw-dir /tmp/js1-check/raw --report-dir /tmp/js1-check/reports
```

These replays are labeled `seeded` in their output, as required. They report rule-v2 verdicts, so "Sr. Counsel" fails only on its title. The committed run 2 report was made under rule v1.

### Live commands

These change files in this folder. On a clone, a live watch would be **run 3** against the committed state, so point it at `/tmp` unless you mean to add a run:

```bash
# The watch: one live fetch
python3 -m agent.watch --board databricks --state /tmp/js1-live/state.json --raw-dir /tmp/js1-live/raw --report-dir /tmp/js1-live/reports

# 3. Two judges on a run's new postings (re-reads saved evidence; calls Claude once per posting)
python3 -m agent.judge reports/run-databricks-2026-10-30T204649Z.json

# 4. Experiments (real Claude calls)
python3 -m experiments.select_labeling_set          # reproducible 20-posting set, seed 7375
python3 -m experiments.sampling                     # 5 postings x 4 fresh calls
python3 -m experiments.prompt_experiment prompts/baseline.md dev
python3 -m experiments.prompt_experiment prompts/revision.md dev
python3 -m experiments.prompt_experiment prompts/baseline.md held_out
python3 -m experiments.prompt_experiment prompts/revision.md held_out
python3 -m experiments.action_surface
```

`--from-file` without `--seeded` is refused, so a run from a saved response can't pass as live.

Raw responses are saved gzipped and byte-for-byte. To read one:

```bash
gunzip -c evidence/raw/<file>.json.gz | head
```

**Re-running changes things.** A new `agent.watch` run updates `state/` and adds files. Claude calls produce new replies.

## What ran (all real, all dated)

| When (ET) | What | Result | Evidence |
|---|---|---|---|
| 2026-10-29 17:26 | CONTRACT.md committed, before any code | — | commit `891aec3` |
| 2026-10-29 17:29 | Run 1, **datadog**, live | 397 postings, 0 new (baseline) | `reports/run-datadog-2026-10-29T212918Z.md` |
| 2026-10-29 17:31 | Run 1, **databricks**, live (the board was switched; see CONTRACT.md) | 906 postings, 0 new (baseline) | `reports/run-databricks-2026-10-29T213155Z.md` |
| 2026-10-30 16:46 | **Run 2, databricks, live, second calendar day** | 903 postings, **10 new**, all `not_relevant` (rule v1) | `reports/run-databricks-2026-10-30T204649Z.md`, `state/databricks-seen_ids.json` |
| 2026-10-30 | Rule v2 (US state names count as US), a dated contract change | — | commit `83a4089` |
| 2026-10-30 17:15 | Both judges on run 2's 10 new postings | rule: 10 not_relevant. Claude: 2 valid (agree), 8 INVALID (empty `resume_fields`) | `reports/judged-run-databricks-2026-10-30T204649Z.md` |
| 2026-10-30 17:22 | Sampling, 20 calls | 0 spread; 0/20 match hand labels | [SAMPLING.md](SAMPLING.md) |
| 2026-10-30 17:23–17:27 | Prompt experiment, 40 calls | baseline 4/10 dev, 4/10 held-out. Revision 9/10 dev, 10/10 held-out | [PROMPT-EXPERIMENT.md](PROMPT-EXPERIMENT.md) |
| 2026-10-30 | Action-surface comparison, 3 calls | all three said not_relevant; the agent's fetch lost text | [ACTION-SURFACE.md](ACTION-SURFACE.md) |

No run was seeded. Both watch runs on Databricks were live, a calendar day apart.

## Files

**Documents:**
- `CONTRACT.md`: In / Out / Refuses / the rule / wrong versions / failure sentence, with dated changes.
- `SOURCES.md`: what I used, what I did, what Claude contributed.
- `FRICTIONAL.md`: the dated log.

**Code:**
- `agent/`
  - `fetch.py`: the allow-list.
  - `persona.py`: the fictional-résumé guard.
  - `state.py`: new-by-id.
  - `rule.py`: the record judge.
  - `claude_judge.py`: the judgment judge and its validator.
  - `watch.py`, `judge.py`: the command-line entry points.
- `tests/`: 43 offline tests (`test_rule.py` 19, `test_watch.py` 11, `test_claude_judge.py` 7, `test_wrong_versions.py` 6). Test postings are constructed and labeled as such in `tests/fixtures.py`.
- `prompts/`: `baseline.md`, and `revision.md`, which is the baseline plus one line.
- `labels/`: `LABELING-RULE.md`, `selection.json`, `LABELING-SHEET.md`, `hand_labels.json`.
- `experiments/`: scripts, `SAMPLING-RESULTS.json`, `results/`.

**Evidence:**
- `evidence/raw/`: the board responses.
- `evidence/claude/`: every Claude reply, verbatim, with time and model.
- `evidence/action-surface/`: the three surface runs.
- `state/`: one seen-ids file per board.
- `reports/`: run reports and the judged report.

## Sign-off — Job-Search Agent 1

**Checked:**
- **Allow-list:** only `https://boards-api.greenhouse.io`. Look-alike hosts and plain http are refused before any network call. Tested by `test_watch.TestAllowList`.
  - The code also refuses redirects that leave the allow-list. That part is *not* tested.
- **Fictional-résumé guard:** a real-looking résumé stops the run before any fetch. Tested by `test_watch.TestPersona` and `test_real_looking_resume_stops_before_any_fetch`.
- **Raw response saved byte-for-byte.** Tested by `test_raw_response_saved_byte_for_byte`.
- **Baseline reports none; later runs report only unseen ids.** Tested by `test_baseline_then_new_only`, `test_removed_then_reposted_id_is_not_new`, and live: run 2 reported 10 of 903.
- **Each of the 5 rule checks, including whole-word boundaries.** Tested by `test_rule.py`.
- **The 3 wrong versions are caught.** Tested by `test_wrong_versions.py`.
- **The validator rejects 14 malformed reply shapes, and an INVALID reply is never shown as a verdict.** Tested by `test_claude_judge.py`.
- **The rule against my own judgment:** 12/20 agree. See PROMPT-EXPERIMENT.md.

**How:**
- **By a test I wrote before reading Claude's code:** none. I specified the rules and the 3 wrong versions in CONTRACT.md before any code (`891aec3`), and Claude wrote the tests against that contract.
- **By hand:**
  - I ran the full test suite myself: on 2026-10-29 (34 tests, OK), and again on 2026-10-30 after the newer tests were added (`python3 -B -m unittest discover -s tests -t . -v`: 43 tests, OK).
  - I hand-labeled 20 real postings with my labeling rule (`labels/hand_labels.json`).
  - **I tested my failure sentence.** I applied CONTRACT.md's 5 checks by hand to run 2's 10 new postings: 10/10 matched rule v1 and v2 (`labels/contract_hand_check.json`). All 10 failed on title or location, so checks 4–5 were not exercised by hand.
  - I re-read FRICTIONAL.md on 2026-10-30, including the 10-30 entries, and confirmed it matches what happened.
- **By recomputation:**
  - The rule verdicts in every report are recomputed from the saved raw response.
  - The selection of the 20 postings is reproducible: same seed, same output, checked by Claude with `cmp`.
- **With Claude's help:** Claude wrote all the code, the tests, the prompt wording and the first drafts of every document. It also ran the experiments and pointed out the US-location gap and the "sponsor" wording.

**Not checked:**
1. **Check 5 on a real posting.** No real posting on either board said it can't sponsor visas, so the no-sponsorship check has only been exercised on constructed postings.
2. **Any posting I would call "fit".** All 20 hand labels are "not fit", so I never tested whether the revised prompt (or the rule) correctly accepts a good job. A prompt that always says no would also score 10/10.
3. **The validator's `.0` path quirk.** It rejects `education.0.end_date` but accepts `education[0].end_date`. I found this after seeing results and left it unfixed, so it cost the revision one point and made two action-surface replies INVALID.
4. **Updated postings.** A posting whose content changes but keeps its id is never reported again.
5. **Greenhouse's terms of use.** I used the public, documented job-board endpoint at one request per run, with a descriptive User-Agent, but I did not read Greenhouse's terms in full.
6. **Rule v2's location list beyond the formats I saw.** "Georgia" the country would be read as the US state.
7. **The agent surface's actual tool calls.** The CLI summary has no transcript.

**Not claiming:**
- That this agent finds jobs worth Priya's time. On Databricks, my rule called 8 jobs relevant that I judged not fit.
- That Claude's judgment is correct in general, or that 10/10 on 10 held-out postings would hold on another sample, board, day or model.
- That 4 identical replies mean a posting's verdict never varies.
- That it works on Lever, Ashby or SmartRecruiters. Only Greenhouse is implemented.

**Signed:** Lavanya R, 2026-10-30

## Driver's seat

| Part of the task | Claude did | I did | Why it stays mine | Where the split shows |
|---|---|---|---|---|
| What counts as relevant | asked the questions, typed up the answers, proposed the visa-phrase list | chose every rule, the 3 wrong versions and the failure sentence; approved the phrase list | the verdicts are only as good as the definition, and I have to defend it | `891aec3` (CONTRACT.md before any code); CONTRACT.md provenance note |
| Changing the rule | found that Databricks drops "USA" (111/903 passing) | chose to fix it as a dated v2, before labeling | changing the rule after seeing answers would be tuning to them | `47662ea` (run 2 under v1) then `83a4089` (v2) |
| Which board | measured 10 boards under my rule | chose Databricks after Datadog had 0/397 | where the agent looks is a judgment about my search | CONTRACT.md change note, 2026-10-29 |
| Ground truth | picked 20 postings by a fixed seed, summarized the requirements | wrote/chose the labeling rule; labeled all 20 | the labels are the answer key; if Claude wrote them, the experiment would score Claude against Claude | `323ee74` (rule and set) then `8f752da` (labels), before any Claude call on them |
| The one prompt change | ran the baseline, explained the two candidate changes in simple terms | chose B, the experience/graduation line | which failure matters more is my call | `prompts/revision.md` (one added line); FRICTIONAL 2026-10-30 |
| Code, tests, runs, drafts | wrote all of it and ran it | ran the tests myself; read the logs and reports | I am responsible for what I submit, and I have to be able to explain it | FRICTIONAL "I ran the tests myself"; SOURCES.md |
| Sign-off | drafted the text | decided to sign; edited the line myself in TextEdit and committed it myself | only I can vouch for it | my commit "docs(js1): sign the JS1 sign-off" (2026-10-30). It is the only commit in this folder without a Claude co-author line |

**Transcript lines.** These are quoted verbatim from my Claude Code session. The transcript itself stays on my machine, as the brief requires.

| Date | I wrote / chose | What it decided |
|---|---|---|
| 2026-10-29 | "give me an alternate without paying any money" | rejected the paid API-key route, so the Claude judge uses `claude -p` on my NEU login |
| 2026-10-29 | "option A" | chose to write the contract by answering multiple-choice questions |
| 2026-10-29 | card: "Disagrees with my hand check" | the failure sentence |
| 2026-10-29 | card: "Switch to Databricks (Recommended)" | the board change after Datadog's 0/397 |
| 2026-10-30 | card: "Fix the rule, dated (Recommended)" | rule v2 |
| 2026-10-30 | card: "My own judgment" | the labeling rule |
| 2026-10-30 | "B" | the one prompt change (the experience/graduation line) |
