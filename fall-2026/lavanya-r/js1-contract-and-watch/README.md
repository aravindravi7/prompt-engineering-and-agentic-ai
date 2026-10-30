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

Run everything from this folder:

```bash
cd fall-2026/lavanya-r/js1-contract-and-watch
```

```bash
# 1. Tests: offline, no network, no Claude. 43 tests.
python3 -m unittest discover -s tests -t . -v

# 2. The watch: one live fetch. The first run on a board is the baseline.
python3 -m agent.watch --board databricks

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

# A run from a saved response must be labeled seeded (refused otherwise):
python3 -m agent.watch --from-file evidence/raw/<file>.json.gz --seeded --state /tmp/s.json
```

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
  - I ran the full test suite myself on 2026-10-29 (34 tests, OK). It now has 43.
  - I hand-labeled 20 real postings.
  - I read FRICTIONAL.md and confirmed it matches what happened.
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

**Signed or withheld:** ____________ (name, date)

## Driver's seat

| Part of the task | Claude did | I did | Why it stays mine | Where the split shows |
|---|---|---|---|---|
| What counts as relevant | asked the questions, typed up the answers, proposed the visa-phrase list | chose every rule, the 3 wrong versions and the failure sentence; approved the phrase list | the verdicts are only as good as the definition, and I have to defend it | `891aec3` (CONTRACT.md before any code); CONTRACT.md provenance note |
| Changing the rule | found that Databricks drops "USA" (111/903 passing) | chose to fix it as a dated v2, before labeling | changing the rule after seeing answers would be tuning to them | `47662ea` (run 2 under v1) then `83a4089` (v2) |
| Which board | measured 10 boards under my rule | chose Databricks after Datadog had 0/397 | where the agent looks is a judgment about my search | CONTRACT.md change note, 2026-10-29 |
| Ground truth | picked 20 postings by a fixed seed, summarized the requirements | wrote/chose the labeling rule; labeled all 20 | the labels are the answer key; if Claude wrote them, the experiment would score Claude against Claude | `323ee74` (rule and set) then `8f752da` (labels), before any Claude call on them |
| The one prompt change | ran the baseline, explained the two candidate changes in simple terms | chose B, the experience/graduation line | which failure matters more is my call | `prompts/revision.md` (one added line); FRICTIONAL 2026-10-30 |
| Code, tests, runs, drafts | wrote all of it and ran it | ran the tests myself; read the logs and reports | I am responsible for what I submit, and I have to be able to explain it | FRICTIONAL "I ran the tests myself"; SOURCES.md |
| Sign-off | drafted the text | decide whether to sign or withhold | only I can vouch for it | the line above |
