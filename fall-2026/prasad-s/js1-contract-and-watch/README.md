# Job-Search Agent 1: The Contract and the Watch

## What this is

This is the first layer of my job-search agent. It is one board, one résumé,
new postings only, and every verdict is justified.

- **The board:** the agent reads the public Greenhouse board for Stripe, from one
  allow-listed URL. It saves the raw response as evidence, and it remembers the
  posting ids it has seen in `state.json`.
- **What it reports:** only postings new since the last run. The first run is a
  baseline that reports none as new.
- **The résumé:** a fictional persona, Alex Rivera, in
  [resume_persona.json](resume_persona.json).
- **Two judges, side by side for each new posting:**
  - **The rule** (a record) is the written rule in [CONTRACT.md](CONTRACT.md) §4.
    Anyone can recompute it by hand.
  - **Claude** (a judgment) is labeled `judgment (Claude)`. I ran Claude myself,
    outside the agent, one posting per fresh Incognito chat, under a fixed prompt
    contract. The agent only reads and validates the saved replies, and it
    rejects any reply that breaks the §6 format.
- **The contract:** [CONTRACT.md](CONTRACT.md) was written before any code. It is
  the specification for everything here.

## Language and toolchain

- **Python 3.11+**, standard library only. 3.11 is the floor, and the repository
  CI runs 3.11, 3.12 and 3.13.
- **Tests:** `unittest`.
- **What I used:** Python 3.13.17, as `python3.13`.
- **No third-party packages.** There is no `requirements.txt`, because nothing
  needs installing.
- **macOS, python.org installer:** a live fetch needs the certificate step first.
  Run `Install Certificates.command`, which is in the `/Applications/Python 3.13/`
  folder. Without it, the HTTPS fetch fails with `CERTIFICATE_VERIFY_FAILED`, as
  my first run-1 attempt did
  ([evidence/run1_attempt1_failed_ssl_2026-10-27.txt](evidence/run1_attempt1_failed_ssl_2026-10-27.txt)).
  The tests and the offline replay need no network and no certificates.
- **Clipboard:** `tools/prep_chat.py` and `tools/save_reply.py` use the macOS
  clipboard (`pbcopy` and `pbpaste`).

## Exact commands

Run every command from this folder (`fall-2026/prasad-s/js1-contract-and-watch/`).

### Tests

```bash
python3.13 -m unittest discover -s tests -v
```

- **The last full run:** 45 of 45 tests passed. Commit 35d4342 records this: "I ran 45/45 tests".
- **Test-can-fail check, 2026-10-27:** with one expected value deliberately
  changed, the suite failed on that case. The output is in
  [evidence/test_can_fail_2026-10-27.txt](evidence/test_can_fail_2026-10-27.txt).

### Live run (uses the network)

```bash
python3.13 -m agent
```

- **Config:** this reads [config.json](config.json).
- **The fetch:** exactly one URL,
  `https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true`, with
  redirects refused.
- **What it writes:**
  - a new evidence file and its sidecar note in `evidence/`;
  - `run_report.json`;
  - `state.json`.

  Both `run_report.json` and `state.json` are tracked files.

### Offline replay of run 1 and run 2 (no network)

The replay re-runs both runs in seeded mode, from the two saved board responses
in `evidence/`. Its state file and reports go under `replay/`, which `.gitignore`
excludes. Seeded mode reads the saved file instead of fetching, and it writes no
new evidence. The real `state.json` and `run_report.json` are not touched. The
config is [replay/config_replay.json](replay/config_replay.json).

From a fresh clone:

```bash
git clone https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai.git
```

```bash
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/prasad-s/js1-contract-and-watch
```

**Replay run 1** (seeded; a baseline, because `replay/state.json` does not exist yet):

```bash
python3.13 -m agent --config replay/config_replay.json --seed evidence/stripe_jobs_content_true_2026-10-27T223947Z.json --report replay/run1_report.json
```

Expected output. The numbers and message are from
[evidence/run_report_run1_2026-10-27.json](evidence/run_report_run1_2026-10-27.json);
the mode is `seeded` here, where the original run 1 was `live`:

