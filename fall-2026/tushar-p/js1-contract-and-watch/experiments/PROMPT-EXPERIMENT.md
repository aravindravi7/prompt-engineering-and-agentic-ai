# Prompt experiment — Job-Search Agent 1

Run on 2026-10-29 · model claude-sonnet-5-5 · temperature not set in the request (API default) · Tushar Patel

## Setup

- **Labels:** 20 Stripe postings, hand-labeled on 2026-10-27 under `experiments/LABELING-RULE.md` (v1.0, committed before labeling). Labels are in `experiments/labels.csv`.
- **Selection:** postings whose title contains "Engineer" (pool of 170), 20 drawn with seed 7375. The first 10 drawn are **dev**, the next 10 **held-out** (`experiments/selection.json`).
- **Label mix:** dev has 1 `relevant` and 9 `not_relevant`. Held-out has 0 `relevant` and 10 `not_relevant`. There are no `cannot_tell` labels.
- **Scoring:** a pass is an exact match between Claude's verdict and my label. An invalid reply counts as a miss.
- **Inputs:** postings come from the baseline raw file `raw/greenhouse-stripe-2026-10-27T203128.json`, with run date 2026-10-27 for R2 (the date the labels used).
- **Order:**
  1. baseline on dev;
  2. one change chosen from the dev results only;
  3. revision on dev;
  4. held-out last, once per prompt (`experiments/results/HELDOUT-LOG.md`).

## The two prompts

| Prompt | File | SHA-256 |
|---|---|---|
| Baseline | `prompts/baseline.txt` | `f5d787a9b88c5ec036b6ba98e1fc254a309e696120f3521e05b9208d0dc92496` |
| Revision | `prompts/revised.txt` | `57a45a61215283556329b7e15000f1be5fc59bd9600c6be96ea91151790e6509` |

**The one change** (lines 27–28 of the prompt, the R4 experience rule):

```
< more than 3 is fail. No matches: unknown. Plain "N years" and spelled-out numbers do not
< count.
---
> more than 3 is fail. No matches: unknown. Also count plain "N years" (for example "2 years of experience") and numbers written in words, with or without a digit in brackets (for example "two (2) years"); the minimum is that number.
```

**Why this change:** the baseline's only dev miss was 8314283, which I labeled `relevant` and Claude judged `cannot_tell`.
- Claude's saved justification (2026-10-29) passed R1, R2, R3, R5 and R6, and marked R4 unknown: "two (2) years" is spelled out and is not a counted form.
- So Claude followed the baseline prompt's R4 exactly. My labeling rule counts any wording, so the miss came from a gap between the prompt and my labeling rule, not from Claude misreading.

## Results

| Prompt | Dev (10) | Held-out (10) | Invalid |
|---|---|---|---|
| Baseline | **9 / 10** (miss: 8314283, `cannot_tell` vs `relevant`) | **10 / 10** | 0 |
| Revision | **10 / 10** | **10 / 10** | 0 |

Result files are in `experiments/results/`:
- `baseline-dev-2026-10-29T190534`
- `revised-dev-2026-10-29T191746`
- `baseline-held-out-2026-10-29T191945`
- `revised-held-out-2026-10-29T192030`

## What this can and cannot show

- **The dev improvement is not evidence that the change generalizes.** I chose the change because of 8314283, so it fixing 8314283 is expected. Once I tuned on it, dev is no longer an independent test of the change.
- **Held-out cannot tell the two prompts apart.** Both scored 10/10, and held-out has no `relevant` posting. It shows only that the revision **did not break any rejects** on these 10 postings. It says nothing about whether the revision recognizes good postings better.
- **A constant answer would score the same.** A judge that always answers `not_relevant` would get 9/10 on dev and 10/10 on held-out, the same as the baseline prompt. With this label mix, the pass rate mostly measures rejecting postings.
- **The sample is tiny.** Ten cases per split, one run per prompt per split. A difference of one case (9 vs 10 on dev) is within what noise could produce. Only the baseline was checked for repeatability (see `SAMPLING-REPORT.md`).
- **Labels are mine alone.** There's no second labeler, so a mistake in my labels would count as Claude's miss, or hide one.
- **One model, default settings.** Nothing here says how another model or setting would do.

## Consequence for the agent

After this change, the Claude judge's R4 no longer matches the code's R4, which still ignores plain "N years" (CONTRACT.md v0.4). The agent still uses `prompts/baseline.txt` by default; I did not switch it. Whether to switch it, or to change the code's R4 to match, is an open decision for a later version.
