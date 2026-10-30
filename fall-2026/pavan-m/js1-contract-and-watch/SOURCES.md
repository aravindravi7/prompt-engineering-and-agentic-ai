# SOURCES — Job-Search Agent 1

## What I used
- Greenhouse public Job Board API: `boards-api.greenhouse.io/v1/boards/gleanwork/jobs?content=true` (Glean, slug `gleanwork`)
- Python 3.14.6; httpx 0.28.1; anthropic 2.3.0 (+ httpx2, required by the SDK); pytest 9.2.0 (full list in `requirements.txt`)
- claude.ai (Northeastern account), Opus 5.5, incognito chats: all Claude judgments
- Claude Code (desktop app): wrote the implementation
- Claude (claude.ai chat): guidance and drafting, listed below
- INFO7375 JS1 assignment brief; TA guidance to use Northeastern's Claude instead of an API key

## What I wrote
- CONTRACT.md: all drafts and decisions (committed `5c57972`, before any code), plus the two dated revisions
- The relevance rule: title, skill, and location checks; the 3-skill threshold; title exclusions; failing on missing location; the intentional "Remote" behavior
- The fictional persona Alex Morgan (`data/persona_alex.json`)
- Every assert in `tests/test_watch.py` and `tests/test_rule_judge.py`, before the code existed (`47fef3f`, `7620c75`, `86b9864`)
- `labels/LABELING_RULE.md`, the choice of 20 postings, and all 20 hand labels and reasons
- `prompts/judge_v1.txt` (baseline) and the one added line in `prompts/judge_v2.txt`
- Every claude.ai chat: pasting each prompt and saving each reply
- The choice of board, the least-autonomy choice, the "Not checked" list, and the sign-off

## What Claude Code contributed (desktop app, October 30, 2026)
- All code in `agent/`: `net.py`, `resume.py`, `watch.py` (`5e30eac`); `rule.py`, `judge.py`, `run.py` (`7bbd664`); `manual_judge.py` (`10f2a91`)
- Choices it made where my spec was silent, which I accepted: usable id = integer; duplicates counted once; sorted `seen_ids`; evidence file naming; tags replaced with a space; SDK retries turned off; a meta/fingerprint file; refusing to re-check a recorded attempt (FRICTIONAL Entries 8, 11, 16)
- Found that the SDK requires httpx2, and checked the allow-list hook offline with a mock
- Flagged the stray "← NEW" markers in my v1 prompt and the contract mismatch after switching to claude.ai
- Action-surface Ways 2 and 3: its replies are saved in `action_surface/`

## What Claude (chat) contributed (claude.ai, October 29–30, 2026)
- A step-by-step breakdown of the assignment
- Review of my CONTRACT.md drafts; it pointed out gaps I then fixed myself (missing raw-response saving and seeded runs, missing Claude schema and validator, HTML decode order, email/phone contradiction, two unverifiable claims, "internship" not excluded) and that "semantic" matching isn't hand-checkable
- Suggested the project layout, `.gitignore`, the function interface, and test skeletons with TODOs (I wrote the asserts); caught my test-indentation bug
- Suggested the no-fences line and section labels in v1, the duplicate-title swap, and Option A as a candidate for v2's one change (I chose it)
- The Claude Code prompts I used
- Drafted `reports/SAMPLING_REPORT.md`, `reports/PROMPT_EXPERIMENT.md`, `reports/ACTION_SURFACE.md`, `reports/CONSTRUCTED_DEMO.md`, the README, and wording for several FRICTIONAL entries, all from my results; I checked the numbers against `runs/` and the screenshots

## What Claude judged
- 58 judgment replies in `runs/` (prompt experiment, sampling, CONSTRUCTED demo), each in a fresh incognito chat and each checked by `validate_reply`. These are model judgments, labeled as such, not facts.