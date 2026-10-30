# FRICTIONAL — Job-Search Agent 1

Dated log of what I tried, what broke, and what I did instead.

## 2026-10-29: Claude access without paying for API credits
- The Claude judge needs a program that asks Claude questions on its own. Claude first suggested an Anthropic API key. I didn't want to pay for credits, so I **rejected** that and asked for a free route.
- **What I did instead:** the program calls the Claude Code command-line tool (`claude -p`) through my NEU login.
  - Installed it with `npm install -g @anthropic-ai/claude-code`, version 2.1.312.
  - The first test call failed with `Failed to authenticate: OAuth session expired and could not be refreshed`.
  - I logged in again with `claude auth login`, and the test call then returned `OK` (model `claude-opus-5-5`).

## 2026-10-29: Writing the contract
- I made every rule decision in CONTRACT.md by picking from multiple-choice questions. Claude typed the answers up.
- I chose the failure sentence from four options Claude offered.
- Committed CONTRACT.md as `891aec3` (2026-10-29 17:26 −0400), before any agent code existed.
- My "whole words only" choice has a side effect I didn't expect. "Software Engineering Intern" does **not** match "Software Engineer", because "Engineering" is a different word. It only passes because of "Intern". I kept the rule as is.

## 2026-10-29: "sponsor" doesn't mean visa sponsorship
- My rule says a job that can't sponsor visas is not relevant for Priya.
- Before writing the phrase list, Claude pulled the real Datadog board. Nine postings mentioned "sponsor", and **none** were about visas: they were "sponsored events", "executive sponsor" and "Sponsorship Sales".
- A rule that just searched for "sponsor" would have wrongly ruled those jobs out. I **accepted** Claude's list of visa-only phrases instead.
- Databricks was the same: "C-suite-sponsored", "executive sponsors".
- **Unresolved:** neither board had any real "we can't sponsor" sentence, so check 5 has only been tested on constructed postings.

## 2026-10-29: The persona résumé had no sponsorship field
- Priya Nair's `resume.example.json` (copied from the Reallocation Engine's `search/examples/`) does not say she needs sponsorship. That fact is in the persona's separate `profile.yml`.
- I **modified** our copy: added `work_authorization.needs_sponsorship: true`, with a `_source` note. The agent still takes one résumé JSON, as the contract says.
- The Reallocation Engine repo itself was only read, never edited.

## 2026-10-29: Run 1 on Datadog was a dead end
- Run 1 on Datadog worked: 397 postings saved, 0 new, which is correct for a baseline.
- Claude then applied my rule to the whole board: **0 of 397 were relevant**.
  - 367 failed the title check.
  - 24 had a bad title word, mostly Senior or Staff.
  - 5 were outside the US.
  - 1 failed the skills check.
- With every verdict "not relevant", the sampling and prompt experiments could not show anything.
- Claude checked my rule against 10 Greenhouse boards. Under rule v1 on 2026-10-29, Databricks had 7 relevant and 74 that missed by one check. (These are v1 numbers. Rule v2 on run 2 gives 17 and 230.) I chose **Databricks** and did run 1 again there (906 postings, 0 new).
- I kept the Datadog run as evidence: `evidence/raw/datadog-…`, `state/datadog-seen_ids.json`, `reports/run-datadog-…`.
- The rule was not changed. CONTRACT.md has a dated note about the board change.
- **Known effect:** every Databricks posting mentions "Databricks", which is one of Priya's skills. On this board the 2-skill check is easier to pass than I intended.
- A Datadog snapshot Claude saved with `curl` at 17:13 had 396 postings. Run 1 at 17:29 had 397, so the board changed within 16 minutes. That snapshot was a scratch file and is not in this folder.

## 2026-10-29: I ran the tests myself
- I read this log and it matches what happened.
- I ran the tests myself with `python3 -m unittest discover -s tests -t . -v`. All 34 passed (`OK`).

## 2026-10-30: Run 2, and the location check was wrong for Databricks
- Run 2 (live, the second calendar day) found **10 new postings** out of 903. All 10 were `not_relevant` under rule v1. Committed as `47662ea` before changing anything.
- In the run 2 table, "Seattle, Washington" failed the US-location check. My v1 rule only looked for "USA" or "United States", the way Datadog writes locations. Databricks writes "San Francisco, California".
  - Only **111 of 903** postings passed the v1 location check.
  - Mostly-US places like San Francisco (66), Mountain View (46), Seattle (21) and New York City (18) all failed it.
