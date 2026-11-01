# Sampling report (Chapter 1)

## Summary

The same question, asked of Claude in fresh conversations: is this posting relevant to Maya Sehgal under my contract? Five postings, four calls each. Every reply is saved, with its timestamp, model and session id, in `sampling/v1-dev1-5-x4.jsonl`.

## Setup

- **Postings:** dev 1–5 from the seeded draw (`labels/draw.json`, seed 20261031). They weren't hand-picked.
- **Prompt:** `prompts/judge.v1.md` (the baseline prompt contract), with the rule text read from CONTRACT.md.
- **Calls:** 20 separate `claude -p` sessions, `--tools ''`, an empty temp directory each, `--no-session-persistence`, `--model claude-sonnet-5-5`. Claude Code CLI 2.1.310. They ran on 2026-10-31 ET (2026-11-01T02:06:40Z to 2026-11-01T02:07:25Z UTC), before I hand-labeled, and the verdicts weren't printed until my labels were committed (3249974).
- **Validator:** the fixed four-key JSON format. 0 of 20 replies were invalid.
- **Rule's first failed gate (RECORD):** dev 1, 3, 4 and 5 fail Gate 1 (title); dev 2 fails Gate 3 ("7+ years").

## Results

| n | id | title | hand label | verdicts (in call order) | agree with each other | agree with hand label |
|---|---|---|---|---|---|---|
| dev 1 | 8124304 | Staff Product Manager, Stripe Tax | not_relevant | not_relevant, not_relevant, not_relevant, not_relevant | yes | 4/4 |
| dev 2 | 8143563 | Product Manager, Support Platform  | not_relevant | not_relevant, not_relevant, not_relevant, not_relevant | yes | 4/4 |
| dev 3 | 8158082 | Program Manager, Risk Operations  | not_relevant | not_relevant, not_relevant, not_relevant, not_relevant | yes | 4/4 |
| dev 4 | 8043083 | Staff Product Manager, Issuing | not_relevant | not_relevant, not_relevant, not_relevant, not_relevant | yes | 4/4 |
| dev 5 | 8053517 | Privacy Operations Program Manager | not_relevant | not_relevant, not_relevant, not_relevant, not_relevant | yes | 4/4 |

All 20 verdicts were `not_relevant`. Each posting got the same verdict all 4 times, and all 20 matched my hand label.

## What I can and cannot conclude

All 20 verdicts (dev 1–5 × 4 fresh calls) were identical and matched my hand labels. That shows repeatability, not correctness: the same answer four times only means the model is consistent on these inputs. Four of the five postings failed on title alone (Gate 1); dev 2 was the only text-gate case (Gate 3, “7+ years”). So this says nothing about Gates 5–6, and Gate 4 only as a later failure on dev 2, or about any relevant posting. Four samples per posting also can’t detect rare flips: a verdict that flips 1 time in 10 would show no flip in four calls about 66% of the time.
