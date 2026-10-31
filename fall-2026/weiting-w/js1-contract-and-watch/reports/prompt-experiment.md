# Prompt experiment (Chapter 2) — one change, measured on held-out cases

**The change, in full.** `diff experiments/prompts/baseline.txt
experiments/prompts/revision.txt` is one inserted paragraph and nothing else:

```
> Evaluate the gates strictly in the order G1_title_block, G2_discipline,
> G3_job_family, G4_location, stop at the first gate that fails, and report that
> first failing gate; do not report a later gate when an earlier one has
> already failed.
```

I picked that change because `gate_failed` is the field the contract is
strictest about (CONTRACT.md O4: null exactly when relevant, otherwise the
**first** failing gate in order) and the baseline prompt stated the gates
without stating that ordering mattered.

**What was run.** 40 judgments on 2026-10-26: 20 real postings × 2 prompt
variants, each in its own fresh context, raw output stored verbatim in
`experiments/results/transcript.json`. Development set of 10 and held-out set
of 10, split by the committed script `tools/select_experiment_postings.py`
(within each gate class, sorted by id, even positions to development and odd to
held-out — arithmetic, not choice). **I looked at the development results
first and the held-out results only at the end**, and I did not change the
revision after seeing either.

**Three numbers, not one**, because collapsing them hides which thing failed:

| | what it measures |
|---|---|
| validator pass | did the output meet the output contract at all |
| rule fidelity | did the verdict match what R-v2 computes — *this is what the prompt asks for* |
| hand-label agreement | did the verdict match my L-v1 label — rule quality and model fidelity mixed together |

---

## Results

| set | prompt | n | validator pass | rule fidelity (verdict) | rule fidelity (gate) | agreement with my L-v1 label |
|---|---|---|---|---|---|---|
| development | baseline | 10 | 10/10 | 10/10 | 10/10 | 10/10 |
| development | revision | 10 | 10/10 | 10/10 | 10/10 | 10/10 |
| held-out | baseline | 10 | **9/10** | 9/9 | 9/9 | **7/9** |
| held-out | revision | 10 | **9/10** | 9/9 | 9/9 | **7/9** |

Rule fidelity and hand-label agreement are computed over the outputs that
validated, since a rejected output has no verdict to compare.

**The revision changed nothing measurable.** Identical on every number, on both
sets. The honest reading is not "the revision is useless" but "the baseline was
already at ceiling on gate ordering, so this experiment had no room to show a
difference" — 10 development cases where the baseline scores 10/10 cannot
distinguish a good change from a no-op. I should have chosen a change aimed at
something the baseline was actually getting wrong, and the thing it was
actually getting wrong is in the next section.

## The one validator rejection, and it is the same posting both times

Posting **7330347, "Principal Data Scientist, Ads"** is the only output in all
40 that the validator rejected — and it was rejected under **both** prompts.
Both times the model emitted a JSON object, then prose, then a second JSON
object. Verbatim, from the transcript (baseline):

> `{"posting_id": 7330347, … "resume_field": "title_block[3]" …}`
> `Wait — correcting the index: "principal" is title_block[4].`
> `{"posting_id": 7330347, … "resume_field": "title_block[4]" …}`

and under the revision:

> `{… "resume_field": "title_block[1]" …}`
> `Correction: the justification should cite title_block[1] as "sr", but the title contains "Principal", which is title_block[2]... let me restate precisely.`
> `{… "resume_field": "title_block[3]" …}`

Three things worth saying about this, in order of how much they bother me:

1. `title_block[3]` **is** `"principal"`. The baseline's first answer was
   correct and its self-correction made it wrong. The revision's first answer
   was wrong and its self-correction landed on the right index. In both cases
   the *verdict* and the *gate* were right throughout; only the index moved.
2. The validator caught it for the right reason — the response was not exactly
   one JSON object — but it would have caught it for that reason even if the
   index had been right, and it would **not** have caught the wrong index if
   the model had emitted a single clean object containing it. `title_block[4]`
   resolves (`"lead"`), and the evidence `"Principal"` does occur in the title,
   so `{"resume_field": "title_block[4]", "posting_field": "title", "evidence":
   "Principal"}` passes every check my validator makes while citing the wrong
   résumé token.
3. Counting a run as a failure because the model thought out loud is the
   validator doing its job, and I am keeping it strict. But it means my
   "validator pass rate" measures format compliance and not much else; the
   error I would actually want caught — a citation pointing at the wrong
   element of the right list — is invisible to it. That is in the sign-off.

