# Prompt experiment (Chapter 2)

*The tables were drafted by Claude Code on 2026-10-31 from the saved replies in `experiment/replies/`, and recomputed with `python3 -m tools.score experiment`. The conclusions were drafted by Claude Code; Varnika reviewed the conclusions on 2026-10-31, from Claude Code's summary of them in chat, and agreed; she did not re-derive the numbers herself.*

## Setup, in the order it happened (UTC, 2026-10-31)

| When | What | Where |
|---|---|---|
| 08:01 | Labeling rule committed, before the 20 postings were seen. Claude Code drafted it at my request. | `LABELING-RULE.md`, `808270d` |
| 08:02 | The 20 postings committed. They were picked mechanically from run 1's saved response: seed 7375, 10 from postings that pass Rules 1–3 and 10 from the rest, 5 + 5 of each into development and held-out. | `postings.json`, `tools/select_experiment.py`, `1b50ba1` |
| 08:20:15 | **My 20 hand labels committed**: 19 `NOT_MATCH`, 1 `MATCH`. | `labels.csv`, `3ff2be4` |
| 08:20:32 | baseline-v1 on the 10 development postings | `replies/baseline-v1/` |
| 08:28:34 | **revision-v1 frozen** with my prediction, before it ran | `REVISION-DECISION.md`, `31f068e` |
| 08:28:59 | revision-v1 on the 10 development postings | `replies/revision-v1/` |
| 08:29 | Both prompts on the 10 held-out postings, last | `replies/*/` |

- **The one change:** revision-v1 adds one instruction to baseline-v1: *judge only the posting's must-have qualifications; preferred or nice-to-have qualifications never count against the candidate.* `diff` shows nothing else.
- **Calls:** every reply is a fresh `claude -p` conversation with no tools, model `claude-opus-5-5`. All 40 replies passed the validator.
- **The held-out set:** no Claude reply on it existed before both prompts were frozen. One exception to disclose: when the development baseline was scored, the scoring tool also printed the held-out rows. Those show only my labels and the rule's verdicts, not Claude's. The revision was chosen from the development miss alone.

## Results: agreement with my hand labels

### Development (10 postings)

| Posting | Hand label | Rule (record) | baseline-v1 | revision-v1 |
|---|---|---|---|---|
| Software Engineer, Research Tools (4981828008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| Staff+ Software Engineer, Developer Productivity (5110511008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| Data Scientist, Growth (5161402008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| Machine Learning Infrastructure Engineer, Safeguards Research (5364804008) | **MATCH** | NOT_MATCH ✗ | N ✗ | N ✗ |
| Software Engineer, Business Technology (5400153008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| Data Engineer, GTM (5418610008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| Recruiting Analytics Data Engineer (5424111008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| [London] Applied AI Architect, Partnerships (5432583008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| Director, Infrastructure Lease Accounting (5441867008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| Manager, Enterprise Sales - Asset & Wealth Management (5464894008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| **Pass rate** | | **9/10** | **9/10** | **9/10** |

### Held-out (10 postings, run last)

| Posting | Hand label | Rule (record) | baseline-v1 | revision-v1 |
|---|---|---|---|---|
| Model Performance Software Engineer, Claude Code (5098025008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| Safeguards Enforcement Analyst, Age-Appropriate Design (5311234008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| AV Operations Specialist (5383710008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| Product Manager, New Markets and Monetization (5386182008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| Manager, Account Executive (5391356008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| IT Systems Engineer, Mobile Client Platform Engineer (5396384008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| Software Engineer, Tokens and Prompt Structures (5421263008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| Applied AI Architect, International Policy (5439830008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| IT Systems Engineer, Client Platform Engineer, macOS (5445625008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| Security Data Engineer (5462966008) | NOT_MATCH | NOT_MATCH ✓ | N ✓ | N ✓ |
| **Pass rate** | | **10/10** | **10/10** | **10/10** |

**My prediction:** 9/10 for revision-v1 on development, frozen in `31f068e`. **Observed:** 9/10. The prediction held.

## What the one change did

- **Verdicts: nothing.** All 40 Claude verdicts are `NOT_MATCH` under both prompts, so no posting changed verdict.
- **Reasons: it moved them toward the must-haves.**
  - Replies whose reason mentions "minimum" or "must-have": baseline 1 of 20, revision 4 of 20.
  - Replies whose reason mentions the salary: baseline 2, revision 1.
  - On row 4, the baseline reason leaned on ML-pipeline experience, much of it from *Preferred qualifications*. The revision reason says: "no shipped Python work and no research-to-deployment ML pipeline experience, **which the posting's minimum qualifications require** for a senior role paying $350K–$500K." So it now argues from must-haves, but it still uses the salary, which the instruction did not mention.
- **Why row 4 did not flip.** "Proficiency in Python" really is a minimum qualification. Aarav lists Python as a skill, but none of his job bullets shows Python work. My label read "Python required" as met by the skills list; Claude reads it as not shown. The rule also says `NOT_MATCH`, for a different reason: Rule 5 finds only one résumé skill (Python), and it needs two. Two machine judges agreeing against me is not evidence that they are right. They fail for different reasons, and my label is a judgment call I would defend, while admitting Claude's reading is defensible too.

## Honest limits

- **Ten cases show very little.** On development, the only posting that could separate the prompts was row 4, and it went the same way under both. The two prompts are indistinguishable on this data. I cannot say the revision is better or worse.
- **The held-out set cannot discriminate.** All 10 held-out labels are `NOT_MATCH`, so a prompt that always answered `NOT_MATCH` would also score 10/10. The 10/10 shows only that neither prompt produced a false `MATCH` on clear negatives.
- **The labels are lopsided** (1 `MATCH` in 20). That is an honest result: most Anthropic postings ask for 5+ years. But it means the experiment measures mostly how well Claude rejects. A better design would have drawn more postings that pass Rules 1–4, so that more possible `MATCH`es were included. I fixed the selection before labeling, so I did not change it afterwards.
- **One person labeled each posting once,** and the labeling rule was drafted by Claude Code (disclosed). A second labeler might mark row 4 `NOT_MATCH`.
- **The results cover one model, one day and this persona.**
