# Labeling protocol (JS1) — written 2026-10-28, before any labeling

## The rule

I label by applying CONTRACT.md §4 by hand, and nothing else. This file adds no criteria.

## Which postings (chosen before looking at any of them)

- Source file: `evidence/stripe_jobs_content_true_2026-10-27T223947Z.json` (the saved board response I use)
- How I pick 20: all postings whose title contains "product" (case-insensitive), sorted by id numerically, ascending. 115 postings match; the first 10 are development, the next 10 are held-out.
- Development set: the first 10. Held-out set: the next 10.
- I record the 20 ids in `experiments/selected_ids.json` before labeling any of them.

## How I label

- I look only at title, location and content, using the posting viewer, which shows no verdicts.
- I do not look at the agent's rule output or any Claude reply for these postings until all my labels for that set are written down.
- Order: all 10 development labels first. I do not open the held-out postings until all 10 development labels are written down and the revised prompt is frozen. Frozen means: the baseline prompt has been run on the development set, the one change has been chosen, and the revised prompt is committed.
- Each label records C1, C2, C3, the verdict, and a one-line reason.

## Sampling report postings

- The 5 postings for the sampling report come from the first 5 of the development set, using the baseline prompt.
