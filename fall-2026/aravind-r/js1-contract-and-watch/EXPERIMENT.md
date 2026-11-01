# Prompt experiment (Chapter 2)

## Summary

A baseline prompt contract and one revision that changes one thing, scored against my hand labels: first on 10 development postings, then on 10 held-out postings that no Claude prompt saw until the final run.

## Setup

- **Labels:** 20 Stripe PM-family postings, deduplicated by title + team, drawn with seed 20261031 and split 10 dev / 10 held-out by the same seed (`labels/draw.json`). The labeling rule (`labels/LABELING-RULE.md`, committed f090693) was written before labeling. I labeled the 12 Gate 1 rows by hand; for the other 8, Claude (chat) read Gates 3–6 from grep output I ran, and I reviewed and set each label (`labels/hand-labels.json`, committed 3249974).
- **Baseline, v1** (`prompts/judge.v1.md`): the contract's rule, the persona, the posting, and a fixed four-key JSON output.
- **Revision, v2** (`prompts/judge.v2.md`): one change. A required `evidence` object quotes the sentence behind gates 2, 3, 5 and 6, or says "not found". The validator rejects a missing or malformed evidence object. Quote fidelity (every quote is an exact substring of the posting text Claude was given) is recorded but never rejects a reply or changes a verdict.
- **Pass:** Claude's verdict equals my hand label. An invalid reply counts as a fail.
- **Calls:** one fresh `claude -p` session per posting per prompt, `--tools ''`, `--model claude-sonnet-5-5`, Claude Code CLI 2.1.310. Dev runs happened before labeling, verdicts hidden. Held-out ran once, at the end (2026-11-01T02:52–02:53Z, commit e42aa75).
- **Rule check:** the rule (RECORD), recomputed, agreed with my hand labels on 20/20 verdicts and on every first failed gate (`node tools/score.mjs --rule`).

## Results

| run | set | n | passes (verdict = hand label) | invalid | quote fidelity ok |
|---|---|---|---|---|---|
| experiment/v1-dev.jsonl | dev | 10 | 10/10 | 0 | n/a |
| experiment/v2-dev.jsonl | dev | 10 | 10/10 | 0 | 10/10 |
| experiment/v1-heldout.jsonl | heldout | 10 | 9/10 | 1 | n/a |
| experiment/v2-heldout.jsonl | heldout | 10 | 10/10 | 0 | 10/10 |

The one failure: held-out 7 (7984866) under v1. The reply was a valid JSON object followed by prose ("Correction to the above: …"). The validator rejected it as not a bare JSON object, and it was recorded, not repaired.

## Limits and conclusions

Both prompts scored 10/10 on dev, so dev could not distinguish them. On held-out, v1 scored 9/10 and v2 10/10; the only difference is one format failure (held-out 7, v1: valid JSON followed by prose, rejected by the validator), not a wrong verdict. One event in ten cases is not evidence that the v2 change caused it. The base rate limits everything: held-out has 0 relevant postings and dev has 1, so a judge that always said “not relevant” would score 10/10 and 9/10. These pass rates mainly show the absence of false positives, not the ability to find relevant roles. v2’s quote fidelity was 10/10 on both sets, so in these 20 calls Claude never cited text absent from the posting. The most informative case was held-out 7: my literal rule passed “7+ years in Product Management” (no “experience” in the sentence) and failed it on location. v1’s reply (the invalid one) read the posting’s meaning and failed it on Gate 3; v2, under the same rule, applied it literally, noted the “7+ years” line and passed Gate 3 as “not stated”, agreeing with my rule. On held-out 1, Claude agreed with my rule (title fails), not with my gut that GTM Planning is PM-relevant.
