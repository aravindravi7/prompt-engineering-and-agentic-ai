# Sampling report (Chapter 1) — Job-Search Agent 1

## What I ran
- Prompt: prompts/judge_v1.txt (unchanged during sampling)
- Postings: 5 from my hand-labeled set: 2 clear relevant, 1 clear not_relevant, 2 borderline (picked while labeling, before any Claude run)
- Samples: 4 per posting, each in a fresh claude.ai incognito chat (Opus 5.5), October 30, 2026
- Sample r1 for each posting is its v1 chat from the prompt experiment (also a fresh incognito chat with the same prompt). r2–r4 were run separately for sampling.
- Every reply was checked by the same validator as the rest of the agent (agent/judge.py validate_reply), with one retry allowed.
- Raw prompts and replies: runs/prompt_exp/v1/ (r1) and runs/sampling_r2/, runs/sampling_r3/, runs/sampling_r4/ (each with results.csv)

## Results

| Posting | My label | r1 | r2 | r3 | r4 | Spread |
|---|---|---|---|---|---|---|
| 4742953005 Agentic Runtime | relevant | relevant | relevant | relevant | relevant | 4/4 same |
| 4428090005 Product Backend | relevant | relevant | relevant | relevant | relevant | 4/4 same |
| 4744818005 ML Enterprise Brain | not_relevant | not_relevant | not_relevant | not_relevant | not_relevant | 4/4 same |
| 4696752005 APIs & Context Platform (borderline) | not_relevant | not_relevant | not_relevant | not_relevant | not_relevant | 4/4 same |
| 4605446005 AI & Security (borderline) | not_relevant | not_relevant | not_relevant | not_relevant (attempt 2) | not_relevant | 4/4 same |

- Verdict spread: 0 of 5 postings changed verdict across 4 samples (20/20 consistent).
- Agreement with my hand label: 5/5 postings, every sample.
- ⚠️ Version A: Format: all 20 final replies were valid. One extra attempt (4605446005, r3) happened because I saved my prompt instead of Claude's reply; that was my copy error, not Claude's output.
- ⚠️ Version B: Format: 1 of 21 replies failed the validator (4605446005, r3, attempt 1: not valid JSON only). The retry in a new chat was valid. So the format is not perfectly stable, even with an explicit no-fences instruction.
- Format: all 20 final replies were valid. One extra attempt (4605446005, r3) happened because of my own copy error: the attempt-1 reply file contains text I had copied from my help chat, not Claude's reply. Attempt 2 was a new fresh chat and passed the validator. No reply from Claude failed validation.

## What I can conclude
- On these 5 postings, with this prompt and this model on this day, Claude's verdict was repeatable: the same answer in 4 out of 4 fresh chats each, including the 2 borderline cases.
- Its verdicts matched my hand labels on all 5.

## What I cannot conclude
- **Repeatability is not correctness.** Four identical answers show Claude is consistent, not that it is right. My hand labels are one person's judgment, not ground truth.
- **Small sample.** With 0 flips in 20 samples, a rough rule-of-three estimate says the per-chat flip rate on postings like these could still be as high as about 15% (approximately 3/20). Four samples per posting cannot detect rare flips.
- **Only the verdict was compared.** I did not measure whether the justification text or the cited fields stayed the same across chats.
- **No control over settings.** claude.ai chats don't expose temperature or other sampling settings, so this measures the chat product as I used it, not the model under controlled conditions.
- **Not generalizable.** Only 5 postings from one company, one persona, one model, one day.