```text
mode: seeded
total_fetched: 711
new_count: 0
baseline run: 711 ids saved, 0 postings reported as new
```

**Replay run 2** (seeded):

```bash
python3.13 -m agent --config replay/config_replay.json --seed evidence/stripe_jobs_content_true_2026-10-29T011132Z.json --report replay/run2_report.json
```

Expected:

- **The first four lines** are as follows. The numbers are from
  [evidence/run_report_run2_2026-10-28.json](evidence/run_report_run2_2026-10-28.json)
  and
  [evidence/run_report_run2_seeded_rerun_with_claude_2026-10-29.json](evidence/run_report_run2_seeded_rerun_with_claude_2026-10-29.json):

  ```text
  mode: seeded
  total_fetched: 721
  new_count: 29
  29 new postings
  ```

- **Then one entry for each of the 29 new postings:**
  - `rule verdict (record): not_relevant` for all 29;
  - `judgment (Claude): not_relevant` for 27;
  - `judgment (Claude): rejected` for 2 (8332676 and 8130876).

  These are the same verdicts as the saved seeded re-run report
  ([evidence/run_report_run2_seeded_rerun_with_claude_2026-10-29.json](evidence/run_report_run2_seeded_rerun_with_claude_2026-10-29.json)),
  because the replay reads the same 29 saved replies in [claude_outputs/](claude_outputs/).

**Checks after the replay.** `cmp` prints nothing when two files are byte-identical.

```bash
cmp replay/state.json evidence/state_after_run2_2026-10-28.json
```

```bash
python3.13 tools/compare_verdicts.py replay/run2_report.json
```

- **The `cmp` check:** `replay/state.json` should hold 740 ids
  ([evidence/state_after_run2_2026-10-28.json](evidence/state_after_run2_2026-10-28.json)).
- **The `compare_verdicts` check:** its last line should read
  `records: 29  agree: 27  disagree: 0  rejected: 2`
  (the saved seeded re-run report; commit fc69190).

To compare after replay run 1 instead, before running replay run 2:

```bash
cmp replay/state.json evidence/state_after_run1_2026-10-27.json
```

To replay again from the start, delete the replay outputs first:

```bash
rm -f replay/state.json replay/run1_report.json replay/run2_report.json
```

### The tools

All of these tools read only, except `tools/save_reply.py`.

```bash
python3.13 tools/show_posting.py 7392697
```

`tools/show_posting.py <posting_id> [--source FILE] [--for-claude]` shows one
posting's title, location and §4-cleaned content, with no verdicts. The default
source is the board file named in [experiments/selected_ids.json](experiments/selected_ids.json).

```bash
python3.13 tools/prep_chat.py 7392697 --set dev --prompt prompts/claude_prompt_revision.txt
```

`tools/prep_chat.py <posting_id> --set run2|sampling|dev|heldout [--prompt FILE]`
builds one chat prompt and copies it to the clipboard. It prints only the id,
the set, the prompt version and a character count.

```bash
python3.13 tools/save_reply.py 7392697 --set dev --model "Opus 5.5" --prompt prompts/claude_prompt_revision.txt
```

`tools/save_reply.py <posting_id> --set SET --model "MODEL" [--repeat N] [--prompt FILE]`
saves the reply on the clipboard byte for byte, with its metadata entry. It
refuses to overwrite, so for an id that already has a saved reply, like the one
above, it refuses.

```bash
python3.13 tools/score_replies.py experiments/sampling --labels experiments/hand_labels_development.json
```

```bash
python3.13 tools/score_replies.py experiments/prompt_experiment/baseline --split development --labels experiments/hand_labels_development.json
```

```bash
python3.13 tools/score_replies.py experiments/prompt_experiment/revision --split development --labels experiments/hand_labels_development.json
```

```bash
python3.13 tools/score_replies.py experiments/prompt_experiment/baseline --split held_out --labels experiments/hand_labels_heldout.json
```

```bash
python3.13 tools/score_replies.py experiments/prompt_experiment/revision --split held_out --labels experiments/hand_labels_heldout.json
```

