# Prompt experiment (Chapter 2)

**Pass rate** = how often Claude's verdict equals my hand label (`experiment/labels.csv`, written before any Claude answer). An invalid reply counts as a fail. Development set: 10 postings. Held-out set: 10 postings, run last, once per prompt, and never used to change a prompt.

## The one change

| | File | What it says about experience |
|---|---|---|
| Baseline | `experiment/prompts/baseline.md` | the title has no senior/intern word, **and the description does not ask for 3 or more years** |
| Revision | `experiment/prompts/revision-no-years.md` | the title has no senior/intern word. **Do not use any years of experience the description asks for.** |

Nothing else differs (`diff` shows one changed line: line 6). I chose this change after the baseline dev run, because my hand labels did not check years.

**Prediction, written before the revision ran:** dev goes from 3/10 to about 7/10. 7661919, 8009057, 5552549004 and 5691886004 should flip to Relevant and match my labels. 5551730004 should stay Not Relevant (no matching skills). 8213988 and 8026211 should stay Relevant and still not match.

## Results

All four runs used `python3 -m agent experiment PROMPT --split dev|held-out`, model `claude-sonnet-5-5`, one fresh `claude -p` conversation per posting. Every reply is saved in `evidence/claude/experiment/<prompt>-<split>/`, and each run's `results.md` has the full table with Claude's reasons.

| | Dev (10) | Held-out (10) |
|---|---|---|
| Baseline (`baseline.md`) | **3/10** (2026-10-31 00:27:55Z) | **4/10** (16:37:46Z) |
| Revision (`revision-no-years.md`) | **7/10** (16:36:42Z) | **8/10** (16:38:45Z) |
| For comparison: "Not Relevant" every time | 5/10 | 4/10 |
| For comparison: the written rule (record) | 3/10 | 4/10 |

Invalid replies: 0 of 40.

* **The prediction held.** On dev, the four predicted postings flipped to Relevant and matched my labels, and the other three misses stayed as predicted.
* **Held-out ran last.** It was run once per prompt after the revision was fixed, and nothing was changed after seeing it. The revision went from 4/10 to 8/10 there too, so the gain was not only on the postings I looked at.
* **The baseline did no better than answering "Not Relevant" every time** (3 vs 5 on dev, 4 vs 4 on held-out). With the baseline, Claude agreed with the written rule on all 20 postings.

## Honest limits

* **A higher score here does not mean a better judge.** The revision matches my labels more because it copies how I labelled: by title, without reading years. It drops the contract's rule that the description asks for under 3 years. For a 0–2 year candidate, a job asking for 4+ or 5+ years is a weak match, and the revision calls those Relevant.
* **The watcher still uses `baseline.md` and the written rule**, which follow `CONTRACT.md`. The revision is only part of this experiment.
* **Both prompts still miss the same 4 postings**: 8213988 and 8026211 (dev), 7838591 and 8026207 (held-out). Both prompts call them Relevant and I labelled them Not Relevant, so no wording change about years can fix them. 5551730004 is a miss for both because its description names none of the candidate's skills.
* **The sets are small.** Ten postings per set means one posting moves the score by 10 points. Each prompt ran once per posting. The sampling report showed repeatable verdicts for the baseline on five postings, but the revision's repeatability was not tested.
* **One labeller and one model.** The labels are mine, from one sitting, and stayed unchanged after I saw Claude's answers. Only `claude-sonnet-5-5` was tried.
