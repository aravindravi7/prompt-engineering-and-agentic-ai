# Prompt experiment (Chapter 2)

**Ran:** 2026-10-30, 21:23–21:27 UTC.

**Setup:**
- Each call was a fresh `claude -p` conversation, no tools, model `claude-opus-5-5`.
- **Code:** `experiments/prompt_experiment.py`.
- **Raw replies:** `evidence/claude/experiment/<prompt>-<split>/`.
- **Scores:** `experiments/results/`.

## Order of work

**How the order is proved:**
- Steps 1–3 were each committed before the next step started.
- Steps 4–6 landed together in one commit, `ab2a6b9`. Their order is shown by each reply's `asked_at` time (UTC) in `experiments/results/`:

| Run | Time (UTC, 2026-10-30) |
|---|---|
| baseline on dev | 21:23:11–21:23:25 |
| revision on dev | 21:26:04–21:26:23 |
| baseline on held-out | 21:26:39–21:26:52 |
| revision on held-out | 21:26:58–21:27:09 |

**The steps:**

1. **Labeling rule** (`labels/LABELING-RULE.md`), written first: "Fit = a recent MS grad with an AI co-op could realistically get this job, and it would use her AI/data skills."
2. **20 real postings** chosen reproducibly (`experiments/select_labeling_set.py`, seed 7375).
   - Picked from run 2's Databricks response, excluding run 2's own new postings.
   - Strata: 8 rule-relevant, 8 that miss one check, 4 others.
   - Split 10 development / 10 held-out.
3. **Lavanya hand-labeled all 20** (`labels/hand_labels.json`, commit `8f752da`) before Claude saw any of them. **All 20 were "not fit".**
4. **Baseline prompt** (`prompts/baseline.md`) on development only.
5. **One change**, chosen by Lavanya after seeing the development results.
6. **Both prompts on held-out**, run last.

## The one change

`prompts/revision.md` is `prompts/baseline.md` plus one added line (`diff prompts/baseline.md prompts/revision.md`):

> 6. The posting must not require more experience than the job seeker has, or a graduation date she does not meet.

**Why this change:**
- On development, 3 baseline failures were "relevant" verdicts that followed the rule but disagreed with the hand label on experience level.
- Lavanya chose this over the other candidate, a format fix for the 3 INVALID replies.

## Results

A pass means the validator accepted the reply **and** its verdict matched the hand label. INVALID counts as a fail.

| Prompt | Development (10) | Held-out (10) |
|---|---|---|
| baseline | 4/10 (3 INVALID, 3 wrong) | 4/10 (3 INVALID, 3 wrong) |
| revision | 9/10 (1 INVALID) | **10/10** |
| *for comparison:* rule v2 (record) | 6/10 | 6/10 |

- **The baseline's INVALIDs:** all 6 had `"resume_fields": []` on title-based rejections.
  - The verdict inside every one was `not_relevant`, which matched the hand label.
  - Under a validator that allowed empty `resume_fields`, the baseline would have scored 7/10 on each split. The gap to the revision would then be 7 → 9 and 7 → 10, not 4 → 9 and 4 → 10.
- **The revision's single INVALID** (#12, dev): Claude cited `education.0.end_date`. My validator accepts `education[0].end_date` but not the `.0` form, so it rejected the reply. The verdict inside, `not_relevant`, matched the hand label.
  - This is an inconsistency in my validator. I found it after seeing results and **did not change it**, so the score stays 9/10.
  - CONTRACT.md's list of rejections does not mention field names that don't exist; the validator added that check. Under the contract as written, this reply would have been valid, and the revision would have scored 10/10 on dev.
- **The rule and Claude are held to different standards on citing résumé fields.**
  - The rule's justification always lists résumé fields, because check 4 always reports which skill fields it compared, even when the title alone decided.
  - Claude was marked INVALID for leaving `resume_fields` empty on exactly that kind of title-only rejection.
- **A side effect I did not target:** the revision also removed the empty-`resume_fields` replies (6 → 0). Once experience was a check, Claude cited `education` / `experience` fields.

## Honest limits

- **Every label is "not fit".**
  - A prompt that always answers `not_relevant` would also score 10/10.
  - This experiment cannot tell whether the revision wrongly rejects real fits, because there were none to reject.
  - The jump from 4 to 10 shows the revision stopped saying "relevant" to experienced-level jobs. It does **not** show it can still recognise a good one.
- **Ten cases are very few.**
  - One posting is 10 percentage points.
  - 10/10 on held-out is still consistent with a true pass rate as low as about 74% (95%, one-sided: 0.05^(1/10) ≈ 0.74).
- **The change moves Claude toward my labeling rule**, which is about experience level. Improvement against my labels was expected. It is not evidence that Claude judges jobs better in general.
- **One run per posting per prompt.** The sampling report suggests these verdicts are stable, but that was only 5 postings, each asked 4 times.
- **The development set overlaps the sampling postings** (#1, #3, #6, #10, #12). That is by design: the development set is the part I was allowed to look at.
- **The rule itself was not revised.** Rule v2 scored 12/20 against my labels. Adding an experience check to CONTRACT.md would be a new rule version, left for the next layer.
