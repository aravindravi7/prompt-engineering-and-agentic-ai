# Sampling report (Chapter 1)

**What ran (2026-10-31, 06:32–06:34 UTC):** the baseline prompt contract ([`prompts/baseline.txt`](prompts/baseline.txt))
on 5 dev postings, 4 calls each = 20 calls. Each call was a fresh `claude -p` session (no tools, no history,
empty working directory). Every reply passed the validator. Model reported for every call: `claude-opus-5-5`.
Raw log with every reply and session id: [`experiments/sampling/calls.jsonl`](experiments/sampling/calls.jsonl).

**Why these 5:** all are dev postings (so held-out stayed unseen) and they cover the rule's boundaries: the one
US new-grad SWE posting, a US high-school internship, a US master's ML intern, and two non-US SWE early-career
postings (Singapore, Dublin).

| posting | title | location | 4 verdicts (call order) | agreement | rule (record) | my hand label |
|---|---|---|---|---|---|---|
| 8128744 | Software Engineer, New Grad | SF, Seattle, NY | RELEVANT, RELEVANT, RELEVANT, NOT RELEVANT | **3/4** | RELEVANT | RELEVANT |
| 8241260 | High School Internship, Software Engineering | Seattle, SF | NOT ×4 | 4/4 | NOT RELEVANT | NOT RELEVANT |
| 8333074 | Master's Machine Learning Engineer, Intern | SF, NYC, Seattle | NOT ×4 | 4/4 | NOT RELEVANT | NOT RELEVANT |
| 8160776 | Software Engineer, New Grad | Singapore | NOT ×4 | 4/4 | NOT RELEVANT | NOT RELEVANT |
| 8097801 | Software Engineer, Intern | Dublin | NOT ×4 | 4/4 | NOT RELEVANT | NOT RELEVANT |

**Where the spread came from (from the saved replies).** The split posting says *"We work mostly in Java, Ruby,
JavaScript, Scala, and Go. We believe new programming languages can be learned…"*. Three calls counted Java,
JavaScript and Go as preferred skills; the fourth said they "appear only as Stripe's stack" and called the posting
NOT RELEVANT. All four cited the same three skills — the calls agreed on the *evidence* and disagreed on whether it
meets "requires or prefers". The same sentence split the evidence again in the evidence lists for 8241260
(call 2 cited no skills; calls 1, 3, 4 cited three) without changing that verdict.

**Ten more calls on 8128744 outside this table** (prompt-experiment dev runs): baseline said NOT RELEVANT,
revision said RELEVANT. Across all six calls on this posting in the logs: 4 RELEVANT, 2 NOT RELEVANT.

## What I can and cannot conclude

_My words — to write._ Questions to answer:
- Four identical NOT RELEVANT verdicts on 4 postings: does that show Claude is *right*, or only that it repeats?
  What did comparing against my hand label add?
- The one posting I labeled RELEVANT is the one that split. What does that say about trusting a single call?
- Five postings, four calls each: what is too small here to claim anything about?
