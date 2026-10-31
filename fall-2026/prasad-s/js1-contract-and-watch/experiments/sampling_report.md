# Sampling report (JS1): the same prompt, four fresh chats per posting

Draft by Claude Code on 2026-10-30, from saved files only. Each number is
followed by the file it comes from. All paths are relative to the JS1 folder.

## What was done

- **Postings:** the first 5 postings of the development set. They are
  6348471, 7202630, 7369543, 7392697 and 7456716
  ([labeling_protocol.md](labeling_protocol.md), "Sampling report postings";
  [selected_ids.json](selected_ids.json), `development`).
- **Chats:** each posting went to Claude in 4 separate chats, so 5 × 4 =
  20 replies ([sampling/metadata.json](sampling/metadata.json): 20 entries,
  keys `<id>_r1` to `<id>_r4`).
- **Prompt:** `prompts/claude_prompt_baseline.txt`, version baseline-v1, for all 20
  ([chat_plan.md](chat_plan.md); [sampling/metadata.json](sampling/metadata.json):
  `prompt_version` is `baseline-v1` in all 20 entries).
- **Model:** Opus 5.5, as recorded in all 20 entries of
  [sampling/metadata.json](sampling/metadata.json).
- **Conversation:** every chat was a fresh Incognito chat, with one posting per chat
  ([chat_plan.md](chat_plan.md); [sampling/metadata.json](sampling/metadata.json):
  `conversation` is `fresh Incognito chat` in all 20 entries).
- **When:** 2026-10-29, from 20:53:31 to 21:15:05 local time (UTC−04:00), which is
  2026-10-30 00:53:31Z to 01:15:05Z ([sampling/metadata.json](sampling/metadata.json),
  the earliest and latest `collected`).
- **How the replies were checked:** each saved reply was run through the agent's §6 validator and compared with
  my hand label by `tools/score_replies.py`. The output was saved as
  [evidence/score_sampling_baseline_2026-10-30.txt](../evidence/score_sampling_baseline_2026-10-30.txt).
- **Commit:** the 20 replies were committed in a4ff13d (2026-10-29 21:17, `git log`).

## Results per posting

The source for the hand label is
[hand_labels_development.json](hand_labels_development.json). The title
comes from the board file named in [selected_ids.json](selected_ids.json)
(`evidence/stripe_jobs_content_true_2026-10-27T223947Z.json`), with the
ends trimmed. Every other column comes from
[evidence/score_sampling_baseline_2026-10-30.txt](../evidence/score_sampling_baseline_2026-10-30.txt).

| posting_id | title | hand label | verdicts r1, r2, r3, r4 | accepted | RESUME_FIELD lines identical | POSTING_FIELD lines identical |
|---|---|---|---|---|---|---|
| 6348471 | Product Marketing Manager | not_relevant | not_relevant, not_relevant, not_relevant, not_relevant | 4/4 | no | no |
| 7202630 | Staff Product Designer, Link | not_relevant | not_relevant, not_relevant, not_relevant, not_relevant | 4/4 | no | no |
| 7369543 | Backend/API Engineer, Money as a Service (Product) | not_relevant | rejected, not_relevant, rejected, rejected | 1/4 | no | yes |
| 7392697 | Product Manager, Link - Consumer | not_relevant | not_relevant, not_relevant, not_relevant, not_relevant | 4/4 | yes | no |
| 7456716 | Account Executive, Product Sales - Stablecoin Issuing | not_relevant | not_relevant, not_relevant, not_relevant, not_relevant | 4/4 | no | no |

- **Totals:** `replies: 20  accepted: 17  rejected: 3  PASS: 17  pass rate: 17/20 = 85%`
  ([evidence/score_sampling_baseline_2026-10-30.txt](../evidence/score_sampling_baseline_2026-10-30.txt)).
- **"Identical"** means the same lines in the same order across all 4 repeats, taken
  from the raw reply text (`tools/score_replies.py`).

## Rejection reasons

All 3 rejected replies are for posting 7369543: r1, r3 and r4. Each was
rejected for the same three reasons, quoted here from
[evidence/score_sampling_baseline_2026-10-30.txt](../evidence/score_sampling_baseline_2026-10-30.txt):

```
- RESUME_FIELD target_titles='Associate Product Manager | Product Manager | Product Analyst' is not a résumé target_titles value
- RESUME_FIELD locations='New York | NYC | Remote' is not a résumé locations value
- RESUME_FIELD skills='Python | SQL | A/B testing | roadmapping | user research' is not a résumé skills value
```

## How much they varied

All from
[evidence/score_sampling_baseline_2026-10-30.txt](../evidence/score_sampling_baseline_2026-10-30.txt).

- **Verdicts:** all 17 accepted replies gave `not_relevant`, the same as the hand label for each posting.
  No accepted reply gave `relevant`.
- **Acceptance:** 4 of the 5 postings had 4/4 replies accepted. 7369543 had 1/4 accepted.
- **RESUME_FIELD lines:** identical across the 4 repeats for 1 of the 5 postings (7392697).
- **POSTING_FIELD lines:** identical across the 4 repeats for 1 of the 5 postings (7369543).
- **Both kinds of lines:** no posting had both its RESUME_FIELD lines and its POSTING_FIELD lines
  identical across all 4 repeats.

## Conclusion

Same prompt, same posting, four fresh chats: the verdict is the stable part, the citations are not. All 17 accepted replies said not_relevant, matching my hand labels, and no accepted reply said relevant. But the RESUME_FIELD lines were identical across all four repeats for only 1 of the 5 postings, and the POSTING_FIELD lines for only 1 of the 5; no posting had both identical. The repeats even disagreed about acceptance itself on one posting — 7369543 was rejected in 3 of its 4 chats, each time for the same three reasons: a whole candidate list written as one RESUME_FIELD value. That looks systematic rather than random: 7369543 is the one posting of the five where all three conditions fail, so every candidate value was checked, and that is exactly the situation the baseline instruction handles worst. The postings with two failing conditions were all accepted 4/4, so with five postings this is a pattern to test, not a rule. So the run shows two things: on these postings the verdict does not drift, but the form of the reply does, and the one posting where it drifted to rejection was the one where every condition failed. The limit is partly one I wrote down before the chats (all five hand labels are not_relevant), plus the small number of repeats: 4 per posting, so this says nothing about how stable a relevant verdict would be.


____