`tools/score_replies.py FOLDER [--labels FILE] [--split development|held_out]`
runs the agent's §6 validator on each saved reply and prints PASS or FAIL per
[experiments/scoring.md](experiments/scoring.md), then totals.

```bash
python3.13 tools/compare_hand_labels.py experiments/hand_labels_development.json
```

```bash
python3.13 tools/compare_hand_labels.py experiments/hand_labels_heldout.json
```

`tools/compare_hand_labels.py [LABELS_FILE]` puts my hand C1, C2, C3 and verdict
next to the rule's, one posting per line.

```bash
python3.13 tools/compare_verdicts.py evidence/run_report_run2_seeded_rerun_with_claude_2026-10-29.json
```

`tools/compare_verdicts.py <run_report.json>` shows the rule verdict and
`judgment (Claude)` side by side for each record in a run report.

## What ran

All times are local (UTC−04:00) unless marked Z.

**Run 1: live baseline, 2026-10-27**
- **First attempt:** it failed with `CERTIFICATE_VERIFY_FAILED`. Nothing was fetched or written
  ([evidence/run1_attempt1_failed_ssl_2026-10-27.txt](evidence/run1_attempt1_failed_ssl_2026-10-27.txt)).
- **Second attempt:** this was the baseline, at 2026-10-27T22:39:47Z (18:39 local).
  - 711 postings were fetched, 0 were reported as new, and 711 ids were saved
    ([evidence/run_report_run1_2026-10-27.json](evidence/run_report_run1_2026-10-27.json),
    [evidence/run1_terminal_2026-10-27.txt](evidence/run1_terminal_2026-10-27.txt),
    [evidence/state_after_run1_2026-10-27.json](evidence/state_after_run1_2026-10-27.json)).
  - The raw response, 5,526,436 bytes, is
    [evidence/stripe_jobs_content_true_2026-10-27T223947Z.json](evidence/stripe_jobs_content_true_2026-10-27T223947Z.json),
    with its [sidecar note](evidence/stripe_jobs_content_true_2026-10-27T223947Z.json.sidecar.json).
- **Commit:** 9078be3.

**Run 2: live, second calendar day**
- **When:** the evidence file's name carries the UTC date, 2026-10-29T01:11:32Z, but
  the run was on 2026-10-28 at 21:11 local time.
- **Counts:**
  - 721 postings were fetched and 29 were new;
  - the rule verdict was `not_relevant` for all 29, so 0 were relevant;
  - 740 ids were saved

  ([evidence/run_report_run2_2026-10-28.json](evidence/run_report_run2_2026-10-28.json),
  [evidence/run2_terminal_2026-10-28.txt](evidence/run2_terminal_2026-10-28.txt),
  [evidence/state_after_run2_2026-10-28.json](evidence/state_after_run2_2026-10-28.json)).
- **Claude at this run:** `judgment (Claude)` was `rejected` for all 29, with the reason
  `claude_outputs/metadata.json does not exist`. The replies were saved the next day.
- **Recount:** my independent recount of new ids was 29, the same ids as the agent's
  ([evidence/run2_recount_by_me_2026-10-28.txt](evidence/run2_recount_by_me_2026-10-28.txt)).
- **Raw response:** 5,607,841 bytes,
  [evidence/stripe_jobs_content_true_2026-10-29T011132Z.json](evidence/stripe_jobs_content_true_2026-10-29T011132Z.json),
  with its [sidecar note](evidence/stripe_jobs_content_true_2026-10-29T011132Z.json.sidecar.json).
- **Commit:** 135b223.

**Seeded re-run of run 2 with Claude's replies, 2026-10-29** (seeded, not live)
- **The replies:** I collected 29 replies on 2026-10-29 between 15:00 and 15:42. Every one
  came from a fresh Incognito chat with Opus 5.5 and prompt baseline-v1
  ([claude_outputs/metadata.json](claude_outputs/metadata.json)).
- **The re-run:** a seeded run read the run-2 board file, starting from a copy of the
  run-1 state in the gitignored `rerun_run2/` folder, at 2026-10-29T19:45:39Z.
