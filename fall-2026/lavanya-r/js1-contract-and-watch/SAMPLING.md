# Sampling report (Chapter 1)

**Ran:** 2026-10-30, 21:22 UTC.

**Setup:**
- Each call was a fresh `claude -p` conversation: no tools, no saved session, an empty working folder.
- Every reply reported model `claude-opus-5-5`.
- **Prompt:** `prompts/baseline.md`, unchanged.
- **Code:** `experiments/sampling.py`.
- **Raw replies:** `evidence/claude/sampling/<posting_id>-<k>.json`, one file per call.
- **Summary:** `experiments/SAMPLING-RESULTS.json`.

**Postings:**
- 5 real Databricks postings from run 2's saved response.
- Chosen by a fixed rule: the first 3 "rule-relevant" and the first 2 other postings in the **development** split.
- Each was asked **4 times**, 20 calls in all.

## Results

| # | Posting | Hand label (Lavanya) | Rule v2 (record) | Claude ×4 (judgment) | Claude = hand label |
|---|---|---|---|---|---|
| 1 | Staff Software Engineer - Backend | not fit | not_relevant | INVALID ×4 | 0/4 |
| 3 | Staff Software Engineer - Streaming | not fit | not_relevant | INVALID ×4 | 0/4 |
| 6 | Software Engineer, Web Products | not fit | relevant | relevant ×4 | 0/4 |
| 10 | Specialist Solutions Architect - Azure Infrastructure & AI Platform | not fit | relevant | relevant ×4 | 0/4 |
| 12 | Software Engineer - New Grad (2027 Start) | not fit | relevant | relevant ×4 | 0/4 |

**Spread:**
- **None.** Every posting got the same outcome in all 4 calls.
- That includes the 8 INVALID replies. All 8 were `not_relevant` with `"resume_fields": []`, which CONTRACT.md does not allow, so the validator rejected them. The same format mistake repeated 4/4 on the same postings.

**Agreement with the hand label:** **0 of 20 calls.**
- If the validator had accepted empty `resume_fields`, #1 and #3 would have matched, giving 8/20.
- In all 12 valid replies, Claude agreed with the written rule.

## What I can conclude

- **Repeatability is not correctness.** Claude said "relevant" for #6, #10 and #12 every time, and it was wrong every time by my hand label.
  - It was applying my rule faithfully. The rule is what disagrees with me: it checks title words but not experience level.
  - In one reply for #12 (21:22 UTC), Claude noted on its own that the posting's "fall 2026/spring 2027 graduation window doesn't match the seeker's 2025-12 completion, but the rule doesn't test for that."
- On this date, with this prompt and this model, Claude's verdict on these 5 postings was stable enough that a single call would have told me the same thing as four.

## What I cannot conclude

- **That it never varies.** 4 calls is a small sample.
  - If Claude flipped its verdict 10% of the time on a posting, I would still see 4 identical answers about 66% of the time (0.9⁴).
  - So "0 flips seen" only rules out frequent flipping.
- **Anything about other postings, other days, or other models.** The sample is 5 postings, all from one board, all labeled "not fit" by me.
- **That my hand label is "true".** It is one person's judgment under `labels/LABELING-RULE.md`.
