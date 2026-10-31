# Prompt experiment (Chapter 2) — Job-Search Agent 1

## Setup
- Labels: 20 Glean postings hand-labeled by me (labels/labels.csv) using labels/LABELING_RULE.md, written and committed before labeling. 6 relevant, 14 not_relevant.
- Split: random with seed 7375, done before labeling (labels/split.txt): 10 dev, 10 held-out, 3 relevant in each.
- Prompts:
  - Baseline: prompts/judge_v1.txt
  - Revision: prompts/judge_v2.txt. One change, one added line: "Treat a posting as not relevant if the years of experience it requires clearly exceed the candidate's experience." (`diff` shows exactly one line.)
- Runs: each posting judged in its own fresh claude.ai incognito chat (Opus 5.5), October 30, 2026; 40 chats total. Every reply checked by agent/judge.py validate_reply, one retry allowed. Held-out was run only after v1 and v2 were both final on dev.
- Scoring: `python -m agent.manual_judge score`; an invalid final reply counts as a fail. Raw prompts, replies and results: runs/prompt_exp/.

## Why this change
Required years of experience decided 5 of my 20 hand labels, and 4 held-out postings require 5+ years, but v1 never mentions experience level. This line tests whether saying it explicitly changes Claude's verdicts. It brings one factor from my own labeling rule into the prompt, so any gain would partly mean "closer to my judgment," not "more correct."

## Results

| Prompt | Dev | Held-out |
|---|---|---|
| v1 (baseline) | 10/10 (100%) | 10/10 (100%) |
| v2 (one change) | 10/10 (100%) | 10/10 (100%) |
| Always "not_relevant" | 7/10 (70%) | 7/10 (70%) |

- Invalid final replies: 0 of 40.
- Both prompts beat the always-not_relevant baseline by 3 postings on each split.
- v1 and v2 gave the same verdict on every one of the 20 postings.

## What this shows
- The revision made **no measurable difference**. Both prompts agreed with my labels on all 20 postings.
- v1 already weighed required experience on its own: for example, 4696752005 (strong API/platform fit, 8+ years) was judged not_relevant by both prompts.
- Dev could never show an improvement, because v1 was already at 10/10 there (a ceiling effect).

## Honest limits
- **Ten cases per split is very little.** One disagreement would move a score by 10 points, and a 10/10 score cannot separate two good prompts.
- **Agreement with me, not correctness.** My labels are one person's judgment. 100% agreement means Claude judged like me on these 20 postings, not that either of us is right.
- **The set may be too easy.** Only 2 postings were borderline for me; with more hard cases, the prompts might differ.
- **One sample per posting per prompt.** The sampling report shows verdicts were stable for 5 postings, but these 40 runs are single chats.
- **Process errors.** Two attempt-1 records were caused by my copy-paste mistakes (4746908005 v1 dev; 4696752005 v1 held-out), not by Claude. I deleted those rows and recorded the real replies (FRICTIONAL Entries 17 and 21).
- One company, one persona, one model, one day.