- **Result:** 29 new; `judgment (Claude)` was `not_relevant` for 27, all agreeing with the
  rule, and `rejected` for 2
  ([evidence/run_report_run2_seeded_rerun_with_claude_2026-10-29.json](evidence/run_report_run2_seeded_rerun_with_claude_2026-10-29.json)).
- **Commit:** fc69190.

**Sampling chats, 2026-10-29**
- **The chats:** 5 development postings × 4 fresh Incognito chats, giving 20 replies, all
  Opus 5.5 and baseline-v1, from 20:53 to 21:15
  ([experiments/sampling/metadata.json](experiments/sampling/metadata.json)).
- **Result:** 17 accepted, 3 rejected, all 3 for posting 7369543. 17 of 20 passed
  ([evidence/score_sampling_baseline_2026-10-30.txt](evidence/score_sampling_baseline_2026-10-30.txt)).
- **Report:** [experiments/sampling_report.md](experiments/sampling_report.md).
- **Commit:** a4ff13d.

**Prompt experiment, 2026-10-29 to 2026-10-30**
- **The chats:** 40 replies, each from a fresh Incognito chat with Opus 5.5
  ([experiments/prompt_experiment/baseline/metadata.json](experiments/prompt_experiment/baseline/metadata.json),
  [experiments/prompt_experiment/revision/metadata.json](experiments/prompt_experiment/revision/metadata.json)).
- **Scores:**
  - development: baseline-v1 9/10, revision-v1 10/10;
  - held-out: baseline-v1 10/10, revision-v1 10/10.

  The sources are [evidence/score_dev_baseline_2026-10-30.txt](evidence/score_dev_baseline_2026-10-30.txt),
  [evidence/score_dev_revision_2026-10-30.txt](evidence/score_dev_revision_2026-10-30.txt),
  [evidence/score_heldout_baseline_2026-10-30.txt](evidence/score_heldout_baseline_2026-10-30.txt)
  and [evidence/score_heldout_revision_2026-10-30.txt](evidence/score_heldout_revision_2026-10-30.txt).
- **Hand labels vs the rule:** 10/10 agree on development
  ([evidence/hand_vs_rule_development_2026-10-29.txt](evidence/hand_vs_rule_development_2026-10-29.txt))
  and 10/10 on held-out
  ([evidence/heldout_labels_vs_rule_2026-10-30.txt](evidence/heldout_labels_vs_rule_2026-10-30.txt)).
- **Report:** [experiments/prompt_experiment_report.md](experiments/prompt_experiment_report.md),
  which has the order of events and the commit for each step.

**Action-surface demos, 2026-10-29 to 2026-10-30.** The same posting, 8154295, three ways
([experiments/action_surface/action_surface.md](experiments/action_surface/action_surface.md)):
- **Way 1, paste into a chat:** the run-2 reply
  [claude_outputs/8154295.txt](claude_outputs/8154295.txt), collected 2026-10-29 at 15:00
  from a fresh Incognito chat with Opus 5.5.
- **Way 2, give Claude a file:**
  [experiments/action_surface/way2_input_8154295.txt](experiments/action_surface/way2_input_8154295.txt)
  and [experiments/action_surface/way2_reply_8154295.txt](experiments/action_surface/way2_reply_8154295.txt).
- **Way 3, an agent fetching and writing its own state:** Claude Code, on 2026-10-30 at
  23:00 local (2026-10-31T03:00:43Z).
  - It made one live fetch and saved 746 ids.
  - The raw response was not committed; its SHA-256 is in the log.
  - See [experiments/action_surface/way3_agent/actions_log.md](experiments/action_surface/way3_agent/actions_log.md)
    and [experiments/action_surface/way3_agent/state.json](experiments/action_surface/way3_agent/state.json).
- **Commit:** 8164231.

**Constructed examples, not real data.**
- **The expected-outcome tables in [tests/expected/](tests/expected/):** 14 rule cases,
  7 watch cases, 15 refusal cases (8 URL and 7 résumé) and 13 validator cases. I wrote them
  by hand on 2026-10-26, before any code (commit 5969e44). Each file's `note` says it is
  constructed.
