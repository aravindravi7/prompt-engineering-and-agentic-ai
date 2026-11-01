# Prompt experiment (Chapter 2)

## Setup

- **Postings:** 20 real postings from the live Databricks board fetched on 2026-10-31 (`snapshots/databricks-2026-10-31T233230Z-live.json`),
  picked by `experiments/select_postings.py` (seed 7375) in three strata: 8 with a title word and no seniority word,
  4 early-career, and 8 others. Positives are rare on this board, so likely candidates are oversampled. Then a random 10/10 split
  into development and held-out sets.
- **Labeling rule (written first, in CONTRACT.md):** relevant if Arya could apply honestly today: the role matches her
  AI/ML/data target, it is not senior, and she has at least 2 of the core skills the posting asks for. While labeling
  I added one blanket rule in the chat: any posting outside the US is not relevant.
- **Labels:** `labels/hand_labels.csv`, committed in d61f9b4 **before** any Claude call on these postings.
  Dev: 2 relevant and 8 not. Held-out: **0 relevant** and 10 not.
- **Pass:** Claude's verdict equals my hand label. A reply the validator rejects counts as a fail.
- **Calls:** one fresh `claude -p` call per posting per prompt, model `claude-sonnet-5-5`, 2026-10-31 ~23:50 UTC.

## The one change

| prompt | file | difference |
|---|---|---|
| v1 baseline | `experiments/prompts/v1_baseline.md` | task, résumé, posting, and a fixed JSON output format |
| v2 revision | `experiments/prompts/v2_criteria.md` | v1 **plus one paragraph**: my labeling rule, including "located in the US" |

`diff experiments/prompts/v1_baseline.md experiments/prompts/v2_criteria.md` shows exactly that paragraph and a blank line.
I chose this change after seeing v1 on dev (9/10, with #4 the only miss). The question was: does giving Claude **my** criteria bring it closer to **my** labels?

## Results (recomputed by `python3 -m experiments.summarize`)

| judge | dev (10) | held-out (10) | rejected by validator |
|---|---|---|---|
| Claude, v1 prompt | 9/10 | 10/10 | 0 |
| Claude, v2 prompt | 8/10 | 10/10 | 1 |
| written rule (record) | 8/10 | 10/10 | n/a |
| always "not_relevant" | 8/10 | 10/10 | n/a |

Per-call results: `experiments/results/v{1,2}_{dev,heldout}.jsonl`.

- **Dev:** v1 missed only #4, where my label was wrong (see SAMPLING.md). v2 also missed #4, and its reply on #7 was
  **rejected**: the key was `" justification"` with a leading space and there was extra text after the JSON. So v2's lower dev score
  comes from a format failure, not a different judgment.
- **Held-out:** both prompts scored 10/10, and so did the rule and "always say no". **All 10 held-out labels are
  not_relevant**, so this set cannot tell any of these judges apart.

## Honest limits

- **Ten cases show almost nothing.** The whole difference between v1 and v2 is one malformed reply. I can't say
  v2 is worse, and I can't say adding my criteria helps.
- **The held-out set has no positive cases.** 10/10 there is what a judge that never says "relevant" would get. The
  random split put both of my yeses into dev. Next time I'd stratify the split by label.
- **One of my two positive labels (#4) is itself wrong.** On the only posting where v1 "failed", Claude was right and my label was not.
  The answer key has errors too.
- **My written rule matched "always no" on all 20.** It said not relevant to every posting. It misses #3 and #4 because
  "Solutions Engineer" and "Software Engineer" are not in my title-word list. That's a gap in the rule, not a bug in the code.
- One call per posting per prompt: the sampling report shows a borderline posting can flip between calls.
