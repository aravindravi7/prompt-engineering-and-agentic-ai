# CONSTRUCTED demonstration: both judges on "new" postings

**This is a constructed demonstration, not a real run.** Run 2 (live, Oct 30, 4:29 PM ET) found 0 new postings, so the "judge each new posting" path never ran on a real new posting. To show it end to end on real data, I made a copy of Run 1's state with 3 ids removed (state/CONSTRUCTED_demo_state.json; the real state files are untouched) and ran the agent seeded on Run 2's real response.

- Input: evidence/2026-10-30T162946_live_gleanwork.json (real, live)
- State: state/CONSTRUCTED_demo_state.json (CONSTRUCTED: seen_ids_after_run1 minus 4746354005, 4746910005, 4696752005)
- Watch output: mode seeded, new_ids [4746354005, 4746910005, 4696752005]; evidence copy in evidence/CONSTRUCTED_demo/
- Record verdicts: reports/CONSTRUCTED_demo_record.json (agent/rule.py)
- Judgment verdicts: runs/CONSTRUCTED_demo/ (prompt v1, fresh claude.ai incognito chats, Opus 5.5, Oct 30, 2026; checked by validate_reply)

| Posting | Record (rule) | Judgment (Claude) | My hand label |
|---|---|---|---|
| 4746354005 Office Manager | not_relevant (0 skills) | not_relevant | not_relevant |
| 4746910005 Software Engineer | relevant (Java, Python, AWS) | relevant | relevant |
| 4696752005 Software Engineer, APIs & Context Platform | relevant (Java, Python, REST APIs) | not_relevant | not_relevant |

## What the disagreement shows
On 4696752005, the rule says relevant because title, 3 skills and location all pass. The rule does not look at required experience, and the posting asks for 8+ years. Claude's judgment and my hand label both say not_relevant for that reason.
- The **record** is recomputable by anyone, but blind to anything the rule doesn't check.
- The **judgment** considers more, but it is a model's opinion: it can't be recomputed, and its justification isn't verified by the validator.
Both are kept and labeled; neither overwrites the other.