# Prompt experiment results

Every saved run in `experiment/results/`, oldest first. pass = the answer passes the validator AND its verdict matches my label; invalid, unavailable or disagreeing answers fail (FRICTIONAL.md, 'My Pass Definition').

| run | set | prompt (sha256) | model reported | passes | relevant | not relevant | invalid | unavailable | Claude said relevant, I said not | labels in set |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline (2026-10-31T06:34:30Z) | development | `judgment-v1.md` (`401f0f1f`) | claude-haiku-4-5-20251001, claude-sonnet-5-5 | **10/10** | 0 | 10 | 0 | 0 | 0 | not relevant 10 |

## development: each posting, each run

| id | title | my label | baseline 2026-10-31T06:34 |
|---|---|---|---|
| 8692962002 | Specialist Solutions Architect - Data Engineering & Warehousing (Financial Services) | not relevant | not relevant (pass) |
| 7011263002 | PhD GenAI Research Scientist Intern | not relevant | not relevant (pass) |
| 7803651002 | AI Transformation Leader | not relevant | not relevant (pass) |
| 8739506002 | Specialist Solutions Architect - AWS Infrastructure & AI Platform | not relevant | not relevant (pass) |
| 8546367002 | AI Engineer – Forward Deployed Engineering (AI FDE) | not relevant | not relevant (pass) |
| 8756140002 | Senior Payroll Analyst | not relevant | not relevant (pass) |
| 8301830002 | Senior Manager, Identity & Access Management (IAM) | not relevant | not relevant (pass) |
| 8815669002 | Sr. Software Engineer - Ingestion Core team | not relevant | not relevant (pass) |
| 8823193002 | Product Finance Director, R&D Capital Allocation & Engineering Operations | not relevant | not relevant (pass) |
| 8903089002 | Strategic Core Account Executive - Automotive | not relevant | not relevant (pass) |
