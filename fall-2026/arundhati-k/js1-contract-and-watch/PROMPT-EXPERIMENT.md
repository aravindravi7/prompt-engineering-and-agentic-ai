# Prompt experiment (Chapter 2)

**Labels.** 20 real Stripe postings from the live response `evidence/raw/20261031T061636Z-live.json.gz`, picked by
[`make_labeling_set.py`](make_labeling_set.py) (fixed seed, three strata — why: see its docstring) and split 10 dev /
10 held-out. I wrote [`labeling/LABELING-RULE.md`](labeling/LABELING-RULE.md) and committed it (`41a33a4`) before
labeling. My labels and notes: [`labeling/labels.csv`](labeling/labels.csv).

**Prompts.** [`prompts/baseline.txt`](prompts/baseline.txt) and [`prompts/revision.txt`](prompts/revision.txt). The
revision adds one sentence and changes nothing else (`diff prompts/baseline.txt prompts/revision.txt`):

> Role specialization: Include general Software Engineering internships and new-grad roles when they meet the
> approved-skill threshold. Exclude specialized roles such as Machine Learning Engineer, Data Scientist, and Research
> Scientist when their primary responsibilities focus on specialized domain work rather than general software engineering.

**Order (commits show it).** dev labels → baseline on dev → revision written and run on dev (committed `55376c3`) →
both prompts run once on held-out with `--final` before held-out labels existed → held-out labels → score (`684dad2`).

**Pass** = the reply passed the validator AND its verdict equals my hand label. One call per posting per prompt.

| prompt | dev | held-out | invalid replies |
|---|---|---|---|
| baseline | 9/10 | **7/10** | 0 |
| revision | 10/10 | **6/10** | 0 |

Per-posting table: [`experiments/RESULTS.md`](experiments/RESULTS.md) (regenerate: `python3 experiments.py score`).

## What the misses were (from the saved replies)

| row | posting | location | my label | baseline | revision | Claude's stated reason |
|---|---|---|---|---|---|---|
| 2 (dev) | SWE, New Grad | SF/Seattle/NY | RELEVANT | NOT | RELEVANT | baseline: Java/JS/Go "appear only as Stripe's stack" |
| 11 | SWE, Early Career | SF/Seattle/NY | RELEVANT | RELEVANT | **NOT** | revision: same "stack" reading |
| 14 | SWE, New Grad | **Bangalore** | RELEVANT | NOT | NOT | both: not in the US |
| 15 | SWE, Intern | **Singapore** | RELEVANT | NOT | NOT | both: not in the US |
| 16 | SWE, New Grad | **Toronto** | RELEVANT | NOT | NOT | both: not in the US |

- Rows 14–16: my labels say RELEVANT but my written rule requires a US location; both prompts applied the location
  condition. These three misses are a disagreement between my labels and my own rule, not a prompt difference.
- Rows 2 and 11: the only rows where the two prompts differ. Both turn on the same sentence ("We work mostly in
  Java, Ruby, JavaScript, Scala, and Go…"), which the sampling run showed splitting 3–1 under the *same* prompt.
  The revision's sentence is about specialized roles; it does not mention that sentence.
- Row 13: I first labeled it RELEVANT, then changed it to NOT RELEVANT before any held-out result was scored
  (recorded in its note). Both prompts said NOT RELEVANT.

## Honest limits

_My words — to write._ Questions to answer:
- Did the revision improve anything? What would you need to see to believe a +1 on dev or −1 on held-out?
- Ten cases, one call each, with a posting known to flip under the same prompt: how much can 7/10 vs 6/10 show?
- Which misses come from Claude, and which from my labels? What would you change first — the prompt, the rule, or the labels?
