# Prompt experiment report (JS1): baseline-v1 vs revision-v1

Draft by Claude Code on 2026-10-30, from saved files only. Each number is
followed by the file it comes from. All paths are relative to the JS1 folder.

- **Model:** Opus 5.5 for every reply in the experiment. This is recorded in all
  20 entries of [prompt_experiment/baseline/metadata.json](prompt_experiment/baseline/metadata.json)
  and all 20 of [prompt_experiment/revision/metadata.json](prompt_experiment/revision/metadata.json).
- **Conversation:** every chat was a fresh Incognito chat, one posting per
  chat ([chat_plan.md](chat_plan.md); `conversation` is `fresh Incognito chat`
  in all 40 entries).
- **Dates:**
  - development baseline: 2026-10-29;
  - development revision: 2026-10-30;
  - held-out baseline and held-out revision: 2026-10-30.

  The times are in the order of events below, taken from `collected` in the same two metadata files.

## Setup

- **Labeling rule:** I labeled by applying CONTRACT.md §4 by hand, and nothing else.
  Each label records C1, C2, C3, the verdict and a one-line reason. I looked at
  title, location and content in a viewer that shows no verdicts. All 10
  development labels were written before the held-out postings were opened.
  The held-out postings were opened only after the revised prompt was frozen
  ([labeling_protocol.md](labeling_protocol.md)).
- **How the 20 postings were chosen:** from
  `evidence/stripe_jobs_content_true_2026-10-27T223947Z.json`, I took every posting
  whose title contains "product" (case-insensitive) and sorted them by id, ascending.
  115 matched. The first 10 are the development set and the next 10 are the held-out set
  ([selected_ids.json](selected_ids.json): `matching_count` 115, `development` 10 ids,
  `held_out` 10 ids).
- **Scoring rule:** a reply passes only if the §6 validator accepts it and its verdict
  equals my hand label. A rejected reply is a FAIL, and pass rate = passes / 10
  for each cell ([scoring.md](scoring.md)). The scores were produced by `tools/score_replies.py`.
- **The one change:**
  - **The change:** option C in [revision_decision.md](revision_decision.md), a rewrite of the
    failing-condition instruction. The full diff is
    [evidence/prompt_diff_baseline_vs_revision.txt](../evidence/prompt_diff_baseline_vs_revision.txt).
    Only the version line and that instruction differ.
  - **Baseline-v1 instruction:** "When a condition fails, cite the candidate value you checked in
    RESUME_FIELD and the posting's actual text for that field in POSTING_FIELD …".
  - **Revision-v1 instruction:** "When a condition fails, write one RESUME_FIELD line for each
    candidate value you checked — one value per line, never a whole list — and cite the
    posting's actual text for that field in POSTING_FIELD …".

## Order of events

Commit hashes and commit times are from `git log`. The chat times are from
`collected` in the metadata files named, in local time (UTC−04:00).

| # | Event | Commit | Commit time | Chat times |
|---|---|---|---|---|
| 1 | Labeling protocol and selected ids committed | a9a6db6 | 2026-10-28 20:23 | |
| 1a | Final labeling protocol wording committed, still before any labeling | fd5302d | 2026-10-28 20:51 | |
| 2 | Development hand labels committed | 6126445 | 2026-10-29 19:51 | |
| 3 | Scoring rule committed | 4e1d9fd | 2026-10-29 20:38 | |
| 4 | Sampling replies, baseline-v1, 20 replies | a4ff13d | 2026-10-29 21:17 | 2026-10-29 20:53–21:15 ([sampling/metadata.json](sampling/metadata.json)) |
| 5 | Development baseline replies, baseline-v1, 10 replies | 1b6d98e | 2026-10-29 21:55 | 2026-10-29 21:36–21:51 ([prompt_experiment/baseline/metadata.json](prompt_experiment/baseline/metadata.json), `split` development) |
| 6 | Revision frozen: revision-v1 prompt, decision note with prediction, development baseline scores | 323d2b6 | 2026-10-30 20:40 | |
| 7 | Development revision replies, revision-v1, 10 replies | 8c7d5c5 | 2026-10-30 21:07 | 2026-10-30 20:54–21:05 ([prompt_experiment/revision/metadata.json](prompt_experiment/revision/metadata.json), `split` development) |
| 8 | Held-out hand labels committed | 0e3a2f5 | 2026-10-30 22:07 | |
| 9 | Held-out replies, 10 baseline-v1 and 10 revision-v1, with their scores and the held-out labels-vs-rule file | 35d4342 | 2026-10-30 22:53 | baseline 2026-10-30 22:28–22:34, revision 22:39–22:47 (the two metadata files, `split` held_out) |

