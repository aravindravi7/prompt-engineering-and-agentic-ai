# Sampling report (Chapter 1)

Five real Databricks postings. I asked Claude my prompt contract about each one in four fresh conversations and compared every answer with my own hand label.

**What was done by whom.** Yash ran the command on 2026-10-31. Claude wrote `experiment/sample.py`, and wrote this report's setup, results and limitations from the saved run record. The conclusions at the end are Yash's.

## Setup

| | |
|---|---|
| Run record | [`sampling/sampling-2026-10-31T063215Z.json`](sampling/sampling-2026-10-31T063215Z.json) (every answer, raw text included) and [`.md`](sampling/sampling-2026-10-31T063215Z.md) |
| When | 2026-10-31, 06:32:15–06:33:21 UTC (2:32–2:33 am Eastern) |
| Command | `python3 experiment/sample.py --repeats 4 --prompt prompts/judgment-v1.md --model claude-sonnet-5-5` |
| Prompt | `prompts/judgment-v1.md`, sha256 `401f0f1f656e…` |
| Model | requested `claude-sonnet-5-5`. Claude Code reported **both** `claude-sonnet-5-5` and `claude-haiku-4-5-20251001` on every call. Only model names were recorded, not tokens per model, so what Haiku did is not known. |
| Fresh conversations | Every call was a separate `claude -p` run with all tools off, no saved session, and a new empty folder (`judge.call_claude`). |
| Postings | The 5 sampling postings in `selection.json`: picked at random (seed 7375) from titles with a topic word, with no overlap with the 20 experiment postings |
| Labels | Mine, from `LABELING-SHEET.md` (sha256 `aaf13b1f…`), written before any Claude call. All 5 are `not relevant`. |
| Pass | An answer passes the validator **and** its verdict matches my label. Invalid, unavailable or disagreeing answers fail. Written before testing; see FRICTIONAL.md. |

## Results

| id | title | location | my label | run 1 | run 2 | run 3 | run 4 | passes |
|---|---|---|---|---|---|---|---|---|
| 8604579002 | Senior Finance Specialist (Data & AI) | Bengaluru, India | not relevant | not relevant | not relevant | not relevant | not relevant | 4/4 |
| 8688861002 | Accounting Data & Technology Manager | Mountain View / San Francisco, CA | not relevant | not relevant | not relevant | not relevant | not relevant | 4/4 |
| 8574655002 | AI Engineer - FDE (Forward Deployed Engineer) | Seoul, South Korea | not relevant | not relevant | not relevant | not relevant | not relevant | 4/4 |
| 5634684002 | Senior Data Scientist | Mountain View / San Francisco, CA | not relevant | not relevant | not relevant | not relevant | not relevant | 4/4 |
| 8578093002 | Engineering Manager - Data Visualization Platform | Bellevue, WA | not relevant | not relevant | not relevant | not relevant | not relevant | 4/4 |

**20 of 20 answers passed.** All 20 were valid, and none was invalid or unavailable.

## How much the answers varied

| What | Spread across the 4 runs of each posting |
|---|---|
| Verdict | None. Each posting got the same verdict in all 4 runs. |
| `matched_terms` | None. All 20 answers had an empty list. |
| `posting_fields` | None within any posting. |
| `resume_fields` | One posting varied. *AI Engineer - FDE* (8574655002) cited all six résumé fields in three runs and four fields in one run (no `skills.backend_automation` or `skills.database_cloud`). |
| Reason length | Varied: 326–646 characters. Per posting: 362–438, 461–593, 326–529, 468–646 and 406–546. |
| Deciding reasons | The same facts every time, in different words. Run 1, for example: *"The job title contains 'Senior', the posting requires 7+ years of experience… and the location is Bengaluru, India"* (8604579002). *"…the job is located in Seoul, South Korea, outside the United States"* (8574655002). *"The title contains 'Senior', which is an automatic exclusion"* (5634684002). |

Every answer and reason, word for word, is in the run record.

## What this shows and what it does not

**It shows** that on these 5 postings, with this prompt and this model on this night, Claude gave the same verdict 4 times out of 4, and that each verdict matched my label.

**It does not show:**
- **That Claude is correct in general.** Repeating a verdict shows repeatability, not correctness. The agreement here is with my labels, written by one person.
- **Anything about hard cases.** All 5 are clear-cut under my rule: each has a seniority word (Senior, Manager) or a non-US location (Bengaluru, Seoul). The borderline postings went to the prompt experiment, and my rule does not allow overlap.
- **Anything about "relevant" answers.** All 5 labels are `not relevant`, and Claude never answered `relevant`.
- **Stability over time.** That would need more than 4 runs, other days, or another model. All 20 calls ran within about one minute.
- **What the structured fields are worth.** The validator checked almost nothing here, because every answer had empty `matched_terms`. Yet **18 of the 20 reasons name at least one of Priya's skills** in free text, most often Databricks, then Python, SQL, MLflow and LangGraph. The validator does not check free text.

## My conclusions

I found that Claude gave the same relevance verdict for all 5 postings across 4 separate runs each.

All 20 answers were valid and matched my labels. However, the explanations were not exactly the same every time. In one case, Claude also changed which resume fields it listed.

I learned that getting the same verdict does not mean every part of the answer is consistent.

Since all 5 postings were not relevant and had clear reasons for rejection, I cannot conclude that Claude would be equally consistent on more difficult jobs or relevant positions.