- I chose to fix the rule (**v2**): a US state name or "D.C." now also counts. This went into CONTRACT.md as a dated change, before any hand labeling or Claude runs, so the fix could not be tuned to agree with Claude.
- Under v2, 495 of 903 postings pass the location check, and **17 are relevant**.
- The run 1 and run 2 reports stay as v1 produced them.

## 2026-10-30: The Claude judge's first real answers were mostly rejected
- Built the Claude judge: a fresh `claude -p` call per posting, with no tools, no saved session, an empty working folder, and the model pinned to `claude-opus-5-5`.
  - Its prompt contract is `prompts/baseline.md`.
  - A validator rejects anything that is not exactly the contract's JSON object.
  - The résumé is sent without the `personal` block, so Claude never sees a name, email or phone.
- Ran both judges on run 2's 10 new postings (`reports/judged-run-databricks-2026-10-30T204649Z.md`).
  - Rule v2: all 10 `not_relevant`.
  - Claude: 2 valid answers, both `not_relevant`, so both agree with the rule. **8 were rejected as INVALID.**
- All 8 rejections had the same cause: Claude returned `"resume_fields": []`.
  - Example (8860646002, 21:15:48 UTC): Claude said the title "contains none of the required keywords... and it contains the excluded word 'Manager'". No résumé field was needed for that.
  - My contract requires every justification to name résumé **and** posting fields, so the validator rejected those answers exactly as written.
- I kept the validator strict. **Unresolved:** is the contract too strict for title-only rejections, or is the prompt not saying clearly enough that a résumé field is always required? The prompt experiment is where I'll test that.

## 2026-10-30: Hand labels, sampling, and the prompt experiment
- I wrote my labeling rule first ("a recent MS grad with an AI co-op could realistically get this job, and it would use her AI/data skills"). I chose it over "apply my contract by hand". Committed as `323ee74`.
- I labeled all 20 jobs on multiple-choice cards. **All 20 were "not fit".** Most asked for 4–15 years. #11 says it is "not intended for internship, new graduate, or entry-level applicants". #12 "New Grad" requires graduating in fall 2026 or spring 2027, and Priya finished in Dec 2025.
- My own rule agreed with my labels on only **12/20**. All 8 rule-"relevant" jobs I called not fit. The rule never checks experience level. I did **not** change the rule after seeing my labels.
- **Sampling (20 calls):**
  - Claude gave the same outcome 4/4 times on every posting, but matched my label 0/20 times.
  - Repeating the same answer did not make it right.
- **Prompt experiment:**
  - Baseline: 4/10 dev and 4/10 held-out.
  - I chose the revision: one added line for experience and graduation date. It scored 9/10 dev and 10/10 held-out.
- **Caveat I have to own:** with every label "not fit", a prompt that always says no would also score 10/10.
- **Validator inconsistency found after seeing results, left unchanged:** it accepts `education[0].end_date` but rejects `education.0.end_date`, which cost the revision one dev point.
- I got lost partway through. I asked Claude to explain in simple terms before picking the prompt change.

## 2026-10-30: A fresh review, and testing my own failure sentence
- Before submitting, Claude ran an independent read-only review of this folder against the assignment, in a separate Claude agent that had not seen our session.
- It found I had **never tested my own failure sentence**. My labels used `labels/LABELING-RULE.md`, not CONTRACT.md.
- So I applied CONTRACT.md's 5 checks by hand to run 2's 10 new postings (`labels/contract_hand_check.json`).
  - I said `not_relevant` for all 10. That matched rule v1 and rule v2 on all 10, so the failure did not happen on these postings.
  - **Unresolved:** all 10 failed on title or location, so my hand check never exercised the skills or sponsorship checks.
- The review also found loosely worded claims, which I fixed:
  - "each step committed before the next" in PROMPT-EXPERIMENT.md was not true for steps 4–6;
  - ACTION-SURFACE.md had no date;
  - it missed that the agent surface also used `claude-haiku-5-5`;
  - the "can read" claim for surface 2 was untested;
  - the validator is stricter than CONTRACT.md says.
- The action-surface "paste into a chat" step had only been run as a `claude -p` stand-in. So I pasted the same prompt into a new claude.ai chat myself (`evidence/action-surface/1b-chat-claude-ai.json`).
  - The verdict was right: `not_relevant`, citing the 2026–27 graduation window.
  - But the reply I copied back had curly quotes and failed the validator as "not a single JSON object". I don't know whether the chat or my copy/paste changed the quotes.