- **The made-up postings, replies and boards inside the test files:** constructed, not real
  Stripe postings or Claude replies.

## Where everything is

| Path | What it holds |
|---|---|
| [CONTRACT.md](CONTRACT.md) | the contract, written before any code: in, out, refuses, the §4 rule, wrong versions, §6 Claude judge and validator, failure sentence, amendments |
| [resume_persona.json](resume_persona.json) | the fictional persona (Alex Rivera) |
| [config.json](config.json) | the live config: board, allow-list, paths |
| [agent/](agent/) | the agent: config, fetch, state, rule, replies validator, run report, CLI |
| [tests/](tests/) | unittest suites; [tests/expected/](tests/expected/) holds the constructed expected-outcome tables; [tests/wrong_versions/](tests/wrong_versions/) holds the two deliberately wrong implementations (W1, W2) |
| [tools/](tools/) | the helper tools listed under "The tools" |
| [evidence/](evidence/) | saved raw board responses and sidecars, run reports, state after each run, terminal output, score and comparison outputs, the prompt diff |
| [state.json](state.json), [run_report.json](run_report.json) | the state and report written by the last live run (run 2) |
| [claude_outputs/](claude_outputs/) | the 29 run-2 Claude replies and their metadata |
| [prompts/](prompts/) | [baseline-v1](prompts/claude_prompt_baseline.txt) and [revision-v1](prompts/claude_prompt_revision.txt) |
| [experiments/](experiments/) | [labeling protocol](experiments/labeling_protocol.md), [selected ids](experiments/selected_ids.json), [chat plan](experiments/chat_plan.md), [scoring rule](experiments/scoring.md), [revision decision](experiments/revision_decision.md), hand labels ([development](experiments/hand_labels_development.json), [held-out](experiments/hand_labels_heldout.json)) |
| [experiments/sampling/](experiments/sampling/) | the 20 sampling replies and their metadata |
| [experiments/prompt_experiment/](experiments/prompt_experiment/) | baseline and revision replies, development and held-out, and their metadata |
| [experiments/sampling_report.md](experiments/sampling_report.md) | the sampling report |
| [experiments/prompt_experiment_report.md](experiments/prompt_experiment_report.md) | the prompt experiment report |
| [experiments/action_surface/action_surface.md](experiments/action_surface/action_surface.md) | the action-surface comparison and the autonomy choice |
| [replay/](replay/) | [config_replay.json](replay/config_replay.json) for the offline replay; the replay's state and reports are gitignored |

## Known limits

These are copied from [CONTRACT.md](CONTRACT.md) and the two reports.

**From [CONTRACT.md](CONTRACT.md)**
- **One board only:** the agent reads one board, Stripe on Greenhouse, from one URL. It does
  not discover other boards or follow links (§1).
- **Known consequences of plain substring matching (§4):**
  - `SQL` matches inside `NoSQL`, a false positive.
  - `Senior`, `Staff` and `Lead Product Manager` all pass C1, so the rule has no seniority
    filter, even though the persona's `max_years_required` is 3.
  - `roadmap` does not match `roadmapping`, and `APM` does not match `Product Manager`
    (false negatives).
- **`max_years_required`:** it is recorded in the résumé but is not part of the v1 rule (§4).
- **Rejected replies:** Claude.ai often wraps answers in Markdown or adds a sentence. Those
  replies are rejected, never repaired (§6).

**From [experiments/sampling_report.md](experiments/sampling_report.md)**
- **Few repeats, all negative:** 4 repeats per posting, and all 5 hand labels are
  `not_relevant`. So it says nothing about how stable a `relevant` verdict would be.

**From [experiments/prompt_experiment_report.md](experiments/prompt_experiment_report.md)**
- **Cell size:** 10 cases per cell, so one reply moves a pass rate by 10 points.
- **Hand labels:** all 20 are `not_relevant`, and C3 is true in none of them.
- **Held-out:** the held-out baseline also scored 10/10 with no rejections, so on the held-out
  set the two prompts cannot be separated.