## Results

Each cell has 10 replies, one per posting.

| Set | Prompt | PASS | Pass rate | Rejected | Source |
|---|---|---|---|---|---|
| development | baseline-v1 | 9 | 9/10 = 90% | 1 (7586413) | [evidence/score_dev_baseline_2026-10-30.txt](../evidence/score_dev_baseline_2026-10-30.txt) |
| development | revision-v1 | 10 | 10/10 = 100% | 0 | [evidence/score_dev_revision_2026-10-30.txt](../evidence/score_dev_revision_2026-10-30.txt) |
| held-out | baseline-v1 | 10 | 10/10 = 100% | 0 | [evidence/score_heldout_baseline_2026-10-30.txt](../evidence/score_heldout_baseline_2026-10-30.txt) |
| held-out | revision-v1 | 10 | 10/10 = 100% | 0 | [evidence/score_heldout_revision_2026-10-30.txt](../evidence/score_heldout_revision_2026-10-30.txt) |

- **Accepted replies:** every accepted reply in the four files gave `not_relevant`, the same as the hand
  label, so every FAIL in the table is a rejection.
- **The one rejection** (development baseline, 7586413), quoted from
  [evidence/score_dev_baseline_2026-10-30.txt](../evidence/score_dev_baseline_2026-10-30.txt):

  ```
  - RESUME_FIELD locations='New York | NYC | Remote' is not a résumé locations value
  - RESUME_FIELD skills='Python | SQL | A/B testing | roadmapping | user research' is not a résumé skills value
  ```

## Hand labels vs rule

| Set | Labels | Agree | Disagree | Hand C1 true | Hand C2 true | Hand C3 true | Source |
|---|---|---|---|---|---|---|---|
| development | 10 | 10 | 0 | 4 | 6 | 0 | [evidence/hand_vs_rule_development_2026-10-29.txt](../evidence/hand_vs_rule_development_2026-10-29.txt), commit 8ccdd54 |
| held-out | 10 | 10 | 0 | 3 | 5 | 0 | [evidence/heldout_labels_vs_rule_2026-10-30.txt](../evidence/heldout_labels_vs_rule_2026-10-30.txt), commit 35d4342 |

In both files, C1, C2, C3 and the verdict each differ 0 times
(`C1 differs: 0  C2 differs: 0  C3 differs: 0  verdict differs: 0`).

## Prediction and result

The prediction is quoted from [revision_decision.md](revision_decision.md),
which was committed in 323d2b6 before any revision chat.

| Prediction (quoted) | Result | Source |
|---|---|---|
| "Development set: 10/10 PASS (100%)." | 10/10 = 100%. 7586413 accepted, PASS | [evidence/score_dev_revision_2026-10-30.txt](../evidence/score_dev_revision_2026-10-30.txt) |
| "Held-out set: 9/10 PASS or better, and no reply rejected for the list-as-one-value reason." | 10/10 = 100%, 0 rejected | [evidence/score_heldout_revision_2026-10-30.txt](../evidence/score_heldout_revision_2026-10-30.txt) |
| "What would tell me the change did NOT work: a revision reply in either set rejected because Claude cited a whole candidate list as one RESUME_FIELD value, joined with " \| " — or the development score staying at 9/10, with 7586413 failing the same way." | 0 of 20 revision-v1 replies rejected. Development score 10/10 | the two revision score files above |

