# Prompt experiment (2026-10-31)

## 1. Setup

- **Postings:** 20 real Databricks postings from `evidence/raw/2026-10-30T23-59-22Z.json`.
- **Split:** frozen in `LABEL_SET.md` before labeling (commit `f18cbae`). Entries 1, 3, 5 … are the development split (10 postings), and entries 2, 4, 6 … are the held-out split (10 postings).
- **Hand labels:** `labels/HAND_LABELS.md` (commit `f55b88d`), written before either judge ran on these postings.
- **Prompts:** `prompts/baseline.txt` and `prompts/revised.txt`, both committed in `a4021ff`. They are identical except that the revised prompt adds one line after the instructions:
  > Check every mandatory eligibility condition before giving the verdict.
- **Claude judge:** `js1.claude_judge`, which runs the `claude` CLI in print mode with model `claude-sonnet-4-6`.
  - Every tool is disabled, and no MCP servers or slash commands are loaded.
  - It runs from an empty temporary directory.
  - Each reply is checked by a strict JSON validator, with one retry on an invalid reply.
- **Runner:** `python3 -m experiments.run_experiment --split dev|heldout` (commit `388e788`). It also runs the rule judge on each posting.
- **Scoring:** a prompt passes on a posting when the result is valid and its verdict equals my hand label. An invalid result is a fail.

## 2. My words (verbatim)

BEGIN
**7. Baseline prompt.** The baseline prompt should ask Claude to review a posting against Priya's résumé and profile, return either relevant or not relevant, and explain its decision using actual fields from the input. It must follow the fixed JSON output format.

**8. One revision.** I'll make one change: add an explicit instruction telling Claude to check every mandatory eligibility condition before producing its verdict. Everything else, including the output schema and model settings, should remain unchanged.

**9. Expected improvement.** I expect the checklist to reduce mistakes where Claude notices matching skills but overlooks a disqualifying requirement, such as seniority, clearance, or denied sponsorship.

**10. Passing criteria.** A response passes only when it produces valid JSON matching the required schema and its verdict matches my independent hand label. Invalid responses count as failures.

**11. Keep or reject the revision.** I'll keep the revision if it improves the development-set pass rate and does not reduce performance on the held-out set. I'll report both results even if the revision performs worse, and I won't tune it again using held-out results.

**12. Limitations of 10 cases.** Ten cases are not enough to prove that a prompt will work reliably across different companies, job boards, or large numbers of postings. They can only show how it performed on this small dataset.
END

## 3. Development results

- **Run:** 2026-10-31T00-59-14Z (UTC), run by me in Terminal.
- **Evidence:** `evidence/experiment/dev/2026-10-31T00-59-14Z/`; results table in `experiments/results_dev.md`; commit `d7411f4`.
- **Earlier partial run:** `2026-10-31T00-55-10Z`, interrupted. It is kept, but not scored.

| posting_id | title | my hand label | rule verdict | baseline verdict | revised verdict | baseline | revised |
|---|---|---|---|---|---|---|---|
| 7737233002 | Software Engineer - Backend | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8029666002 | Software Engineer - Backend | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8401114002 | Staff Machine Learning Engineer | not relevant | not relevant | not relevant | invalid | pass | fail |
| 8546367002 | AI Engineer – Forward Deployed Engineering (AI FDE) | not relevant | relevant | not relevant | not relevant | pass | pass |
| 8569392002 | Senior AI Engineer - FDE (Forward Deployed Engineer) | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8648494002 | Forward Deployed Engineer | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8692962002 | Specialist Solutions Architect - Data Engineering & Warehousing (Financial Services) | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8824168002 | Technical Enablement Specialist  - Field Engineering Onboarding | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8847738002 | Software Engineering Intern (2027 Start) - London | not relevant | not relevant | not relevant | not relevant | pass | pass |
| 8921476002 | Forward Deployed Engineer | not relevant | not relevant | not relevant | not relevant | pass | pass |

- **Baseline:** 10/10
- **Revised:** 9/10
- **Rule:** 9/10
- **Calls and invalid results:** 23 Claude calls made: 20 first attempts and 3 retries. 1 result was invalid (revised, 8401114002).

### Every validator rejection in the dev run

There were 4 rejections, all for the same reason: `resume_field 'resume_experience_tools' is not a field given in the input`. Each reply cited "Databricks Genie API" with `resume_field: "resume_experience_tools"`. That is a key in the judge's own input; the validator accepts only the field names listed under it (`experience[0].bullets[0]`). Re-checked with that one key allowed, all 4 replies pass every other validation rule.

| prompt | posting | attempt | verdict in the rejected reply | final result |
|---|---|---|---|---|
| baseline | 8401114002 | 1 | not relevant | valid on retry: not relevant |
| revised | 8401114002 | 1 | relevant | invalid after retry |
| revised | 8401114002 | 2 | relevant | (same result) |
| revised | 8921476002 | 1 | not relevant | valid on retry: not relevant |

**8401114002 under the revised prompt.** On "Staff Machine Learning Engineer", both revised replies said "relevant", and both were rejected only for citing `resume_experience_tools`. The scored result is "invalid". The revision's real verdict on that posting was "relevant", which is wrong against my hand label ("not relevant"); the title fails the seniority check. Fixing the validator would not have turned this fail into a pass.

**Rule judge miss.** The rule judge passed 8546367002 as "relevant" even though its description says the role "is not intended for internship, new graduate, or entry-level applicants". The baseline and revised prompts both said "not relevant".

**Decision.** Commit `d7411f4` records it: "Revision dropped per my rule". Under Q11 the revision is kept only if it improves the development pass rate. It scored 9/10 against the baseline's 10/10.

## 4. Held-out results

- **First held-out run:** 2026-10-31T01-26-20Z (UTC), run by me in Terminal, commit `4a46925`. Evidence is in `evidence/experiment/heldout/2026-10-31T01-26-20Z/`, with the results table in `experiments/results_heldout.md`.
- **Claude calls failed:** 38 of the 39 calls made failed with exit code 1 and "You've hit your limit · resets 8pm (America/New_York)". The only valid result was the baseline on 7958982002. The Claude scores for this run (baseline 1/10, revised 0/10) reflect the usage limit, not the prompts.
- **Rule judge:** 9/10. It passed 8760167002 ("AI Engineer – Forward Deployed Engineering (AI FDE), U.S. Public Sector (Federal Focus)") as "relevant" despite that posting's Secret-clearance-eligibility requirement.
- **Rerun:** the Claude held-out run is to be rerun after the limit resets, with the same prompts and the same validator (commit `4a46925`: "to be rerun after reset with the same prompts"). I will update this section after the rerun.

## 5. Limits

- **No relevant postings:** all 20 hand labels are "not relevant". Neither split can show whether a prompt finds relevant postings; it can only show whether it avoids wrong "relevant" verdicts.
- **Validator bug left in place:** both splits use the same validator. Its `resume_experience_tools` bug was deliberately not fixed between splits, so the held-out run is judged by the same rules as the dev run. In the first held-out run it rejected no replies, because only 1 call returned a reply.
- **Small sample:** 10 postings per split, one run each. The separate sampling check (`experiments/SAMPLING_REPORT.md`) found the same verdict in every valid repeat of the baseline prompt, but different skills cited from run to run.