- **The odds:** at the baseline whole-list rejection rate of 6/69, the probability of 0 failures
  in the revision's 20 replies is (21/23)^20 ≈ 0.162. That assumes independent failures.

## Driver's seat

| What Claude did | What I did | Why that part stays mine | Evidence (commit or file) |
|---|---|---|---|
| Reviewed the contract; listed the 16 issues | Made each decision: board, persona, rule, quirks | The rule decides what counts as relevant for the persona | contract changelog; b27b1a8 → 5cd4c28 |
| Typed the corrected rule table | Wrote all the cases and answers; checked the 4 corrections myself | Expected answers must come before the code | 5969e44, the note in rule_cases.json |
| Claude Code wrote the agent and tools | Ran every test myself; the test-can-fail check; the offline replay | "Run your tests yourself" | cf8708c, evidence/test_can_fail_2026-10-27.txt |
| Explained the labeling method; did not check answers — though one method reminder led me to re-check and change my first label's C1 | All 20 hand labels | They're the ground truth everything is compared against | 6126445 (development), 0e3a2f5 (held-out), the two hand-vs-rule files in evidence/ |
| Found the pattern (whole-list rejections on failed conditions) and listed options A, B, C | Chose C, with a reason and a prediction written before any revision chat | The experiment's one change is my judgment | 323d2b6, experiments/revision_decision.md |
| Claude Code built "reuse" against my plan; Claude.ai spotted the mismatch | Decided to stick to my committed plan and had it reverted | My plan is the spec, not Claude's guess | 1bf0301 ("no reuse, per chat_plan.md") |


## Sign-off — Job-Search Agent 1

**Checked:**
- The rule (C1–C3) on 14 constructed cases, including all the pinned quirks — tests/expected/rule_cases.json, written before any code.
- "New since last run" by id, including the number-vs-text trap — watch_cases.json, S01–S07.
- The allow-list and the persona refusals — refusal_cases.json, including the two URL tricks.
- The validator — validator_cases.json, including V12, where a wrong verdict still passes validation.
- Both wrong versions, W1 and W2, are caught — tests/test_wrong_versions.py.
- That the tests can fail — evidence/test_can_fail_2026-10-27.txt.
- The rule agrees with my hand labels on 20 of 20 real postings, on every condition — the two evidence/*labels_vs_rule* files.
- Run 2's 29 new ids, recounted by my own script — evidence/run2_recount_by_me_2026-10-28.txt.
- Both runs replay offline, with byte-identical state files — README replay commands, run by me on 2026-10-30.
- Runs from a clean copy of the committed folder (git archive of HEAD on 2026-10-31): 45/45 tests pass, and the offline replay of run 1 gives byte-identical state.

**How:**
- By hand: the labels.
- By a test written before reading Claude's code: the four tables.
- By recomputation: the recount, the fingerprints, the replay, and the labels-vs-rule comparison.
- With Claude's help: Claude Code wrote the code, the W1/W2 versions, and the scoring tools; Claude.ai reviewed the contract and suggested wording.

**Not checked:**
- No real posting was ever relevant — C3 was true for none of them, so the rule's "all three pass" path is tested only on constructed cases.
- Whether a leftover &nbsp; in the cleaned text can hide a skill — never tested.
- Real network failures: timeouts, 404s, and real redirects were never triggered. Only the refusal logic is unit-tested.
- Python 3.11 and 3.12: the tests ran only on 3.13, and the files were only compiled under 3.11.
- Claude's REASON text: never checked. The validator checks the format and the citations only, as V12 shows.
- Any other model, or a normal (non-Incognito) chat.
- I did not read every line of the agent code myself.

**Not claiming:**
- That any posting is worth applying to.
- That Claude's judgment is right in general.
- That the revision caused the improvement — the results are consistent with it, and 0 failures in 20 replies had about a 16% chance of happening anyway.
- That this works for other boards or personas.
- That "new" means "newly created" — 7337544 and others had older ids but were new to the agent; why they were missing from run 1 was not checked.

**Signed:** Prasad Shinde, 2026-10-31

```