## Limits

- **Cell size:** each cell has 10 cases, so one reply moves a cell's pass rate by 10 points
  (the four score files: `replies: 10`; [scoring.md](scoring.md)).
- **Hand labels:** all 20 are `not_relevant`. That is 10 of 10 in
  [hand_labels_development.json](hand_labels_development.json) and 10 of 10 in
  [hand_labels_heldout.json](hand_labels_heldout.json).
- **Whole-list rejections across every baseline-v1 reply:** 6 of 69. In each one a whole candidate
  list, joined with " | ", was written as one RESUME_FIELD value:

  | baseline-v1 replies | Total | Whole-list rejections | Source |
  |---|---|---|---|
  | Run 2 | 29 | 2 (8332676, 8130876) | [evidence/run_report_run2_seeded_rerun_with_claude_2026-10-29.json](../evidence/run_report_run2_seeded_rerun_with_claude_2026-10-29.json); [claude_outputs/metadata.json](../claude_outputs/metadata.json) for prompt and model |
  | Sampling | 20 | 3 (7369543 r1, r3, r4) | [evidence/score_sampling_baseline_2026-10-30.txt](../evidence/score_sampling_baseline_2026-10-30.txt) |
  | Development baseline | 10 | 1 (7586413) | [evidence/score_dev_baseline_2026-10-30.txt](../evidence/score_dev_baseline_2026-10-30.txt) |
  | Held-out baseline | 10 | 0 | [evidence/score_heldout_baseline_2026-10-30.txt](../evidence/score_heldout_baseline_2026-10-30.txt) |
  | **All baseline-v1** | **69** | **6** | the four rows above |

- **Revision-v1:** 0 whole-list rejections in 20 replies, 10 development and 10 held-out
  ([evidence/score_dev_revision_2026-10-30.txt](../evidence/score_dev_revision_2026-10-30.txt),
  [evidence/score_heldout_revision_2026-10-30.txt](../evidence/score_heldout_revision_2026-10-30.txt)).
- **Chance of 0 failures at the baseline rate:** suppose the revision's 20 replies each failed
  independently at the baseline's observed whole-list rejection rate. The chance of 0 failures is then:

  ```
  baseline rate          p = 6 / 69 = 2 / 23 ≈ 0.0870
  one reply passes       1 − p = 63 / 69 = 21 / 23 ≈ 0.9130
  20 replies, 0 failures (21 / 23)^20 ≈ 0.162
  ```

  That is about 16%.

## Conclusion

The results are consistent with the one change doing what it was aimed at. Development went from 9/10 with baseline-v1 to 10/10 with revision-v1: 7586413, the only baseline failure, was accepted under the revision and passed. Across all 20 revision replies, development and held-out, not one was rejected for the list-as-one-value reason, against 6 of 69 baseline replies rejected for exactly that. Both predictions, committed before any revision chat, were met — development 10/10, and held-out at 9/10 or better with no list-as-one-value rejection (it came in at 10/10) — and neither thing I wrote down as "the change did not work" happened. Two qualifications keep me from claiming more than that. First, the held-out baseline also scored 10/10 with no rejections, so on the held-out set the two prompts cannot be separated; the difference shows only on development, and there it is one reply. Second, at the baseline whole-list rejection rate of 6/69, getting 0 failures in 20 replies by chance alone has a probability of about 16% (assuming the replies fail independently), so the revision result is what the change predicts, not proof that the instruction caused it. The standing limit covers the whole experiment: all 20 hand labels are not_relevant, and C3 was true in none of them, so the prompts are compared only on negative cases — on how they cite failing conditions, which is where the baseline failed. Within that scope, the targeted failure did not appear in any of the 20 revision replies, and nothing else in the prompt changed: only the version line and one instruction differ.


____
