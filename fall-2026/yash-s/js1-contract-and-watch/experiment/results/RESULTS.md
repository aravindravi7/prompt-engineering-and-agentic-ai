# Prompt experiment results

Every saved run in `experiment/results/`, oldest first. pass = the answer passes the validator AND its verdict matches my label; invalid, unavailable or disagreeing answers fail (FRICTIONAL.md, 'My Pass Definition').

| run | set | prompt (sha256) | model reported | passes | relevant | not relevant | invalid | unavailable | Claude said relevant, I said not | labels in set |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline (2026-10-31T06:34:30Z) | development | `judgment-v1.md` (`401f0f1f`) | claude-haiku-4-5-20251001, claude-sonnet-5-5 | **10/10** | 0 | 10 | 0 | 0 | 0 | not relevant 10 |
| revision (2026-10-31T06:41:20Z) | development | `judgment-v2.md` (`291bd93f`) | claude-haiku-4-5-20251001, claude-sonnet-5-5 | **10/10** | 0 | 10 | 0 | 0 | 0 | not relevant 10 |
| baseline (2026-10-31T06:41:56Z) | held_out | `judgment-v1.md` (`401f0f1f`) | claude-haiku-4-5-20251001, claude-sonnet-5-5 | **10/10** | 0 | 10 | 0 | 0 | 0 | not relevant 10 |
| revision (2026-10-31T06:42:37Z) | held_out | `judgment-v2.md` (`291bd93f`) | claude-haiku-4-5-20251001, claude-sonnet-5-5 | **9/10** | 0 | 9 | 1 | 0 | 0 | not relevant 10 |

## development: each posting, each run

| id | title | my label | baseline 2026-10-31T06:34 | revision 2026-10-31T06:41 |
|---|---|---|---|---|
| 8692962002 | Specialist Solutions Architect - Data Engineering & Warehousing (Financial Services) | not relevant | not relevant (pass) | not relevant (pass) |
| 7011263002 | PhD GenAI Research Scientist Intern | not relevant | not relevant (pass) | not relevant (pass) |
| 7803651002 | AI Transformation Leader | not relevant | not relevant (pass) | not relevant (pass) |
| 8739506002 | Specialist Solutions Architect - AWS Infrastructure & AI Platform | not relevant | not relevant (pass) | not relevant (pass) |
| 8546367002 | AI Engineer – Forward Deployed Engineering (AI FDE) | not relevant | not relevant (pass) | not relevant (pass) |
| 8756140002 | Senior Payroll Analyst | not relevant | not relevant (pass) | not relevant (pass) |
| 8301830002 | Senior Manager, Identity & Access Management (IAM) | not relevant | not relevant (pass) | not relevant (pass) |
| 8815669002 | Sr. Software Engineer - Ingestion Core team | not relevant | not relevant (pass) | not relevant (pass) |
| 8823193002 | Product Finance Director, R&D Capital Allocation & Engineering Operations | not relevant | not relevant (pass) | not relevant (pass) |
| 8903089002 | Strategic Core Account Executive - Automotive | not relevant | not relevant (pass) | not relevant (pass) |

## held_out: each posting, each run

| id | title | my label | baseline 2026-10-31T06:41 | revision 2026-10-31T06:42 |
|---|---|---|---|---|
| 6866538002 | Data Science Intern (2027 Start) | not relevant | not relevant (pass) | not relevant (pass) |
| 8697991002 | Specialist Solutions Architect - AI/ML | not relevant | not relevant (pass) | invalid (FAIL) |
| 8739507002 | Specialist Solutions Architect - Azure Infrastructure & AI Platform | not relevant | not relevant (pass) | not relevant (pass) |
| 8760167002 | AI Engineer – Forward Deployed Engineering (AI FDE), U.S. Public Sector (Federal Focus) | not relevant | not relevant (pass) | not relevant (pass) |
| 8859666002 | Data+AI Workforce Transformation Practitioner — Customer Delivery | not relevant | not relevant (pass) | not relevant (pass) |
| 8099343002 | Staff Software Engineer - Fullstack | not relevant | not relevant (pass) | not relevant (pass) |
| 8472398002 | Engineering Manager - Databricks SQL Control Plane | not relevant | not relevant (pass) | not relevant (pass) |
| 8628029002 | Strategic Core Account Executive | not relevant | not relevant (pass) | not relevant (pass) |
| 6328388002 | Solutions Architect - Emerging Enterprise (Startups) | not relevant | not relevant (pass) | not relevant (pass) |
| 8384595002 | Staff Software Engineer - Frontend (NYC) | not relevant | not relevant (pass) | not relevant (pass) |
