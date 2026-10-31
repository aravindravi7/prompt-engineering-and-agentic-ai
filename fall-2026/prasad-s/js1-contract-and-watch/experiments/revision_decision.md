# Revision decision (JS1 prompt experiment) — 2026-10-30

Written after the development baseline was scored and before any
revision chat. The held-out set has not been opened.

## What the baseline showed

- Development baseline (baseline-v1, 10 postings): 9/10 PASS (90%).
  The one FAIL, 7586413, was rejected by the validator: Claude cited
  `locations=New York | NYC | Remote` and
  `skills=Python | SQL | A/B testing | roadmapping | user research`
  as single values. (evidence/score_dev_baseline_2026-10-30.txt)
- Sampling (baseline-v1, 5 postings x 4): 17/20 accepted. Posting
  7369543 was rejected in 3 of its 4 repeats, for the same reason.
  (evidence/score_sampling_baseline_2026-10-30.txt)
- Run 2 (baseline-v1, 29 postings): 27 agree, 2 rejected (8332676,
  8130876), same reason.

Across all 59 baseline-v1 replies, 6 were rejected, and all 6 for the
same cause: a whole candidate list written as one RESUME_FIELD value.

## The pattern

It happens on postings where a condition FAILS. The baseline prompt
says: "When a condition fails, cite the candidate value you checked."
For a failed condition every value was checked, so Claude copies the
whole list, joined with " | " as the CANDIDATE block shows it.

## Options considered (one change only)

- A. Show each candidate value on its own line instead of joined with " | ".
- B. Add a rule: one value per RESUME_FIELD line; never copy a list or use "|".
- C. Rewrite the failing-condition instruction: write one RESUME_FIELD
  line for each candidate value checked.

## Decision

C. It addresses the root cause: the instruction sentence that tells
Claude what to cite when a condition fails. The full change is in
evidence/prompt_diff_baseline_vs_revision.txt: only the version line
and that sentence differ.

## Prediction (written before any revision chat)

- Development set: 10/10 PASS (100%). The one baseline FAIL, 7586413, was rejected for the list-as-one-value reason only, and C changes exactly that instruction; the other 9 already pass.
- Held-out set: 9/10 PASS or better, and no reply rejected for the list-as-one-value reason. Any FAIL there is a verdict mismatch or a different rejection, not this one.
- What would tell me the change did NOT work: a revision reply in either set rejected because Claude cited a whole candidate list as one RESUME_FIELD value, joined with " | " — or the development score staying at 9/10, with 7586413 failing the same way.

## Limits

With 10 cases per set, one reply moves the pass rate by 10 points. The
development baseline had only one failure, so the development set can
show at most a 1-reply improvement; the held-out set matters more. All
10 development labels are not_relevant.

Drafted with help from Claude.ai on 2026-10-30, from my scored results;
the choice of C, its reason and the prediction are mine.