## Every verdict error is the rule's error, not the model's

This is the clearest result in the experiment. Across all 40 judgments, the
model's verdict disagreed with my hand label on exactly two postings, and both
are postings where **R-v2 itself** disagrees with my hand label:

| posting | title | location / Job Family | model | R-v2 | my label |
|---|---|---|---|---|---|
| 7131934 | Machine Learning Engineer | Remote - Ontario, Canada | relevant | relevant | **no** |
| 8282760 | Analytics Engineer | Data Science, Remote - US | not_relevant (G2) | not_relevant (G2) | **yes** |

There is not a single judgment in the 40 where the model got the rule wrong and
the rule was right. Both held-out misses are R-v2's two known defects, faithfully
reproduced: the G4 remote false positive pre-registered in CONTRACT.md §4.2
item 3 on 2026-10-21, and the G2 closed-list false negative pre-registered in
`experiments/labeling-rule.md` the same day ("Analytics Engineer" is not on
`target_title_phrases`). **Improving this prompt cannot fix either of them.**
The thing to fix is the rule, and fixing the rule is a version bump, not a
prompt edit.

## How little ten cases can show

Ten cases per set, and the sets are not samples. `tools/select_experiment_postings.py`
drew them stratified by gate class — 8 relevant, 4 G2 failures, 8 G1 failures
across the 20 — against a board where **143 of 161** postings fail G1. So:

- **These rates do not describe the board.** On a proportional sample, roughly
  9 of 10 postings would be a seniority token in a title, and the headline
  number would mostly measure whether the model can find the word "Senior".
- **Two classes are missing entirely, and the absences are facts about the
  board, not conveniences.** The board has exactly **one** posting that fails
  G3_job_family, and it is in the sampling set, so G3 appears nowhere in these
  40. **No** posting on this board fails G4_location at all, so the gate behind
  the headline false positive is never the *reported* gate — it fires by
  letting things through.
- **A 10/10 and a 9/10 are not distinguishable at this size.** One posting is
  10 percentage points. The single held-out rejection moved the validator rate
  from 1.00 to 0.90 by itself, and if the selection had put 7330347 in the
  development set instead, the development column would read 0.90 and the
  held-out column 1.00 with nothing about the prompts having changed.
- **One repetition per cell.** The sampling report found zero variance across
  four repetitions, which is the only reason I am willing to read a single
  judgment per cell at all — and that evidence is itself five postings deep.

## What I would change next, and why not now

Not the prompt. The prompt is at ceiling on the only thing it can control. The
two things worth changing are both in the rule, and each is its own version
bump so that the next experiment reads one variable:

1. **G4** should require a US scope rather than the substring `"remote"`. That
   one change fixes 7131934, 6512458, and the 22 other non-US remote postings
   on this board.
2. **G1** should read the `Management Level` metadata field (`IC3`, `IC5`,
   `IC6`, `M2`, `D1`) instead of guessing seniority from title words. The board
   states the level explicitly and R-v2 ignores it, which means a plain-titled
   IC6 posting passes G1 today — pinned as behaviour in
   `tests/test_rule_worked_examples.py::test_seniority_is_judged_from_the_title_not_management_level`.

## Where these labels are weak

All 25 labels are mine. Four of them (8299781, 6512458, 7131934, 8282760 — the
rows L-v1 does not settle mechanically) I decided on 2026-10-26 with nothing in
front of me. The other 21 were first derived by Claude applying L-v1's own L1
and L2 wording mechanically to the title, and on 2026-10-30 I checked all 21
row by row, found they matched what I would have filled in myself, and changed
none. `experiments/labels/labels-L-v1.json` records which is which per row.

Neither set is a **blind** label, in two different ways, and both are reasons
to read every agreement number here as weaker than it looks:

1. Before I decided the four author rows, Claude had already told me what R-v2
   returns for each of them, and for 6512458 also what the model returned. I
   disagreed with the agent on all four, which is the opposite of what
   anchoring would produce — but the labels were made with the agent's verdict
   known.
2. The 21 derived rows were confirmed after I had seen the aggregate results of
   all 60 judgments. Confirming a label you already know the scoreboard for is
   not the same as writing it blind.

What I would do differently in layer 2 is dull and would have cost nothing: all
labels in a committed file before a single judgment is run.
