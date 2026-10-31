# LABELING RULE — Prompt experiment (Job-Search Agent 1)

Version 1.0 · 2026-10-27 · Tushar Patel
Written and committed **before** any posting was labeled and before any Claude run.

## What a label means

A label is my verdict on whether a posting is relevant for the fictional persona Cole Palmer (`persona/cole-palmer.example.json`).

- I apply the **criteria of CONTRACT.md R1–R6** myself, by reading the whole posting.
- Where the code's matching is narrower than the criterion, I apply the criterion as meant, not the code. For example:
  - plain "2 years" counts as a year requirement;
  - any US city counts as US.

Labels: `relevant` | `not_relevant` | `cannot_tell`.

## The checks, as I apply them by hand

- **R1 Title.** The title names a Software, AI, or Backend Engineer role. It fails if it is Senior, Staff, Principal, Lead, Manager, or Intern.
- **R2 Freshness.** `first_published` (or `updated_at` if missing) is 21 days or fewer before **2026-10-27**.
- **R3 Location.** At least one listed location is in the US, including any US city and US remote or hybrid. If it says only "Remote" or a placeholder like "N/A", the result is unknown.
- **R4 Experience.** I read every stated experience requirement, in any wording: "N+", ranges, plain "N years", or spelled out. The largest minimum must be 3 or less. If no requirement is stated, the result is unknown.
- **R5 Sponsorship.** It fails if the posting says, in any wording, that it will not sponsor a visa. Business uses of "sponsor" (executive sponsor, event sponsors) do not count.
- **R6 Skills.** At least one of Cole's listed skills appears in the posting.

**Verdict:** any check fails → `not_relevant`. Otherwise, any check unknown → `cannot_tell`. Otherwise → `relevant`.

## Which postings

- **Source:** the baseline raw file `raw/greenhouse-stripe-2026-10-27T203128.json` (715 postings). It is fixed, so the set does not drift.
- **Pool:** postings whose title contains "Engineer" (case-insensitive substring, so it also includes "Engineering").
- **Pick:** 20 at random from the pool, seed **7375**.
- **Split:** with the same seed, the first 10 drawn go to **dev** and the next 10 go to **held-out**.
- Selection is done by a script, so anyone can reproduce the same 20.

## How I label

- I label all 20 by hand **before** any Claude run on them.
- I do not look at the code's rule verdicts for these postings while labeling.
- For each posting I record the label, the result of each check (pass / fail / unknown), and a one-line note on any fail or unknown, in `experiments/labels.csv`.
- I write labels once. If I later find I mislabeled a posting, I add a correction row with the date and the reason. I don't overwrite the original.

## How results are scored

- **Pass:** Claude's verdict exactly equals my label. `cannot_tell` against `relevant` counts as a miss.
- **Report:** passes out of 10, separately for dev and held-out, for the baseline prompt and the one revision.
- **Order:** the baseline and the revision are both run on dev first. The one change is chosen after seeing **dev** results only. Held-out is run last, once per prompt.
- **Sampling report:** 5 postings from the **dev** set, each asked 4 times in fresh API calls.
- **Limits:** 10 cases per set is very small. A difference of one or two cases may be noise.
