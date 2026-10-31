# Sampling report (Chapter 1) — what a model's answer is and is not

**What was run.** On 2026-10-26 I asked Claude my prompt contract
(`experiments/prompts/baseline.txt`) about 5 real postings from the board
response saved that day, **4 times each in 4 separate fresh contexts** — 20
judgments. Every raw response is stored byte-for-byte in
`experiments/results/transcript.json`, with its model label, timestamp and the
prompt-contract file it came from. `tools/score.py` recomputes every number
below from that file; nothing here was typed in by hand.

**Model.** `claude-sonnet`, via a Claude Code subagent. The harness exposes the
model family but not a pinned build identifier, so I cannot name the exact
version, and that is itself a limit on reproducibility: someone re-running this
next month may be sampling a different model under the same label.

**How the 5 postings were chosen.** By the committed script
`tools/select_experiment_postings.py`, not by hand: the one posting that fails
G3, the lowest-id relevant posting in the US, the lowest-id relevant posting
outside the US (the false positive pre-registered in CONTRACT.md §4.2), the
lowest-id G2 failure, and the lowest-id G1 failure. This set is deliberately
**not** representative of the board — it is one case per gate — so nothing here
is a rate over all 161 postings.

---

## The verdicts

| posting | title | location | 4 verdicts | 4 gates | distinct raw outputs | rule R-v2 | my L-v1 label |
|---|---|---|---|---|---|---|---|
| 8299781 | Machine Learning Engineer, Answers Relevance | Remote - United States | not_relevant ×4 | G3_job_family ×4 | 1 | not_relevant / G3 | **yes** |
| 6469397 | Software Engineer, Ads | Remote - United States | relevant ×4 | null ×4 | 2 | relevant | yes |
| 6512458 | Software Engineer, Ads | Remote - Ontario, Canada | relevant ×4 | null ×4 | 1 | relevant | **no** |
| 8153017 | Account Executive, Mid-Market (DACH) | Amsterdam, Netherlands | not_relevant ×4 | G2_discipline ×4 | 2 | not_relevant / G2 | no |
| 6909091 | Senior Software Engineer, Ads | Remote - United States | not_relevant ×4 | G1_title_block ×4 | 1 | not_relevant / G1 | no |

**Spread: zero.** 20 of 20 judgments passed the validator. Across all five
postings, all four repetitions returned the same `verdict` and the same
`gate_failed`. Agreement with the recomputable rule verdict: 20/20 on the
verdict, 20/20 on the gate.

**What did vary: the justification.** On two of the five postings the raw
output was not byte-identical across repetitions (`distinct raw outputs` = 2).
The differences were in which fields the justification cited, never in the
answer. Two examples, both real, both in the transcript:

- posting 6469397, repetition 3 added a fourth citation:
  `{"resume_field": "title_block[0]", "posting_field": "title", "evidence": "Software Engineer, Ads"}`
  — `title_block[0]` is `"senior"`, and the evidence quoted is the whole title.
  The citation says, in effect, "G1 passed", but it pairs the token `senior`
  with a string that does not contain it.
- posting 8153017, repetitions 1 and 4 quoted the full title
  `"Account Executive, Mid-Market (DACH)"` as the evidence for G2 while
  repetitions 2 and 3 quoted just `"Account Executive"`.

Both of those **passed my validator**, and that is a finding about my
validator, not about the model: it checks that the field path resolves and that
the evidence string occurs in the field named, and it does not and cannot check
that the pairing means anything. A justification can be well-formed and empty
of content. I did not know that before running this; it is in the sign-off
under "Not checked", and the first thing I would add to the validator in layer
2 is a check that a citation for a passing `title_block` gate quotes something
other than the whole title.

---

## Repeating the same verdict proves repeatability, not correctness

This is the part of Chapter 1 the numbers above make concrete, and I want to be
exact about it rather than gesture at it.

My own L-v1 labels disagree with the model on **2 of the 5 postings** — 12 of
20 judgments agree, a rate of 0.60. And the rule disagrees with me on exactly
the same two postings, at exactly the same rate. The model and the rule agree
with each other 20/20 and disagree with me 8/20:

- **6512458, "Software Engineer, Ads", Remote - Ontario, Canada.** Model:
  relevant, 4 times out of 4, `confidence: high` every time. Rule: relevant.
  Me: no — the persona cannot take a Canada-only remote role. This is the false
  positive I pre-registered in CONTRACT.md §4.2 item 3 on 2026-10-21, before I
  had seen any real data, and the real board turned out to carry 24 non-US
  remote postings for it to fire on.
- **8299781, "Machine Learning Engineer, Answers Relevance", Remote - United
  States.** Model: not_relevant at G3, 4 times out of 4, `confidence: high`.
  Rule: not_relevant at G3, because this posting's `Job Family` value is
  `null` — one of 10 such postings out of 161. Me: yes. L-v1 does not read
  Job Family at all; I would judge this on the title and the location and I
  would look at it.

So on this set, four identical answers at high confidence told me nothing about
whether the answer was right. They told me the pipeline is deterministic enough
to be audited — which is worth having, and is why the rule verdict sits next to
the judgment in every run report — and they told me nothing else. The one case
where the model was *least* useful is the one where it was most consistent: it
rejected a Remote-US ML engineering role 4 times out of 4 at high confidence
because of a missing metadata field, and said so in a well-formed
justification, and I would have applied to that job.

## What I can conclude, and what I cannot

**Can conclude.** Under this prompt contract, on these 5 postings, this model
reproduced the written rule exactly: 20/20 verdicts, 20/20 gates, 20/20 passing
the output validator. For judging *the rule as written*, the model is behaving
as a slightly expensive, slightly fuzzy reimplementation of 40 lines of Python
— which is an argument for keeping the Python, not for keeping the model.

**Cannot conclude.** That the verdicts are right: they match the rule, the rule
is mine, and the rule is wrong about 2 of these 5 postings by my own label.
Nothing about the other 156 postings on the board — this set was picked one per
gate and is not a sample of anything. Anything about variance in general: four
repetitions on five postings would not detect a verdict that flips 5% of the
time, and I cannot tell "this model is deterministic here" from "this model
happened to be deterministic on these five easy-to-mechanise postings". Nothing
about a different model, a different day, or a different build — the label is
`claude-sonnet` and the build is not pinned.

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
